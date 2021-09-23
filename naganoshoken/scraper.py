import pandas as pd
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select

from .driver import prepare_driver


class Scraper:
    def __init__(
        self,
        shiten_num: str,
        koza_num: str,
        password: str,
        headless=True,
    ):
        self.shiten_num = shiten_num
        self.koza_num = koza_num
        self.password = password
        self.driver = prepare_driver(headless=headless)

    def __del__(self):
        if self.driver is not None:
            self.driver.quit()

    def phase01_jump_to_login_page(self):
        self.driver.get("https://naganosec.co.jp/trade/e-service/")
        login_btn = self.driver.find_element_by_xpath('//div[@class="es_login_box"]/a')
        login_btn.click()

    def phase02_fill_login_page_form(self):
        shop_input = self.driver.find_element_by_xpath('//input[@name="shop"]')
        shop_input.send_keys(self.shiten_num)
        customer_input = self.driver.find_element_by_xpath('//input[@name="customer"]')
        customer_input.send_keys(self.koza_num)
        pass_input = self.driver.find_element_by_xpath('//input[@name="pass"]')
        pass_input.send_keys(self.password)
        login_btn = self.driver.find_element_by_xpath('//div[@class="cmn-btn-area"]/a')
        login_btn.click()

    def phase03_jump_to_shisanmeisai_page(self):
        main_frame = self.driver.find_element_by_xpath(
            '//frameset[@id="main-fs"]/frame[@id="main-fm"]'
        )
        self.driver.switch_to.frame(main_frame)
        shisankanri_btn = self.driver.find_element_by_xpath(
            '//div[@id="nav"]/ul/li[2]/a'
        )
        shisankanri_btn.click()
        shisanmeisai_btn = self.driver.find_element_by_xpath(
            '//div[@id="nav"]/ul/li[2]/ul/li[1]'
        )
        shisanmeisai_btn.click()

    def phase04_load_shisanmeisai_table(self) -> pd.DataFrame:
        sel_hyouji = Select(
            self.driver.find_element_by_xpath('//select[@name="sel_hyouji"]')
        )
        sel_hyouji.select_by_index(3)

        rows = []
        while True:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            for tr_soup in (
                soup.find("table", {"class": "custody"}).find("tbody").find_all("tr")
            ):
                row = [
                    td_soup.text.strip().replace(",", "")
                    for td_soup in tr_soup.find_all("td")
                ]
                rows.append(row)
            try:
                next_btn = self.driver.find_element_by_xpath(
                    '//a[@class="pager-btn next-active"]'
                )
            except NoSuchElementException:
                next_btn = None
            if next_btn:
                next_btn.click()
            else:
                break

        df = pd.DataFrame(
            data=rows,
            columns=["商品", "銘柄名(コース)", "預り数量", "評価単価", "評価金額(円)", "取得金額(円)", "評価損益(円)"],
        )
        numcols = ["預り数量", "評価単価", "評価金額(円)", "取得金額(円)", "評価損益(円)"]
        for col in numcols:
            df[col] = df[col].apply(lambda it: float("nan") if it == "-" else float(it))
        return df

    def run(self) -> pd.DataFrame:
        self.phase01_jump_to_login_page()
        self.phase02_fill_login_page_form()
        self.phase03_jump_to_shisanmeisai_page()
        df = self.phase04_load_shisanmeisai_table()
        return df
