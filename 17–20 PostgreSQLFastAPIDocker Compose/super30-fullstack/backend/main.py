import os 
import psycopg 
from fastapi import FastAPI,HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str

app = FastAPI(title="Super30 Database API")

def getconnection(): 
    return psycopg.connect( host=os.getenv("DB_HOST", "db"), 
                           port=int(os.getenv("DB_PORT", "5432")), 
                           dbname=os.getenv("POSTGRES_DB", "super30db"), 
                           user=os.getenv("POSTGRES_USER", "super30user"), 
                           password=os.environ["POSTGRES_PASSWORD"],
                               row_factory=dict_row, )

@app.get("/") 
def home(): 
    return {"message": "FastAPI is connected to the PostgreSQL service"}

@app.get("/health") 
def health(): 
        try: 
            with getconnection() as conn: 
                conn.execute("SELECT 1") 
                return {"status": "healthy", "database": "connected"} 
        except Exception: return {"status": "unhealthy", "database": "unavailable"}

@app.post("/items") 
def createitem(name: str): 
    with getconnection() as conn: row = conn.execute( "INSERT INTO items (name) VALUES (%s) RETURNING id, name", (name,) ).fetchone() 
    return row

@app.get("/items") 
def listitems(): 
    with getconnection() as conn: rows = conn.execute( "SELECT id, name FROM items ORDER BY id" ).fetchall() 
    return rows

@app.get("/items/{item_id}")
def get_item(item_id: int):
    with getconnection() as conn:
        row = conn.execute(
            "SELECT id, name FROM items WHERE id = %s",
            (item_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return row


@app.put("/items/{item_id}")
def update_item(item_id: int, item: ItemCreate):
    with getconnection() as conn:
        row = conn.execute(
            """
            UPDATE items
            SET name = %s
            WHERE id = %s
            RETURNING id, name
            """,
            (item.name, item_id)
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return row


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    with getconnection() as conn:
        row = conn.execute(
            """
            DELETE FROM items
            WHERE id = %s
            RETURNING id, name
            """,
            (item_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return {
        "message": "Item deleted successfully",
        "item": row
    }