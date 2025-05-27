# ============================== #
#         CodeBot Main           #
# ============================== #

# ---------- Imports ----------
import os
import discord
from dotenv import load_dotenv
from typing import Final
from discord import Embed, Intents
from discord.ext import commands
from db import UserResponseDB
from response import CohereAssistant

# ---------- Load Environment Variables ----------
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_BOT_TOKEN")

# ---------- CodeBot Class ----------
class CodeBot:
    def __init__(self):
        intents = Intents.default()
        intents.message_content = True  # Enable reading message content
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        self.db = UserResponseDB()  # Initialize user response DB
        self.ai = CohereAssistant()  # Initialize AI assistant

    # ---------- Send Embed Messages in Chunks ----------
    @staticmethod
    async def send_chunks(send_func, content: str):
        if not isinstance(content, str):
            content = str(content)
        if content.strip():
            chunks = [content[i:i + 2000] for i in range(0, len(content), 2000)]  # Split by Discord message limit
            for chunk in chunks:
                embed = discord.Embed(
                    title="Code - Bot",
                    description=chunk,
                    color=0x00ff99
                )
                embed.set_footer(text="Type /chelp for help")
                await send_func(embed=embed)
        else:
            await send_func(content="Sorry, I couldn't generate a response.")  # Handle empty response

    # ---------- Handle Queries ----------
    async def handle_query(self, interaction, query, is_dm=False):
        try:
            await interaction.response.defer()  # Defer response for processing time
            result = await self.ai.query(query, interaction.user.id)
            await self.db.store_response(interaction.user.id, query, result)  # Save to DB for context
            if is_dm:
                await self.send_chunks(interaction.user.send, result)
                await self.send_chunks(interaction.followup.send, "Check your DM")
            else:
                await self.send_chunks(interaction.followup.send, result)
        except discord.Forbidden:
            await self.send_chunks(
                interaction.followup.send,
                "❌ I couldn't DM you. Please check your privacy settings."
            )
        except Exception as e:
            print(f"[ERROR] handle_query - {e}")
            await self.send_chunks(interaction.followup.send, self.ai.error_message())

    # ---------- Register Slash Commands ----------
    def register_commands(self):
        @self.bot.tree.command(name="coh", description="Get your query answered in current channel")
        async def code_help_public(interaction: discord.Interaction, query: str):
            await self.handle_query(interaction, query, is_dm=False)

        @self.bot.tree.command(name="cph", description="Get your query answered privately in your DM")
        async def code_help_private(interaction: discord.Interaction, query: str):
            if interaction.guild is None:
                await code_help_public(interaction=interaction, query=query)  # Already in DM
            else:
                await self.handle_query(interaction, query, is_dm=True)

        @self.bot.tree.command(name="dbt", description="Ask doubts related to code")
        async def code_doubt(interaction: discord.Interaction, query: str):
            try:
                await interaction.response.defer()
                result = await self.ai.query(query, interaction.user.id)
                await self.db.store_response(interaction.user.id, query, result)
                await self.send_chunks(interaction.followup.send, result)
            except Exception as e:
                print(f"[ERROR] /dbt - {e}")
                await self.send_chunks(interaction.followup.send, self.ai.error_message())

        @self.bot.tree.command(name="debug", description="Provide code for debug")
        async def debug_code(interaction: discord.Interaction, code: str):
            try:
                await interaction.response.defer()
                result = await self.ai.doubt(code, interaction.user.id)
                await self.db.store_response(interaction.user.id, code, result)
                await self.send_chunks(interaction.followup.send, result)
            except Exception as e:
                print(f"[ERROR] /debug - {e}")
                await self.send_chunks(interaction.followup.send, self.ai.error_message())

        @self.bot.tree.command(name="resources", description="Generate useful resources")
        async def recommend_resources(interaction: discord.Interaction, topic: str, number : int):
            try:
                await interaction.response.defer()
                resource = await self.ai.resources(topic,number)
                await self.send_chunks(interaction.followup.send, resource)
            except Exception as e:
                print(f"[ERROR] /resources - {e}")
                await self.send_chunks(interaction.followup.send, self.ai.error_message())

        @self.bot.tree.command(name="tips", description="Generate random tips related to any topic")
        async def random_tip(interaction: discord.Interaction, topic: str, number : int):
            try:
                await interaction.response.defer()
                tip = await self.ai.tips(topic, number)
                await self.send_chunks(interaction.followup.send, tip)
            except Exception as e:
                print(f"[ERROR] /tips - {e}")
                await self.send_chunks(interaction.followup.send, self.ai.error_message())

        @self.bot.tree.command(name="chelp", description="Help menu")
        async def code_help_info(interaction: discord.Interaction):
            try:
                await interaction.response.defer()
                await self.send_chunks(interaction.followup.send, self.ai.help_message())
            except Exception as e:
                print(f"[ERROR] /chelp - {e}")
                await self.send_chunks(interaction.followup.send, self.ai.error_message())

    # ---------- Bot Ready Event ----------
    async def on_ready(self):
        await self.bot.tree.sync()  # Sync commands with Discord
        await self.db.initialize()  # Prepare database
        print(f"Bot active : {self.bot.user}")

    # ---------- Run Bot ----------
    def run(self):
        @self.bot.event
        async def on_ready():
            await self.on_ready()
        self.register_commands()
        self.bot.run(TOKEN)

# ---------- Main Execution ----------
if __name__ == "__main__":
    CodeBot().run()
