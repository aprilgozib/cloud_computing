from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db_setup import SessionLocal, engine
import model
from schema import StudentSchemaCreate, StudentSchemaReturn
from typing import List, Dict, Any
import redis
import time
import os
import json

app = FastAPI()

# Redis connection with password from environment
redis_password = os.getenv('REDIS_PASSWORD')
try:
    redis_client = redis.Redis(host='redis', port=6379, db=0, password=redis_password, decode_responses=True)
    # Test the connection
    redis_client.ping()
    print("Redis connection successful")
except Exception as e:
    print(f"Redis connection failed: {e}")
    redis_client = None

model.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "api", "timestamp": time.time()}

@app.post("/student/add", response_model=StudentSchemaReturn)
def add_new_student(student: StudentSchemaCreate, db: Session = Depends(get_db)):
    start_time = time.time()
    
    new_student = model.StudentModel(
        student_id=student.student_id,
        first_name=student.first_name,
        last_name=student.last_name,
        module_code=student.module_code
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    if redis_client:
        try:
            # Invalidate /all cache here so the next /all fetch is fresh
            redis_client.delete("students:all")
        except Exception as e:
            print(f"Redis setex failed: {e}")

    return new_student

@app.get("/student/all", response_model=List[StudentSchemaReturn])
def read_items(db: Session = Depends(get_db)):
    start_time = time.time()
    
    # Try cache first (only if Redis is available)
    cache_key = "students:all"
    cached = None
    
    if redis_client:
        try:
            cached = redis_client.get(cache_key)
        except Exception as e:
            print(f"Redis get failed: {e}")
    
    if cached:
        try:
            cached_students = json.loads(cached)
            return cached_students
        except Exception as e:
            print(f"Redis cache read failed: {e}")
    
    students = db.query(model.StudentModel).all()
    
    # Cache for 2 minutes (only if Redis is available)
    if redis_client:
        try:
            students_data = [{
                "student_id": s.student_id,
                "first_name": s.first_name,
                "last_name": s.last_name,
                "module_code": s.module_code
            } for s in students]
            redis_client.setex(cache_key, 120, json.dumps(students_data))
        except Exception as e:
            print(f"Redis setex failed: {e}")
    
    return students

@app.get("/student/all/with-cache-info")
def read_items_with_cache_info(db: Session = Depends(get_db)) -> Dict[str, Any]:
    start_time = time.time()
    
    # Try cache first (only if Redis is available)
    cache_key = "students:all"
    cached = None
    cache_status = "miss"
    ttl = None
    cache_age = None
    
    if redis_client:
        try:
            cached = redis_client.get(cache_key)
            if cached:
                cache_status = "hit"
                ttl = redis_client.ttl(cache_key)
                cache_age = 120 - ttl if ttl > 0 else None  # Calculate cache age
        except Exception as e:
            print(f"Redis get failed: {e}")
    
    response_time = time.time() - start_time
    
    if cached:
        try:
            cached_students = json.loads(cached)
            return {
                "data": cached_students,
                "cache_info": {
                    "status": cache_status,
                    "source": "redis",
                    "ttl_seconds": ttl,
                    "cache_age_seconds": cache_age,
                    "response_time_ms": round(response_time * 1000, 2)
                }
            }
        except Exception as e:
            print(f"Redis cache read failed: {e}")
    
    # Fetch from database
    students = db.query(model.StudentModel).all()
    students_data = [{
        "student_id": s.student_id,
        "first_name": s.first_name,
        "last_name": s.last_name,
        "module_code": s.module_code
    } for s in students]
    
    # Cache for 2 minutes (only if Redis is available)
    if redis_client:
        try:
            redis_client.setex(cache_key, 120, json.dumps(students_data))
        except Exception as e:
            print(f"Redis setex failed: {e}")
    
    response_time = time.time() - start_time
    
    return {
        "data": students_data,
        "cache_info": {
            "status": "miss",
            "source": "database",
            "ttl_seconds": 120,  # New cache TTL
            "cache_age_seconds": 0,  # Fresh from database
            "response_time_ms": round(response_time * 1000, 2)
        }
    }

@app.delete("/student/cache/clear")
def clear_students_cache():
    """Clear the students cache from Redis"""
    start_time = time.time()
    
    cache_key = "students:all"
    cleared = False
    
    if redis_client:
        try:
            result = redis_client.delete(cache_key)
            cleared = result > 0
        except Exception as e:
            print(f"Redis delete failed: {e}")
            return {"success": False, "error": str(e)}, 500
    
    response_time = time.time() - start_time
    
    return {
        "success": True,
        "cleared": cleared,
        "cache_key": cache_key,
        "response_time_ms": round(response_time * 1000, 2)
    }