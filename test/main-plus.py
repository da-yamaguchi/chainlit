"""
使用するモデルやパラメータの調整を可能にしたバージョン
"""

import os
import chainlit as cl
from chainlit.input_widget import Slider
from dotenv import load_dotenv

from llm_response import generate_message, generate_bedrock_message, SYSTEM_CONTENT
from vector_search import vector_search, insert_log

load_dotenv()

# ファイル添付機能を非表示に
cl.config.features.spontaneous_file_upload = None

# 会話の履歴を格納する変数
message_history = [
    {
        "role":"system",
        "content":SYSTEM_CONTENT
    }
]

@cl.set_chat_profiles
async def chat_profile():
    """
    画面の上部に表示されるモデル一覧を設定する
    """
    
    return [
        cl.ChatProfile(
            name=os.environ["AZURE_GPT_4O_MINI_NAME"],
            # markdown_description="The underlying LLM model is **gpt-4**.",
            markdown_description="AzureOpenAIの**gpt-4o-mini**モデルを使用します。",
            # icon="icon画像のURLを指定します。",
        ),
        cl.ChatProfile(
            name=os.environ["AZURE_GPT_4O_NAME"],
            # markdown_description="The underlying LLM model is **gpt-4**.",
            markdown_description="AzureOpenAIの**gpt-4**モデルを使用します。",
            # icon="icon画像のURLを指定します。",
        ),
        # cl.ChatProfile(
        #     name="Claude-3-Sonnet",
        #     markdown_description="Amazon Bedrockの**Claude 3 Sonnet**モデルを使用します。",
        # ),
        cl.ChatProfile(
            name="Claude-3.5-Sonnet",
            markdown_description="Amazon Bedrockの**Claude 3.5 Sonnet**モデルを使用します。",
        ),
        cl.ChatProfile(
            name="QA-Search",
            markdown_description="QA登録された情報から質問に近い、回答を探します。",
        ),
        cl.ChatProfile(
            name=os.environ["AZURE_OPENAI_DEPLOY_NAME"],
            # markdown_description="The underlying LLM model is **gpt-35-turbo-16k**.",
            markdown_description="AzureOpenAIの**gpt-35-turbo-16k**モデルを使用します。\ngpt-4o-miniがコスト、性能としても上位互換のため、本モデルの使用は非推奨です。",
            # icon="icon画像のURLを指定します。",
        ),
    ]

@cl.on_chat_start
async def start():
    """
    Chatを開始したタイミングで一度だけ呼ばれる。
    """
    # # パラメータの設定項目を定義する
    # settings = await cl.ChatSettings(
    #     [
    #         Slider(
    #             id="max_tokens",
    #             label="最大応答",
    #             initial=800,
    #             min=1,
    #             max=4000,
    #             step=1
    #         ),
    #         Slider(
    #             id="temperature",
    #             label="温度パラメータ",
    #             initial=0,
    #             min=0,
    #             max=1,
    #             step=0.01
    #         )
    #     ]
    # ).send()

    # await update_settings(settings)
    
@cl.on_settings_update
async def update_settings(settings):
    """
    パラメータの設定を変更する。
    """
    cl.user_session.set("llm_parameters",settings)
    
@cl.on_message
async def main(message: cl.Message):
    """
    ユーザーからメッセージが送られたら実行される関数
    """
    chat_profile = cl.user_session.get("chat_profile")
    message_history.append({
        "role":"user",
        "content":message.content
    })
    
    if chat_profile == "QA-Search":
        search_result = vector_search(message.content)
        
        if search_result["user_message"]:
            response_content = search_result["user_message"]
        else:
            response_content = ""
            for result in search_result["results"]:
                response_content += f"{result['document']['content']}\n\n"
        
        # VECTOR_SEARCHの場合のみログを保存
        insert_log(message.content, search_result)
    elif chat_profile == "Claude-3.5-Sonnet":
        response = generate_bedrock_message(message_history)
        response_content = response["content"]
    else:
        response = generate_message(
            message_history,
            model_name=chat_profile,
        )
        response_content = response["content"]
    
    await cl.Message(content=response_content).send()
    
    message_history.append({
        "role":"assistant",
        "content":response_content
    })

## ログイン認証機能 ここから
# USERNAME = os.getenv("USERNAME")
# PASSWORD = os.getenv("PASSWORD")

# @cl.password_auth_callback
# def auth_callback(username: str, password: str):
#     print("auth_callback")
#     return username == USERNAME and password == PASSWORD

## ログイン認証機能 ここまで
