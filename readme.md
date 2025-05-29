=============README - FILE=============

# CODE - BOT 

📌 ABOUT
--------
CodeBot is a smart Discord AI bot powered by Cohere's AI models. It helps users with code-related queries, debugging, learning resources, and coding tips. It supports both public and private interaction, maintains user-specific history, and responds using AI-generated answers.

✨ FEATURES
----------
- 🔍 **`/coh <query>`**: Get coding help in the current channel.  
- 📩 **`/cph <query>`**: Receive AI help via private DM.  
- 🐞 **`/debug <code>`**: Debug your code and get suggestions.  
- 🧪 **`/dbg <code>`**: Get AI-powered code improvements.  
- 📚 **`/resources <topic>`**: Get curated learning material links.  
- 📝 **`/tips <topic>`**: Receive coding tips related to a topic.  
- 🆘 **`/chelp`**: Show all available commands.  
- 🧠 Stores per-user interaction history in SQLite.  


🛠️ SETUP INSTRUCTIONS
---------------------
1. **Clone the repository:**
   ```bash
   git clone https://github.com/IDKHowToCodeFR/Code-Bot.git
   cd Code-Bot
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your keys:
   ```
   DISCORD_BOT_TOKEN=your_discord_bot_token
   AI_API_KEY=your_cohere_api_key
   USER_CONTEXT=your_database_path.db
   SYSTEM_INSTR_MSG=your_system_instructions_for_query
   SYSTEM_INSTR_DBT=your_system_instructions_for_doubt
   SYSTEM_INSTR_STRICT=additional_instructions
   ```

5. Run the bot:
   ```bash
   python CodeBot/codebot.py
   ```

---

## 🚀 USAGE

Use the following slash commands inside Discord once the bot is running:

| Command           | Description                              |
|-------------------|------------------------------------------|
| `/cph <query>`    | Get personalized help in your DM        |
| `/coh <query>`    | Get public help in the current channel  |
| `/dbt <code>`     | Analyze and improve your code            |
| `/debug <code>`   | Find potential bugs in your code         |
| `/resources <topic> <number>` | Get learning resources for a topic  |
| `/tips <topic> <number>`       | Get random tips on a topic         |
| `/chelp`          | Display the help menu                    |

---

## 📁 CODE STRUCTURE

- `codebot.py` - Main bot logic, command registration, Discord interactions
- `response.py` - CohereAssistant class for AI chat and responses
- `db.py` - Async SQLite database management for user query-response history
- `.env` - Environment variables for secrets and system instructions

---

## 🌐 PROJECT STRUCTURE
```
Code-Bot/
│
├── codebot.py          # Main bot logic and command handlers
├── response.py         # Cohere assistant API wrapper
├── db.py               # SQLite database interface for user history
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not committed)
├── Procfile            # Procfile for depolyment
└── README.md           # This file
```
---

## 📑 Notes
User history is stored in an SQLite database specified by `USER_CONTEXT` in `.env`.

The bot splits long responses into Discord-friendly embed messages.  
Handles errors and privacy restrictions gracefully (e.g., if DMs are blocked).

---

## 🤝 CONTRIBUTING

Contributions, issues, and feature requests are welcome!  
Feel free to check the [issues page](https://github.com/IDKHowToCodeFR/Code-Bot/issues).

---

## 📜 LICENSE
This project is licensed under the MIT License.

---

## 🙌 ACKNOWLEDGEMENTS

- [Cohere AI](https://cohere.ai) for the AI language model API  
- [discord.py](https://discordpy.readthedocs.io/) for Discord bot framework  
- Inspired by community efforts to improve coding assistance through AI

---

*Happy Coding!* 🎉
