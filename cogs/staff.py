# =======================================================
#  Casual Havocer Bot Systems
#  Author: Nothing Around Us
#  Created: 2025
#  File: logging.py
#  Description:
#      This cog handles moderation logging and saving and sending warns in the server
#      to a specified mod-log channel.
# =======================================================

from typing import List
import discord
from discord.ext import commands
from discord import app_commands, interactions
# from utils.checks import checkAuthorized
from cogs import MassShiftView
from utils.logger import INFRACTIONLOG_CHANNEL_ID, PROMOLOG_CHANNEL_ID, MSLOG_CHANNEL_ID, logCommand


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
            value=f"Congratulations on your promotion to <@&{promo_id}>\n\nYour outstanding commitment, strong work ethic, and dedication to the staff team have truly set you apart. This promotion is a direct reflection of the effort and excellence you consistently bring. We’re excited to see you take on new challenges, grow in your new role, and continue making a meaningful impact.",
            inline=False
        )
        embed.add_field(
            name="",
            value=(f"> Reason: {reason}\n"
                   f"> Issuer: {interaction.user.mention}"),
            inline=False
        )
        if signed:
            embed.add_field(name="Signed,", value=signers_formatted, inline=False)

        if interaction.guild and interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)

        log_channel = self.bot.get_channel(PROMOLOG_CHANNEL_ID)
        
        await interaction.followup.send(
            "✅ Promotion sent.",
            ephemeral=True,
        )
        
        await log_channel.send(
            content=f"-# <:Pings:1446510438505255098> {user.mention}",
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
            role_ids = [r.strip("<@&> ") for r in additional.replace(",", " ").split()]
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
            value=f"The Los Angales High Ranking Team has decided to proceed with disciplinary actions regarding your conduct.\n{user.mention} — Your account has received an infraction for the following reason(s). Further details will be provided in due course.\n\nIf you believe this was a mistake or would like to appeal, please submit an appeal request.",
            inline=False
        )
        embed.add_field(name="Username:",
                        value=f"{user.mention}", inline=True)
        embed.add_field(name="Reason:", value=reasons, inline=True)
        embed.add_field(name="Action:", value=action.value, inline=True)

        if signers_formatted:
            embed.add_field(name="Signed,", value=signers_formatted, inline=False)

        embed.add_field(
            name="",
            value=f"> Issued By: {interaction.user.mention}",
            inline=False,
        )

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
            content=f"-# <:Pings:1446510438505255098> {user.mention}",
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

# =======================================================
# Setup function for cog loading
# =======================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Loggers(bot))
