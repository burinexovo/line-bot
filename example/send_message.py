import os
import time
import json
import uuid
from datetime import datetime
import linebot.v3.messaging
from linebot.v3.messaging.models.broadcast_request import BroadcastRequest
from linebot.v3.messaging.models.push_message_request import PushMessageRequest
from pprint import pprint
from linebot.v3.messaging.rest import ApiException
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from dotenv import load_dotenv

load_dotenv()
USER_FILE = os.getenv("USER_ID_FILES")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)


def broadcast_message(msg):
    with ApiClient(configuration) as api_client:
        msg_api = MessagingApi(api_client)

        try:
            msg_api.broadcast(
                BroadcastRequest(
                    messages=[TextMessage(text=msg)]
                ),
                x_line_retry_key=str(uuid.uuid4())
            )
            print("廣播完成")
        except Exception as e:
            print("發生錯誤：", e)


def load_users():
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def push_message(msg):
    users = load_users()
    with ApiClient(configuration) as api_client:
        msg_api = MessagingApi(api_client)

        for uid, info in users.items():
            # print(uid, info)
            if info.get("enabled", True):
                try:
                    msg_api.push_message(
                        PushMessageRequest(
                            to=uid,
                            messages=[TextMessage(text=msg)]
                        )
                    )
                    print("推播完成")
                except Exception as e:
                    print(f"推播 {uid} 發生錯誤: {e}")


if __name__ == "__main__":
    curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # broadcast_message(msg=f"廣播測試 {curr_time}")
    push_message(msg=f"推播測試 {curr_time}")
