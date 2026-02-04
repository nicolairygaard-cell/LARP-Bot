# =======================================================
#  Casual Havocer Bot Systems
#  Author: Nothing Around Us
#  Created: 2025
#  File: __init__.py
#  Description:
#      Initializes the events package for handling bot
#      events. This file can remain empty.
#      Can also include shared utilities or constants for the events package.
# =======================================================
from imaplib import Commands
import discord
from discord import app_commands
from discord.ui import Modal, TextInput, View, button, Button
from discord.ext import commands

from utils.logger import SESSION_CHANNEL_ID
from utils.serverAPI.service import ServerAPIService


class SayModal(Modal, title="Send a Message"):
    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel
        self.message = TextInput(
            label="Message",
            style=discord.TextStyle.paragraph,
            placeholder="Type your message here...",
            required=True,
        )
        self.add_item(self.message)

    async def on_submit(self, interaction: discord.Interaction):
        await self.channel.send(self.message.value)
        await interaction.response.send_message(
            f"✅ Message sent to {self.channel.mention}",
            ephemeral=True
        )


class SessionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.session_link = "https://policeroleplay.community/join/CSRPSS"
        self.add_item(
            discord.ui.Button(
                label="Join Session",
                style=discord.ButtonStyle.link,
                url=self.session_link,
                emoji="<:Game:1446509973785018480>"
            )
        )


class VoteView(discord.ui.View):
    def __init__(self, bot: commands.Bot, starter: discord.Member, vote_goal: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.starter = starter
        self.vote_goal = vote_goal
        self.voters = set()
        self.api_service = ServerAPIService()

    @discord.ui.button(label="Vote", emoji="<:check:1446513651841237013>", style=discord.ButtonStyle.green, custom_id="session_vote_button")
    async def vote_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user.id in self.voters:
            return await interaction.response.send_message(
                "❌ You already voted!",
                # << add remove vote button in ephemeral
                view=RemoveVoteView(self),
                ephemeral=True
            )

        self.voters.add(user.id)

        await interaction.response.send_message(
            f"✅ You voted! **({len(self.voters)}/{self.vote_goal})**",
            ephemeral=True
        )

        # Check if vote goal reached
        if len(self.voters) >= self.vote_goal:
            await self.send_session_started(interaction)


    @discord.ui.button(label="View Voters", emoji="<:Group:1446513726206513374>", style=discord.ButtonStyle.blurple, custom_id="session_view_voters")
    async def view_voters_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.voters:
            return await interaction.response.send_message("No voters yet!", ephemeral=True)

        voter_list = "\n".join([f"<@{uid}>" for uid in self.voters])

        embed = discord.Embed(
            title="🗳️ Session Vote — Voters",
            description=voter_list,
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def send_session_started(self, interaction: discord.Interaction):
        serverInfo = self.api_service.get_server_data()
        queue_data = self.api_service.get_queue()

        # ❌ REMOVE THIS — causes InteractionResponded error
        # await interaction.response.defer(ephemeral=True)

        try:
            queue = queue_data[0]
        except IndexError as e:
            queue = 0
        
        embed = discord.Embed(
            title="<:Serve:1446510659255926814> Los Angeles Roleplay 🌲",
            color=discord.Color.green()
        )
        embed.add_field(
            name="<:Game:1446509973785018480> Session Start-Up",
            value="> The in-game server has started up! Join the server for some great roleplays!",
            inline=False
        )
        embed.add_field(
            name="<:Game:1446509973785018480> Server Information",
            value=(
                f"<:Arrow:1446532329290858526> Server Name: {serverInfo['Name']}\n"
                f"<:Arrow:1446532329290858526> Current Players: {serverInfo['CurrentPlayers']}/{serverInfo['MaxPlayers']}\n"
                f"<:Arrow:1446532329290858526> Queue: `{int(queue)}`\n"
                f"<:Arrow:1446532329290858526> Server Code: [CSRPSS](https://policeroleplay.community/join/CSRPSS)\n"
                f"<:Arrow:1446532329290858526> Server Owner: [Zenosiqe](https://roblox.com/users/2350285288/profile)"
            ),
            inline=False
        )
        embed.set_footer(text=f"Started by {interaction.user}", icon_url=interaction.user.avatar)

        channel = self.bot.get_channel(SESSION_CHANNEL_ID)
        await channel.send(
            content="<@&1408082244693786718>",
            embed=embed
        )


class RemoveVoteView(discord.ui.View):
    def __init__(self, parent):
        super().__init__(timeout=30)
        self.parent = parent

    @discord.ui.button(label="Remove Vote", style=discord.ButtonStyle.red)
    async def remove_vote(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user.id not in self.parent.voters:
            return await interaction.response.send_message(
                "❌ You haven’t voted yet.",
                ephemeral=True
            )

        self.parent.voters.remove(user.id)

        await interaction.response.send_message(
            f"🔴 Vote removed! **({len(self.parent.voters)}/{self.parent.vote_goal})**",
            ephemeral=True
        )


# ======= Mass Shifts =======
class MassShiftView(View): # WIP -cough- -cough-
    def __init__(self, votes_required: int, host: discord.Member):
        super().__init__(timeout=None)
        self.votes_required = votes_required
        self.host = host
        self.voters = set()

    @button(label="✅ Vote", style=discord.ButtonStyle.success)
    async def vote_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id in self.voters:
            self.voters.remove(interaction.user.id)
            await interaction.response.send_message("⚠️ You’re vote has been removed.", ephemeral=True)
            return

        self.voters.add(interaction.user.id)
        await interaction.response.send_message(
            f"🗳️ {interaction.user.mention}, your vote has been counted!",
            ephemeral=True
        )

        if len(self.voters) >= self.votes_required:
            button.disabled = True
            await interaction.message.edit(view=self)
            mentions = " ".join(f"<@{uid}>" for uid in self.voters)

            await interaction.channel.send(
                f"🎉 **Vote Goal Reached!**\n"
                f"{mentions}"
            )

    @button(label="📋 View Participants", style=discord.ButtonStyle.secondary)
    async def participants_button(self, interaction: discord.Interaction, button: Button):
        if not self.voters:
            await interaction.response.send_message("No one has voted yet.", ephemeral=True)
            return

        voters_list = ", ".join(f"<@{uid}>" for uid in self.voters)
        await interaction.response.send_message(
            f"**Participants:**\n{voters_list}",
            ephemeral=True
        )

    @button(label="📘 Mass shift promo guide", style=discord.ButtonStyle.primary)
    async def promo_guide_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message((
            "📘 **Mass Shift Guide**\n\n"
            "These are only hosted with the permission Directive Team+.\n"
            "Promotions apply to the following:\n\n"
            "Awaiting Training -> Trial Moderator ❌ (Must complete your trainings.)\n"
            "Trial Moderator -> Junior Moderator ✅\n"
            "Junior Moderator -> Moderator ✅\n"
            "Moderator -> Senior Moderator ✅\n"
            "Senior Moderator -> Head Moderator ✅\n"
            "Head Moderator -> Trial Admin ❌( Must be handpicked by CMG+)\n"
            "Trial Admin -> Admin ✅\n"
            "Admin -> Senior Admin✅\n"
            "Senior Admin-> Head Admin ✅\n"
            "Head Admin -> Trial IA ❌( Must be handpicked by CMG+)\n\n"
            "🔒 Head Admin+ cannot be promoted from a M/S\n"
            "📩 Open a SHR Ticket to claim your promotion."
            ), 
        ephemeral=True)
        