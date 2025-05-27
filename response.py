# ============================== #
#        Cohere Assistant        #
# ============================== #

# ---------- Imports ----------
import os
from dotenv import load_dotenv
import cohere
from db import UserResponseDB

# ---------- Load Environment Variables ----------
load_dotenv()

# ---------- Assistant Class ----------
class CohereAssistant:
    def __init__(self):
        self.client = cohere.ClientV2(api_key=os.getenv("AI_API_KEY"))  # Initialize Cohere client
        self.instr_query = os.getenv("SYSTEM_INSTR_MSG", "")  # System prompt for general queries
        self.instr_dbt = os.getenv("SYSTEM_INSTR_DBT", "")  # System prompt for doubts
        self.instr_strict = os.getenv("SYSTEM_INSTR_STRICT", "")  # Additional strict instructions
        self.db = UserResponseDB()  # DB to fetch user context

    # ---------- Build User Context ----------
    async def _build_context(self, user_id: int) -> str:
        history = await self.db.get_history(user_id)  # Fetch recent Q&A history
        return "\n".join(f"Q: {h[0]}\nA: {h[1]}" for h in reversed(history))  # Format for prompt

    # ---------- Chat with Cohere ----------
    async def _chat(self, system_msg: str, user_prompt: str) -> str:
        response = self.client.chat(
            model="command-a-03-2025",
            messages=[
                {"role": "system", "content": system_msg + self.instr_strict},  # Combine system instructions
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.message.content[0].text  # Extract reply text

    # ---------- General Query ----------
    async def query(self, prompt: str, user_id: int) -> str:
        context = await self._build_context(user_id)  # Get user context
        full_prompt = f"{context}\nQ: {prompt}\nA:" if context else prompt  # Append current question
        return await self._chat(self.instr_query, full_prompt)

    # ---------- Code Doubt ----------
    async def doubt(self, prompt: str, user_id: int) -> str:
        context = await self._build_context(user_id)  # Get user context
        full_prompt = f"{context}\nQ: {prompt}\nA:" if context else prompt  # Append current question
        return await self._chat(self.instr_dbt, full_prompt)  # Use doubt-specific instructions

    # ---------- Resource Recommendation ----------
    async def resources(self, topic: str, n : int) -> str:
        return await self._chat(self.instr_query, f"Give me links to at-least {n} resources related to {topic} ")  # Request resource links

    # ---------- Random Tips ----------
    async def tips(self, topic: str, n : int) -> str:
        return await self._chat(self.instr_query, f"Give me {n} random tips related to {topic} ")  # Request tips list

    # ---------- Help Menu ----------
    @staticmethod
    def help_message() -> str:
        return (
            "**🤖 Code - Bot Help Menu**\n\n"
            "Here are the commands you can use:\n\n"
            "📬 **Private & Public Help**\n"
            "• `/cph <query>`       — _DMs you personalized help_\n"
            "• `/coh <query>`       — _Public help in this channel_\n\n"

            "🛠️ **Debug & Analyze Code**\n"
            "• `/dbt <code>`        — _Analyze and improve your code_\n"
            "• `/debug <code>`      — _Detect potential bugs in your code_\n\n"

            "📚 **Learning Resources & Tips**\n"
            "• `/resources <topic>` — _Get curated study materials_\n"
            "• `/tips <topic>`      — _Receive a helpful tip on the topic_\n\n"

            "❓ **Utility**\n"
            "• `/chelp`             — _Show this help menu_\n\n"

            "💡 *Start typing any command to get assistance with your code.*\n"
            "_Happy Coding!_ 🎉"
        )  # Static help text

    # ---------- Error Message ----------
    @staticmethod
    def error_message() -> str:
        return "⚠️ An error occurred while processing your request"  # Generic error message
