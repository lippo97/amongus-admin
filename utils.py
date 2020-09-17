import asyncio
import discord
from discord.utils import get

async def join(ctx):
    channel = ctx.message.author.voice.channel
    await leave(ctx)
    await channel.connect()

async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client:
        await voice_client.disconnect()

def check_privileges(role_name, print_unauthorized_message):
    def decorator(func):
        async def inner(*args, **kwargs):
            ctx = args[0]
            if get(ctx.message.author.roles, name=role_name):
                await func(*args, **kwargs)
            else:
                print_unauthorized_message(ctx)
        return inner
    return decorator
