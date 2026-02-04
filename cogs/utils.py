# =======================================================
#  Casual Havocer Bot Systems
#  Author: Nothing Around Us
#  Created: 2025
#  File: general.py
#  Description:
#      The main utility commands for the bot.
# =======================================================

import time
import discord
from discord.ext import commands
from discord import app_commands, interactions
from cogs import SayModal
# from utils.checks import checkAuthorized
from utils.logger import logCommand, PROMOLOG_CHANNEL_ID
from datetime import datetime

NICK_ROLE_IDS = [
    1459976055174463573,  # Founders
    1459953040563114186,  # SHR
    1459976416673267791,  # HR
    1459901357594247191,  # IA team
]

SAY_ALLOWED_ROLE_IDS = [
    1459976055174463573,  # Founders
    1459953040563114186,  # SHR
    1459976416673267791,  # HR
    1459901357594247191,  # IA team
]


class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="say", description="Send a custom message to a channel.")
    async def say(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        if not any(role.id in SAY_ALLOWED_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                "⛔ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        modal = SayModal(channel)
        await interaction.response.send_modal(modal)

    @app_commands.command(name="setnick", description="Change another member's nickname.")
    @app_commands.describe(
        member="The member to change the nickname of",
        nickname="The new nickname to set"
    )
    async def setnick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        nickname: str
    ):
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in NICK_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                "⛔ You don't have permission to use this command.",
                ephemeral=True
            )
            return
        try:
            old_nick = member.nick if member.nick else member.name
            await member.edit(nick=nickname)
            await interaction.followup.send(
                f"✅ Changed {member.mention}'s nickname from **{old_nick}** to **{nickname}**",
                ephemeral=True
            )
            try:
                await logCommand(self.bot, "setnick", interaction.user, f"Changed {member} nickname from {old_nick} to {nickname}")
            except Exception as e:
                print(f"Logging error: {e}")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: {e}", ephemeral=True)

    @app_commands.command(name="serverinfo", description="Shows info about the server.")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(
            title=f"Server Info - {guild.name}",
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(
            name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Created On", value=guild.created_at.strftime(
            "%b %d, %Y"), inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Displays info about a user.")
    @app_commands.describe(user="The user to get information about")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member):
        roles = [role.mention for role in user.roles if role !=
                 interaction.guild.default_role]
        embed = discord.Embed(
            title=f"User Info - {user}",
            color=user.color,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Joined Server", value=user.joined_at.strftime(
            "%b %d, %Y"), inline=True)
        embed.add_field(name="Account Created", value=user.created_at.strftime(
            "%b %d, %Y"), inline=True)
        embed.add_field(name="Roles", value=", ".join(
            roles) if roles else "None", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ping", description="Checks the bot's latency.")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latency is `{latency}ms`.")

    @app_commands.command(name="uptime", description="Show how long the bot has been online.")
    async def uptime(self, interaction: discord.Interaction):
        if not hasattr(self.bot, "start_time"):
            self.bot.start_time = time.time()

        seconds = int(time.time() - self.bot.start_time)
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        await interaction.response.send_message(
            f"⏱️ Uptime: **{hours}h {minutes}m {seconds}s**"
        )
    
    @app_commands.command(name="purge", description="Purge messages in this channel.")
    @app_commands.describe(amount="Number of messages to delete")
    async def purge(
        self,
        interaction: discord.Interaction,
        amount: int
    ):
        if not any(role.id in SAY_ALLOWED_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                "⛔ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        # Respond immediately so Discord doesn't think the command timed out
        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(limit=amount)

        await interaction.followup.send(
            f"🧹 Deleted **{len(deleted)}** messages in {interaction.channel.mention}.",
            ephemeral=True
        )
        await logCommand(
            self.bot,
            "purge",
            interaction.user,
            f"Purged {len(deleted)} messages in <#{interaction.channel.id}>."
        )

# =======================================================
# Setup function for cog loading
# =======================================================


async def setup(bot: commands.Bot):
    await bot.add_cog(Util(bot))
