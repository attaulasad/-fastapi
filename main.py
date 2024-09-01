from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.collection import Collection
from jinja2 import Environment, FileSystemLoader

app = FastAPI()

# MongoDB setup
client = MongoClient("mongodb+srv://asad007:asad113@cluster0.nhczc.mongodb.net/?retryWrites=true&w=majority")

db = client["notes_db"]
notes_collection: Collection = db["notes"]

# Jinja2 setup
template_env = Environment(loader=FileSystemLoader('templates'))

# Pydantic model for a note
class NoteIn(BaseModel):
    content: str

class NoteOut(BaseModel):
    id: str
    content: str

@app.post("/notes/", response_model=NoteOut)
def create_note(note: NoteIn):
    result = notes_collection.insert_one({"content": note.content})
    note_id = str(result.inserted_id)
    return {"id": note_id, "content": note.content}

@app.get("/notes/{note_id}", response_model=NoteOut)
def read_note(note_id: str):
    note = notes_collection.find_one({"_id": note_id})
    if note:
        return {"id": note["_id"], "content": note["content"]}
    else:
        raise HTTPException(status_code=404, detail="Note not found")

@app.put("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: str, note: NoteIn):
    result = notes_collection.update_one({"_id": note_id}, {"$set": {"content": note.content}})
    if result.matched_count:
        return {"id": note_id, "content": note.content}
    else:
        raise HTTPException(status_code=404, detail="Note not found")

@app.delete("/notes/{note_id}")
def delete_note(note_id: str):
    result = notes_collection.delete_one({"_id": note_id})
    if result.deleted_count:
        return {"message": "Note deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Note not found")

@app.get("/notes/", response_class=HTMLResponse)
async def list_notes(request: Request):
    notes = list(notes_collection.find())
    template = template_env.get_template('notes_list.html')
    return template.render(notes=notes)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    template = template_env.get_template('home.html')
    return template.render()

@app.post("/submit_note/")
async def submit_note(
    request: Request
):
    form = await request.form()
    content = form.get("content")
    if content:
        result = notes_collection.insert_one({"content": content})
        return {"id": str(result.inserted_id), "content": content}
    else:
        raise HTTPException(status_code=400, detail="No content provided")
