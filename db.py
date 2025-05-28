# ============================== #
#         Database Module        #
# ============================== #

# --- Imports ---
import aiosqlite
import os
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()
DB_NAME = os.getenv("USER_CONTEXT")  # SQLite DB filename from .env

# --- Persistent DB Connection ---
_db_connection = None  # Global connection to avoid repeated opening

# --- Initialize DB (Create Table + Index) ---
async def initialize():
    global _db_connection
    if _db_connection is None:
        _db_connection = await aiosqlite.connect(DB_NAME)
        await _db_connection.execute("""
            CREATE TABLE IF NOT EXISTS user_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Index for fast lookup by user and time
        await _db_connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_user_time ON user_responses(user_id, timestamp);"
        )
        await _db_connection.commit()

# --- Store a User's Prompt + Response ---
async def store_user_response(user_id: int, prompt: str, response: str):
    await _db_connection.execute(
        "INSERT INTO user_responses (user_id, prompt, response) VALUES (?, ?, ?)",
        (user_id, prompt, response)
    )
    await _db_connection.commit()

# --- Fetch User History (Truncate to max_chars) ---
async def get_user_history(user_id: int, max_chars: int = 1500):
    """
    Returns a list of Q&A strings for a user, capped by total character length.
    Newest entries are included first, but returned oldest-first for prompt building.
    """
    async with _db_connection.execute(
        "SELECT prompt, response FROM user_responses WHERE user_id = ? ORDER BY timestamp DESC",
        (user_id,)
    ) as cursor:
        rows = await cursor.fetchall()

    history = []
    total_len = 0
    for prompt, response in reversed(rows):  # oldest to newest
        entry = f"Q: {prompt}\nA: {response}\n"
        total_len += len(entry)
        if total_len > max_chars:
            break
        history.append(entry)

    return history
