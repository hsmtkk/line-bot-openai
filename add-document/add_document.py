import os
import sys
from langchain_community.document_loaders.pdf import UnstructuredPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_pinecone.vectorstores import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings


def main(file_path: str) -> None:
    loader = UnstructuredPDFLoader(file_path)
    raw_docs = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    docs = text_splitter.split_documents(raw_docs)
    vector_store = init_vector_store()
    vector_store.add_documents(docs)


def init_vector_store() -> PineconeVectorStore:
    embedding = OpenAIEmbeddings()
    store = PineconeVectorStore.from_existing_index(
        index_name=os.environ["PINECONE_INDEX_NAME"], embedding=embedding
    )
    return store


if __name__ == "__main__":
    main(sys.argv[1])
