from fastapi import FastAPI
from schema import StudentSchemaCreate, StudentSchemaReturn
from typing import List
import time

app = FastAPI()

# Health check endpoint
@app.get("/health")
def health_check():
    return {"service": "api", "status": "healthy", "timestamp": time.time()}

@app.post("/student/add", response_model=StudentSchemaReturn)
def add_new_student(student: StudentSchemaCreate):
    return student

@app.get("/student/all", response_model=List[StudentSchemaReturn])
def read_items():    
    return []