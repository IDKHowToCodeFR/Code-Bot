# ============================== #
#         CodeBot Main           #
# ============================== #

# --- Imports ---
import os
import logging
import discord
import response  # Your custom module that handles API interaction
from dotenv import load_dotenv
from discord import Embed, Intents
from discord.ext import commands
import textwrap
from db import initialize, store_user_response  # DB-related logic

# --- Load Bot Token ---
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("CodeBot")

# --- Set Required Intents ---
intents = Intents.default()
intents.message_content = True  # Required for reading user messages
bot = commands.Bot(command_prefix='!', intents=intents)


# --- Embed Helper: Split large messages into chunks and send as embeds ---
CODE_BLOCK = "```"

async def send_chunks(send_func, content: str):
    if not isinstance(content, str):
        content = str(content)

    content = content.strip()
    if not content:
        # Handle case where there's nothing meaningful to send
        await send_func(content="Sorry, I couldn't generate a response.")
        return

    chunks = []         # Final list of message segments to send
    current = []        # Current chunk being assembled
    length = 0          # Character count of current chunk
    in_code_block = False  # Track if we're inside a code block

    # Work line-by-line to preserve formatting and avoid mid-line breaks
    lines = content.splitlines(keepends=True)
    for line in lines:
        stripped = line.strip()

        # Toggle code block tracking when encountering ```
        if stripped.startswith(CODE_BLOCK):
            in_code_block = not in_code_block

        # If adding this line exceeds Discord's limit, start a new chunk
        if length + len(line) > 2000:
            if in_code_block:
                # Close open code block before breaking to next chunk
                current.append(CODE_BLOCK + "\n")
                chunks.append("".join(current))

                # Reopen code block in the new chunk
                current = [CODE_BLOCK + "\n"]
                length = len(CODE_BLOCK) + len(line)
            else:
                chunks.append("".join(current))
                current = []
                length = len(line)

        current.append(line)
        length += len(line)

    # Add remaining chunk if any
    if current:
        if in_code_block and not current[-1].strip().startswith(CODE_BLOCK):
            # Close any unterminated code block
            current.append(CODE_BLOCK + "\n")
        chunks.append("".join(current))

    # Send each chunk as a Discord embed
    for i, chunk in enumerate(chunks):
        title = "Code - Bot" if i == 0 else " "  # Title only on first embed

        embed = Embed(
            title=title,
            description=chunk[:2000],  # Hard cap to prevent Discord API error
            color=0x00ff99
        )

        # Fetch bot owner to show in footer
        app_info = await bot.application_info()
        owner = app_info.owner
        embed.set_footer(text=f"Type /chelp for help • Made by @{owner.name}")

        try:
            await send_func(embed=embed)
        except Exception as e:
            logger.error(f"Failed to send chunk: {e}")



# ============================== #
#      Slash Command Handlers    #
# ============================== #

# --- Public code help (in current channel) ---
@bot.tree.command(name="coh", description="Get your query answered in current channel")
async def code_help_public(interaction: discord.Interaction, query: str):
    try:
        if interaction.response.is_done():
            return
        await interaction.response.defer(thinking=True)
        result = await response.query(query, interaction.user.id)
        await store_user_response(interaction.user.id, query, result)
        await send_chunks(interaction.followup.send, result)
    except discord.NotFound:
        logger.warning("Interaction expired before we could respond.")
    except Exception as e:
        logger.error(f"[ERROR] /coh - {e}", exc_info=True)
        await send_chunks(interaction.followup.send, response.error())


# --- Private code help (via DM) ---
@bot.tree.command(name="cph", description="Get your query answered privately in your DM")
async def code_help_private(interaction: discord.Interaction, query: str):
    if interaction.guild is None:
        await code_help_public(interaction=interaction, query=query)
    else:
        try:
            if interaction.response.is_done():
                return
            await interaction.response.defer()
            await send_chunks(interaction.followup.send, "Check your DM 🫣🫣")
            result = await response.query(query, interaction.user.id)
            await store_user_response(interaction.user.id, query, result)
            await send_chunks(interaction.user.send, result)
        except discord.Forbidden:
            logger.error(f"[ERROR] /cph - Cannot DM user {interaction.user}")
            await send_chunks(
                interaction.followup.send,
                ("❌ I couldn't DM you. Please check your privacy settings to allow messages from server members.\n\n"
                 "**To receive help in DMs, go to:**\n*Server Settings → Privacy Settings → Enable DMs from server members*")
            )
        except Exception as e:
            logger.error(f"[ERROR] /cph - {e}", exc_info=True)
            await send_chunks(interaction.followup.send, response.error())

# --- General code doubt ---
@bot.tree.command(name="doubt", description="Ask doubt related to code")
async def code_dbg(interaction: discord.Interaction, query: str):
    try:
        if interaction.response.is_done():
            return
        await interaction.response.defer()
        result = await response.query(query, interaction.user.id)
        await store_user_response(interaction.user.id, query, result)
        await send_chunks(interaction.followup.send, result)
    except Exception as e:
        logger.error(f"[ERROR] /doubt - {e}", exc_info=True)
        await send_chunks(interaction.followup.send, response.error())


# --- Debug code ---
@bot.tree.command(name="debug", description="Provide code for debug")
async def dbg_code(interaction: discord.Interaction, code: str):
    try:
        if interaction.response.is_done():
            return
        await interaction.response.defer()
        result = await response.debug(code, interaction.user.id)
        await store_user_response(interaction.user.id, code, result)
        await send_chunks(interaction.followup.send, result)
    except Exception as e:
        logger.error(f"[ERROR] /debug - {e}", exc_info=True)
        await send_chunks(interaction.followup.send, response.error())


# --- Resource recommendation ---
@bot.tree.command(name="resources", description="Get resources on a topic")
async def resources(interaction: discord.Interaction, topic: str, n: int = 3):
    try:
        if interaction.response.is_done():
            return
        await interaction.response.defer()
        result = await response.resources(topic, n)
        await send_chunks(interaction.followup.send, result)
    except Exception as e:
        logger.error(f"[ERROR] /resources - {e}", exc_info=True)
        await send_chunks(interaction.followup.send, response.error())


# --- Tips on a topic ---
@bot.tree.command(name="tips", description="Get tips on a topic")
async def tips(interaction: discord.Interaction, topic: str, n: int = 1):
    try:
        if interaction.response.is_done():
            return
        await interaction.response.defer()
        result = await response.tips(topic, n)
        await send_chunks(interaction.followup.send, result)
    except Exception as e:
        logger.error(f"[ERROR] /tips - {e}", exc_info=True)
        await send_chunks(interaction.followup.send, response.error())


# --- Help command ---
@bot.tree.command(name="chelp", description="Display help menu")
async def show_help(interaction: discord.Interaction):
    try:
        if interaction.response.is_done():
            return
        await interaction.response.defer()
        help_text = response.chelp()
        await send_chunks(interaction.followup.send, help_text)
    except Exception as e:
        logger.error(f"[ERROR] /chelp - {e}", exc_info=True)
        await send_chunks(interaction.followup.send, response.error())

# --- Strictness Control ---
@bot.tree.command(name="strict", description="Toggle Strictness (Default : True) (Type : y / n)")
async def strictness(interaction : discord.Interaction , value : str):
    try :
        if interaction.response.is_done():
            return
        await interaction.response.defer()
        send = await response.set_strict(value)
        await send_chunks(interaction.followup.send,send)
    except Exception as e:
        logger.error(f"[Error] /strict - {e}", exc_info = True)
        await send_chunks(interaction.followup.send, response.error())

# ============================== #
#           Events               #
# ============================== #

# --- Bot Ready Event ---
@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        await initialize()  # Initialize the SQLite DB
        await bot.tree.sync()  # Sync slash commands with Discord
        logger.info("Slash commands synced successfully.")
    except Exception as e:
        logger.error(f"Failed during on_ready initialization: {e}")


# ============================== #
#         Run the Bot            #
# ============================== #

bot.run(TOKEN)
