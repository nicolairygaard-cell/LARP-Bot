# =======================================================
#  Casual Havocer Bot Systems
#  Author: Nothing Around Us
#  Created: 2025
#  File: swat.py
#  Description:
#      All the SWAT related commands for the bot.
# =======================================================

import discord
from discord.ext import commands
from discord import app_commands, interactions
# from utils.checks import checkAuthorized
from cogs import SessionView, VoteView
from utils.logger import logCommand, SESSION_CHANNEL_ID
from utils.serverAPI.service import ServerAPIService

SESSION_ALLOWED = [
    1459976055174463573,  # Founders
    1459953040563114186,  # SHR
]


class sessions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_service = ServerAPIService()

    session = app_commands.Group(
        name="session",
        description="Commands related to managing sessions"
    )

    @session.command(name="start", description="Announce a session start-up.")
    async def start_session(
        self,
        interaction: discord.Interaction,
    ):
        author_roles = [role.id for role in interaction.user.roles]
        if not any(rid in SESSION_ALLOWED for rid in author_roles):
            await interaction.response.send_message(
                "❌ You don’t have permission to use this command.", ephemeral=True
            )
            return

        serverInfo = self.api_service.get_server_data()
        queue_data = self.api_service.get_queue()
        await interaction.response.defer(ephemeral=True)

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
            value=(
                f"> The in-game server has started up! Join the server for some great roleplays!"
            ),
            inline=False
        )
        embed.add_field(
            name="<:Game:1446509973785018480> Server Information",
            value=(
                f"<:Arrow:1446532329290858526> Server Name: {serverInfo['Name']}\n"
                f"<:Arrow:1446532329290858526> Current Players: {serverInfo['CurrentPlayers']}/{serverInfo['MaxPlayers']}\n"
                f"<:Arrow:1446532329290858526> Queue: `{queue}`\n"
                f"<:Arrow:1446532329290858526> Server Code: [LARPPS](https://policeroleplay.community/join/LARPPS)\n"
                f"<:Arrow:1446532329290858526> Server Owner: [Nicolai_ryggard](https://www.roblox.com/users/2908274817/profile)\n"
            ),
            inline=False
        )
        embed.set_footer(
            text=f"Started by {interaction.user}", icon_url=interaction.user.avatar)

        embed.set_image('https://media.discordapp.net/attachments/1460315004401221785/1467902454992736399/New_Project_6.webp?ex=6984b531&is=698363b1&hm=0b3d0f0b94c9fb16974201649460360e0865cf7da359d276632e786c409cd3be&=&format=webp&width=2576&height=860')

        try:
            session_channel = self.bot.get_channel(SESSION_CHANNEL_ID)
            if session_channel:
                await session_channel.send(content="<@&1460687235157463080>", embed=embed, view=SessionView())
                await logCommand(
                    self.bot,
                    "startsession",
                    interaction.user,
                    f"Started a session."
                )
                await interaction.followup.send(content="Session started!", ephemeral=True)
            else:
                print(
                    f"Session channel with ID {SESSION_CHANNEL_ID} not found.")
        except Exception as e:
            print(f"Error sending session start message: {e}")

    @session.command(name="shutdown", description="Announce a session shutdown.")
    async def end_session(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        author_roles = [role.id for role in interaction.user.roles]
        if not any(rid in SESSION_ALLOWED for rid in author_roles):
            await interaction.response.send_message(
                "❌ You don’t have permission to use this command.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="<:Serve:1446510659255926814> Los Angeles Roleplay 🌲",
            color=discord.Color.red()
        )
        embed.add_field(
            name="<:Game:1446509973785018480> Session Shutdown",
            value=(
                "> The in-game server has now shutdown. A new session will be initiated by server management at a later time. Thank you for joining!\n"
                "> <:Warn:1446510110636769347> Please do not join the in-game server at this time. You may be moderated if you do so."
            ),
            inline=False
        )
        embed.set_footer(
            text=f"Session shutdown by {interaction.user}", icon_url=interaction.user.avatar)

        embed.set_image('https://media.discordapp.net/attachments/1460315004401221785/1467902454992736399/New_Project_6.webp?ex=6984b531&is=698363b1&hm=0b3d0f0b94c9fb16974201649460360e0865cf7da359d276632e786c409cd3be&=&format=webp&width=2576&height=860')

        await self.bot.get_channel(SESSION_CHANNEL_ID).send(embed=embed)
        await interaction.followup.send(content="Session ended!", ephemeral=True)
        await logCommand(
            self.bot,
            "endsession",
            interaction.user,
            "Ended the current session."
        )

    @session.command(name="vote", description="Create a vote to start a session.")
    @app_commands.describe(goal="Number of votes required to start the session")
    async def vote_session(self, interaction: discord.Interaction, goal: int):
        author_roles = [role.id for role in interaction.user.roles]
        if not any(rid in SESSION_ALLOWED for rid in author_roles):
            await interaction.response.send_message(
                "❌ You don’t have permission to use this command.", ephemeral=True
            )
            return

        if goal < 1:
            return await interaction.response.send_message("❌ Goal must be at least 1.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title="<:Serve:1446510659255926814> Los Angeles Roleplay 🌲",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="<:Game:1446509973785018480> Session Vote",
            value=(
                f"> The in-game server session may be started soon. Press the **Vote** button below to vote for the session. If this vote receives at least **{goal} votes**, a session will be started!\n"
                f"> If you vote, you are **required** to join. Failure to do so may result in moderation."
            ),
            inline=False
        )
        embed.set_footer(
            text=f"Vote initiated by {interaction.user}",
            icon_url=interaction.user.avatar
        )

        embed.set_image('https://media.discordapp.net/attachments/1460315004401221785/1467902454992736399/New_Project_6.webp?ex=6984b531&is=698363b1&hm=0b3d0f0b94c9fb16974201649460360e0865cf7da359d276632e786c409cd3be&=&format=webp&width=2576&height=860')

        view = VoteView(self.bot, interaction.user, goal)

        session_channel = self.bot.get_channel(SESSION_CHANNEL_ID)
        await session_channel.send(content="<@&1460687235157463080>", embed=embed, view=view)

        await interaction.followup.send(f"Session vote started! Required votes: **{goal}**", ephemeral=True)

        await logCommand(
            self.bot,
            "votesession",
            interaction.user,
            f"Started a session vote with goal {goal}."
        )

    @session.command(name="boost", description="Announce a session boost.")
    async def boost_session(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        author_roles = [role.id for role in interaction.user.roles]
        if not any(rid in SESSION_ALLOWED for rid in author_roles):
            await interaction.response.send_message(
                "❌ You don’t have permission to use this command.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="<:Serve:1446510659255926814> Los Angeles Roleplay 🌲",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="<:Game:1446509973785018480> Session Boost",
            value=(
                "The in-game server player count is low. Join now to avoid the queue and enjoy some great roleplays!"
            ),
            inline=False
        )
        embed.set_footer(
            text=f"Session boost by {interaction.user}", icon_url=interaction.user.avatar)
        embed.set_image('https://media.discordapp.net/attachments/1460315004401221785/1467902454992736399/New_Project_6.webp?ex=6984b531&is=698363b1&hm=0b3d0f0b94c9fb16974201649460360e0865cf7da359d276632e786c409cd3be&=&format=webp&width=2576&height=860')
        await self.bot.get_channel(SESSION_CHANNEL_ID).send(content="<@&1460687235157463080> @everyone", embed=embed, view=SessionView())
        await interaction.followup.send(content="Session boost announced.", ephemeral=True)
        await logCommand(
            self.bot,
            "boostsession",
            interaction.user,
            "Announced a session boost."
        )

    @session.command(name="status", description="Get the current session status from the server.")
    async def session_status(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)

        server_data = self.api_service.get_server_data()
        queue_data = self.api_service.get_queue()

        if server_data is None:
            return await interaction.followup.send("❌ Could not retrieve server data.", ephemeral=True)

        try:
            queue = queue_data[0]
        except IndexError as e:
            queue = 0

        players_online = server_data["CurrentPlayers"]
        max_players = server_data["MaxPlayers"]
        embed = discord.Embed(
            title="<:Serve:1446510659255926814> Los Angeles Roleplay 🌲",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="<:Game:1446509973785018480> Current Session Status",
            value=(
                f"> **Players Online:** {players_online}/{max_players}\n"
                f"> **Players in Queue:** {queue}\n"
            ),
            inline=False
        )
        embed.set_footer(
            text="Session Status",
            icon_url=self.bot.user.avatar
        )
        await interaction.followup.send(embed=embed, ephemeral=False)


# =======================================================
# Setup function for cog loading
# =======================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(sessions(bot))

"""{
  "Name": "API Test",
  "OwnerId": 1,
  "CoOwnerIds": [
    1
  ],
  "CurrentPlayers": 1,
  "MaxPlayers": 1,
  "JoinKey": "APIServer",
  "AccVerifiedReq": "Disabled / Email / Phone/ID",
  "TeamBalance": true
}
"""
