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
from langchain_openai import ChatOpenAI
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_pinecone.vectorstores import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.chains.retrieval_qa.base import BaseRetrievalQA


def get_secrets() -> dict[str, str]:
    secret_arn = os.environ["SECRET_ARN"]
    client = boto3.client("secretsmanager")
    value = client.get_secret_value(SecretId=secret_arn)
    secret_str = value["SecretString"]
    secrets = json.loads(secret_str)
    return secrets


secrets = get_secrets()

access_token = secrets["CHANNEL_ACCESS_TOKEN"]
line_config = Configuration(access_token=access_token)

channel_secret = secrets["CHANNEL_SECRET"]
line_handler = WebhookHandler(channel_secret)

os.environ["OPENAI_API_KEY"] = secrets["OPENAI_API_KEY"]
os.environ["PINECONE_API_KEY"] = secrets["PINECONE_API_KEY"]


def get_qa() -> BaseRetrievalQA:
    embedding = OpenAIEmbeddings()
    store = PineconeVectorStore.from_existing_index(
        index_name=os.environ["PINECONE_INDEX_NAME"], embedding=embedding
    )
    chat_openai = ChatOpenAI()
    qa = RetrievalQA.from_llm(llm=chat_openai, retriever=store.as_retriever())
    return qa


qa = get_qa()


def lambda_handler(event, context):
    print(f"{event=}")
    print(f"{context=}")

    @line_handler.add(MessageEvent, message=TextMessageContent)
    def handle_message(event: MessageEvent):
        input = event.message.text
        output = qa.invoke(input)
        print(f"{output=}")
        result = output["result"]
        print(f"{result=}")
        req = ReplyMessageRequest(
            replyToken=event.reply_token,
            messages=[TextMessage(text=result)],
        )
        with ApiClient(line_config) as client:
            line_bot_api = MessagingApi(client)
            line_bot_api.reply_message_with_http_info(req)

    body = event["body"]
    signature = event["headers"]["x-line-signature"]
    line_handler.handle(body, signature)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "ok"}),
    }
