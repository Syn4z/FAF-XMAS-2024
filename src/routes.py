from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# PostgreSQL Database Configuration
DATABASE_URL = "postgresql://user:password@localhost:5432/santa_db"
database = Database(DATABASE_URL)


# Data Models
class Preference(BaseModel):
    child_name: str
    gift_preferences: List[str]
    age: int
    behavior_rating: int

class UpdatePreference(BaseModel):
    gift_preferences: Optional[List[str]] = None
    age: Optional[int] = None
    behavior_rating: Optional[int] = None


# Endpoints
@router.get("/preferences/")
def get_preferences():
    """Retrieve all preferences from the database."""
    return {"preferences": preferences_db}

@router.post("/preferences/")
def add_preferences(preference: Preference):
    """Add new preferences to the database."""
    preferences_db.append(preference)
    return {"message": "Preference added successfully", "preference": preference}

@router.put("/preferences/{child_name}")
def update_preferences(child_name: str, updated_data: UpdatePreference):
    """Update an existing child's preferences in the database."""
    for preference in preferences_db:
        if preference.child_name == child_name:
            if updated_data.gift_preferences is not None:
                preference.gift_preferences = updated_data.gift_preferences
            if updated_data.age is not None:
                preference.age = updated_data.age
            if updated_data.behavior_rating is not None:
                preference.behavior_rating = updated_data.behavior_rating
            return {"message": "Preference updated successfully", "preference": preference}
    
    raise HTTPException(status_code=404, detail="Child preference not found")

@router.post("/model/predict/")
def predict_delivery_efficiency(preference: Preference):
    """
    Predict delivery efficiency or gift happiness based on preferences.
    Mock implementation: adjust efficiency based on behavior rating.
    """
    efficiency = 100 - (10 - preference.behavior_rating) * 5
    return {"child_name": preference.child_name, "predicted_efficiency": efficiency}

@router.post("/path/shortest/")
def get_shortest_path(path_request: PathRequest):
    """Calculate the shortest path using path finding algorithm."""
    path = get_route() # Call path finding algorithm
    return path

@router.get("/hello/")
def say_hello():
    """Simple hello world endpoint."""
    return {"message": "Hello, World!"}
