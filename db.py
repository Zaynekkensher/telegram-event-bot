import asyncio
import asyncpg
import os

DB_URL = os.getenv("DB_URL")

CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    city TEXT NOT NULL,
    type TEXT NOT NULL,
    place TEXT,
    description TEXT
);
"""

async def create_connection():
    conn = await asyncpg.connect(DB_URL)
    await conn.execute(CREATE_EVENTS_TABLE)
    await conn.close()

asyncio.run(create_connection())