import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Person, Photo, Tag

app = FastAPI(title="Family Tree API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers
class PersonCreate(Person):
    pass

class PhotoCreate(Photo):
    pass

class IDModel(BaseModel):
    id: str

@app.get("/")
def root():
    return {"message": "Family Tree Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Persons
@app.post("/api/persons", response_model=IDModel)
def create_person(person: PersonCreate):
    try:
        inserted_id = create_document("person", person)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/persons")
def list_persons():
    try:
        docs = get_documents("person")
        # Convert ObjectId to string
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Photos
@app.post("/api/photos", response_model=IDModel)
def create_photo(photo: PhotoCreate):
    try:
        inserted_id = create_document("photo", photo)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/photos")
def list_photos():
    try:
        docs = get_documents("photo")
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Seed example data
@app.post("/api/seed")
def seed_example():
    try:
        # Only seed if empty
        has_people = len(get_documents("person", {}, 1)) > 0
        has_photos = len(get_documents("photo", {}, 1)) > 0
        if has_people and has_photos:
            return {"status": "ok", "message": "Already seeded"}
        # Create persons
        people_ids = []
        john_id = create_document(
            "person",
            Person(full_name="John Carter", relation="Grandfather", birth_year=1942,
                   photo_url="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=600&q=80&auto=format&fit=crop")
        )
        people_ids.append(john_id)
        mary_id = create_document(
            "person",
            Person(full_name="Mary Carter", relation="Grandmother", birth_year=1945,
                   photo_url="https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?w=600&q=80&auto=format&fit=crop")
        )
        people_ids.append(mary_id)
        alice_id = create_document(
            "person",
            Person(full_name="Alice Carter", relation="Mother", birth_year=1975,
                   photo_url="https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=80&auto=format&fit=crop")
        )
        people_ids.append(alice_id)
        # Create photo with tags
        tags = [
            {"person_id": john_id, "x": 0.28, "y": 0.55, "label": "John"},
            {"person_id": mary_id, "x": 0.62, "y": 0.52, "label": "Mary"},
            {"person_id": alice_id, "x": 0.45, "y": 0.40, "label": "Alice"},
        ]
        create_document(
            "photo",
            Photo(
                title="Family Reunion 2001",
                url="https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?w=1600&q=80&auto=format&fit=crop",
                tags=tags  # type: ignore
            )
        )
        return {"status": "ok", "people": people_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
