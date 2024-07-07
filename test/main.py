
"""
基本形のAzureOpenAIと接続したアプリ
"""
import chainlit as cl

from llm_response import generate_message, SYSTEM_CONTENT

# 会話の履歴を格納する変数
message_history = [
    {
        "role":"system",
        "content":SYSTEM_CONTENT
    }
]
@cl.on_message
async def main(message: cl.Message):
    """
    ユーザーからメッセージが送られたら実行される関数
    """

    message_history.append({
        "role":"user",
        "content":message.content
    })

    # Azure OpenAI Serviceと通信を行う
    response = generate_message(message_history)

    # 画面にAzure OpenAI Serviceから受け取った応答を表示する
    await cl.Message(
        content=response["content"]
    ).send()

    message_history.append({
        "role":"assistant",
        "content":response["content"]
    })