# Common database module
from .mongodb import (
    get_mongo_client,
    get_database,
    close_mongo_connection,
    get_users_collection,
    get_restaurants_collection,
    get_reviews_collection,
    get_favorites_collection,
    get_sessions_collection,
    get_preferences_collection,
    get_photos_collection,
    get_menus_collection,
)

__all__ = [
    'get_mongo_client',
    'get_database',
    'close_mongo_connection',
    'get_users_collection',
    'get_restaurants_collection',
    'get_reviews_collection',
    'get_favorites_collection',
    'get_sessions_collection',
    'get_preferences_collection',
    'get_photos_collection',
    'get_menus_collection',
]
