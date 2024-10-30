import csv
import logging
import os
import sys
from datetime import datetime
from typing import Set, Tuple

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, \
    StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)


class YahooFinanceCrawler:
    def __init__(self, region: str, driver_path: str, output_file: str = None):
        self.region = region.lower()
        self.driver_path = driver_path
        if not os.path.exists("extract_data"):
            os.makedirs("extract_data")
        sanitized_region = self.region.replace(" ", "_")
        self.output_file = output_file or os.path.join(
            "extract_data",
            f"finance_data_{sanitized_region}_{datetime.now().strftime('%m%d%Y')}.csv",
        )
        self.url = "https://finance.yahoo.com/screener/new"
        self.driver = self._init_driver()
        self.data: Set[Tuple[str, str, str]] = set()
        logging.info(f"Crawler inicializado para a região: {self.region}")

    def _init_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        logging.info("Driver do Chrome inicializado em modo headless")
        return driver

    def fetch_data(self) -> None:
        logging.info(f"Acessando a URL: {self.url}")
        self.driver.get(self.url)
        self._unselect_default_region()
        if not self._apply_region_filter():
            logging.error(
                f"Filtro de região '{self.region}' não encontrado. Encerrando o programa.")
            self.close()
            sys.exit()
        logging.info("Iniciando extração de dados")
        self._extract_data()
        logging.info("Extração de dados concluída")
        self._save_to_csv()

    def _unselect_default_region(self) -> None:
        try:
            filter_area = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[data-test='label-filter-list']"))
            )
            region_button = filter_area.find_element(By.CSS_SELECTOR,
                                                     "[data-icon='new']")
            region_button.click()

            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "dropdown-menu"))
            )
            menu = self.driver.find_element(By.ID, "dropdown-menu")

            us_checkbox = WebDriverWait(menu, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     "//span[contains(text(), 'United States')]/../input[@type='checkbox']")
                )
            )
            self.driver.execute_script("arguments[0].click();", us_checkbox)
            logging.info("Região padrão 'United States' desmarcada")

            close_button = menu.find_element(By.CLASS_NAME, "close")
            close_button.click()
        except NoSuchElementException:
            logging.warning(
                "Não foi possível desmarcar 'United States' no filtro padrão.")

    def _apply_region_filter(self) -> bool:
        try:
            filter_area = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[data-test='label-filter-list']"))
            )
            for _ in range(3):
                try:
                    region_button = filter_area.find_element(By.CSS_SELECTOR,
                                                             "[data-icon='new']")
                    region_button.click()
                    WebDriverWait(self.driver, 15).until(
                        EC.visibility_of_element_located(
                            (By.ID, "dropdown-menu"))
                    )
                    break
                except StaleElementReferenceException:
                    filter_area = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                    "[data-test='label-filter-list']"))
                    )
            menu = self.driver.find_element(By.ID, "dropdown-menu")
            soup = BeautifulSoup(menu.get_attribute("innerHTML"), "html.parser")
            country_elements = soup.find_all("span", string=True)
            available_countries = {
                country.text.strip().lower(): country.text.strip() for country
                in country_elements
            }
            if self.region not in available_countries:
                logging.error(
                    f"Região '{self.region}' não está na lista de países disponíveis. Encerrando o programa.")
                self.close()
                sys.exit()
            country_original_name = available_countries[self.region]
            logging.info(f"Selecionando o país: {country_original_name}")
            self._select_region(menu, country_original_name)
            find_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[data-test='find-stock']"))
            )
            find_button.click()
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.ID, "screener-results"))
            )
            logging.info("Filtro de região aplicado com sucesso")
            return True
        except (NoSuchElementException, TimeoutException,
                StaleElementReferenceException) as e:
            logging.error(f"Erro ao tentar aplicar o filtro de região: {e}")
            return False

    def _select_region(self, menu, country_name: str) -> None:
        checkbox = menu.find_element(
            By.XPATH,
            f"//span[contains(text(), '{country_name}')]/../input[@type='checkbox']"
        )
        checkbox.click()
        close_button = menu.find_element(By.CLASS_NAME, "close")
        close_button.click()
        logging.info(f"Região '{country_name}' selecionada")

    def _extract_data(self) -> None:
        page_number = 1
        while True:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.ID, "screener-results"))
                )
                logging.info(f"Extraindo dados da página {page_number}")
                self._parse_page_data()
                next_button = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "//span/span[contains(text(), 'Next')]/ancestor::button"))
                )
                self.driver.execute_script("arguments[0].click();", next_button)
                page_number += 1
            except TimeoutException:
                logging.info(
                    "Todas as páginas foram extraídas ou o botão 'Next' não está mais disponível")
                break
            except StaleElementReferenceException:
                logging.warning(
                    "Elemento 'Next' ficou stale, tentando recarregar o botão 'Next' para continuar")
                continue

    def _parse_page_data(self) -> None:
        results = self.driver.find_element(By.ID, "screener-results")
        soup = BeautifulSoup(results.get_attribute("innerHTML"), "html.parser")
        table = soup.find("tbody")
        rows = table.find_all("tr") if table else []
        for row in rows:
            cols = row.find_all("td")
            if cols:
                stock_data = (cols[0].text.strip(), cols[1].text.strip(),
                              cols[2].text.strip())
                self.data.add(stock_data)
        logging.info(f"{len(rows)} ações foram extraídas nesta página")

    def _save_to_csv(self) -> None:
        with open(self.output_file, "w", newline="",
                  encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile,
                                    fieldnames=["symbol", "name", "price"])
            writer.writeheader()
            for symbol, name, price in self.data:
                writer.writerow(
                    {"symbol": symbol, "name": name, "price": price})
        logging.info(f"Dados salvos em {self.output_file}")

    def close(self) -> None:
        self.driver.quit()
        logging.info("Driver fechado e execução finalizada")
