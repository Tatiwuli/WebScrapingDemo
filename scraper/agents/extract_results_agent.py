from scraper.agents.base_agent import BaseAgent
from scraper.tools import SeleniumExtractPostsTool, SeleniumExtractHtmlTool
from string import Template

ROLE = "HTML expert"
BACKSTORY = f"""
You are a {ROLE} that identify css selectors and values that locate a blog_item ( a "container" that represents a blog item and that wraps all its
information) , blog_date, and blog_url in a website.
You prioritize finding essential and stable selectors that enable Selenium to directly and accuratedly 
locate the blogs and scrape their information 
"""
GOAL = """
Your goal is to produce output in the specified JSON format. The JSON output should contain selectors and values for:
1. blog_item
2. blog_date
3. blog_url

**JSON Format:**

{

 "blog_item": {
    "selector": "xxx",
    "value": "xxx"
  },
  "blog_date": {
    "selector": "xxx",
    "value": "xxx"
  },
   "blog_url": {
    "selector": "xxx",
    "value": "xxx" 
  }
}

**Rules:**
- Use only one of these selector types: "id", "name", "xpath", "css selector", "class name".
- The blog_url should have a clickable url that navigate to that blog.
- If you cannot find a stable dropdown or option, use "none" for both the selector and value.
- Only include the most unique and stable parts of the class names that are likely to remain consistent across pages. Avoid responsive, hover, or state-specific classes
- Return the output in JSON format, strictly following the structure above.

"""

user_prompt_template = Template("""
Given the following HTML, extract CSS selectors for blog_item,  blog_date, and blog_url. Return in a valid JSON format for direct use by Selenium.
Following is the previous failed cases, including the failed selector type, selector value, and error message.
Please take them into consideration when identifying the CSS selector and values for blog_item , blog_url, and blog_date,
Failed cases:
${failed_experiences}

HTML Content:                                                                
${cleaned_html}
""")


class ExtractResultsAgent(BaseAgent):
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
        """Learn the CSS selectors for extracting blog posts."""
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
            print("\n🤖 ExtractResults Agent output: ", selectors)


            print("\nTesting the selectors with Selenium...")
            extract_posts_tool = SeleniumExtractPostsTool(selectors=selectors)
            
            success, error_message = extract_posts_tool.extract_page_one_url(
                driver=driver  # use the shared driver with sort results,
            )

            if error_message == "":
                print(
                    "🎉\n Extracting one URL is successfuly completed! These selectors are correct")

                knowledge_structure = {
                    "extract_posts_section": selectors

                }
                self.knowledge_base.save_knowledge(
                    new_url=url,  knowledge_dict=knowledge_structure
                )
                print("\n✅ Saved the selectors into knowledge")
                success = True
                break
            else:
                blog_item = selectors.get("blog_item", {})
                blog_url = selectors.get("blog_url", {})
                blog_date = selectors.get("blog_date", {})
                print("\n⚠️ The selectors are incorrect")
                # save the failed result to memory
                failed_memory = f"blog_item: {blog_item}, blog_date: {
                    blog_date}, blog_url: {blog_url}, error_message: {error_message}"
                self.memory.append_memory(failed_memory=failed_memory)
                retries += 1
                print(
                    f"\nRetrying... Attempt {retries}/{self.max_retry_times} reties")
        
        return success
