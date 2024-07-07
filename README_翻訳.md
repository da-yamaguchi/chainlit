# Literal AI による Chainlit へようこそ 👋

**数週間ではなく、数分で本番稼働可能な対話型AI アプリケーションを構築 ⚡️**

Chainlitは、開発者がスケーラブルな対話型AIまたはエージェントアプリケーションを構築できるオープンソースの非同期Pythonフレームワークです。

- ✅ ChatGPTのようなアプリケーション
- ✅ 埋め込み型チャットボット & ソフトウェアコパイロット
- ✅ Slack & Discord
- ✅ カスタムフロントエンド（独自のエージェント体験を構築）
- ✅ APIエンドポイント

完全なドキュメントは[こちら](https://docs.chainlit.io)で利用可能です。Chainlitに関する質問は、Chainlitを使用して構築された[Chainlit Help](https://help.chainlit.io/)にすることができます！

> [!注意]  
> **エンタープライズサポート**については[こちら](https://forms.gle/BX3UNBLmTF75KgZVA)からお問い合わせください。
> LLMアプリケーションを監視・評価する製品、[Literal AI](https://literalai.com)をチェックしてください！これはPythonやTypeScriptのアプリケーションで動作し、プロジェクトに`LITERAL_API_KEY`を追加することでChainlitと[シームレスに](https://docs.chainlit.io/data-persistence/overview)連携します。

## インストール

ターミナルを開いて以下を実行してください：

```bash
$ pip install chainlit
$ chainlit hello
```

これでブラウザに`hello app`が開けば、セットアップ完了です！

## 🚀 クイックスタート

### 🐍 Pure Python

`demo.py`という新しいファイルを作成し、以下のコードを記述してください：

```python
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
```

では、実行してみましょう！

```
$ chainlit run demo.py -w
```

## 🎉 主要機能と統合

完全なドキュメントは[こちら](https://docs.chainlit.io)で利用可能です。主要な機能：

- [💬 マルチモーダルチャット](https://docs.chainlit.io/advanced-features/multi-modal)
- [💭 思考の連鎖の可視化](https://docs.chainlit.io/concepts/step)
- [💾 データ永続化 + ヒューマンフィードバック](https://docs.chainlit.io/data-persistence/overview)
- [🐛 デバッグモード](https://docs.chainlit.io/data-persistence/enterprise#debug-mode)
- [👤 認証](https://docs.chainlit.io/authentication/overview)

Chainlitはすべてのプログラムやライブラリと互換性がありますが、以下の統合も提供しています：

- [LangChain](https://docs.chainlit.io/integrations/langchain)
- [Llama Index](https://docs.chainlit.io/integrations/llama-index)
- [Autogen](https://github.com/Chainlit/cookbook/tree/main/pyautogen)
- [OpenAI Assistant](https://github.com/Chainlit/cookbook/tree/main/openai-assistant)
- [Haystack](https://docs.chainlit.io/integrations/haystack)

## 📚 その他の例 - クックブック

OpenAI、Anthropic、LangChain、LlamaIndex、ChromaDB、Pineconeなどのツールやサービスを活用したChainlitアプリの様々な例を[こちら](https://github.com/Chainlit/cookbook)で見つけることができます。

Chainlitに追加してほしいものがあれば、Githubのissuesや[Discord](https://discord.gg/k73SQ3FyUh)で教えてください。

## 💁 貢献

急速に進化する分野におけるオープンソースの取り組みとして、新機能の追加やドキュメントの改善を通じた貢献を歓迎します。

貢献方法の詳細については、[こちら](.github/CONTRIBUTING.md)をご覧ください。

## 📃 ライセンス

Chainlitはオープンソースで、[Apache 2.0](LICENSE)ライセンスの下で提供されています。