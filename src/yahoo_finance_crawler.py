import csv
import time
from datetime import datetime
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import sys


class YahooFinanceCrawler:
    def __init__(self, region: str, driver_path: str, output_file: str = None):
        self.region = region.lower()  # Normaliza `region` para minúsculas para comparação
        self.driver_path = driver_path
        # Nome do arquivo CSV no formato `finance_data_<region>_MMDDYYYY.csv`
        self.output_file = output_file or f"finance_data_{self.region}_{datetime.now().strftime('%m%d%Y')}.csv"
        self.url = "https://finance.yahoo.com/screener/new"
        self.driver = self._init_driver()
        self.data: List[Dict[str, str]] = []

    def _init_driver(self):
        service = Service(self.driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def fetch_data(self) -> None:
        self.driver.get(self.url)
        if not self._apply_region_filter():
            print(
                f"Filtro de região '{self.region}' não encontrado. Encerrando o programa.")
            self.close()
            sys.exit()

        self._extract_data()
        self._save_to_csv()

    def _apply_region_filter(self) -> bool:
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

            # Extrai a lista de países disponíveis usando BeautifulSoup
            soup = BeautifulSoup(menu.get_attribute("innerHTML"), "html.parser")
            country_elements = soup.find_all("span", string=True)

            # Cria um dicionário para armazenar os países com minúsculas para comparação e os nomes originais
            available_countries = {
                country.text.strip().lower(): country.text.strip() for country
                in country_elements}

            # Verifica se `region` está na lista de países disponíveis (em minúsculas)
            if self.region not in available_countries:
                print(
                    f"Região '{self.region}' não está na lista de países disponíveis. Encerrando o programa.")
                self.close()
                sys.exit()  # Encerra o programa se o país não estiver disponível

            # Obtemos o nome original do país para clicar no checkbox
            country_original_name = available_countries[self.region]
            print(f"Selecionando o país: {country_original_name}")

            self._unselect_default_region(menu)
            self._select_region(menu, country_original_name)

            find_button = self.driver.find_element(By.CSS_SELECTOR,
                                                   "[data-test='find-stock']")
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "[data-test='find-stock']")))
            find_button.click()

            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "screener-results")))
            return True
        except (NoSuchElementException, TimeoutException):
            return False

    def _unselect_default_region(self, menu) -> None:
        try:
            us_checkbox = menu.find_element(
                By.XPATH,
                f"//span[contains(text(), 'United States')]/../input[@type='checkbox']",
            )
            us_checkbox.click()
        except NoSuchElementException:
            pass

    def _select_region(self, menu, country_name: str) -> None:
        checkbox = menu.find_element(
            By.XPATH,
            f"//span[contains(text(), '{country_name}')]/../input[@type='checkbox']",
        )
        checkbox.click()
        close_button = menu.find_element(By.CLASS_NAME, "close")
        close_button.click()

    def _extract_data(self) -> None:
        more_data = True
        while more_data:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(
                        (
                            By.XPATH,
                            "//span/span[contains(text(), 'Next')]/ancestor::button",
                        )
                    )
                )
                self._parse_page_data()

                next_button = self.driver.find_element(
                    By.XPATH,
                    "//span/span[contains(text(), 'Next')]/ancestor::button"
                )
                if next_button.is_enabled():
                    self.driver.execute_script("arguments[0].click();",
                                               next_button)
                    time.sleep(1)
                else:
                    more_data = False
            except TimeoutException:
                more_data = False

    def _parse_page_data(self) -> None:
        results = self.driver.find_element(By.ID, "screener-results")
        soup = BeautifulSoup(results.get_attribute("innerHTML"), "html.parser")
        table = soup.find("tbody")
        rows = table.find_all("tr") if table else []

        for row in rows:
            cols = row.find_all("td")
            if cols:
                stock_data = {
                    "symbol": cols[0].text.strip(),
                    "name": cols[1].text.strip(),
                    "price": cols[2].text.strip(),
                }
                self.data.append(stock_data)

    def _save_to_csv(self) -> None:
        with open(self.output_file, "w", newline="",
                  encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile,
                                    fieldnames=["symbol", "name", "price"])
            writer.writeheader()
            writer.writerows(self.data)
        print(f"Dados salvos em {self.output_file}")

    def close(self) -> None:
        self.driver.quit()
