# =======================================================
#  Casual Havocer Bot Systems
#  Author: Nothing Around Us
#  Created: 2025
#  File: main.py
#  Description:
#      Secondary bot entry point.
#      Can be launched standalone or as a subprocess from the main bot.
# =======================================================

import os
import asyncio
import discord  # type: ignore
from discord.ext import commands  # type: ignore
from discord import app_commands  # type: ignore
from json import load as json_load

from Keep_alive import app
from hypercorn.asyncio import serve
from hypercorn.config import Config
# -------------------------------------------------------
# Load config
# -------------------------------------------------------
# configFile = json_load(open("config.json"))

bot = commands.Bot(
    command_prefix=f"CSRPSS!",
    intents=discord.Intents.all()
)

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = "1459892780334710940"

# -------------------------------------------------------
# Events
# -------------------------------------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    cmds = bot.tree.get_commands()
    print(f"📋 Loaded {len(cmds)} command(s) before sync:", [c.name for c in cmds])

    try:
        bot.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} command(s) to guild {GUILD_ID}")
    except Exception as e:
        print(f"⚠️ Failed to sync commands: {e}")

# -------------------------------------------------------
# Cog loader
# -------------------------------------------------------

async def load_cogs():
    for filename in os.listdir("./cogs/"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"✅ Loaded cog: {filename}")

# -------------------------------------------------------
# Entry point
# -------------------------------------------------------
async def main():
    # Hypercorn config (Flask async server)
    config = Config()
    config.bind = ["0.0.0.0:8000"]
    config.use_reloader = False

    await load_cogs()

    await asyncio.gather(
        serve(app, config),   # keep_alive server
        bot.start(TOKEN)      # discord bot
    )

def start():
    asyncio.run(main())

if __name__ == "__main__":
    start()
