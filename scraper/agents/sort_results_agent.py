from string import Template

from scraper.agents.base_agent import BaseAgent
from scraper.tools import SeleniumSortResultsTool, SeleniumExtractHtmlTool


ROLE = "HTML expert"
BACKSTORY = f"""
You are a {ROLE} tasked with analyzing HTML content to locate elements for web automation.
You identify CSS selectors and values that locate a dropdown menu and options within them, which can be used in Selenium to automate clicks.
You should focus on finding the essential and stable selectors that will enable Selenium to directly interact with these elements.
"""

GOAL = """
Your goal is to produce output in the specified JSON format. The JSON output should contain selectors and values for both:
1. The dropdown menu container that needs to be clicked to open the menu.
2. The specific option within the dropdown menu that matches a target text specified in the user prompt.

**JSON Format:**

{
  "sort_dropdown": {
    "selector": "xxx",
    "value": "xxx" (CSS selector value to locate and click the dropdown **menu**)
  },
  "sort_date_option": {
    "selector": "xxx",
    "value": "xxx" (CSS selector value to locate and click the specific option within the dropdown menu)
  }
}

**Notes:**
- Use only one of these selector types: "id", "name", "xpath", "css selector", "class name".
- For the dropdown menu, **ensure that the selector accurately locates the clickable element that opens the menu**, not just the currently selected option.
- The specific sorting option should be an interactive element that matches the target text in the user prompt.
- If you cannot find a stable dropdown or option, use "none" for both the selector and value.
- Return the output in JSON format, strictly following the structure above.
"""


user_prompt_template = Template(
    """
Given the following html of a webpage content, identify the CSS selector and value for the dropdown menu and the sort options components,
where Selenium can click on the dropdown, and select the date to sort. Please return your output in the exact JSON format specified.

Following is the previous failed cases, including the failed selector type, selector value, and error message.
Please take them into consideration when identifying the CSS selector and values for the  dropdown menu and the sort options components,
Failed cases:
${failed_experiences}

HTML content:
${cleaned_html}
"""
)


class SortResultsAgent(BaseAgent):
    def __init__(self, llm_model_name: str = "gpt-4o", max_retry_times: int = 3):
        BaseAgent.__init__(
            self,
            role=ROLE,
            backstory=BACKSTORY,
            goal=GOAL,
            llm_model_name=llm_model_name,
            pydantic_format=None,
        )
        self.max_retry_times = max_retry_times
        self.ignored_tags = [
            "script",
            "footer",
            "style",
            "iframe",
            "a",
            "meta"
        ]

        self.extract_html_tool = SeleniumExtractHtmlTool()

    def learn(self, driver,  result_page_url: str, url: str):
        success = False
        retries = 0
        while retries < self.max_retry_times:
            print(f"\n Learning for the {retries+1} time...")
            # Fetch and clean HTML content
            html_content = self.extract_html_tool(url=result_page_url)
            cleaned_html = self.clean_html(html_content)

            # Retrieve the previous failed experiences
            failed_experiences = self.memory.export_memory()

            # Locate CSS selectors and values with LLM
            user_prompt = user_prompt_template.substitute(
                cleaned_html=cleaned_html, failed_experiences=failed_experiences
            )
            selectors = self.llm(
                system_prompt=self.system_prompt, user_prompt=user_prompt
            )
            print("\n🤖 Sort Agent output: ", selectors)

            dropdown_info = selectors.get("sort_dropdown", {})
            dropdown_selector = dropdown_info.get("selector")
            dropdown_value = dropdown_info.get("value")
            sort_option_info = selectors.get("sort_date_option", {})
            sort_option_selector = sort_option_info.get("selector")
            sort_option_value = sort_option_info.get("value")

            print(
                f"\n 🤖 Identified dropdown selector and value: {dropdown_selector} {dropdown_value}")
            print(
                f"\n 🤖 Identified sort option selector and value: {sort_option_selector}, {sort_option_value}")

            # Sort results
            print("\nTesting the selectors with Selenium...")
            sort_results_tool = SeleniumSortResultsTool(selectors)
            success, error_message = sort_results_tool(
                driver=driver
            )

            # If error message is empty and the selected_option is true
            if success == True and error_message == "":
                print(
                    "🎉\nSort is successfuly completed! These selectors are correct")

                # save the successful result to knowledge base
                knowledge_structure = {
                    "sort_section": selectors
                }
                
                self.knowledge_base.save_knowledge(
                    new_url=url, knowledge_dict=knowledge_structure
                )
                print("\n✅ Saved the selectors into knowledge")
                
                break
            else:
                # save the failed result to memory
                print("\n⚠️ The selectors are incorrect")
                failed_memory = f"""
                        dropdown_selector: {dropdown_selector}, dropdown_value: {dropdown_value},
                        sort_option_selector: {sort_option_selector}, sort_option_value: {sort_option_value}
                        """
                self.memory.append_memory(failed_memory=failed_memory)
                retries += 1
                print(
                    f"\n Retrying... Attempt {retries}/{self.max_retry_times} reties")

        return success
