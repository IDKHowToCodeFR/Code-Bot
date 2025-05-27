# ============================== #
#         Database Module        #
# ============================== #

# ---------- Imports ----------
import aiosqlite
import os
from dotenv import load_dotenv

# ---------- Load Environment Variables ----------
load_dotenv()
DB_NAME = os.getenv("USER_CONTEXT")  # DB file path

# ---------- UserResponseDB Class ----------
class UserResponseDB:
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path  # DB connection path

    # ---------- Initialize Table ----------
    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)  # Create table if missing
            await db.commit()

    # ---------- Store User Response ----------
    async def store_response(self, user_id: int, prompt: str, response: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO user_responses (user_id, prompt, response) VALUES (?, ?, ?)",
                (user_id, prompt, response)
            )  # Insert user Q&A
            await db.commit()

    # ---------- Retrieve User History ----------
    async def get_history(self, user_id: int, limit: int = 3000):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT prompt, response
                FROM user_responses
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (user_id, limit)
            ) as cursor:
                return await cursor.fetchall()  # Fetch recent Q&A pairs
