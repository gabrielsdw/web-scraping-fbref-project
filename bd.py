
from pymongo.mongo_client import MongoClient
import os

uri = "mongodb+srv://gabrielsdw:54321@fbref.jnldk9q.mongodb.net/?retryWrites=true&w=majority&appName=fbref"


def conecta_db(url, nome_db, nome_collection):

    client = MongoClient(url)

    db = client[nome_db]
    
    return db[nome_collection]


def insert_db(collection, data):
    collection.insert_many(data)

