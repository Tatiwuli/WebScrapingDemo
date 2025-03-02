from scraper.agents.base_agent import BaseAgent
from scraper.tools import SeleniumExtractPostsTool, SeleniumExtractHtmlTool
from string import Template

ROLE = "HTML expert"
BACKSTORY = f"""
You are a {ROLE} that identify css selectors and values that locate a button that it's clickable and
when it's clicked, it switches to the next page of the search results in a website
You prioritize finding essential and stable selectors that enable Selenium to directly and accuratedly 
locate the blogs and scrape their information 
"""
GOAL = """
Your goal is to produce output in the specified JSON format. 
Please note that if there is a number that represent the page number in the selector value, please replace
this number with `{page_num}` as a placeholder.

**JSON Format:**

{

 "next_page_button": {
    "selector": "xxx",
    "value": "xxx"
  }
}

**Notes:**
- Use only one of these selector types: "id", "name", "xpath", "css selector", "class name".
- The next_page_button should be clickable for Selenium.
- IF there is an explicit number in the found value, replace it with  `{page_num}` as a placeholder . So, that Selenium can dynamically insert numbers.
- If you cannot find a stable tag, use "none" for both the selector and value.
- Only include the most unique and stable parts of the class names that are likely to remain consistent across pages. Avoid responsive, hover, or state-specific classes
- Return the output in JSON format, strictly following the structure above.

"""

user_prompt_template = Template("""
Given the following HTML, extract CSS selectors for next_page_button. Return in a valid JSON format for direct use by Selenium.
Following is the previous failed cases, including the failed selector type, selector value, and error message.
Please take them into consideration when identifying the CSS selector and values for the next_page_button.
Failed cases:
${failed_experiences}

HTML Content:                                                                
${cleaned_html}
""")


class ChangePageAgent(BaseAgent):
    def __init__(self, llm_model_name="gpt-4o", max_retry_times: int = 3):
        BaseAgent.__init__(
            self, role=ROLE, backstory=BACKSTORY,
            goal=GOAL,
            llm_model_name=llm_model_name,
            pydantic_format=None,
        )
        self.max_retry_times = max_retry_times
        self.ignored_tags = ['script', 'style',
                             'nav', 'footer', 'meta', 'header']

        self.extract_html_tool = SeleniumExtractHtmlTool()

    def learn(self, driver, result_page_url: str, url: str):
        """Learn the CSS selectors to change page."""
        success = False
        retries = 0
        while retries < self.max_retry_times:
            print(f"\n Learning for the {retries+1} time..")
            html_content = self.extract_html_tool(url=result_page_url)
            cleaned_html = self.clean_html(html_content)

            # Retrieve the previous failed experiences
            failed_experiences = self.memory.export_memory()

            user_prompt = user_prompt_template.substitute(failed_experiences=failed_experiences,
                                                          cleaned_html=cleaned_html)

            selectors = self.llm(
                system_prompt=self.system_prompt, user_prompt=user_prompt)
            print("\n🤖 ChangePage Agent output: ", selectors)

            # Initialize the tool for changing page
            print("\nTesting the selectors with Selenium...")
            extract_posts_tool = SeleniumExtractPostsTool(selectors=selectors)
            # Change a few pages
            for times in range(2):
                success, error_message = extract_posts_tool.change_page(
                    page_num=1 + times,
                    driver=driver  # use the shared driver with sort results
                )

            if error_message == "":
                print(
                    "🎉\n Changing one page is successfuly completed! These selectors are correct")

                knowledge_structure = {
                    "extract_posts_section": selectors

                }
                self.knowledge_base.save_knowledge(
                    new_url=url,  knowledge_dict=knowledge_structure
                )
                print("\n✅ Saved the selectors into knowledge")
                success = True
                break
            # If Selenium fails to change page
            else:
                print("\n⚠️ The selectors are incorrect")
                # Save the failed result to memory
                next_page_button = selectors["next_page_button"]
                failed_memory = f"next_page_button: {next_page_button}"
                self.memory.append_memory(failed_memory=failed_memory)
                retries += 1
                print(
                    f"\nRetrying... Attempt {retries}/{self.max_retry_times} reties")

        
        return success
