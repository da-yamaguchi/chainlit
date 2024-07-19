import os
from openai import AzureOpenAI
import pymongo
from urllib.parse import quote_plus
import datetime
import pytz

# Azure OpenAI client initialization
AOAI_client = AzureOpenAI(
    api_key = os.environ['AZURE_OPENAI_API_KEY'],
    api_version = os.environ['OPENAI_API_VERSION'],
    azure_endpoint = os.environ['AZURE_OPENAI_ENDPOINT']
)

# MongoDB client initialization
mongo_conn = f"mongodb+srv://{quote_plus(os.environ['cosmos_db_mongo_user'])}:{quote_plus(os.environ['cosmos_db_mongo_pwd'])}@{os.environ['cosmos_db_mongo_server']}?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
mongo_client = pymongo.MongoClient(mongo_conn)
db = mongo_client[os.environ['cosmos_db_mongo_dbname']]
collection = db[os.environ['cosmos_db_mongo_collectionname']]

def generate_embeddings(text):
    response = AOAI_client.embeddings.create(input=text, model=os.environ['openai_embeddings_deployment'])
    embeddings = response.model_dump()
    return embeddings['data'][0]['embedding']

def vector_search(query):
    query_embedding = generate_embeddings(query)
    pipeline = [
        {
            '$search': {
                "cosmosSearch": {
                    "vector": query_embedding,
                    "path": "contentVector",
                    "k": int(os.environ['vector_search_numList'])
                },
                "returnStoredSource": True
            }
        },
        {'$project': { 'similarityScore': { '$meta': 'searchScore' }, 'document' : '$$ROOT' } }
    ]
    results = collection.aggregate(pipeline)
    return results

def insert_log(query, results):
    log_collection = db[os.environ['cosmos_db_mongo_log_collectionname']]
    japan_tz = pytz.timezone('Asia/Tokyo')
    current_time_japan = datetime.datetime.now(japan_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    log_data = {
        "query": query,
        "timestamp": current_time_japan,
        "results": []
    }
    
    for result in results:
        data = {
            "Similarity Score": result['similarityScore'],
            "No": result['document'].get('No'),
            "title": result['document'].get('title'),
            "content": result['document'].get('content'),
        }
        log_data["results"].append(data)
    
    return log_collection.insert_one(log_data)