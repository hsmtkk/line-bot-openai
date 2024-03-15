import os

from langchain_openai import ChatOpenAI
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_pinecone.vectorstores import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings


def init_vector_store() -> PineconeVectorStore:
    embedding = OpenAIEmbeddings()
    store = PineconeVectorStore.from_existing_index(
        index_name=os.environ["PINECONE_INDEX_NAME"], embedding=embedding
    )
    return store


def main():
    store = init_vector_store()
    llm = ChatOpenAI()
    qa = RetrievalQA.from_llm(llm=llm, retriever=store.as_retriever())
    answer = qa.invoke("Summarize this document in 3 lines.")
    print(answer)


if __name__ == "__main__":
    main()
