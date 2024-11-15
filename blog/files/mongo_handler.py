from pymongo import MongoClient

def MongoInsertHandler(doc):
    uri             = "mongodb+srv://<username>:<password>@<mongo-endpoint>/?retryWrites=true&w=majority"
    collection_name = "incoming"

    try:
        client = MongoClient(uri)
    # return a friendly error if a URI error is thrown 
    except Exception as e:
        print(e)

    # use a database
    db = client["emqx-kafka-mongo-app"]

    # use a collection
    my_collection = db[collection_name]

    # INSERT DOCUMENTS
    #
    # In this example, You can insert individual documents using collection.insert_one().
    # If you are creating multiple documents then we can insert them all with insert_many().
    try:
        print("Inserting document: {}".format(doc))
        result = my_collection.insert_one(doc)
        print("Document inserted!")
    # return a friendly error if the operation fails
    except Exception as e:
        print(e)

# if __name__ == "__main__":
#     document = {"hello": "HI"}
#     MongoInsertHandler(document)