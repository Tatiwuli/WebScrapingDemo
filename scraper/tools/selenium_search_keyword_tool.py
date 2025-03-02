from selenium.webdriver.common.keys import Keys
import time
from typing import Tuple



class SeleniumSearchKeywordTool():
    def __init__(self, selectors):
        self.selectors = selectors

    def __call__(self, driver, keyword):
        """Output the searched page's URL."""

        self.driver = driver 
        
        # Locate the search bar element and type the keyword
        search_bar_selector = self.selectors['search_bar']['selector']
        search_bar_value = self.selectors['search_bar']['value']

        try:
       
            print(f"\n🔎 Starting searching for {keyword} with these selectors: {search_bar_selector}, {search_bar_value}")
            
            search_bar = self.driver.find_element(
                by=search_bar_selector, value=search_bar_value)
            
            search_bar.send_keys(keyword)
            # Press "Enter" to submit the search
            search_bar.send_keys(Keys.RETURN)
            print("✅ Submitted search")
            result_page_url = self.driver.current_url
            return result_page_url, ""
        
        except Exception as e:
            return None, e
    
       