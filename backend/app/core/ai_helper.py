from openai import OpenAI
from abc import ABC, abstractmethod
from app.core.config import settings
from app.utils.prompt_helper import PromptHelper, PromptType


class AiClientBase(ABC):
    @abstractmethod
    def chat_without_stream(self, system_prompt: str, user_message: str) -> str:
        """
        定义聊天接口，子类需要实现具体调用逻辑
        """
        pass

class OpenAiChat(AiClientBase):
    def __init__(self, api_key: str, url: str, model: str) -> None:
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url=url
        )
        
    def chat_without_stream(self, system_prompt: str, user_message: str) -> str:        
        """
        发送非流式聊天请求，返回聊天结果
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            # logger.error("调用 OpenAI API 时发生异常: %s", e)
            raise
            


class AiHelper():
    deepseek_client = OpenAiChat(settings.DEEPSEEK_API,settings.DEEPSEEK_URL,settings.DEEPSEEK_MODEL)
    
    def chat_with_deepseek(self, user_prompt:str):
        promt = PromptHelper.get_prompt(PromptType.CHAT)
        response = self.deepseek_client.chat_without_stream(promt,user_prompt)
        return response

if __name__ == "__main__":
    ai_helper = AiHelper()
    response = ai_helper.chat_with_deepseek("请问你是谁")
    print(response)
