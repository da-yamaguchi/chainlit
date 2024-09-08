import os
import chainlit as cl
from chainlit.input_widget import Slider
from dotenv import load_dotenv

from llm_response import generate_message, generate_bedrock_message, SYSTEM_CONTENT
from vector_search import vector_search, insert_log

load_dotenv()

# ファイル添付機能を非表示に
cl.config.features.spontaneous_file_upload = None

# 最大メッセージ数を定義（例: システムメッセージ + 10往復のやり取り）
MAX_MESSAGES = 21

# 会話の履歴を格納する変数
message_history = [
    {
        "role":"system",
        "content":SYSTEM_CONTENT
    }
]

# message_historyを更新する関数
def update_message_history(new_message):
    global message_history
    message_history.append(new_message)
    
    # メッセージ数が最大数を超えた場合、古いメッセージを削除
    if len(message_history) > MAX_MESSAGES:
        # print(f"メッセージ数が最大数を超えた場合")
        # システムメッセージを保持
        system_messages = [msg for msg in message_history if msg["role"] == "system"]
        
        # ユーザーとアシスタントのメッセージをペアで取得
        user_assistant_pairs = []
        for i in range(1, len(message_history) - 1, 2):
            if message_history[i]["role"] == "user" and message_history[i+1]["role"] == "assistant":
                user_assistant_pairs.append((message_history[i], message_history[i+1]))
        
        # 古いペアを削除し、新しいペアを保持
        pairs_to_keep = user_assistant_pairs[-(MAX_MESSAGES - len(system_messages))//2:]
        
        # 削除されるメッセージを表示
        pairs_to_remove = user_assistant_pairs[:-len(pairs_to_keep)]
        for user_msg, assistant_msg in pairs_to_remove:
            # print(f"削除されるメッセージ: ユーザー: {user_msg['content']}, アシスタント: {assistant_msg['content']}")
            print("削除されるメッセージがありました。")
        
        # 新しいmessage_historyを構築
        new_message_history = system_messages[:]
        for user_msg, assistant_msg in pairs_to_keep:
            new_message_history.extend([user_msg, assistant_msg])
        
        # 最新のメッセージを追加
        new_message_history.append(new_message)
        
        message_history = new_message_history
    # else:
        # print(f"メッセージ数が最大数を超えなかった場合")

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
            name="Claude-3.5-Sonnet",
            markdown_description="Amazon Bedrockの**Claude 3.5 Sonnet**モデルを使用します。",
        ),
        cl.ChatProfile(
            name="QA-Search",
            markdown_description="QA登録された情報から質問に近い、回答を探します。",
        ),
        cl.ChatProfile(
            name=os.environ["AZURE_GPT_4O_NAME"],
            # markdown_description="The underlying LLM model is **gpt-4**.",
            markdown_description="AzureOpenAIの**gpt-4**モデルを使用します。",
            # icon="icon画像のURLを指定します。",
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
    # 現在のチャットプロファイルを取得
    chat_profile = cl.user_session.get("chat_profile")
    # 以前のチャットプロファイルをセッションから取得
    previous_chat_profile = cl.user_session.get("previous_chat_profile")

    # チャットプロファイルが変更された場合、履歴をリセット
    if chat_profile != previous_chat_profile:
        global message_history
        message_history = [
            {
                "role": "system",
                "content": SYSTEM_CONTENT
            }
        ]
        # セッションに新しいプロファイルを保存
        cl.user_session.set("previous_chat_profile", chat_profile)

    # ユーザーメッセージを追加
    update_message_history({
        "role":"user",
        "content":message.content
    })

    # ローディングスピナーを表示
    loading_message = cl.Message(content="応答を生成中...")
    await loading_message.send()
    await cl.sleep(0.1) # sleepをいれないとcontentが表示されない

    try:
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
    finally:
        # ローディングスピナーを非表示
        await loading_message.remove()
    
    await cl.Message(content=response_content).send()
    
    # アシスタントの応答を追加
    update_message_history({
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
