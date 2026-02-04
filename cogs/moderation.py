# =======================================================
#  Casual Havocer Bot Systems
#  Author: Nothing Around Us
#  Created: 2025
#  File: moderation.py
#  Description:
#      Contains moderation commands such as ban,
#      kick, mute, and other related commands.
# =======================================================

import time
import discord
from discord.ext import commands
from discord import app_commands, interactions
from cogs import SayModal
# from utils.checks import checkAuthorized
from utils.logger import logCommand
from datetime import datetime, timedelta


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.describe(user="Member to kick", reason="Reason for kicking")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Kick a member from the server."""
        if user == interaction.user:
            await interaction.response.send_message("❌ You can't kick yourself.", ephemeral=True)
            return

        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You can't kick this member.", ephemeral=True)
            return

        await user.kick(reason=reason)

        await logCommand(
            self.bot,
            "kick",
            interaction.user,
            f"Target: {user} (`{user.id}`)\nReason: {reason}"
        )

        await interaction.response.send_message(
            f"👢 **{user}** was kicked.\n📄 Reason: {reason}"
        )

    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.describe(user="Member to ban", reason="Reason for banning")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Ban a member from the server."""
        if user == interaction.user:
            await interaction.response.send_message("❌ You can't ban yourself.", ephemeral=True)
            return

        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You can't ban this member.", ephemeral=True)
            return

        await user.ban(reason=reason)

        await logCommand(
            self.bot,
            "ban",
            interaction.user,
            f"Target: {user} (`{user.id}`)\nReason: {reason}"
        )

        await interaction.response.send_message(
            f"🔨 **{user}** was banned.\n📄 Reason: {reason}"
        )

    @app_commands.command(name="timeout", description="Timeout a member.")
    @app_commands.describe(user="Member to timeout", minutes="Duration in minutes", reason="Reason for timeout")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str = "No reason provided"):
        """Timeout a member for a specified duration."""
        if minutes <= 0:
            await interaction.response.send_message("❌ Time must be greater than 0.", ephemeral=True)
            return

        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You can't timeout this member.", ephemeral=True)
            return

        duration = timedelta(minutes=minutes)
        await user.timeout(duration, reason=reason)

        await logCommand(
            self.bot,
            "timeout",
            interaction.user,
            f"Target: {user} (`{user.id}`)\nDuration: {minutes} minutes\nReason: {reason}"
        )

        await interaction.response.send_message(
            f"⏱️ **{user}** timed out for **{minutes} minutes**.\n📄 Reason: {reason}"
        )

    @app_commands.command(name="untimeout", description="Remove a member's timeout.")
    @app_commands.describe(user="Member to remove timeout from")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def untimeout(self, interaction: discord.Interaction, user: discord.Member):
        """Remove timeout from a member."""
        await user.timeout(None)

        await logCommand(
            self.bot,
            "untimeout",
            interaction.user,
            f"Target: {user} (`{user.id}`)"
        )

        await interaction.response.send_message(
            f"♻️ Timeout removed for **{user}**."
        )

    async def cog_app_command_error(self, interaction, error):
        """A local error handler for all commands in this cog."""
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )


# =======================================================
# Setup function for cog loading
# =======================================================


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
