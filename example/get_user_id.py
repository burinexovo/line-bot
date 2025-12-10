import os
import json
from datetime import datetime
from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()
USER_FILE = os.getenv("USER_ID_FILES")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

configuration = Configuration(access_token=LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


# 載入 JSON（如果沒有檔案就建立空 dict）
def load_users():
    # 檔案不存在 → 建新檔 {}
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w", encoding="utf-8") as f:
            f.write("{}")
        return {}

    # 檔案存在，但為空
    if os.path.getsize(USER_FILE) == 0:
        with open(USER_FILE, "w", encoding="utf-8") as f:
            f.write("{}")
        return {}

    # 嘗試讀取 JSON
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    # 如果 JSON 被亂碼影響或格式錯誤 → 自動重建
    except json.JSONDecodeError:
        print("⚠ users.json 損壞，已自動重建為空文件。")
        with open(USER_FILE, "w", encoding="utf-8") as f:
            f.write("{}")
        return {}


# 儲存 JSON
def save_users(data):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# 更新 users 字典：如果是新 user 就加入，回傳是否有新增
def save_user_if_new(users, uid, username):
    if uid not in users:
        users[uid] = {
            "name": username,
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            # "enabled": True,
        }
        print("新增使用者：", uid, username)
        return True
    return False


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # ---- 解析 JSON ----
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        app.logger.warning("Invalid JSON body")
        abort(400)

    users = load_users()
    users_updated = False  # 有新增新使用者才會改成 True

    # 準備好 Messaging API client
    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)

        # 逐個 event 處理 user 收集
        for event in data.get("events", []):
            source = event.get("source", {})
            user_id = source.get("userId")

            if not user_id:
                continue  # 群組、room，有可能沒有 userId

            # 已存在就不用再查 profile / 寫檔
            if user_id in users:
                continue

            # 只對「新 user」查 profile
            username = None
            try:
                profile = api.get_profile(user_id)
                username = profile.display_name
                app.logger.info(f"取得新使用者 Profile：{user_id} / {username}")
            except Exception as e:
                app.logger.warning(f"取得 Profile 失敗 user_id={user_id}: {e}")

            # 更新 users dict（有新增才會回 True）
            if save_user_if_new(users, user_id, username):
                users_updated = True

    # 如果這次真的有新增使用者 → 寫一次 JSON 就好
    if users_updated:
        save_users(users)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id

    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)

        # # 回覆訊息
        # reply_text = (
        #     f"你好 {username}！\n"
        #     f"你的 userId 已儲存 😎" if is_new else
        #     f"歡迎回來 {username}～你的資料已存在！"
        # )

        # api.reply_message(
        #     ReplyMessageRequest(
        #         reply_token=event.reply_token,
        #         messages=[TextMessage(text=reply_text)]
        #     )
        # )


if __name__ == "__main__":
    app.run(port=5213, debug=True)
