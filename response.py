# ============================== #
#        CodeBot Response        #
# ============================== #

# --- Imports ---
import os
from dotenv import load_dotenv
import cohere
from db import get_user_history
import asyncio

# --- Load Environment Variables ---
load_dotenv()
instr_query: str = os.getenv("SYSTEM_INSTR_MSG")       # Instruction for regular queries
instr_dbg: str = os.getenv("SYSTEM_INSTR_DBT")         # Instruction for debugging
instr_strict: str = os.getenv("SYSTEM_INSTR_STRICT")   # Extra strict enforcement prompt

# --- Initialize Cohere Client (Singleton) ---
client = cohere.ClientV2(api_key=os.getenv("AI_API_KEY"))

# --- Helper: Build Prompt with User History ---
async def build_prompt(prompt: str, user_id: int) -> str:
    history = "".join(await get_user_history(user_id))  # Retrieve past interactions
    full_prompt = f"{history}\nQ: {prompt}\nA:" if history else f"Q: {prompt}\nA:"
    return full_prompt

# --- Query Handler (General Code Help) ---
async def query(prompt: str, user_id: int) -> str:
    full_prompt  = await build_prompt(prompt, user_id)
    response = client.chat(
        model="command-a-03-2025",
        messages=[
            {"role": "system", "content": instr_query + instr_strict},
            {"role": "user", "content": full_prompt},
        ],
    )
    return response.message.content[0].text

# --- Debug Handler (Bug Fixing / Review) ---
async def debug(prompt: str, user_id: int) -> str:
    full_prompt = await build_prompt(prompt, user_id)
    response = client.chat(
        model="command-a-03-2025",
        messages=[
            {"role": "system", "content": instr_dbg + instr_strict},
            {"role": "user", "content": full_prompt},
        ],
    )
    return response.message.content[0].text

# --- Resource Finder (Learning Links) ---
async def resources(topic: str, n: int) -> str:
    response = client.chat(
        model="command-a-03-2025",
        messages=[
            {"role": "system", "content": instr_query + instr_strict},
            {"role": "user", "content": f"Give me links to at least {n} resources related to {topic}."}
        ],
    )
    return response.message.content[0].text

# --- Tip Generator (Coding Advice) ---
async def tips(topic: str, n: int) -> str:
    response = client.chat(
        model="command-a-03-2025",
        messages=[
            {"role": "system", "content": instr_query + instr_strict},
            {"role": "user", "content": f"Give me {n} random tips related to {topic}."}
        ],
    )
    return response.message.content[0].text

# --- Help Menu Text ---
def chelp():
    return (
        "**📌 Available Commands:**\n"
        "• `📩 /cph <query>` — *DMs you personalized help*\n"
        "• `🌐 /coh <query>` — *Public help in this channel*\n"
        "• `🐞 /dbg <code>` — *Analyze and improve your code*\n"
        "• `🔍 /debug <code>` — *Find potential bugs in code*\n"
        "• `📚 /resources <topic>` — *Get curated learning material*\n"
        "• `📝 /tips <topic>` — *Receive a random tip related to topic*\n"
        "• `🆘 /chelp` — *Display this help message menu*\n\n"
        "**Type a command to get started. Happy coding!**"
    )

# --- Error Fallback Text ---
def error():
    return "⚠️ An error occurred while processing your request."
