import os
import time
from typing import List,Dict
from dotenv import load_dotenv
from openai import AzureOpenAI
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

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

def generate_tsuzumi_message(
        messages: List[Dict]
    ):

    try:
        api_key=os.environ["AZURE_INFERENCE_CREDENTIAL_TSUZUMI_7B"]
        if not api_key:
            raise Exception("A key should be provided to invoke the endpoint")

        client = ChatCompletionsClient(
            endpoint='https://tsuzumi-7b-gvwbx.eastus2.models.ai.azure.com',
            credential=AzureKeyCredential(api_key)
        )

        # model_info = client.get_model_info()
        # print("Model name:", model_info.model_name)
        # print("Model type:", model_info.model_type)
        # print("Model provider name:", model_info.model_provider_name)

        payload = {
        # "messages": [
        #     {
        #     "role": "user",
        #     "content": "I am going to Tokyo, what should I see?"
        #     },
        #     {
        #     "role": "assistant",
        #     "content": "Paris, the capital of France, is known for its stunning architecture, art museums, historical landmarks, and romantic atmosphere. Here are some of the top attractions to see in Paris:\n\n1. The Eiffel Tower: The iconic Eiffel Tower is one of the most recognizable landmarks in the world and offers breathtaking views of the city.\n2. The Louvre Museum: The Louvre is one of the world's largest and most famous museums, housing an impressive collection of art and artifacts, including the Mona Lisa.\n3. Notre-Dame Cathedral: This beautiful cathedral is one of the most famous landmarks in Paris and is known for its Gothic architecture and stunning stained glass windows.\n\nThese are just a few of the many attractions that Paris has to offer. With so much to see and do, it's no wonder that Paris is one of the most popular tourist destinations in the world."
        #     },
        #     {
        #     "role": "user",
        #     "content": "What about Osaka?"
        #     }
        # ],
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.15
        }

        response = client.complete(payload)

        return {
                    "role":"assistant",
                    "content":response.choices[0].message.content
        }

        # print("Response:", response.choices[0].message.content)
        # print("Model:", response.model)
        # print("Usage:")
        # print("	Prompt tokens:", response.usage.prompt_tokens)
        # print("	Total tokens:", response.usage.total_tokens)
        # print("	Completion tokens:", response.usage.completion_tokens)

    except Exception as e:
        return {
            "role": "error",
            "content": f"エラーが発生しました: {str(e)}"
        }
