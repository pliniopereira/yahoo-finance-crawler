import unittest
from unittest.mock import MagicMock, patch
from src.yahoo_finance_crawler import YahooFinanceCrawler
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os


class TestYahooFinanceCrawler(unittest.TestCase):
    def setUp(self):
        # Definindo o caminho do ChromeDriver e a região
        self.driver_path = "/usr/local/bin/chromedriver"
        self.region = "Argentina"

        # Criando uma instância do crawler com mocks
        self.crawler = YahooFinanceCrawler(
            region=self.region, driver_path=self.driver_path
        )
        self.crawler.driver = MagicMock()

    @patch("src.yahoo_finance_crawler.YahooFinanceCrawler._parse_page_data")
    def test_extract_data_structure_valid_data(self, mock_parse_page_data):
        self.crawler.data = [
            {
                "symbol": "AMX.BA",
                "name": "América Móvil, S.A.B. de C.V.",
                "price": "2089.00",
            },
            {"symbol": "NOKA.BA", "name": "Nokia Corporation", "price": "557.50"},
        ]
        self.crawler._parse_page_data()
        self.assertEqual(len(self.crawler.data), 2)
        self.assertIn("symbol", self.crawler.data[0])
        self.assertIn("name", self.crawler.data[0])
        self.assertIn("price", self.crawler.data[0])

    @patch("src.yahoo_finance_crawler.YahooFinanceCrawler._apply_region_filter")
    def test_filter_region_success(self, mock_apply_region_filter):
        # Mock para simular um filtro de região bem-sucedido
        mock_apply_region_filter.return_value = True
        result = self.crawler._apply_region_filter()
        self.assertTrue(result)

    @patch("src.yahoo_finance_crawler.YahooFinanceCrawler._select_region")
    def test_filter_region_fail(self, mock_select_region):
        # Mock para simular uma falha ao selecionar a região (lançando NoSuchElementException)
        mock_select_region.side_effect = NoSuchElementException

        # Executa o método e verifica se ele retorna False ao capturar a exceção
        result = self.crawler._apply_region_filter()
        self.assertFalse(
            result,
            "O método _apply_region_filter deveria retornar False ao falhar na seleção da região.",
        )

    def test_save_to_csv(self):
        # Dados simulados para teste
        self.crawler.data = [
            {
                "symbol": "AMX.BA",
                "name": "América Móvil, S.A.B. de C.V.",
                "price": "2089.00",
            },
            {"symbol": "NOKA.BA", "name": "Nokia Corporation", "price": "557.50"},
        ]

        # Salva os dados simulados em um CSV
        self.crawler._save_to_csv()

        # Verifica se o arquivo CSV foi criado corretamente
        filename = f"yahoo_finance_data_{self.region}.csv"
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Verifica se o CSV tem o cabeçalho e os dados corretos
        self.assertEqual(lines[0].strip(), "symbol,name,price")
        self.assertTrue(
            "AMX.BA" in lines[1]
            and "América Móvil, S.A.B. de C.V." in lines[1]
            and "2089.00" in lines[1]
        )
        self.assertTrue(
            "NOKA.BA" in lines[2]
            and "Nokia Corporation" in lines[2]
            and "557.50" in lines[2]
        )

        # Remove o arquivo de teste após a verificação
        os.remove(filename)

    def test_handle_partial_data(self):
        # Testa o comportamento quando alguns campos estão vazios
        self.crawler.data = [
            {"symbol": "AMX.BA", "name": "América Móvil, S.A.B. de C.V.", "price": ""},
            {"symbol": "", "name": "Nokia Corporation", "price": "557.50"},
        ]
        self.crawler._save_to_csv()
        filename = f"yahoo_finance_data_{self.region}.csv"

        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.assertEqual(len(lines), 3)  # Cabeçalho + 2 linhas de dados
        os.remove(filename)

    @patch("src.yahoo_finance_crawler.YahooFinanceCrawler.close")
    def test_close_browser(self, mock_close):
        self.crawler.close()
        mock_close.assert_called_once()

    def tearDown(self):
        # Fechar o navegador e limpar dados após cada teste
        self.crawler.close()


if __name__ == "__main__":
    unittest.main()
