from openai import OpenAI
import json
from dotenv import load_dotenv
import os

from .base_llm import BaseLLM

load_dotenv()


class OpenAILLM(BaseLLM):
    def __init__(
        self, model_name: str = "gpt-4o", temperature: float = 0.1, pydantic_format=None
    ):
        super().__init__(model_name=model_name, temperature=temperature)
        self.model_name = model_name
        self.pydantic_format = pydantic_format
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def __call__(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        response_string = response.choices[0].message.content
        response_dict = json.loads(response_string)

        return response_dict
