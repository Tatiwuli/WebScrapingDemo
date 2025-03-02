from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
import time
import re


class SeleniumExtractPostsTool():
    def __init__(self, selectors):
        self.selectors = selectors

    def extract_page_one_url(self, driver):
        self.driver = driver
        success = False
        blog_url = None  # Ensure blog_url is defined
        error_message = ""  # Store error message if any

        try:
            # Locate blog items
            blog_items = driver.find_elements(
                by=self.selectors['blog_item']['selector'],
                value=self.selectors['blog_item']['value']
            )

            if not blog_items:
                error_message = "No blog items found on the page."
                print(f"⚠️ {error_message}")
                return success, error_message

        except Exception as e:
            error_message = f"Error finding blog item: {e}"
            print(f"⚠️ {error_message}")
            return success, error_message

        # Process only the first blog item
        for blog_item in blog_items[:1]:
            try:
                blog_url_element = blog_item.find_element(
                    by=self.selectors['blog_url']['selector'], value=self.selectors['blog_url']['value']
                )
                blog_url = blog_url_element.get_attribute('href')

                # Extract date
                blog_date_element = blog_item.find_element(
                    by=self.selectors['blog_date']['selector'], value=self.selectors['blog_date']['value']
                )

                success = True  # ✅ Mark success only after URL extraction succeeds
                break  # ✅ Stop after successfully processing the first blog item

            except Exception as e:
                error_message = f"Error finding elements inside blog item: {e}"
                print(f"⚠️ {error_message}")
                continue  # ✅ Do not return early, try processing another item

        return success, error_message if not success else ""


    def extract_page_urls(self, driver):
        """ Extract blog posts' url and date from a single page """

        self.driver = driver
        posts_data = []  # Collect data across all pages
        unique_urls = set()

        try:

            # Locate blog items
            print("🔎 Locating a blog item ...")
            blog_items = driver.find_elements(
                by=self.selectors['blog_item']['selector'],
                value=self.selectors['blog_item']['value']
            )

        except Exception as e:
            print(f"⚠️ Error finding blog item: {e}")
            return posts_data, e

        print("\n 🎉 Located the blog item!")
        for blog_item in blog_items:
            try:
                # Extract URL
                print("🔎 Locating the blogs' urls...")
                blog_url_element = blog_item.find_element(
                    by=self.selectors['blog_url']['selector'], value=self.selectors['blog_url']['value']
                )
                blog_url = blog_url_element.get_attribute('href')
                print("\n 🎉 Located the blogs' urls!")

                if not blog_url or blog_url in unique_urls:
                    continue  # Skip duplicates
                unique_urls.add(blog_url)

                # Extract date
                print("🔎 Locating the blogs' date..")
                blog_date_element = blog_item.find_element(
                    by=self.selectors['blog_date']['selector'], value=self.selectors['blog_date']['value']
                )
                blog_date_text = blog_date_element.text.strip()
                blog_date = self.process_date(blog_date_text)
                print("\n 🎉 Located the blogs' dates!\n")

                # Append post data
                posts_data.append({
                    "url": blog_url,
                    "date": blog_date
                })
                print(f"🔗 Collected blog: {blog_url}, Date: {blog_date}")

            except Exception as e:
                print(f"⚠️ Error processing blog item: {e}")
                continue

        return posts_data, ""

    def change_page(self, page_num, driver):
        """Navigate to the specified page."""
        success = False

        try:
            # Check if we need to close banner
            self.close_cookie_banner(driver)
            # Prepare the value for next_page_button selector
            next_page_button_dict = self.selectors["next_page_button"]
            next_page_selector_template = next_page_button_dict["value"]
            next_page_selector_value = next_page_selector_template.format(
                page_num=str(page_num))

            
            next_page_button = driver.find_element(
                by=next_page_button_dict["selector"], value=next_page_selector_value)
            print("\n🎉 Located the button to change to next page")

            time.sleep(5)

            next_page_button.click()
            print("\n🎉 Changed to next page")

            time.sleep(1)
            success = True
            return success, ""

        except Exception as e:
            print(f"⚠️ Error navigating to page {page_num}: {e}")
            return success, e

    def __call__(self, driver, time_range_days=None):
        """
       Extracting URLs page-by-page while ensuring that only posts within the time_range_days are collected.
        """
        all_data = []  # Collect valid data across all pages
        page_num = 1

        # Define the time_range_days threshold
        threshold_date = datetime.now(
            # 1 day by default
        ) - timedelta(days=time_range_days) if time_range_days else 1

        while True:
            print(f"\nScraping Page {page_num}...")

            # Extract data from the current page
            page_data, empty_error = self.extract_page_urls(driver)

            # Filter posts based on time_range_days if provided
            if time_range_days:
                page_data = [
                    post for post in page_data
                    if post["date"] and post["date"] >= threshold_date
                ]

                if not page_data:
                    print(
                        f"\nNo valid posts found on page {page_num}. Stopping scraping.")
                    break

            all_data.extend(page_data)

            # Move to the next page
            success = self.change_page(
                page_num=page_num + 1,
                driver=driver
            )
            if not success:
                break  # Exit if no more pages

            page_num += 1

        print(f"\n 🎉 Scraping completed. Total pages scraped: {page_num}")
        print(f"\n Total blogs collected: {len(all_data)}")

        return all_data

    @staticmethod
    def process_date(date_text):
        """Convert raw date text into a datetime object."""
        date_regex = re.compile(
            r"(\d+)\s*天前|(\d+)\s*小時前|(\d{4})年(\d{1,2})月(\d{1,2})日"
        )
        match = date_regex.search(date_text)
        if match:
            if match.group(1):  # Days ago
                return datetime.now() - timedelta(days=int(match.group(1)))
            elif match.group(2):  # Hours ago
                return datetime.now() - timedelta(hours=int(match.group(2)))
            elif match.group(3):  # Absolute date
                year, month, day = int(match.group(3)), int(
                    match.group(4)), int(match.group(5))
                return datetime(year, month, day)
        return None

    @staticmethod
    def close_cookie_banner(driver):
        """Close the cookie banner if present."""
        try:
            # check if banner appears first
            cookie_banner = driver.find_element(
                "css selector", ".dialog.floating")
        except NoSuchElementException:
            print("Cookie banner not found. Proceeding...")
            return
        # If there's a cookie banner
        try:
            # Close it
            print("🔴 Cookie banner detected. Closing it...")
            close_button = driver.find_element(
                "css selector", "button[aria-label='close cookie message']")
            print("🔴 Cookie button detected. Closing it...")
            close_button.click()

            time.sleep(2)  # Wait for the banner to close

        except Exception as e:
            print(f"⚠️ Error closing cookie banner: {e}")
