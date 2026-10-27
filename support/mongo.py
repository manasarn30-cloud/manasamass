import logging
from datetime import datetime
from django.conf import settings
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

logger = logging.getLogger('streamflix')

# Singleton client instance
_mongo_client = None


def get_mongo_client():
    """
    Returns a connected MongoClient or None if MongoDB is unavailable.
    Uses short timeout to avoid blocking web requests when offline.
    """
    global _mongo_client
    if _mongo_client is not None:
        return _mongo_client

    mongo_uri = getattr(settings, 'MONGO_URI', 'mongodb://localhost:27017/')
    try:
        # 1.5s server selection timeout for quick responsiveness
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1500)
        # Ping the server to test connection
        client.admin.command('ping')
        _mongo_client = client
        _ensure_indexes(client)
        return _mongo_client
    except (ServerSelectionTimeoutError, PyMongoError) as e:
        logger.warning(f"MongoDB connection unavailable: {e.__class__.__name__}. Running in resilient mode.")
        return None
    except Exception as e:
        logger.warning(f"Failed to initialize MongoDB client: {e}")
        return None


def get_mongo_db():
    """Returns database object or None."""
    client = get_mongo_client()
    if client is not None:
        db_name = getattr(settings, 'MONGO_DB_NAME', 'streamflix_db')
        return client[db_name]
    return None


def _ensure_indexes(client):
    """Ensures indexing on conversation_id and timestamp."""
    try:
        db_name = getattr(settings, 'MONGO_DB_NAME', 'streamflix_db')
        db = client[db_name]
        db.chat_logs.create_index([("conversation_id", ASCENDING), ("timestamp", DESCENDING)])
        db.chat_logs.create_index([("timestamp", DESCENDING)])
        db.chat_feedback.create_index([("conversation_id", ASCENDING)])
        db.chat_feedback.create_index([("timestamp", DESCENDING)])
    except Exception as e:
        logger.warning(f"Could not create MongoDB indexes: {e}")


def log_chat_message(conversation_id, message_role, message_text, user_id=None,
                     anonymous_session_id=None, matched_faq_id=None,
                     detected_error_code=None, response_type="text",
                     support_ticket_reference=None):
    """
    Persists a chat message in the MongoDB chat_logs collection.
    Never logs passwords, tokens, or private secrets.
    """
    db = get_mongo_db()
    if db is None:
        logger.info(f"MongoDB offline: chat message [{conversation_id}] not persisted to MongoDB.")
        return False

    doc = {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "anonymous_session_id": anonymous_session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "role": message_role,
        "message_text": message_text,
        "matched_faq_id": matched_faq_id,
        "detected_error_code": detected_error_code,
        "response_type": response_type,
        "support_ticket_reference": support_ticket_reference,
    }

    try:
        db.chat_logs.insert_one(doc)
        return True
    except PyMongoError as e:
        logger.error(f"Failed to insert chat log into MongoDB: {e.__class__.__name__}")
        return False


def log_chat_feedback(conversation_id, message_id, rating, feedback_text=None, user_id=None):
    """
    Persists chatbot rating/feedback in the MongoDB chat_feedback collection.
    """
    db = get_mongo_db()
    if db is None:
        logger.info(f"MongoDB offline: chat feedback [{conversation_id}] not persisted to MongoDB.")
        return False

    doc = {
        "conversation_id": conversation_id,
        "message_id": message_id,
        "rating": rating,  # 'helpful' or 'not_helpful'
        "feedback_text": feedback_text or "",
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
    }

    try:
        db.chat_feedback.insert_one(doc)
        return True
    except PyMongoError as e:
        logger.error(f"Failed to insert chat feedback into MongoDB: {e.__class__.__name__}")
        return False


def get_conversation_history(conversation_id, limit=20):
    """
    Retrieves previous messages for a conversation if MongoDB is connected.
    """
    db = get_mongo_db()
    if db is None:
        return []

    try:
        cursor = db.chat_logs.find(
            {"conversation_id": conversation_id},
            {"_id": 0}
        ).sort("timestamp", ASCENDING).limit(limit)
        return list(cursor)
    except Exception as e:
        logger.warning(f"Error reading conversation history from MongoDB: {e}")
        return []


def check_mongo_health():
    """
    Returns (status: bool, message: str) for health-check endpoint.
    """
    mongo_uri = getattr(settings, 'MONGO_URI', 'mongodb://localhost:27017/')
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1200)
        client.admin.command('ping')
        return True, "connected"
    except Exception as e:
        return False, f"unavailable ({e.__class__.__name__})"
