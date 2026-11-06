#!/usr/bin/env python3
"""Checks for Mark Six fetch: HKJC mapping, lottery.hk parse, and a hard deadline."""
import http.server
import json
import socket
import threading
import time
import unittest
from unittest import mock

import fetch_marksix


FIXTURE_HTML = """
<table>
  <tr>
    <td>26/115</td>
    <td>27/10/2026</td>
    <td>
      <ul class="balls">
        <li>2</li><li>4</li><li>18</li><li>21</li><li>24</li><li>47</li>
        <li class="ball -plus">31</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>26/114</td>
    <td>24/10/2026</td>
    <td>
      <ul class="balls">
        <li>9</li><li>25</li><li>26</li><li>28</li><li>44</li><li>45</li>
        <li class="ball -plus">20</li>
      </ul>
    </td>
  </tr>
</table>
"""


class ParseDrawsTest(unittest.TestCase):
    def test_known_draws(self):
        draws = fetch_marksix.parse_lottery_hk_draws(FIXTURE_HTML)
        self.assertEqual(
            draws,
            [
                {
                    "draw_number": "26/115",
                    "draw_date": "2026-10-27",
                    "numbers": [2, 4, 18, 21, 24, 47],
                    "special_number": 31,
                    "source": "lottery.hk",
                },
                {
                    "draw_number": "26/114",
                    "draw_date": "2026-10-24",
                    "numbers": [9, 25, 26, 28, 44, 45],
                    "special_number": 20,
                    "source": "lottery.hk",
                },
            ],
        )

    def test_missing_table_is_a_clear_error(self):
        with self.assertRaises(ValueError):
            fetch_marksix.parse_lottery_hk_draws("<html><body>no results</body></html>")


class FetchDeadlineTest(unittest.TestCase):
    def test_silent_peer_hits_the_deadline(self):
        """A peer that accepts and never answers must not block past the deadline."""
        listener = socket.socket()
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]
        held = []

        def _accept():
            conn, _ = listener.accept()
            held.append(conn)
            time.sleep(30)

        thread = threading.Thread(target=_accept, daemon=True)
        thread.start()
        started = time.monotonic()
        try:
            with self.assertRaises(fetch_marksix.FetchDeadlineExceeded):
                fetch_marksix.fetch_html(
                    f"http://127.0.0.1:{port}/",
                    connect_timeout=10,
                    read_timeout=30,
                    deadline=2,
                )
            elapsed = time.monotonic() - started
            self.assertLess(elapsed, 5, f"fetch blocked for {elapsed:.1f}s")
        finally:
            for conn in held:
                conn.close()
            listener.close()

    def test_retries_fail_fast_with_a_clear_message(self):
        started = time.monotonic()
        with self.assertRaises(RuntimeError):
            fetch_marksix.with_retries(
                "local-refused",
                lambda: fetch_marksix.fetch_html(
                    "http://127.0.0.1:9/",
                    connect_timeout=1,
                    read_timeout=1,
                    deadline=2,
                ),
                attempts=2,
                backoff_seconds=0,
            )
        self.assertLess(time.monotonic() - started, 8)


class LocalPageTest(unittest.TestCase):
    def test_successful_page_is_returned(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                body = FIXTURE_HTML.encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, fmt, *args):
                return

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            html = fetch_marksix.fetch_html(
                f"http://127.0.0.1:{server.server_address[1]}/",
                connect_timeout=2,
                read_timeout=2,
                deadline=5,
            )
            draws = fetch_marksix.parse_lottery_hk_draws(html)
            self.assertEqual(draws[0]["draw_number"], "26/115")
            json.dumps(draws)
        finally:
            server.shutdown()


class HkjcGraphqlTest(unittest.TestCase):
    def test_maps_result_draws_and_skips_open_draws(self):
        payload = {
            "data": {
                "lotteryDraws": [
                    {
                        "year": "2026",
                        "no": 116,
                        "drawDate": "2026-10-31T21:30:00+08:00",
                        "status": "Result",
                        "drawResult": {
                            "drawnNo": ["1", "2", "3", "4", "5", "6"],
                            "xDrawnNo": "7",
                        },
                    },
                    {
                        "year": "2026",
                        "no": 117,
                        "drawDate": "2026-11-04",
                        "status": "Open",
                        "drawResult": None,
                    },
                ]
            }
        }

        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return payload

        class FakeSession:
            def mount(self, *args, **kwargs):
                return None

            def post(self, url, timeout, headers, json):
                self.url = url
                self.body = json
                self.headers = headers
                return FakeResponse()

            def close(self):
                return None

        fake = FakeSession()
        with mock.patch.object(fetch_marksix, "_session", return_value=fake):
            draws = fetch_marksix.fetch_hkjc_draws()

        self.assertEqual(
            draws,
            [
                {
                    "draw_number": "26/116",
                    "draw_date": "2026-10-31",
                    "numbers": [1, 2, 3, 4, 5, 6],
                    "special_number": 7,
                    "source": "hkjc-graphql",
                }
            ],
        )
        self.assertEqual(fake.url, fetch_marksix.HKJC_URL)
        self.assertEqual(fake.body["operationName"], "marksixResult")
        self.assertEqual(fake.body["variables"], {"lastNDraw": fetch_marksix.HKJC_LAST_N})
        self.assertIn("fragment lotteryDrawsFragment", fake.body["query"])

    def test_graphql_errors_are_rejected(self):
        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {"errors": [{"message": "WHITELIST_ERROR"}]}

        class FakeSession:
            def mount(self, *args, **kwargs):
                return None

            def post(self, *args, **kwargs):
                return FakeResponse()

            def close(self):
                return None

        with mock.patch.object(fetch_marksix, "_session", return_value=FakeSession()):
            with self.assertRaises(ValueError):
                fetch_marksix.fetch_hkjc_draws()


if __name__ == "__main__":
    unittest.main()
