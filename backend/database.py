import os
import pymongo
import uuid
import datetime
import logging

logger = logging.getLogger()

# MongoDB Client (Global to reuse across invocations for warm starts)
client = None

# Collection Names
TODOS_COLLECTION = 'todos'
NOTES_COLLECTION = 'notes'
KEYWORDS_COLLECTION = 'keywords'

def _get_db():
    global client
    db_name = os.environ.get('MONGO_DB_NAME', 'voice_assistant')
    if not client:
        user = os.environ.get('MONGO_USERNAME')
        password = os.environ.get('MONGO_PASSWORD')
        
        instance_id = os.environ.get('MONGO_INSTANCE_ID')
        private_network_id = os.environ.get('MONGO_PRIVATE_NETWORK_ID')
        cert_file = os.environ.get('MONGO_TLS_CERT_FILE', 'cert.pem')
        
        # If running in Scaleway Function, cert.pem should be in root (./cert.pem) or backend/cert.pem
        if not os.path.exists(cert_file):
             # Fallback to relative path if needed
             cert_file = os.path.join(os.path.dirname(__file__), cert_file)

        if not instance_id or not private_network_id:
            # Fallback for local testing or public endpoint
            host = os.environ.get('MONGO_HOST')
            if host:
                uri = f"mongodb+srv://{user}:{password}@{host}/?retryWrites=true&w=majority"
            else:
                 # If we are mocking or testing without DB, this might fail unless we mock client
                 logger.warning("MONGO_INSTANCE_ID or MONGO_HOST not set. DB operations will fail.")
                 return None 
        else:
            # Scaleway Private Network Connection String
            host = f"{instance_id}.{private_network_id}.internal"
            uri = f"mongodb+srv://{user}:{password}@{host}/?tls=true&tlsCAFile={cert_file}"

        client = pymongo.MongoClient(uri)
        
    return client[db_name]

def get_mongo_collection():
    """Legacy helper for backward compatibility, returns 'todos' collection"""
    db = _get_db()
    return db[TODOS_COLLECTION] if db is not None else None

def save_todo_item(text, priority):
    try:
        collection = get_mongo_collection()
        if collection is None:
             raise Exception("Database connection not configured")

        item = {
            'id': str(uuid.uuid4()),
            'text': text,
            'priority': priority,
            'created_at': datetime.datetime.utcnow().isoformat(),
            'status': 'pending'
        }
        
        collection.insert_one(item)
        # Remove _id (ObjectId) before returning
        item.pop('_id', None)
        return item
    except Exception as e:
        logger.error(f"Mongo Error: {e}")
        raise e

def save_note_item(text):
    try:
        db = _get_db()
        if db is None:
             raise Exception("Database connection not configured")
        
        collection = db[NOTES_COLLECTION]
        
        item = {
            'id': str(uuid.uuid4()),
            'text': text,
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        
        collection.insert_one(item)
        item.pop('_id', None)
        return item
    except Exception as e:
        logger.error(f"Mongo Error saving note: {e}")
        raise e

def delete_todo_item(item_id):
    try:
        collection = get_mongo_collection()
        if collection is not None:
            result = collection.delete_one({'id': item_id})
            return result.deleted_count > 0
        return False
    except Exception as e:
        logger.error(f"Mongo Error deleting todo: {e}")
        return False

def delete_note_item(item_id):
    try:
        db = _get_db()
        if db is not None:
            collection = db[NOTES_COLLECTION]
            result = collection.delete_one({'id': item_id})
            return result.deleted_count > 0
        return False
    except Exception as e:
        logger.error(f"Mongo Error deleting note: {e}")
        return False

def get_all_todos():
    try:
        collection = get_mongo_collection()
        if collection is not None:
            # Sort by created_at descending (newest first)
            items = list(collection.find({}, {'_id': 0}).sort('created_at', -1))
            return items
        return []
    except Exception as e:
        logger.error(f"Mongo Error listing todos: {e}")
        return []

def get_all_notes():
    try:
        db = _get_db()
        if db is not None:
            collection = db[NOTES_COLLECTION]
            items = list(collection.find({}, {'_id': 0}).sort('created_at', -1))
            return items
        return []
        return []
    except Exception as e:
        logger.error(f"Mongo Error listing notes: {e}")
        return []

def get_all_keywords():
    try:
        db = _get_db()
        if db is not None:
            collection = db[KEYWORDS_COLLECTION]
            # Return as a dictionary {key: value}
            items = list(collection.find({}, {'_id': 0}))
            keywords = {item['key']: item['value'] for item in items if 'key' in item and 'value' in item}
            return keywords
        return {}
    except Exception as e:
        logger.error(f"Mongo Error listing keywords: {e}")
        return {}

def save_keyword(key, value):
    try:
        db = _get_db()
        if db is None:
             raise Exception("Database connection not configured")
        
        collection = db[KEYWORDS_COLLECTION]
        
        item = {
            'id': str(uuid.uuid4()),
            'key': key.lower(), # Normalize to lowercase
            'value': value,
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        
        # Upsert: Update if key exists, otherwise insert
        collection.update_one(
            {'key': key.lower()},
            {'$set': item},
            upsert=True
        )
        return item
    except Exception as e:
        logger.error(f"Mongo Error saving keyword: {e}")
        raise e

def delete_keyword(key):
    try:
        db = _get_db()
        if db is not None:
            collection = db[KEYWORDS_COLLECTION]
            # Delete by key (which is unique/primary for our usage)
            result = collection.delete_one({'key': key.lower()})
            return result.deleted_count > 0
        return False
    except Exception as e:
        logger.error(f"Mongo Error deleting keyword: {e}")
        return False
