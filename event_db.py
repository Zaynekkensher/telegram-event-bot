import asyncpg
import os

DB_URL = os.getenv("DB_URL")

async def add_event(chat_id, date, time, city, type_, place, description):
    conn = await asyncpg.connect(DB_URL)
    await conn.execute("""
        INSERT INTO events (chat_id, date, time, city, type, place, description)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    """, chat_id, date, time, city, type_, place, description)
    await conn.close()

async def get_events(chat_id):
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch("""
        SELECT id, date, time, city, type, place, description
        FROM events
        WHERE chat_id = $1
        ORDER BY date, time
    """, chat_id)
    await conn.close()
    return rows

async def delete_event(chat_id, event_id):
    conn = await asyncpg.connect(DB_URL)
    await conn.execute("""
        DELETE FROM events
        WHERE chat_id = $1 AND id = $2
    """, chat_id, event_id)
    await conn.close()

__all__ = ["add_event", "get_events", "delete_event"]
