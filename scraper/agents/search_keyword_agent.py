from string import Template

from scraper.agents.base_agent import BaseAgent
from scraper.tools import SeleniumExtractHtmlTool, SeleniumSearchKeywordTool


ROLE = "HTML expert"
BACKSTORY = f"""
You are an {ROLE} tasked with identifying CSS selectors and their values within HTML content provided.

Your responsibility is to locate and extract CSS selectors for specific components of a webpage, ensuring they are formatted for direct use with Selenium.
Your output helps Selenium locate and interact with these specified webpage components accurately.
"""

GOAL = """
Your goal is to produce output in this specific JSON format: 
{
    'component_name' : {
      "selector": "xxx",
      "value": "xxx"
    }
}

Rules:
- Use only the following selector types in your output: ["id", "name", "xpath", "link text", "tag name", "class name", "css selector"].
- Do not include any additional explanations, comments, or code blocks in your output.
- Format your response precisely according to the JSON structure provided

Example:
{
    "search_bar": {
        "selector": "name",
        "value": "q"
    }
}
"""

user_prompt_template = Template(
    """
Given the following html of a webpage content, identify the CSS selector and value for the 'search_bar' component,
where Selenium can type in the keywords and perform search. Please return your output in the exact JSON format specified.

Following is the previous failed cases, including the failed selector type, selector value, and error message.
Please take them into consideration when identifying the CSS selector and value for the 'search_bar' component. 
Failed cases:
${failed_experiences}

HTML content:
${cleaned_html}
"""
)


class SearchKeywordAgent(BaseAgent):
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
            "aside",
            "article",
            "section",
        ]
        self.extract_html_tool = SeleniumExtractHtmlTool()

    def learn(self, driver, url: str, keyword: str):
        success = False
        retries = 0
        while retries < self.max_retry_times:
            print(f"\n Learning for the {retries+1} time..")
            # Fetch and clean HTML content
            html_content = self.extract_html_tool(url=url)
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
            print("\n🤖 Search Agent output: ", selectors)

           
            selector_type = selectors["search_bar"]["selector"]
            selector_value = selectors["search_bar"]["value"]
            print(
                f"\n 🤖 Identified selector type: {selector_type}")
            print(
                f"\n 🤖 Identified selector value: {selector_value}")

            # Perform search
            print("\nTesting the selectors with Selenium...")
            self.search_keyword_tool = SeleniumSearchKeywordTool(selectors)
            result_page_url, error_message = self.search_keyword_tool(
                driver=driver,
                keyword=keyword,
            )
            if result_page_url and (error_message == "") and (result_page_url != url):
                # save the successful result to knowledge base
                print(
                    "🎉\n Search is successfuly completed! These selectors are correct")

                knowledge_structure = {
                    "search_section": selectors
                }
                self.knowledge_base.save_knowledge(
                    new_url=url, knowledge_dict=knowledge_structure
                )
                print("\n✅ Saved the selectors into knowledge")
                success = True
                break
            else:
                print("⚠️ The selectors are incorrect")
                # save the failed result to memory
                failed_memory = f"selector_type: {selector_type}, selector_value: {
                    selector_value}, error_message: {error_message}"
                self.memory.append_memory(failed_memory=failed_memory)
                retries += 1
                print(
                    f"\nRetrying... Attempt {retries}/{self.max_retry_times} reties")

        return success, result_page_url
