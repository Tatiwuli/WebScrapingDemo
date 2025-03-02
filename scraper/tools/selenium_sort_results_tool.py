from selenium.webdriver.common.keys import Keys
import time
from typing import Tuple


# This class use Selenium to click on a drop down menu and sort by Date

class SeleniumSortResultsTool():
    def __init__(self, selectors):
        self.selectors = selectors

    def __call__(self, driver):
        """Output the sorted searched page's URL."""
        self.driver = driver
        success = False
        # Locate the drop down menu element and click
        try:
            print("\n🔎 Locating the dropdown menu for sorting...")
            dropdown_menu = self.driver.find_element(

                by=self.selectors['sort_dropdown']['selector'], value=self.selectors['sort_dropdown']['value'])

            print("\n 🎉 Located the menu!")
            # open the dropdown menu
            dropdown_menu.click()
            print("\n ✅Clicked")
            
            time.sleep(1)
            
        except Exception as e:
            print("Dropdown exception", e)
        
            return success, e

        # Locate the option and click
        try:
            time.sleep(5)
            print("🔎 Locating the sorting by Date option...")
            date_sort_option = self.driver.find_element(
                by=self.selectors['sort_date_option']['selector'], value=self.selectors['sort_date_option']['value'])
            
            print("\n 🎉 Located the Date option!")
            # click on the sort option
            date_sort_option.click()
            print("\n ✅Clicked")

            # wait to sort the results
            time.sleep(3)
            success = True
            return success, ""

        except Exception as e:
            print("date sort exception", e)
            return success, e
