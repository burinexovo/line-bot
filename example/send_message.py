import os
import time
import uuid
from datetime import datetime
import linebot.v3.messaging
from linebot.v3.messaging.models.broadcast_request import BroadcastRequest
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

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)


def broadcast_message(msg):
    with ApiClient(configuration) as api_client:
        msg_api = MessagingApi(api_client)

        broadcast_request = BroadcastRequest(
            messages=[
                TextMessage(text=msg)
            ]
        )

        try:
            msg_api.broadcast(
                broadcast_request,
                x_line_retry_key=str(uuid.uuid4())
            )
            print("推播完成")
        except Exception as e:
            print("發生錯誤：", e)


def push_message(msg):
    pass


if __name__ == "__main__":
    curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    broadcast_message(msg=f"推播測試 {curr_time}")
    push_message(msg=f"測試 {curr_time}")
