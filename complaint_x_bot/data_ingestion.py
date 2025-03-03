from langchain_astradb import AstraDBVectorStore
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
import os
from complaint_x_bot.data_converter import dataconverter
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = "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"
ASTRA_DB_API_ENDPOINT = "https://a62810eb-d5f2-4bb3-9751-e10bf05b2215-us-east-2.apps.astra.datastax.com"
ASTRA_DB_APPLICATION_TOKEN = "AstraCS:qAjUSNWCXtSRIphONLKtgEZb:3f216000c1c35736f81f3259dc4ea5ebb5617aa422619d8247bf56093ab709bf"
ASTRA_DB_KEYSPACE = "default_keyspace"
HF_TOKEN = "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"


embedding = HuggingFaceInferenceAPIEmbeddings(api_key= HF_TOKEN, model_name= "BAAI/bge-base-en-v1.5")

def data_ingestion(status):
    vstore = AstraDBVectorStore(
    embedding= embedding,
    collection_name= "insurance_bot",
    api_endpoint = ASTRA_DB_API_ENDPOINT,
    token = ASTRA_DB_APPLICATION_TOKEN,
    namespace = ASTRA_DB_KEYSPACE

)
    
    storage = status
    if storage == None:
        docs = dataconverter()
        insert_ids = vstore.add_documents(docs)
    else:
        return vstore
    return vstore, insert_ids

if __name__ =="__main__":
    vstore, insert_ids = data_ingestion(None)
    print(f"\n Inserted {len(insert_ids)} documents.")
    results = vstore.similarity_search("Can you tell me about liability coverage in auto insurance?")
    for res in results:
        print(f"\n {res.page_content} [{res.metadata}]")

