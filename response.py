import os
from dotenv import load_dotenv
import cohere
from db import get_user_history
import asyncio

load_dotenv()
instr_query: str = os.getenv("SYSTEM_INSTR_MSG", "")
instr_dbg: str = os.getenv("SYSTEM_INSTR_DBT", "")
instr_strict: str = os.getenv("SYSTEM_INSTR_STRICT", "")

client = cohere.ClientV2(api_key=os.getenv("AI_API_KEY"))  # reused single instance

async def build_prompt(prompt: str, user_id: int) -> str:
    history = "".join(await get_user_history(user_id))
    full_prompt = f"{history}\nQ: {prompt}\nA:" if history else f"Q: {prompt}\nA:"
    return full_prompt

async def query(prompt: str, user_id: int) -> str:
    full_prompt  = await build_prompt(prompt, user_id)
    # If client.chat() is synchronous, consider:
    # response = await asyncio.to_thread(client.chat, model="command-a-03-2025", messages=[...])
    response = client.chat(
        model="command-a-03-2025",
        messages=[
            {"role": "system", "content": instr_query + instr_strict},
            {"role": "user", "content": full_prompt},
        ],
    )
    return response.message.content[0].text

async def debug(prompt: str, user_id: int) -> str:
    # history = "".join(get_user_history(user_id))
    full_prompt = await build_prompt(prompt, user_id)
    response = client.chat(
        model="command-a-03-2025",
        messages=[
            {"role": "system", "content": instr_dbg + instr_strict},
            {"role": "user", "content": full_prompt},
        ],
    )
    return response.message.content[0].text

async def resources(topic: str, n :int) -> str:
    response = client.chat(
        model="command-a-03-2025",
        messages=[
            {"role": "system", "content": instr_query + instr_strict},
            {"role": "user", "content": f"Give me links to at least {n} resources related to {topic}."}
        ],
    )
    return response.message.content[0].text

async def tips(topic: str , n : int) -> str:
    response = client.chat(
        model="command-a-03-2025",
        messages=[
            {"role": "system", "content": instr_query + instr_strict},
            {"role": "user", "content": f"Give me {n} random tips related to {topic}."}
        ],
    )
    return response.message.content[0].text

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
        "*Type a command to get started. Happy coding!*"
    )

def error():
    return "⚠️ An error occurred while processing your request."
