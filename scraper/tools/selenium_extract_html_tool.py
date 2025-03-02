import time
from .selenium_base_tool import BaseSeleniumTool


class SeleniumExtractHtmlTool(BaseSeleniumTool):
    def __init__(self):
        super().__init__()

    def __call__(self, url: str) -> str:
        self.driver = self.init_driver()
        self.get_url(url=url)
        time.sleep(3)

        # Scroll to the bottom of the page to load all content
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        html = self.driver.page_source

        self.close_driver()
        return html
