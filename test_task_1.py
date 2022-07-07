import os
import sys
import time

import requests
import win32com.client as client
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import unittest


class test_task1(unittest.TestCase):

    def setUp(self) -> None:
        working_directory = os.getcwd()
        _chrome_driver_path = working_directory + "//" + "chromedriver.exe"
        self.jenkins_url = '192.168.0.117:8080'
        self.email = str(os.getenv('Email'))
        self.place = str(os.getenv('City'))
        self.chromeOptions = webdriver.ChromeOptions()
        self.chromeOptions.add_argument("--ignore-certificate-error")
        self.chromeOptions.add_argument("--ignore-ssl-errors")
        self.chromeOptions.headless = False
        self.prefs = {'safebrowsing.enabled': 'false'}
        self.chromeOptions.add_experimental_option("prefs", self.prefs)
        self.driver = webdriver.Chrome(chrome_options=self.chromeOptions,
                                       executable_path=rf'{_chrome_driver_path}')
        self.driver.implicitly_wait(time_to_wait='4000')
        self.driver.get('https://www.accuweather.com/')
        self.driver.maximize_window()

    def test_get_temperature(self):
        try:
            _place = self.place
            self.wait_until_element_visible(elem="//div[@class='searchbar-content']//form//input")
            self.driver.find_element(By.XPATH, value="//div[@class='searchbar-content']//form//input").send_keys(
                _place)
            user_data = self.driver.find_elements(By.XPATH,
                                                  value="//div[@class='results-container']//div[contains(@class,"
                                                        "'search-bar-result')]")
            for data in user_data:
                if _place in data.text:
                    data.click()
            self.wait_until_element_visible(elem="//p[contains(@class,'weather-card__subtitle')]")
            city = self.get_text_from_element(elem="//h1[@class='header-loc']")
            assert _place in city, f"{_place} is not shown as per user search"
            _time = self.get_text_from_element(elem="//p[contains(@class,'weather-card__subtitle')]")
            _current_temperature = self.get_text_from_element(elem="(//div[contains(@class,'weather-card__panel "
                                                                   "details-container')]//div/span)[2]")
            _air_quality = self.get_text_from_element(
                elem="(//div[contains(@class,'weather-card__panel details-container')]//div/span)[4]")
            _winds = self.get_text_from_element(elem="(//div[contains(@class,'weather-card__panel "
                                                     "details-container')]//div/span)[6]")
            _winds_gusts = self.get_text_from_element(elem="(//div[contains(@class,'weather-card__panel "
                                                           "details-container')]//div/span)[8]")
            print(_place, _time, _current_temperature, _air_quality, _winds, _winds_gusts)

            self.sending_email(_place, _time, _current_temperature, _air_quality, _winds, _winds_gusts)
        except:
            print(sys.exc_info())
            self.driver.quit()

    def wait_until_element_visible(self, elem, delay=60) -> None:
        try:
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, elem)))
            print("Page is ready!")
        except TimeoutException as e:
            print(e)
            self.driver.quit()

    def get_text_from_element(self, elem) -> str:
        return self.driver.find_element(By.XPATH, value=str(elem)).text

    def sending_email(self, _place, _time, _current_temperature, _air_quality, _winds, _winds_gusts) -> None:

        jenkins_url = self.get_jenkins_console()

        body_pattern = "Hi,\n\n" \
                       f"\tCurrent Time: {_time}\t\n" \
                       f"\tCurrent Temperature: {_current_temperature}\t\n" \
                       f"\tAir_Quality : {_air_quality}\t\n" \
                       f"\tWinds : {_winds}\t\n" \
                       f"\tWinds Gusts : {_winds_gusts}\t\n\n" \
                       f"\t{jenkins_url}" \
                       "This is an autogenerated email"

        _outlook_instance = client.Dispatch('Outlook.Application')
        _message = _outlook_instance.CreateItem(0)
        _message.To = self.email
        _message.Subject = f"Today {_place} Weather Reports"
        _message.Body = body_pattern
        _message.Save()
        _message.Send()

    def get_jenkins_console(self):
        build_number = os.getenv('BUILD_NUMBER')
        job_name = 'Get Temperature'
        build_console_url = 'http://{}/job/{}/{}/consoleFull/'.format(self.jenkins_url, job_name, build_number)
        return build_console_url

    def tearDown(self) -> None:
        self.driver.quit()
