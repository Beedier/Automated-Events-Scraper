import unittest
from datetime import datetime, timedelta
from library import get_dates_info, get_relative_dates, get_date_range_info

class TestDateFunctions(unittest.TestCase):

    def test_get_dates_info(self):
        # Test with default behavior (including week_start and month_start)
        result = get_dates_info()
        self.assertIn("today", result)
        self.assertIn("month_end", result)
        self.assertIn("week_end", result)
        self.assertIn("month_str", result)
        self.assertIn("week_start", result)
        self.assertIn("month_start", result)

        # Test with exclude week_start and month_start
        result = get_dates_info(include_week_start=False, include_month_start=False)
        self.assertNotIn("week_start", result)
        self.assertNotIn("month_start", result)

    def test_get_relative_dates(self):
        # Test for 5 days from today
        result = get_relative_dates(5)
        expected_date = (datetime.today() + timedelta(days=5)).strftime("%Y-%m-%d")
        self.assertEqual(result["relative_date"], expected_date)

        # Test for -5 days from today (negative case)
        result = get_relative_dates(-5)
        expected_date = (datetime.today() - timedelta(days=5)).strftime("%Y-%m-%d")
        self.assertEqual(result["relative_date"], expected_date)

    def test_get_date_range_info_valid(self):
        # Test valid date range input
        date_range = "01 January 2025 – 31 January 2025"
        result = get_date_range_info(date_range)
        self.assertEqual(result["start_date"], "20250101")
        self.assertEqual(result["end_date"], "20250131")

    def test_get_date_range_info_invalid(self):
        # Test invalid date format
        date_range = "Invalid Date Range"
        result = get_date_range_info(date_range)
        self.assertIsNone(result)

    def test_edge_case_leap_year(self):
        # Test leap year handling
        date_range = "28 February 2024 – 01 March 2024"
        result = get_date_range_info(date_range)
        self.assertEqual(result["start_date"], "20240228")
        self.assertEqual(result["end_date"], "20240301")

    def test_edge_case_month_end(self):
        # Test month-end scenario (e.g., month ending on a weekend)
        dates_info = get_dates_info()
        month_end = datetime.strptime(dates_info["month_end"], "%Y-%m-%d")
        self.assertEqual(month_end.month, datetime.today().month)
        self.assertTrue(month_end.day <= 31)

    def test_get_dates_info_for_current_month(self):
        # Test the previous month scenario
        dates_info = get_dates_info()
        today = datetime.today()
        self.assertEqual(dates_info["month_str"], today.strftime("%b-%Y"))

if __name__ == '__main__':
    unittest.main()
