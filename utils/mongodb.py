import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client[os.getenv("MONGO_DATABASE", "academicworld")]
faculty_col = db["faculty"]
publications_col = db["publications"]
favorites_col = db["favorite_publications"]


def w05_publication_trend_mongo(keyword):
    pipeline = [
        {"$unwind": "$keywords"},
        {"$match": {"keywords.name": {"$regex": keyword, "$options": "i"}}},
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    return list(publications_col.aggregate(pipeline))


def w04_search_faculty(keyword, limit=15):
    results = faculty_col.find(
        {"keywords.name": {"$regex": keyword, "$options": "i"}},
        {"name": 1, "affiliation": 1, "keywords": 1, "_id": 0}
    ).limit(limit)
    return list(results)


def w08_search_publications(keyword, limit=20):
    pipeline = [
        {"$unwind": "$keywords"},
        {"$match": {"keywords.name": {"$regex": keyword, "$options": "i"}}},
        {"$group": {
            "_id": "$id",
            "title": {"$first": "$title"},
            "year": {"$first": "$year"},
            "venue": {"$first": "$venue"},
            "numCitations": {"$first": "$numCitations"}
        }},
        {"$sort": {"numCitations": -1}},
        {"$limit": limit},
    ]
    return list(publications_col.aggregate(pipeline))


def w08_add_favorite(pub_id, title, year, venue):
    from datetime import datetime
    try:
        favorites_col.insert_one({
            "publication_id": pub_id,
            "title": title,
            "year": year,
            "venue": venue,
            "status": "unread",
            "note": "",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })
        return True, "Added to favorites."
    except Exception as e:
        return False, "Already in favorites." if "duplicate" in str(e).lower() else str(e)


def w08_remove_favorite(pub_id):
    favorites_col.delete_one({"publication_id": pub_id})


def w08_get_favorites():
    return list(favorites_col.find({}, {"_id": 0}).sort("updated_at", -1))
