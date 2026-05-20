import unittest

from app.routers.analysis import _build_hot_cold_layer1_pool


class LayeredPickLogicTest(unittest.TestCase):
    def test_builds_pool_from_requested_hot_and_cold_counts(self):
        appearance_count = {
            1: 10,
            2: 9,
            3: 8,
            4: 7,
            5: 6,
            6: 5,
            7: 4,
            8: 3,
            9: 2,
            10: 1,
        }

        result = _build_hot_cold_layer1_pool(
            appearance_count=appearance_count,
            max_reg=10,
            complex_size=7,
            hot_count=3,
            cold_count=2,
            hot_pct=60,
        )

        self.assertEqual(result["hot_numbers"], [1, 2, 3])
        self.assertEqual(result["cold_numbers"], [9, 10])
        self.assertEqual(result["supplement_numbers"], [4, 5])
        self.assertEqual(result["pool"], [1, 2, 3, 4, 5, 9, 10])


if __name__ == "__main__":
    unittest.main()
