from typing import List
"""
memory.py

This class tracks failed experiences during the HTML Inspection of LLM Agents.

Entirely Developed by another Software Engineer

"""

class Memory:
    def __init__(self):
        self._failed_memories = []

    def append_memory(self, failed_memory: str) -> None:
        self._failed_memories.append(failed_memory)

    def get_memory(self) -> List[str]:
        return self._failed_memories
    
    def export_memory(self) -> str:
        if not self._failed_memories:
            return "There is no previous failed experience."
        
        failed_experiences = ""
        for i, memory in enumerate(self._failed_memories, start=1):
            # Note: The following cleaning processes are specific to the selenium unable to locate element error message
            cleaned_memory = memory.split("Stacktrace:")[0]
            cleaned_memory = cleaned_memory.split("(Session info:")[0].strip()
            failed_experiences += f"{i}. {cleaned_memory}\n"

        return failed_experiences

    def clear_memory(self) -> None:
        self._failed_memories.clear()