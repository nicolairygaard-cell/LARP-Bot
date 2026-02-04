# =======================================================
#  Casual Havocer Bot Systems
#  Author: Nothing Around Us
#  Created: 2025
#  File: logging.py
#  Description:
#      This cog handles moderation logging and saving and sending warns in the server
#      to a specified mod-log channel.
# =======================================================

from datetime import datetime
from typing import List
import discord
from discord.ext import commands
from discord import app_commands, interactions
# from utils.checks import checkAuthorized
from cogs import MassShiftView
from utils.logger import INFRACTIONLOG_CHANNEL_ID, PROMOLOG_CHANNEL_ID, RETIRMENTLOG_CHANNEL_ID, logCommand


ALLOWED_ROLE_IDS = [
    1459976055174463573,  # Founders
    1459953040563114186,  # SHR
    1459976416673267791,  # HR
    1459901357594247191,  # IA team
]

PROMO_ROLE_IDS = [
    1459976055174463573,  # Founders
    1459953040563114186,  # SHR
]


MS_ROLE_IDS = [
    1459976055174463573,  # Founders
    1459953040563114186,  # SHR
    1459976416673267791,  # HR
]

Infraction_ROLE_RELATIONS = {
    "Warning 1": 1460719868654387335,
    "Warning 2": 1460719868331556904,
    "Warning 3": 1460719867698090159,
    "Strike 1": 1460719867069206641,
    "Strike 2": 1460719864607019059,
    "Strike 3": 1460719870487302366,
    "Suspension": 1460719869484863763,
    "UI": 1459902888208892128,
    "Blacklist": 1460350380566122558,
}


class Loggers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    logging = app_commands.Group(
        name="issue",
        description="Commands related to issuing promotions and infractions"
    )

    @logging.command(name="promotion", description="Announce a promotion")
    @app_commands.describe(
        user="User to promote",
        promo="Promotion rank",
        reason="Reason for promotion",
        signed="Comma-separated signers",
        additional="Comma-separated additional roles",
        remove="Comma-separated roles to remove",
    )
    async def log_Promo(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        promo: discord.Role,
        reason: str,
        signed: str = None,
        additional: str = None,
        remove: str = None,
    ):
        author_roles = [r.id for r in interaction.user.roles]
        if not any(rid in PROMO_ROLE_IDS for rid in author_roles):
            await interaction.response.send_message(
                "❌ You don’t have permission to use this command.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        user_roles = [role.id for role in user.roles]
        promo_id = promo.id
        user.add_roles(promo, reason="Staff promotion")

        if additional:
            extra_roles = []
            for rid in additional.replace(",", " ").split():
                role = interaction.guild.get_role(int(rid.strip("<@&>")))
                if role:
                    extra_roles.append(role)
            if extra_roles:
                await user.add_roles(*extra_roles)

        if remove:
            extra_remove = []
            for rid in remove.replace(",", " ").split():
                role = interaction.guild.get_role(int(rid.strip("<@&>")))
                if role:
                    extra_remove.append(role)
            if extra_remove:
                await user.remove_roles(*extra_remove)

        reasons_list = [r.strip() for r in reason.split(",")]
        reasons_formatted = "\n".join(f"- {r}" for r in reasons_list)
        if signed:
            signers_list = [s.strip() for s in signed.split(",")]
            signers_formatted = "\n".join(signers_list)

        embed = discord.Embed(
            title="🎉 Staff Promotion",
            color=0xFFA500
        )
        embed.add_field(
            name="",
            value=f"Congratulations on your promotion to <@&{promo_id}>\n\nYour outstanding commitment, strong work ethic, and dedication to the staff team is the reason for your promotion.",
            inline=False
        )
        embed.add_field(
            name="",
            value=(f"> Reason: {reason}\n"
                   f"> Issuer: {interaction.user.mention}"),
            inline=False
        )
        if signed:
            embed.add_field(
                name="Signed,", value=signers_formatted, inline=False)

        if interaction.guild and interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)

        embed.set_image("https://media.discordapp.net/attachments/1460315004401221785/1467904331197190387/Promotions.webp?ex=69840e30&is=6982bcb0&hm=005a911a3227267a2884edee78591c489b1e6a85533a43afcfda427d3169f0c3&=&format=webp&width=2576&height=860")

        log_channel = self.bot.get_channel(PROMOLOG_CHANNEL_ID)

        await interaction.followup.send(
            "✅ Promotion sent.",
            ephemeral=True,
        )

        await log_channel.send(
            content=f"{user.mention}",
            embed=embed,
        )

        # ---------------- COMMAND LOG ----------------
        try:
            details = (
                f"Promoted {user.mention} (`{user.id}`)\n"
                f"New Role: {promo}\n"
                f"Reason: {reason}\n"
                f"Signed by: {signers_formatted}"
            )
            await logCommand(self.bot, "promote", interaction.user, details)
        except Exception as e:
            print("Command log error:", e)

        try:
            await user.send(f"🎉 Congratulations! You have been promoted to **{promo.name}** in {interaction.guild.name}!")
        except discord.Forbidden:
            pass  # DMs closed

    @logging.command(name="infraction", description="Announce an infraction")
    @app_commands.describe(
        user="User to infract",
        reasons="Comma-separated reasons for the infraction",
        signed="Comma-separated signers",
        action="Action taken",
        additional="Comma-separated additional roles",
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Notice", value="Notice"),
            app_commands.Choice(name="Warning 1", value="Warning 1"),
            app_commands.Choice(name="Warning 2", value="Warning 2"),
            app_commands.Choice(name="Warning 3", value="Warning 3"),
            app_commands.Choice(name="Strike 1", value="Strike 1"),
            app_commands.Choice(name="Strike 2", value="Strike 2"),
            app_commands.Choice(name="Strike 3", value="Strike 3"),
            app_commands.Choice(name="Suspension", value="Suspension"),
            app_commands.Choice(name="Under Investigation", value="UI"),
            app_commands.Choice(name="Staff Blacklist", value="Blacklist"),
            app_commands.Choice(name="Termination", value="Termination"),
        ]
    )
    async def log_infraction(
        self,
        interaction: discord.Interaction,
        user: discord.Member | discord.User,
        reasons: str,
        action: app_commands.Choice[str],
        signed: str = None,
        additional: str = None,
    ):
        # ---------------- PERMISSIONS ----------------
        author_roles = [role.id for role in interaction.user.roles]
        if not any(rid in ALLOWED_ROLE_IDS for rid in author_roles):
            await interaction.response.send_message(
                "❌ You don’t have permission to use this command.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        # ---------------- PARSE INPUT ----------------
        role = None

        reasons_list = [r.strip() for r in reasons.split(",")]
        reasons_formatted = "\n".join(f"- {r}" for r in reasons_list)

        signers_formatted = None
        if signed:
            signers_list = [s.strip() for s in signed.split(",")]
            signers_formatted = "\n".join(signers_list)

        # ---------------- ROLE ASSIGNMENT ----------------
        if action.value not in ("Termination", "Notice"):
            role_id = Infraction_ROLE_RELATIONS.get(action.value)
            role = interaction.guild.get_role(role_id) if role_id else None
            if role and isinstance(user, discord.Member):
                await user.add_roles(role, reason="Staff infraction")

        # ---------------- ADDITIONAL ROLES ----------------
        added_extra_roles = []
        if additional and isinstance(user, discord.Member):
            role_ids = [r.strip("<@&> ")
                        for r in additional.replace(",", " ").split()]
            for rid in role_ids:
                if rid.isdigit():
                    role2 = interaction.guild.get_role(int(rid))
                    if role2:
                        added_extra_roles.append(role2)

            if added_extra_roles:
                await user.add_roles(*added_extra_roles)

        # ---------------- EMBED ----------------
        embed = discord.Embed(
            title="⚠️ Staff Infraction",
            color=discord.Color.red(),
        )

        embed = discord.Embed(
            title="⚠️ Staff Infraction",
            color=0xFF0000
        )
        embed.add_field(
            name="",
            value=f"Your account has recieved an infraction for the following reason(s). If you would like to appeal please submit an infraction appeal.",
            inline=False
        )
        embed.add_field(name="Username:",
                        value=f"{user.mention}", inline=True)
        embed.add_field(name="Reason:", value=reasons, inline=True)
        embed.add_field(name="Action:", value=action.value, inline=True)

        if signers_formatted:
            embed.add_field(
                name="Signed,", value=signers_formatted, inline=False)

        embed.add_field(
            name="",
            value=f"> Issued By: {interaction.user.mention}",
            inline=False,
        )

        embed.set_image("https://media.discordapp.net/attachments/1460315004401221785/1467904331566284913/New_Project_7.webp?ex=69840e30&is=6982bcb0&hm=83370a2b9f2e0622ff87ddf599703a413a2ffda97ca9ca68e2d211af3127639f&=&format=webp&width=2576&height=860")

        if interaction.guild and interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)

        # ---------------- SEND LOG + FOLLOWUPS ----------------
        log_channel = self.bot.get_channel(INFRACTIONLOG_CHANNEL_ID)
        if not log_channel:
            await interaction.followup.send(
                "❌ Log channel not found.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            "✅ Infractions sent.",
            ephemeral=True,
        )

        await log_channel.send(
            content=f"{user.mention}",
            embed=embed,
        )

        # ---------------- COMMAND LOG ----------------
        try:
            await logCommand(
                self.bot,
                "infract",
                interaction.user,
                f"Infracted {user} ({action.value}) for reasons: {reasons}",
            )
        except Exception as e:
            print("Command log error:", e)

        # ---------------- DM USER ----------------
        role_name = role.name if role else action.value
        try:
            await user.send(
                f"⚠️ You have received an infraction ({role_name}) in **{interaction.guild.name}**.\n"
                f"**Action Taken:** {action.value}\n"
                "Please check the server for more details."
            )
        except discord.Forbidden:
            pass  # DMs closed

    @logging.command(name="retirment", description="Announce a staff members retirment")
    @app_commands.describe(
        user="The staff member retiring",
        role="The staff member's role/rank"
    )
    async def log_retirment(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member,
        role: discord.Role
    ):
        embed = discord.Embed(
            title="🎖️ Staff Retirement",
            description=(
                f"Today we recognize **{user.mention}** for their service.\n\n"
                f"After serving as **{role.mention}**, they are officially retiring."
            ),
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )

        embed.add_field(
            name="Staff Member",
            value=user.mention,
            inline=True
        )

        embed.add_field(
            name="Final Rank",
            value=role.mention,
            inline=True
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        embed.set_footer(
            text="Thank you for your dedication and hard work."
        )

        log_channel = self.bot.get_channel(RETIRMENTLOG_CHANNEL_ID)
        if not log_channel:
            await interaction.followup.send(
                "❌ Log channel not found.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            "✅ Retirment sent.",
            ephemeral=True,
        )

        await log_channel.send(
            content=f"{user.mention}",
            embed=embed,
        )

        # ---------------- COMMAND LOG ----------------
        try:
            await logCommand(
                self.bot,
                "retirment",
                interaction.user,
                f"Retired {user}, their rank was {role.mention}",
            )
        except Exception as e:
            print("Command log error:", e)


# =======================================================
# Setup function for cog loading
# =======================================================


async def setup(bot: commands.Bot):
    await bot.add_cog(Loggers(bot))
