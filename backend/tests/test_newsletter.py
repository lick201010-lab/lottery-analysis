import tempfile
import unittest

from app.routers.newsletter import NewsletterSubscribeRequest, save_subscriber


class NewsletterSubscribeTest(unittest.TestCase):
    def test_invalid_email_is_rejected(self):
        with self.assertRaises(ValueError):
            NewsletterSubscribeRequest(email="not-an-email")

    def test_subscribe_normalizes_and_deduplicates_email(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            db_path = f"{tmp}/newsletter.db"
            email = NewsletterSubscribeRequest(email=" User@Example.COM ").email
            first = save_subscriber(email, db_path)
            second = save_subscriber("user@example.com", db_path)

            self.assertEqual(first, "subscribed")
            self.assertEqual(second, "already_subscribed")
            self.assertEqual(email, "user@example.com")


if __name__ == "__main__":
    unittest.main()
