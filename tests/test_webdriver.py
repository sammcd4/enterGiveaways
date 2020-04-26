import unittest
import sys
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class TestWebDriver(unittest.TestCase):

    def test_headless(self):
        chrome_options = Options()
        # chrome_options.add_argument("--disable-extensions")
        if 'win' in sys.platform:
            chrome_options.add_argument("--disable-gpu")

        if 'linux' in sys.platform:
            chrome_options.add_argument("--no-sandbox")

        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        driver.close()

    def test_chrome(self):
        driver = selenium.webdriver.Chrome()
        driver.close()

    def test_firefox(self):
        driver = webdriver.Firefox()
        driver.close()

    def test_chrome_no_automation_switches(self):
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=chrome_options)
        driver.close()

    def test_chrome_incognito(self):
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        driver = webdriver.Chrome(options=chrome_options)
        driver.close()


if __name__ == '__main__':
    unittest.main()