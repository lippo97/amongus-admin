import os
import asyncio
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.utils import get

from controller import Controller
from vision import Vision
from fsm import FSM
from config import static_templates, monitor
from utils import check_privileges, join as _join, leave as _leave

logging.basicConfig(level=logging.INFO)

GA_ROLE_NAME=os.getenv("GA_ROLE_NAME") or 'Game Admin'
TOKEN = os.getenv("LOGIN_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX") or '!'

print(GA_ROLE_NAME)
print(TOKEN)
print(COMMAND_PREFIX)

client = commands.Bot(command_prefix=COMMAND_PREFIX)
main_loop = asyncio.get_event_loop()
should_stop = False # Kill pill for the game recursion

async def set_mute_all(members, mute=True):
    tasks = map(lambda m: set_mute(m, mute=mute), members)
    return await asyncio.gather(*tasks)

async def set_mute(member: discord.Member, mute=True):
    return await member.edit(mute=mute) if not member == client.user else member

async def print_unauthorized_message(ctx):
    await ctx.message.guild.system_channel.send("{} you're not authorized to send this command.".format(ctx.message.author.mention))

@client.event
async def on_ready():
    logging.info('Bot running as {0.user}'.format(client))

@client.command(pass_context=True, name='mute')
async def mute(ctx, member: discord.Member):
    await (check_privileges(GA_ROLE_NAME, print_unauthorized_message)(lambda: set_mute(member)))()

@client.command(pass_context=True, name='unmute')
async def unmute(ctx, member: discord.Member):
    await (check_privileges(GA_ROLE_NAME, print_unauthorized_message)(lambda: set_mute(member, mute=False)))()

@client.command(pass_context=True, name='join')
@check_privileges(GA_ROLE_NAME, print_unauthorized_message)
async def join(ctx):
    await _join(ctx)

@client.command(pass_context=True, name='leave')
@check_privileges(GA_ROLE_NAME, print_unauthorized_message)
async def leave(ctx):
    await _leave(ctx)

@client.command(pass_context=True, name='game')
@check_privileges(GA_ROLE_NAME, print_unauthorized_message)
async def game(ctx):
    await _join(ctx)
    channel = ctx.message.guild.voice_client.channel
    await asyncio.gather(
        set_mute_all(channel.members, mute=False),
        ctx.message.channel.send('Starting game in {}'.format(channel.name)),
        client.change_presence(activity=discord.Game(name='Among Us')),
    )

    vision = Vision(static_templates, monitor)
    fsm = FSM(on_change_state={
        'playing': lambda: asyncio.run_coroutine_threadsafe(set_mute_all(channel.members), main_loop),
        'voting': lambda: asyncio.run_coroutine_threadsafe(set_mute_all(channel.members, mute=False), main_loop)
    })
    controller = Controller(fsm, vision)

    async def step():
        controller.step()
        if not should_stop:
            await asyncio.sleep(1)
            await step()

    global should_stop
    should_stop = False
    await step()

@client.command(pass_context=True, name='endgame')
@check_privileges(GA_ROLE_NAME, print_unauthorized_message)
async def endgame(ctx):
    global should_stop
    should_stop = True
    voice_channel = ctx.message.guild.voice_client.channel
    await asyncio.gather(
        set_mute_all(voice_channel.members, mute=False),
        ctx.send('Ending game in {}'.format(voice_channel.name)),
        client.change_presence(activity=None),
        _leave(ctx),
    )

def main():
    global should_stop
    client.run(TOKEN)
    should_stop = True

if __name__ == '__main__':
    main()
