import discord
import asyncio
from Agents.NunuAI.agent import *
from discord.ext import commands
from dotenv import load_dotenv
from message_db import MessageDB
import logging
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

agent = NunuAI()
message_db = MessageDB()
bot = commands.Bot(command_prefix="!", intents=intents)

APP_NAME = "NunuAI"
USER_ID = "discord_bot"
SESSION_ID = f"general_{USER_ID}" 

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    await agent.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    print(f"Session created for {USER_ID} with app_name {APP_NAME} and session_id {SESSION_ID}")
@bot.event
async def on_message(message):

    message_db.add_message(message.channel.id, 
        message.author.id, 
        message.author.name,
        message.author.display_name, 
        message.content, 
        message.created_at
        )
    # messages = message_db.get_messages(channel_id=message.channel.id, limit=100)
    # print(messages)

    if message.author == bot.user:
        return

    # Check if the bot was mentioned
    if bot.user in message.mentions:
        # Remove the mention from the message content
        content = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not content:
            content = "."
            # await message.channel.send("Hi! How can I help you, {message.author.name}?")

        # Call the agent with the message content
        try:
            response_text = None
            if (SESSION_ID is not None 
                and USER_ID is not None 
                and SESSION_ID != "" 
                and USER_ID != ""):

                print(f"Calling agent with content: \"{content}\", user_id: \"{USER_ID}\", session_id: \"{SESSION_ID}\"") 

                response_text = await agent.call_agent_async(content,user_id=USER_ID,session_id=SESSION_ID)
                if response_text:
                    def split_message(text, max_length=2000):
                        return [text[i:i+max_length] for i in range(0, len(text), max_length)]

                    for chunk in split_message(response_text):
                        await message.channel.send(chunk)
        except Exception as e:
            await message.channel.send(f"An error occurred: {e}")

    await bot.process_commands(message)


@bot.command()
async def show_messages(ctx):
    messages = message_db.get_messages(channel_id=ctx.channel.id, limit=100)
    print(messages)
    await ctx.send(messages)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)


