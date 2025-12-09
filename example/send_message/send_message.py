import time
import uuid
import os
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

print(CHANNEL_ACCESS_TOKEN)

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
            print("成功廣播！結果如下：")

        except Exception as e:
            print("發生錯誤：", e)


if __name__ == "__main__":
    broadcast_message(msg="有客人來了")
