from src.yahoo_finance_crawler import YahooFinanceCrawler

if __name__ == "__main__":
    # Defina o caminho para o ChromeDriver
    driver_path = "/usr/local/bin/chromedriver"

    # Crie uma instância do crawler para a região desejada (Argentina)
    crawler = YahooFinanceCrawler(region="Argentina", driver_path=driver_path)

    try:
        # Busca os dados e salva em um arquivo CSV
        crawler.fetch_data()
    finally:
        # Feche o navegador
        crawler.close()
