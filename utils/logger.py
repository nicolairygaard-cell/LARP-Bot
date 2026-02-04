# =======================================================
#  Casual Havocer Bot Systems
#  Author: Nothing Around Us
#  Created: 2025
#  File: logger.py
#  Description:
#      Logging utility for tracking bot activity, errors,
#      and system events in log files.
# =======================================================

import discord
from datetime import datetime

PROMOLOG_CHANNEL_ID = 1460003607582609418
INFRACTIONLOG_CHANNEL_ID = 1460004034714013932
RETIRMENTLOG_CHANNEL_ID = 1460006549660369079

SESSION_CHANNEL_ID = 1408082245612208209

BOTLOG_CHANNEL_ID = 1468614444455166023
# TESTLOG_CHANNEL_ID = 1434127913422164008

async def logCommand(bot: discord.Client, command_name: str, user: discord.User, details: str) -> discord.Embed:
    """# This command will not work for database saving.
    Logs a command execution directly to the bot log channel.
    Args:
        bot (discord.Client): The bot instance.
        command_name (str): The name of the executed command.
        user (discord.User): The user who executed the command.
        details (str): Additional details about the command execution.
    """
    embed = discord.Embed(
        title="📜 Command Log",
        description=f"Command **`/{command_name}`** was executed.",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="👤 User", value=f"{user.mention} (`{user.id}`)", inline=False)
    embed.add_field(name="ℹ️ Details", value=details or "No details provided.", inline=False)
    embed.set_footer(text=f"Logged by: {user}", icon_url=user.display_avatar.url)
    
    log_channel = bot.get_channel(BOTLOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(embed=embed)
    else:
        print(f"Log channel with ID {BOTLOG_CHANNEL_ID} not found.")
