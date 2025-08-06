from bson import ObjectId
from datetime import datetime
from typing import Any, Dict, List, Union

def serialize_objectid(obj: Any) -> Any:
    """
    Recursively convert MongoDB ObjectId objects to strings for JSON serialization.
    Also handles datetime objects by converting them to ISO format strings.
    
    Args:
        obj: The object to serialize (can be dict, list, ObjectId, datetime, or any other type)
        
    Returns:
        The serialized object with ObjectIds converted to strings
    """
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: serialize_objectid(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_objectid(item) for item in obj]
    else:
        return obj

def prepare_for_json(data: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
    """
    Prepare MongoDB data for JSON serialization by handling ObjectIds and datetimes.
    This is an alias for serialize_objectid for better semantic meaning.
    
    Args:
        data: The data to prepare for JSON serialization
        
    Returns:
        JSON-serializable data
    """
    return serialize_objectid(data)