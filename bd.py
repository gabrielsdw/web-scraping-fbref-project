from pymongo.mongo_client import MongoClient

class Db:
    def __init__(self, user: str, password: str, name_db: str, name_collection: str) -> None:
        self.user = user
        self.password = password
        self.url_connect = f"mongodb+srv://{user}:{password}@fbref.ykohrzq.mongodb.net/?retryWrites=true&w=majority&appName=fbref"
        self.client = MongoClient(self.url_connect)
        self.db = self.client[name_db]
        self.collection = self.db[name_collection]


    def insert_many_db(self, data: list[dict]) -> None:
        try:
            self.collection.insert_many(data)
        except Exception as e:
            print(e)
        else:
            print("Sucess")


if __name__ == '__main__':
    db = Db('gabrielsdw', '54321', 'fbref', 'PremierLeague')
    db.insert_many_db([
        {'2':3},
        {'teste':True}
    ])

























    """uri = "mongodb+srv://gabrielsdw:54321@fbref.ykohrzq.mongodb.net/?retryWrites=true&w=majority&appName=fbref"

    # Create a new client and connect to the server
    client = MongoClient(uri)

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)"""

