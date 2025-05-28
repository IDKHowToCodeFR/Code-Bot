# ============================== #
#         Database Module        #
# ============================== #

import aiosqlite
import os
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("USER_CONTEXT")

# Keep a persistent connection for better performance
_db_connection = None

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
        # Create index on user_id and timestamp for faster queries
        await _db_connection.execute("CREATE INDEX IF NOT EXISTS idx_user_time ON user_responses(user_id, timestamp);")
        await _db_connection.commit()

async def store_user_response(user_id: int, prompt: str, response: str):
    # Use persistent connection instead of opening a new one every time
    await _db_connection.execute(
        "INSERT INTO user_responses (user_id, prompt, response) VALUES (?, ?, ?)",
        (user_id, prompt, response)
    )
    await _db_connection.commit()

async def get_user_history(user_id: int, max_chars: int = 1500):
    """
    Get user history limited by total characters rather than rows for better prompt size control.
    """
    async with _db_connection.execute(
        "SELECT prompt, response FROM user_responses WHERE user_id = ? ORDER BY timestamp DESC",
        (user_id,)
    ) as cursor:
        rows = await cursor.fetchall()

    # Build history until max_chars limit reached
    history = []
    total_len = 0
    for prompt, response in reversed(rows):  # oldest first
        entry = f"Q: {prompt}\nA: {response}\n"
        total_len += len(entry)
        if total_len > max_chars:
            break
        history.append(entry)

    return history
