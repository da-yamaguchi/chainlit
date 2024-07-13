"""
使用するモデルやパラメータの調整を可能にしたバージョン
"""

import os
import chainlit as cl
from chainlit.input_widget import Slider
from dotenv import load_dotenv

from llm_response import generate_message, SYSTEM_CONTENT

load_dotenv()

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
            name=os.environ["AZURE_OPENAI_DEPLOY_NAME"],
            markdown_description="The underlying LLM model is **gpt-35-turbo-16k**.",
            icon="icon画像のURLを指定します。",
        ),
        cl.ChatProfile(
            name=os.environ["AZURE_GPT_4O_NAME"],
            markdown_description="The underlying LLM model is **gpt-4**.",
            icon="icon画像のURLを指定します。",
        ),
    ]

@cl.on_chat_start
async def start():
    """
    Chatを開始したタイミングで一度だけ呼ばれる。
    """
    
    # パラメータの設定項目を定義する
    settings = await cl.ChatSettings(
        [
            Slider(
                id="max_tokens",
                label="最大応答",
                initial=800,
                min=1,
                max=4000,
                step=1
            ),
            Slider(
                id="temperature",
                label="温度パパラメータ",
                initial=0,
                min=0,
                max=1,
                step=0.01
            )
        ]
    ).send()

    await update_settings(settings)
    
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
    llm_parameter = cl.user_session.get("llm_parameters")
    chat_profile = cl.user_session.get("chat_profile")
    message_history.append({
        "role":"user",
        "content":message.content
    })
    
    response = generate_message(
        message_history,
        model_name=chat_profile,
        max_tokens=int(llm_parameter["max_tokens"]),
        temperature=llm_parameter["temperature"]
    )
    
    await cl.Message(
        content=response["content"]
    ).send()
    
    message_history.append({
        "role":"assistant",
        "content":response["content"]
    })