import chainlit as cl


@cl.step(type="tool")
async def tool():
    # 擬似ツール
    await cl.sleep(2)
    return "ツールからの応答!"


@cl.on_message  # この関数は、ユーザーがUIにメッセージを入力するたびに呼び出されます
async def main(message: cl.Message):
    """
    この関数は、ユーザーがUIにメッセージを入力するたびに呼び出されます。
    ツールからの中間応答を送り返し、その後、最終的な回答を送ります。

    引数：
        message: ユーザーのメッセージ。

    戻り値：
        なし。
    """

    final_answer = await cl.Message(content="").send()

    # ツールを呼び出す
    final_answer.content = await tool()

    await final_answer.update()