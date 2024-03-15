import json
import os

import boto3
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent


def get_secrets() -> dict[str, str]:
    secret_arn = os.environ["SECRET_ARN"]
    client = boto3.client("secretsmanager")
    value = client.get_secret_value(SecretId=secret_arn)
    # print(f"{value=}")
    secret_str = value["SecretString"]
    # print(f"{secret_str}")
    secrets = json.loads(secret_str)
    # print(f"{secrets}")
    return secrets


secrets = get_secrets()
access_token = secrets["CHANNEL_ACCESS_TOKEN"]
print(f"{access_token=}")
line_config = Configuration(access_token=access_token)
channel_secret = secrets["CHANNEL_SECRET"]
print(f"{channel_secret=}")
line_handler = WebhookHandler(channel_secret)


def lambda_handler(event, context):
    print(f"{event=}")
    print(f"{context=}")

    @line_handler.add(MessageEvent, message=TextMessageContent)
    def handle_message(event: MessageEvent):
        req = ReplyMessageRequest(
            replyToken=event.reply_token,
            messages=[TextMessage(text=event.message.text)],
        )
        with ApiClient(line_config) as client:
            line_bot_api = MessagingApi(client)
            line_bot_api.reply_message_with_http_info(req)

    body = event["body"]
    signature = event["headers"]["x-line-signature"]
    line_handler.handle(body, signature)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
            }
        ),
    }
