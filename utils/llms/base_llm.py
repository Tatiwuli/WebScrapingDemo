from abc import ABC, abstractmethod
from token_count import TokenCount


class BaseLLM(ABC):
    def __init__(self, model_name: str, temperature: float):
        self.temperature = temperature
        self.client = None
        self.token_counter = TokenCount(model_name=model_name)

    @abstractmethod
    def __call__(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

    def get_text_token(self, text: str) -> int:
        tokens = self.tc.num_tokens_from_string(text)
        return tokens