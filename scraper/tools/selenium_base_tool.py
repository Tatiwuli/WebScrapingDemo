
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

"""This is a Abstract base class for Selenium-based tools, providing shared utilities, including driver initialization, 
    URL handling, and controlled driver management during the scraping process with Selenium"""

class BaseSeleniumTool(ABC):
    def __init__(self, driver=None):
        self.driver = driver

    def init_driver(self):
        if not self.driver:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
            options = Options()
            options.add_argument(f'user-agent={user_agent}')
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=options
            )
        return self.driver

    def get_url(self, url: str):
        self.driver.set_page_load_timeout(10)
        try:
            self.driver.get(url)
        except:
            self.driver.execute_script("window.stop();")

    # only close driver when it's initialized by the tool
    def close_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"⚠️ Error closing driver: {e}")
            finally:
                self.driver = None
