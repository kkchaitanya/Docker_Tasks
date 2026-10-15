import os
from contextlib import asynccontextmanager
from typing import Optional

import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# DATABASE_URL = os.environ["DATABASE_URL"]


def connect():
    # return psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=5)
    # def getconnection(): 
    return psycopg.connect( host=os.getenv("DB_HOST", "db"), 
                           port=int(os.getenv("DB_PORT", "5432")), 
                           dbname=os.getenv("POSTGRES_DB", "students_db"), 
                           user=os.getenv("POSTGRES_USER", "student_admin"), 
                           password=os.environ["POSTGRES_PASSWORD"],
                               row_factory=dict_row, )


def initialize_database():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                name VARCHAR(120) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                course VARCHAR(120) NOT NULL,
                age INTEGER NOT NULL CHECK (age BETWEEN 1 AND 120),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Compose starts this service only after PostgreSQL is healthy.
    initialize_database()
    yield


app = FastAPI(title="Student Management API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StudentIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=255)
    course: str = Field(min_length=1, max_length=120)
    age: int = Field(ge=1, le=120)


class Student(StudentIn):
    id: int
    created_at: str


def serialize(row):
    result = dict(row)
    result["created_at"] = result["created_at"].isoformat()
    return result


@app.get("/health")
def health():
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc


@app.get("/api/students")
def list_students():
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, name, email, course, age, created_at FROM students ORDER BY id DESC"
        ).fetchall()
    return [serialize(row) for row in rows]


@app.post("/api/students", status_code=201)
def create_student(student: StudentIn):
    try:
        with connect() as conn:
            row = conn.execute(
                """INSERT INTO students (name, email, course, age)
                   VALUES (%s, %s, %s, %s)
                   RETURNING id, name, email, course, age, created_at""",
                (student.name.strip(), student.email.strip().lower(),
                 student.course.strip(), student.age),
            ).fetchone()
        return serialize(row)
    except psycopg.errors.UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="A student with this email already exists.") from exc


@app.get("/api/students/{student_id}")
def get_student(student_id: int):
    with connect() as conn:
        row = conn.execute(
            "SELECT id, name, email, course, age, created_at FROM students WHERE id = %s",
            (student_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return serialize(row)


@app.put("/api/students/{student_id}")
def update_student(student_id: int, student: StudentIn):
    try:
        with connect() as conn:
            row = conn.execute(
                """UPDATE students
                   SET name = %s, email = %s, course = %s, age = %s
                   WHERE id = %s
                   RETURNING id, name, email, course, age, created_at""",
                (student.name.strip(), student.email.strip().lower(),
                 student.course.strip(), student.age, student_id),
            ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Student not found")
        return serialize(row)
    except psycopg.errors.UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="A student with this email already exists.") from exc


@app.delete("/api/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    with connect() as conn:
        cur = conn.execute("DELETE FROM students WHERE id = %s", (student_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")
    return Response(status_code=204)
