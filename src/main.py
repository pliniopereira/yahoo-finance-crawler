import logging
import time

from selenium.common.exceptions import WebDriverException

from src.yahoo_finance_crawler import YahooFinanceCrawler

# Configuração de logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

MAX_RETRIES = 3
RETRY_DELAY = 10


def main():
    # Defina o caminho para o ChromeDriver
    driver_path = "/usr/local/bin/chromedriver"
    region = "argentiNa"

    # Crie uma instância do crawler
    crawler = YahooFinanceCrawler(region=region, driver_path=driver_path)
    retries = 0

    while retries < MAX_RETRIES:
        try:
            logging.info("Iniciando o processo de extração de dados.")
            crawler.fetch_data()
            logging.info("Processo de extração concluído com sucesso.")
            break
        except Exception as e:
            logging.error(f"Ocorreu um erro inesperado durante a execução: {e}")
            break
        finally:
            crawler.close()
            logging.info("Navegador fechado.")


if __name__ == "__main__":
    main()
