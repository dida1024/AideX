import json
import asyncio
from openai import AsyncOpenAI
from abc import ABC, abstractmethod
from app.core.config import settings
from app.utils.file_helper import FileHelper
from app.utils.prompt_helper import PromptHelper, PromptType


class AiClientBase(ABC):
    # 定义抽象基类的核心属性
    # model: 模型名称
    # client: AI客户端实例
    model: str
    client: object

    @abstractmethod
    async def chat_without_stream(self, system_prompt: str, user_message: str) -> str:
        """
        定义聊天接口，子类需要实现具体调用逻辑
        """
        pass

class OpenAiChat(AiClientBase):
    def __init__(self, api_key: str, url: str, model: str) -> None:
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=url
        )
        
    async def chat_without_stream(self, system_prompt: str, user_message: str) -> str:        
        """
        发送非流式聊天请求，返回聊天结果
        """
        try:
            response = await self.client.chat.completions.create(
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
    def __init__(self, client: AiClientBase) -> None:
        self.client = client
        self.model = client.model
    
    async def chat(self, user_prompt: str):
        prompt = PromptHelper.get_prompt(PromptType.CHAT)
        response = await self.client.chat_without_stream(prompt, user_prompt)
        return response
    
    async def analyze_document(self, document: str) -> dict:
        """
        文档分析函数，对输入的文档进行智能分析
        
        参数:
            document: 需要分析的文档内容
            
        返回:
            dict: 包含分析结果的字典，包括：
                - summary: 文档摘要
                - keywords: 关键词列表
                - sentiment: 情感分析结果
        """
        
        try:
            prompt = PromptHelper.get_prompt(PromptType.SUMMARY)
            response = await self.client.chat_without_stream(prompt, document)
            return response
        except Exception as e:
            # logger.error("文档分析时发生错误: %s", e)
            raise
            
    def get_model(self) -> str:
        """
        获取当前使用的模型名称
        """
        return self.model

if __name__ == "__main__":
    deepseek_client = OpenAiChat(settings.DEEPSEEK_API, settings.DEEPSEEK_URL, settings.DEEPSEEK_MODEL)
    ai_helper = AiHelper(deepseek_client)
    
    # 获取并打印当前使用的模型
    model_name = ai_helper.get_model()
    print(f"使用的模型: {model_name}")
    
    # # 进行聊天
    # response = ai_helper.chat("请问你是谁")
    # print(response)
    
    async def main():
        file = await FileHelper.load_file("downloads/功能文档.md")
        response = await ai_helper.analyze_document(file)
        print(response)
    
    asyncio.run(main())
    
