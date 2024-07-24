# 社内chainlit

### 仮想の有効化

```bash
chainlit_env\Scripts\activate
```
以下はlinux  
```bash
source chainlit_env/bin/activate
```

### アプリ実行

```bash
chainlit run .\test\main.py 
```
Linux  
```bash
chainlit run ./test/main-plus.py
```

ポート指定で起動する方法  
```bash
chainlit run --port 8888 .\test\main-plus.py 
```
Linux  
```bash
chainlit run --port 8888 ./test/main-plus.py
```

# Systemdサービスファイルの作成と設定

仮想環境を使用するようにSystemdサービスを設定します。

### (1) サービスファイルの作成

以下のコマンドを使用して新しいサービスファイルを作成します。

```bash
sudo nano /etc/systemd/system/chainlit.service
```

### (2) サービスファイルの内容

サービスファイルに以下の内容を追加します：

```ini
[Unit]
Description=chainlitt Service
After=network.target

[Service]
User=d-yamaguchi
WorkingDirectory=/home/d-yamaguchi/Github/chainlit/app
EnvironmentFile=/home/d-yamaguchi/Github/chainlit/app/.env
ExecStart=/home/d-yamaguchi/Github/chainlit/chainlit_env/bin/chainlit run /home/d-yamaguchi/Github/chainlit/app/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### (3) サービスの有効化と起動

作成したサービスファイルを有効化し、サービスを起動します。

```bash
sudo systemctl daemon-reload
sudo systemctl start chainlit.service
```

### ログの確認

サービスの状態やログを確認するには、以下のコマンドを使用します：

```bash
sudo systemctl status chainlit.service
sudo journalctl -u chainlit.service -f
```

### サーバ起動時に自動起動するように設定する
```bash
sudo systemctl enable chainlit.service
```

```bash
sudo systemctl is-enabled chainlit.service
```
このコマンドの出力が enabled であれば、サービスは正しく有効化されています。

### サービスの停止  
```bash
sudo systemctl stop chainlit.service
```

### サービスの無効化  
```bash
sudo systemctl disable chainlit.service
```

### pythonを修正した場合
一般的に、サービスファイルを修正した場合、サービスを再起動する必要があります。  
```bash
sudo systemctl daemon-reload
sudo systemctl restart chainlit.service
```

# ログをファイルへ出力

### ログ出力用スクリプトの作成
```bash
sudo nano /usr/local/bin/slackbot_service_log_output.sh
```
以下の内容をファイルに保存します：
```bash
#!/bin/bash
journalctl -u slackbot.service -f >> /home/d-yamaguchi/Github/FastAPI/log/slackbot_service.log
```
ファイルを保存して閉じた後、このスクリプトに実行権限を与えます：
```bash
sudo chmod +x /usr/local/bin/slackbot_service_log_output.sh
```
### systemd サービスファイルの作成
次に、このスクリプトを実行するための systemd サービスファイルを作成します：
```bash
sudo nano /etc/systemd/system/slackbot_service_log_output.service
```
以下の内容をファイルに保存します：
```ini
[Unit]
Description=Log Output Service for Slackbot
After=network.target

[Service]
ExecStart=/usr/local/bin/slackbot_service_log_output.sh
Restart=always
User=root
Group=root

[Install]
WantedBy=multi-user.target
```
ファイルを保存して閉じます。
### システムデーモンのリロード
新しいサービスファイルを読み込むために、systemd デーモンをリロードします：
```bash
sudo systemctl daemon-reload
```
### サービスの開始と有効化
サービスを開始し、システム起動時に自動的に開始されるように有効化します：
```bash
sudo systemctl start slackbot_service_log_output.service
sudo systemctl enable slackbot_service_log_output.service
```
### ログファイルの確認
```bash
tail -f /home/d-yamaguchi/Github/FastAPI/log/slackbot_service.log
```
