from typing import Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys 

from scraper.tools import SeleniumExtractPostsTool, SeleniumSearchKeywordTool, SeleniumSortResultsTool
from scraper.agents import SearchKeywordAgent, SortResultsAgent, ExtractResultsAgent, ChangePageAgent
from scraper.knowledge import KnowledgeBase


"""This class automates web scraping by leveraging Selenium and AI-powered agents 
    to inspect, search, sort, and extract relevant data from a website."""

class MarketScraper:
    def __init__(self, home_url: str, keyword:str):
        self.driver = None
        self.home_url = home_url
        self.keyword = keyword
        

    def init_driver(self):

        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        options = Options()
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-blink-features=AutomationControlled")

        #options.add_argument("--headless=new")
       

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        print("Shared driver initialized.")
        time.sleep(3)

    def get_url(self, url: str):
        self.driver.set_page_load_timeout(10)
        try:
            self.driver.get(url)
        except:
            self.driver.execute_script("window.stop();")

    def close_driver(self):
        time.sleep(2)
        if self.driver:
            try:
                self.driver.quit()
                print("\nShared driver closed successfully.")
            except Exception as e:
                print(f"\n⚠️Error closing shared driver: {e}")
        time.sleep(2)

    def get_tools(self, knowledge: Dict):
        """Initialize the Selenium tools by mapping the respective HTML tags from knowledge folder"""
        tools = {}
        tool_mapping_table = {
            "search_section": SeleniumSearchKeywordTool,
            "sort_section": SeleniumSortResultsTool,
            "extract_posts_section": SeleniumExtractPostsTool
        }

        for section_name, section_data in knowledge['sections'].items():
            # Get the tool class for the current section
            tool_class = tool_mapping_table.get(section_name)

            if not tool_class:
                print(f"⚠️ Unknown section: {section_name}. Skipping it")
                continue

            # Initialize the tool and store it in the tools dictionary

            tools[section_name] = tool_class(selectors=section_data)
           
        return tools
        
    def inspect_html(self):
        """Use LLM to inspect HTML tags for search, sort, extract, and change pages."""
        search_agent = SearchKeywordAgent()
        sort_agent = SortResultsAgent()
        extract_agent = ExtractResultsAgent()
        change_page_agent = ChangePageAgent()

        print("\n🔍 [STEP 1] Inspecting HTML Tags for Search...")
        success, result_page_url = search_agent.learn(
            url=self.home_url, keyword=self.keyword, driver=self.driver)

        result_page_url = self.driver.current_url
        self.close_driver()

        if not success:
            print(
                "⚠️ [ERROR] Search HTML inspection failed. Human intervention required.")
            return False

        print("✅ [SUCCESS] Search HTML tags successfully inspected.")
        print(f"🔗 [INFO] Result Page URL: {result_page_url}\n")

        print("🚀 [STEP 2] Initializing a new driver for the next steps...")
        self.init_driver()
        self.get_url(result_page_url)

        print("\n🔍 [STEP 3] Inspecting HTML Tags for Sorting...")
        sort_success = sort_agent.learn(
            url=self.home_url, result_page_url=result_page_url, driver=self.driver)

        if not sort_success:
            print(
                "⚠️ [ERROR] Sorting HTML inspection failed. Human intervention required.")
            return False

        print("✅ [SUCCESS] Sorting HTML tags successfully inspected.\n")

        print("🔍 [STEP 4] Inspecting HTML Tags for Extracting Results...")
        extract_success = extract_agent.learn(
            url=self.home_url, result_page_url=result_page_url, driver=self.driver)

        if not extract_success:
            print(
                "⚠️ [ERROR] Extracting Results HTML inspection failed. Human intervention required.")
            return False

        print("✅ [SUCCESS] Extracting Results HTML tags successfully inspected.\n")

        print("🔍 [STEP 5] Inspecting HTML Tags for Changing Pages...")
        change_page_success = change_page_agent.learn(
            url=self.home_url, result_page_url=result_page_url, driver=self.driver)

        if not change_page_success:
            print(
                "⚠️ [ERROR] Changing Pages HTML inspection failed. Human intervention required.")
            return False

        print("✅ [SUCCESS] Changing Pages HTML tags successfully inspected.\n")

        print("🎯 [COMPLETED] HTML inspection process finished successfully!")
        return True


    def extract_urls(self,tools,  time_range_days):

        posts_urls = None
        # search
        if "search_section" in tools:
            search_function =  tools['search_section']
            print(f"🔎 Searching for {self.keyword}\n")

            search_function(driver=self.driver, keyword= self.keyword)

        # initiate another driver for skipping captcha
        result_page_url = self.driver.current_url

        print(f"\n🔗Result page url: {result_page_url}")
        self.close_driver()

        print(f"\nStarting a new driver for Sorting")
        self.init_driver()


        self.get_url(result_page_url)

        # sort
        if "sort_section" in tools:

            sort_function = tools['sort_section']
            print(f"\n🗃️ Sorting results\n")

            sort_function(driver=self.driver)

        # extract results
        if "extract_posts_section" in tools:

            extract_posts_function = tools['extract_posts_section']
            print(f"\n🕸️ Extracting results\n")

            # Call the tool's __call__ method directly
            posts_data = extract_posts_function(
                driver=self.driver,
                time_range_days=time_range_days
            )

            posts_urls = [post_data['url'] for post_data in posts_data]

        return posts_urls
    
    def scrape(self, time_range_days=3):
        """Manages and Executes the full scraping process, including knowledge retrieval, 
        HTML inspection, and data extraction."""

        print("Starting scraping.....")

        self.init_driver()
        self.get_url(self.home_url)
        
        #Retrieve Knowledge
        knowledge_base = KnowledgeBase(self.home_url)
        knowledge = knowledge_base.search_knowledge()
        if not knowledge:
            print("\n There is no knowledge for this website.")
            print("🤖 Triggering agents to inspect the HTML")
            
            
            inspect_success = self.inspect_html() 
            if inspect_success == False:
                print("❌ Inspection failed! Human intervention required. Stopping execution.")
                self.close_driver()  
                sys.exit(1)  

            print("\n🎉 Successfuly learned all the HTML tags to scrape this website!")

        #Search Knowledge again after inspecting 
        knowledge = knowledge_base.search_knowledge()

        print("\nUpdating knowledge and preparing the tools to scrape 🧰")
        tools = self.get_tools(knowledge)
        print("\nScraping the website 🕸️")
        posts_urls = self.extract_urls(tools= tools,
             time_range_days=time_range_days)
        print("\nFinished Scraping the Website 🥳🥳")
        print(posts_urls)

        self.close_driver()

        return posts_urls

