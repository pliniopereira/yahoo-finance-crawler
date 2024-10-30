import os
import shutil
import unittest
from unittest.mock import MagicMock, patch

from parameterized import parameterized
from selenium.common.exceptions import NoSuchElementException

from src.yahoo_finance_crawler import YahooFinanceCrawler


class TestYahooFinanceCrawler(unittest.TestCase):
    def setUp(self):
        self.driver_path = "/usr/local/bin/chromedriver"
        self.region = "Argentina"
        self.crawler = YahooFinanceCrawler(
            region=self.region, driver_path=self.driver_path
        )
        self.crawler.driver = MagicMock()
        self.test_output_dir = "test_output"
        os.makedirs(self.test_output_dir, exist_ok=True)
        self.sample_data = [
            {
                "symbol": "AMX.BA",
                "name": "América Móvil, S.A.B. de C.V.",
                "price": "2089.00",
            },
            {
                "symbol": "NOKA.BA",
                "name": "Nokia Corporation",
                "price": "557.50",
            },
        ]

    @patch("src.yahoo_finance_crawler.YahooFinanceCrawler._parse_page_data")
    def test_extract_data_structure_valid_data(self, mock_parse_page_data):
        self.crawler.data = self.sample_data
        self.crawler._parse_page_data()

        for row in self.crawler.data:
            self.assertIn("symbol", row)
            self.assertIn("name", row)
            self.assertIn("price", row)
            self.assertIsInstance(row["symbol"], str)
            self.assertIsInstance(row["name"], str)
            self.assertIsInstance(row["price"], str)

    @parameterized.expand([(True, True), (False, False)])
    @patch("src.yahoo_finance_crawler.YahooFinanceCrawler._apply_region_filter")
    def test_filter_region(
        self, return_value, expected, mock_apply_region_filter
    ):
        mock_apply_region_filter.return_value = return_value
        result = self.crawler._apply_region_filter()
        self.assertEqual(result, expected)

    @patch("src.yahoo_finance_crawler.YahooFinanceCrawler._select_region")
    def test_filter_region_fail(self, mock_select_region):
        mock_select_region.side_effect = NoSuchElementException
        result = self.crawler._apply_region_filter()
        self.assertFalse(result)

    def test_save_to_csv_structure(self):
        self.crawler.data = self.sample_data
        header = ["symbol", "name", "price"]
        expected_csv_data = [
            header,
            ["AMX.BA", "América Móvil, S.A.B. de C.V.", "2089.00"],
            ["NOKA.BA", "Nokia Corporation", "557.50"],
        ]

        csv_data = [header] + [
            [row["symbol"], row["name"], row["price"]]
            for row in self.crawler.data
        ]
        self.assertEqual(csv_data, expected_csv_data)

    def test_handle_partial_data(self):
        self.crawler.data = [
            {
                "symbol": "AMX.BA",
                "name": "América Móvil, S.A.B. de C.V.",
                "price": "",
            },
            {"symbol": "", "name": "Nokia Corporation", "price": "557.50"},
        ]
        header = ["symbol", "name", "price"]
        expected_csv_data = [
            header,
            ["AMX.BA", "América Móvil, S.A.B. de C.V.", ""],
            ["", "Nokia Corporation", "557.50"],
        ]

        csv_data = [header] + [
            [row.get("symbol", ""), row.get("name", ""), row.get("price", "")]
            for row in self.crawler.data
        ]
        self.assertEqual(csv_data, expected_csv_data)

    def test_handle_empty_data(self):
        self.crawler.data = []
        header = ["symbol", "name", "price"]
        expected_csv_data = [header]

        csv_data = [header] + [
            [row.get("symbol", ""), row.get("name", ""), row.get("price", "")]
            for row in self.crawler.data
        ]
        self.assertEqual(csv_data, expected_csv_data)

    @patch("src.yahoo_finance_crawler.YahooFinanceCrawler.close")
    def test_close_browser(self, mock_close):
        self.crawler.close()
        mock_close.assert_called_once()

    def tearDown(self):
        self.crawler.close()
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)


if __name__ == "__main__":
    unittest.main()
