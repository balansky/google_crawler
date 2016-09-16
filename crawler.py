from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import time
import random
import re


class RobotCheckException(Exception):

    def __init__(self, err_code):
        self.err_code = err_code

    def __str__(self):
        return "robot check error"

class GoogleCrawler():


    def __init__(self, proxy_ip):
        self.search_url = "https://www.google.com/shopping?hl=zh-CN"
        self.og_search = 0
        self.proxy = self.__set_proxy_ip(proxy_ip)
        self.__init_driver()


    def __init_driver(self):
        fp = webdriver.FirefoxProfile()
        self.driver = webdriver.Firefox(proxy=self.proxy, firefox_profile=fp)
        self.driver.maximize_window()
        self.driver.set_page_load_timeout(120)
        self.__nav_to_page("https://www.google.com")


    def __nav_to_page(self,eoru):

        time.sleep(0.5)

        self.validate_driver_page()

        if isinstance(eoru,WebElement):
            eoru.click()
        elif isinstance(eoru, str):
            self.driver.get(eoru)

        time.sleep(0.5)

        self.validate_driver_page()

    def validate_driver_page(self):
        sorry_text = self.driver.title
        if re.search(r'\bsorry\b', sorry_text, re.IGNORECASE):
            raise RobotCheckException(0)
        elif re.search(r'https://www.google.com/.*', sorry_text, re.IGNORECASE):
            raise RobotCheckException(1)


    def __set_proxy_ip(self, proxy_ip):
        proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': proxy_ip,
            'ftpProxy': proxy_ip,
            'sslProxy': proxy_ip,
            'noProxy': '',
        })
        return proxy

    def __find_list_elements(self):
        view_elements = self.driver.find_elements(By.XPATH,"//div[@class='sh-pr__product-results']"
                                                           "/div[contains(@class,'psgi')]/div/div/a")
        if not view_elements:
            menu_item = self.driver.find_element(By.XPATH, "//div[@id='stt__ps-view-m']/div[2]")
            view_url = "https://www.google.com" + menu_item.get_attribute("data-url")
            self.__nav_to_page(view_url)
            time.sleep(1)
            view_elements = self.driver.find_elements(By.XPATH,"//div[@class='sh-pr__product-results']"
                                                           "/div[contains(@class,'psgi')]/div/div/a")
        return view_elements


    def ___parse_description(self,ele):
        try:
            more_btn = ele.find_element_by_xpath(".//a[@class='sh-ds__pspo-fade sh-ds__toggle sh-ds__flt']")
            more_btn.click()
            description = ele.find_element_by_xpath(".//span[@class='sh-ds__full-txt']").text
        except NoSuchElementException:
            description = ele.find_element_by_xpath(".//span[@class='sh-ds__trunc-txt']").text
        return description


    def __parse_detail(self):
        product_detail = {}
        try:
            time.sleep(2)
            psgi = self.driver.find_element(By.XPATH, "//div[@class='g psgi active']")
            psgi_id = psgi.get_attribute("data-docid")
            detail_node = self.driver.find_element(By.XPATH,"//div[@class='pspo-popout pspo-gpop' "
                                                            "and @data-docid='{0}']".format(psgi_id))
            product_detail['goods_title'] = detail_node.find_element_by_xpath(".//a[@class='sh-t__title']").text
            product_detail['goods_url'] = detail_node.find_element_by_xpath(".//a[@class='sh-t__title']").get_attribute("href")
            product_detail['goods_main_image_url'] = detail_node.find_element_by_xpath(".//img").get_attribute("src")
            product_detail['goods_description'] = self.___parse_description(detail_node)
            return product_detail
        except Exception as err:
            # print(str(err))
            pass
        return {}

    def __crawl_page_products(self):
        page_products = []
        list_prod_elements = self.__find_list_elements()
        if list_prod_elements:
            for ele in list_prod_elements:
                ele.click()
                product = self.__parse_detail()
                time.sleep(random.random()*2 + 1)
                if product:
                    page_products.append(product)
        return page_products


    def search_keyword(self,keyword):
        time.sleep(1 + random.random())
        try:
            if self.og_search == 0:
                self.og_search = 1
                raise Exception()
            input_ele = self.driver.find_element_by_id('lst-ib')
            search_btn = self.driver.find_element(By.XPATH,"//div[@id='sblsbb']/button")
            input_ele.clear()
        except Exception:
            self.__nav_to_page(self.search_url)
            input_ele = self.driver.find_element_by_id('gbqfq')
            search_btn = self.driver.find_element(By.XPATH,"//div[@id='gbqfbw']/button")
        input_ele.send_keys(keyword)
        self.__nav_to_page(search_btn)



    def crawl_products_info(self,page):
        try:
            if page < 2:
                return self.__crawl_page_products()
            else:
                curr_page = self.driver.find_element(By.XPATH, "//table[@id='nav']//td[@class='cur']").text
                if curr_page != str(page):
                    page_btn = self.driver.find_element(By.XPATH, "//table[@id='nav']//td"
                                                                  "/a[@class='fl' and @aria-label='Page {0}']".format(page))
                    self.__nav_to_page(page_btn)
                return self.__crawl_page_products()
        except NoSuchElementException:
            return []
