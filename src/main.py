import logging

from yahoo_finance_crawler import YahooFinanceCrawler

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Lista de países disponíveis para referência:
# COUNTRIES = [
#     "Argentina", "Austria", "Australia", "Belgium", "Brazil", "Canada",
#     "Switzerland", "Chile", "China", "Czechia", "Germany", "Denmark",
#     "Estonia", "Egypt", "Spain", "Finland", "France", "United Kingdom",
#     "Greece", "Hong Kong SAR China", "Hungary", "Indonesia", "Ireland",
#     "Israel", "India", "Iceland", "Italy", "Japan", "South Korea", "Kuwait",
#     "Sri Lanka", "Lithuania", "Latvia", "Mexico", "Malaysia", "Netherlands",
#     "Norway", "New Zealand", "Peru", "Philippines", "Pakistan", "Poland",
#     "Portugal", "Qatar", "Romania", "Russia", "Saudi Arabia", "Sweden",
#     "Singapore", "Suriname", "Thailand", "Turkey", "Taiwan", "United States",
#     "Venezuela", "Vietnam", "South Africa",
# ]


def main():
    driver_path = "/usr/local/bin/chromedriver"

    region = input(
        "Digite a região para a extração de dados (ex: Brazil): "
    ).title()

    logging.info(f"Iniciando o processo de extração para {region}.")
    crawler = YahooFinanceCrawler(region=region, driver_path=driver_path)

    try:
        crawler.fetch_data()
        logging.info(
            f"Processo de extração para {region} concluído com sucesso."
        )
    except Exception as e:
        logging.error(f"Ocorreu um erro ao processar {region}: {e}")
    finally:
        crawler.close()
        logging.info("Navegador fechado.")


if __name__ == "__main__":
    main()
