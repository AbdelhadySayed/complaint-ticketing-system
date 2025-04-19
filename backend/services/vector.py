import uuid
from langchain_ollama import OllamaEmbeddings
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except:
    print("pysqlite3 not found, using built-in sqlite3")
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

df = pd.read_csv(
    "archive/Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11 (1).csv")
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = "./chrome_langchain_db"
add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []

    for i, row in df.iterrows():
        document = Document(
            page_content="Complaint: " +
            row["instruction"] + " Answer: " + row["response"],
            metadata={"category": row["category"], "intent": row["intent"]},
            id=str(i)
        )
        ids.append(str(i))
        documents.append(document)

vector_store = Chroma(
    collection_name="problems_and_solutions",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    vector_store.add_documents(documents=documents[:5000], ids=ids[:5000])

retriever = vector_store.as_retriever(
    search_kwargs={"k": 5}
)


def add_reply_to_chromadb(instruction: str, response: str, category: str, intent: str):
    global retriever
    content = "Complaint: "+instruction.strip() + " Answer: " + response.strip()

    doc = Document(
        page_content=content,
        metadata={
            "category": category,
            "intent": intent
        },
        id=str(uuid.uuid4())  # ensure unique ID
    )

    try:
        vector_store.add_documents(documents=[doc])
        retriever = vector_store.as_retriever(
            search_kwargs={"k": 5}
        )
    except Exception as e:
        print(f"Error adding document to ChromaDB: {e}")
