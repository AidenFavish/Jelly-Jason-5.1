import asyncio
from time import sleep
import time
import discord
import json
import server_ids
from secrets import token
from queue import Queue
import random

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


class FileRequest:
    def __init__(self, the_id, item, path, rw, filename):
        self.the_id = the_id  # Random id assigned to each request
        self.item = item  # The item to be added to the path
        self.path = path  # The path where the item will be placed
        self.rw = rw  # If we are just reading the file or also editing it
        self.filename = filename  # The filename of the file we are editing


class SafeFile:  # Thread safe file management with requests, requires manual calling of run()
    def __init__(self):
        self.queue = Queue()  # Queue that manages requests
        self.buffer = {}  # Holds all the return values of the data we read in the appropriate instance

    async def run(self):  # Running the thread safe tasks
        if self.queue.empty():  # If the queue is empty, idle the machine
            return
        else:
            temp: FileRequest = self.queue.get()  # The request information

            with open(temp.filename, "r") as j:  # First opens the instance of the file
                data = json.load(j)

            if "w" in temp.rw:  # If we are editing do the editing

                # Iterate through the path while lagging back to save the reference
                node = data
                for part in range(0, len(temp.path) - 1):
                    node = node[temp.path[part]]

                # Add the item
                if temp.path[len(temp.path) - 1] == len(node):  # Add an element to the end of the array
                    node.append(temp.item)
                elif temp.path[len(temp.path) - 1] < len(node):  # Add an element in a array or dictionary
                    node[temp.path[len(temp.path) - 1]] = temp.item
                else:  # If you try to add even farther index of the array
                    raise RuntimeError

                with open(temp.filename, "w") as j:  # Write to the file
                    json.dump(data, j)

            self.buffer[temp.the_id] = data  # Move the data into the buffer for receiving

    async def request(self, item, path, rw, filename):  # Submits a new job/request
        # Generates a random unused number for an id
        the_id = random.randint(0, 1000)
        while the_id in self.buffer:
            the_id = random.randint(0, 1000)

        # Creates the request and adds it to the queue
        the_request: FileRequest = FileRequest(the_id, item, path, rw, filename)
        self.queue.put(the_request)

        # Checks when the buffer has released the corresponding data
        while the_id not in self.buffer:
            await asyncio.sleep(0.25)

        return self.buffer[the_id]  # return the data the buffer gave us


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
        await safe_file.request(message.content, ["Sup", "bro", 0, "test", 0], "rw", "storage.json")

    return


client.run(token)
