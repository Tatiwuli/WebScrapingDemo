from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import html2text

from utils.llms import OpenAILLM
from scraper.memories import Memory
from scraper.knowledge import KnowledgeBase

"""
This class is an abstract base for AI-powered agents that
inspect HTML. Provides common utilities for cleaning HTML, converting
HTML to Markdown, and storing knowledge for the HTML Inspection process.
"""

class BaseAgent(ABC):
    def __init__(self, role: str, backstory: str, goal: str, llm_model_name: str, pydantic_format):
        self.system_prompt = f"{backstory}\n{goal}"
        self.llm = OpenAILLM(model_name=llm_model_name, pydantic_format=pydantic_format)
        self.memory = Memory()
        self.knowledge_base = KnowledgeBase()
        self.ignored_tags = None
    
    def clean_html(self, html_content: str) -> str:
        """Removes irrelevant tags, whitespace, and duplicate lines from HTML content."""
        soup = BeautifulSoup(html_content, "html.parser")
        for element in soup.find_all(self.ignored_tags):  # irrelevant tags for search
            element.decompose()

        cleaned_content = str(soup)

        # remove unecessary lines
        lines = cleaned_content.split("\n")
        stripped_lines = [line.strip() for line in lines]
        non_empty_lines = [line for line in stripped_lines if line]
        seen = set()
        deduped_lines = [
            line for line in non_empty_lines if not (line in seen or seen.add(line))
        ]
        final_cleaned_content = "".join(deduped_lines)

        return final_cleaned_content

    def html_to_markdown(self, html_content: str) -> str:
        cleaned_html = self.clean_html(html_content)
        markdown_converter = html2text.HTML2Text()
        markdown_converter.ignore_links = False
        markdown_content = markdown_converter.handle(cleaned_html)
        return markdown_content

    @abstractmethod
    def learn(self):
        """Use LLM to learn the agent actions."""
        raise NotImplementedError
    
