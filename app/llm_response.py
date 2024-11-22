import os
import time
from typing import List,Dict
from dotenv import load_dotenv
from openai import AzureOpenAI
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

SYSTEM_CONTENT = """あなたはフレンドリーなアシスタントです。質問に答えて下さい。"""

def generate_message(
        messages: List[Dict],
        # model_name: str = "gpt-35-turbo-16k",
        model_name: str = os.environ["AZURE_OPENAI_DEPLOY_NAME"],
        max_tokens: int = 4000,
        temperature: float = 0.0
    ):
    
    client = AzureOpenAI(
        # api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        # azure_endpoint=os.environ.get("AZURE_OPENAI_API_BASE"),
        # api_version="2023-12-01-preview"
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ["OPENAI_API_VERSION"]
    )

    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model_name,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    
    return {
                "role":"assistant",
                "content":chat_completion.choices[0].message.content
    }

def generate_bedrock_message(messages: List[Dict], chat_profile: str):
    if chat_profile == "Claude-3.5-Sonnet":
        chat = ChatBedrock(
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
            model_kwargs={"temperature": 0.1, "max_tokens": 4000},
        )
    else:
        chat = ChatBedrock(
            model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            model_kwargs={"temperature": 0.1, "max_tokens": 4000},
        )
    
    langchain_messages = []
    for message in messages:
        if message["role"] == "system":
            langchain_messages.append(SystemMessage(content=message["content"]))
        elif message["role"] == "user":
            langchain_messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            langchain_messages.append(AIMessage(content=message["content"]))
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            result = chat.invoke(langchain_messages)
            return {
                "role": "assistant",
                "content": result.content
            }
        except Exception as e:
            if "ThrottlingException" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数バックオフ
                print(f"リトライ中... (試行回数: {attempt + 1}, 待機時間: {wait_time}秒)")
                time.sleep(wait_time)
            else:
                return {
                    "role": "error",
                    "content": f"エラーが発生しました: {str(e)}"
                }
    # try:
    #     result = chat.invoke(langchain_messages)
    
    #     return {
    #         "role": "assistant",
    #         "content": result.content
    #     }
    # except Exception as e:
    #     return {
    #         "role": "error",
    #         "content": f"エラーが発生しました: {str(e)}"
    #     }