import os
import json
from pathlib import Path
from typing import Dict

"""
This class manages storage and retrieval of the HTML tags of a website for data scraping. 
Stores the tags in JSON files in the /websites folder
"""

knowledge_base_path = Path("./scraper/knowledge/websites")
url_character_mapping_table = {
    "/": "_",
    ":": "_",
    ".": "_",
}


class KnowledgeBase:
    def __init__(self, url: str = None):
        self.knowledge_base_path = knowledge_base_path
        self.url = url

    def _url_to_file_path(self, url: str = None) -> Path:
        if url.endswith("/"):
            url = url[:-1]
        for character, replacement in url_character_mapping_table.items():
            url = url.replace(character, replacement)
        
        file_path = self.knowledge_base_path / f"{url}.json"
        print(f"\n 🔎Looking for knowledge file at: {file_path}")
        # changed to save files
        return file_path

    def search_knowledge(self) -> Dict | None:
        file_path = self._url_to_file_path(self.url)
        print("🔗File path: ", file_path)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding='utf-8') as file:
                print(f"\n✅ Knowledge found for URL: {self.url}")
                return json.load(file)
        print(f"\n❗No knowledge found for URL: {self.url}")
        return None

    def save_knowledge(self, new_url: str, knowledge_dict: Dict):
        file_path = self._url_to_file_path(url=new_url)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing knowledge if present
        if file_path.exists():
            with open(file_path, "r") as file:
                existing_data = json.load(file)
        else:
            existing_data = {"url": new_url, "sections": {}}

        # Merge knowledge correctly to prevent overwriting
        for section, data in knowledge_dict.items():
            if section in existing_data["sections"]:
                existing_data["sections"][section].update(data)  # Merge
            else:
                existing_data["sections"][section] = data  # Add new section

        # Save back to file
        with open(file_path, "w") as file:
            json.dump(existing_data, file, indent=4)

        print(f"✅ Knowledge successfully saved for URL: {new_url}")
