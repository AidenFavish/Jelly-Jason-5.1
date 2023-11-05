import asyncio
from time import sleep
import time
import discord
import server_ids
from secrets import token
import random
from SafeFile import SafeFile

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True
intents.invites = True
intents.guilds = True
servers_synced = {}


class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.synced = False  # added to make sure that the command tree will be synced only once
        self.added = False


client = aclient()
tree = discord.app_commands.CommandTree(client)
safe_file = SafeFile()


@client.event
async def on_ready():
    print("I'm in")
    print(client.user)
    while True:
        await asyncio.sleep(0.25)
        await safe_file.run()


@client.event
async def on_member_join(member):
    return


@client.event
async def on_raw_reaction_add(payload):
    return


@client.event
async def on_raw_reaction_remove(payload):
    return


@client.event
async def on_message(message):
    if message.channel.id == server_ids.TESTING:
        response = await safe_file.request(message.content, ["bruh"], "r", "storage.json")
        await message.channel.send(response)

    return


client.run(token)
