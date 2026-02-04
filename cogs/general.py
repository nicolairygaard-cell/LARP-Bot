# =======================================================
#  Casual Havocer Bot Systems
#  Author: Nothing Around Us
#  Created: 2025
#  File: general.py
#  Description:
#      Contains general-purpose commands such as ping,
#      help, and other fun or utility commands.
# =======================================================

import time
import discord
from discord.ext import commands
from discord import app_commands
from utils.logger import PROMOLOG_CHANNEL_ID, logCommand

GUILD_ID = "1424965941426524253"

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="avatar", description="Get a user's profile picture in full size.")
    @app_commands.describe(user="The user to get the avatar of")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member):
        embed = discord.Embed(
            title=f"Avatar - {user}",
            color=discord.Color.green()
        )
        if user.avatar:
            embed.set_image(url=user.avatar.url)
        else:
            embed.description = "❌ This user has no avatar."
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roll", description="Roll a dice.")
    @app_commands.describe(sides="Number of sides on the dice")
    async def roll(self, interaction: discord.Interaction, sides: int = 6):
        if sides < 2:
            await interaction.response.send_message("❌ Dice must have at least 2 sides.")
            return

        import random
        result = random.randint(1, sides)
        await interaction.response.send_message(
            f"🎲 You rolled **{result}** (1–{sides})"
        )
    
# =======================================================
# Setup function for cog loading
# =======================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
