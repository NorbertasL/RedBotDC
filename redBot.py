import asyncio
import math
import os
import random
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from enum import Enum

BOT_NAME = "RedBot"
VERSION = "v1.3.2"
AUTHOR = "RedSpark"

bot = discord.Client()
bot = commands.Bot(command_prefix='!', case_insensitive=True)
bot.remove_command('help')

TOKEN = os.environ.get("RED_BOT_DC_KEY")


ALLIANCES = []
DO_WELCOME_MESSAGE = False


BOSS_TIMMERS = {
    'qa': [24, 6, 'QA'],
    'zaken': [40, 8, 'Zaken'],
    'baium': [120, 8, 'Baium'],
    "antharas": [192, 8, 'Antharas'],
    "valakas": [264, 0, 'Valakas'],
    "frintezza": [48, 2, 'Frintezza']
}


class LOG_TYPE(Enum):
    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"


async def log(message, log_type: LOG_TYPE):
    print(log_type+":"+message)


def loadAllyData():
    try:
        f = open("ALLIANCES.txt", "r")
        lines = f.readlines()
        for line in lines:
            if line.startswith("#") or line.strip() == "":
                continue
            line = line.split("=")
            ally_name = line[0]
            line = line[1].split("+")
            temp_guilds = {}
            for guild in line:
                temp_guilds.update({guild.strip(" \"\n"): -1})
            tempAlly = {ally_name: temp_guilds}
            global ALLIANCES
            ALLIANCES.append(tempAlly)

    except OSError:
        log("ALLIANCES.txt load fail", LOG_TYPE.ERROR)


def loadHelpFile() -> str:
    try:
        f = open("HELP.txt", "r")
        return f.read()
    except OSError:
        return "Sorry failed to load help info, please contact %s" % AUTHOR



@bot.event
async def on_ready():
    loadAllyData()
    print(str(ALLIANCES))
    BOT_WELCOME_MSG = "%s %s is back up!\nIf you need help do !redBot help.\nHave questions?Feel free to contact %s" % \
                      (BOT_NAME, VERSION, AUTHOR)
    # finding log server first
    for guild in bot.guilds:
        # Setting up log service
        if guild.name == LOG_SERVER_NAME:
            LOG_SERVER[LOG_SERVER_NAME] = guild.id
            LOG_SERVER[LOG_CHANNEL_NAME] = get_channel_from_name(guild, LOG_CHANNEL_NAME).id
            await log("Log Settings:"+str(LOG_SERVER))

    for guild in bot.guilds:
        for g in ALLIANCE.keys():
            if guild.name == g:
                await log(guild.name + ": ALLIANCE APPROVED")
                ALLIANCE[g] = guild.id
                c = get_channel_from_name(guild, BOT_CHANNEL)
                if c is not None and DO_WELCOME_MESSAGE:
                    await c.send(BOT_WELCOME_MSG)
    timestamp = datetime.utcnow()
    time = timestamp.strftime('%d/%m/%Y %H:%M:%S')
    await log("######################################\n%s %s has started up on: %s" % (BOT_NAME, VERSION, time))
    await log('We have logged in as {0.user}'.format(bot))
    await log("\nGuild IDS:")
    for g in ALLIANCE.keys():
        await log(g + ":" + str(ALLIANCE[g]))

    await log("\nTOTAL GUILDS:" + str(len(bot.guilds)))
    await log("TOTAL APPROVED GUILDS:" + str(len(ALLIANCE)))




@bot.command()
# Help and info commands
async def redBot(ctx, arg):
    if arg.lower() == "help":
        await log("!redBot help called by -"+str(ctx.message.author))
        # A bit of a joke :)
        if random.randint(0, 9) >= 7:
            await ctx.send("HELP IS ON ITS WAY!!!HOLD ON!!!!")
            await asyncio.sleep(1)
            await ctx.send("Locating %s address via IP....." % ctx.message.author)
            await asyncio.sleep(2)
            await ctx.send("Address found! Calling ambulance!!!")
            await asyncio.sleep(3)
            await ctx.send("Just kidding, here is the help info %s" % ctx.message.author)

        await ctx.send(loadHelpFile())
        return
    await log("!redBot with UNKNOWN_ARGUMENT "+str(arg) + " called by --"+str(ctx.message.author))


@bot.command()
# Print spawn timmers for each boss
async def timmers(ctx):
    msg = "##### Boss Timmers  #####"
    for boss in BOSS_TIMMERS.items():
        t1 = boss[1][0]
        if t1 > 48:
            oldT1 = t1
            t1 = "%d d " % math.trunc(t1 / 24)
            remainder = oldT1 % 24
            t1 += "%d h" % remainder if remainder > 0 else ""
        else:
            t1 = str(t1) + "h"

        t2 = " + %d h" % boss[1][1] if boss[1][1] > 0 else ""

        msg += "\n" + str(boss[1][2]) + ": " + str(t1) + str(t2)
    await ctx.send(msg)
    await log("!timmers called by -"+str(ctx.message.author))


@bot.event
async def on_message(message):
    command = message.content.lower().split()
    if message.author == bot.user:
        return
    post_channel_count = 0

    # using this method for command, because commands are base on channel name and I don't want do hardcode them
    if command[0].startswith("!"):
        await log("!"+str(message.content)+" called by --"+str(message.author))
        timestamp = datetime.utcnow()

        for guild in ALLIANCE:
            post_channel = (get_channel_from_name(bot.get_guild(ALLIANCE.get(guild)), command[0][1:]))

            if post_channel is None:
                continue

            post_channel_count += 1
            # getting cmd_author/name of user that submits command
            cmd_author = str(message.author)
            nick = message.author.nick
            if nick is not None:
                cmd_author += "(" + nick + ")"

            # Making the name look nice
            boss_name = command[0][1:]
            if len(boss_name) > 2:
                boss_name = boss_name[0].upper() + boss_name[1:]
            else:
                boss_name = boss_name.upper()

            # Msg formatting
            post_msg = "**" + boss_name + " [DEAD] - " + timestamp.strftime('%d/%m %H:%M ') \
                       + "(UTC)" + message.content[len(command[0]):] + "**  -- " + str(cmd_author)

            bst = BOSS_TIMMERS.get(command[0][1:])
            if bst:
                tms = timestamp + timedelta(hours=bst[0])
                post_msg += "\n**Next spawn: " + tms.strftime('%d/%m %H:%M') + "(UTC)**"
                if bst[1] > 0:
                    tms = tms + timedelta(hours=bst[1])
                    post_msg += " **- " + tms.strftime('%d/%m %H:%M(UTC)**')

            # Sending Message
            await post_channel.send(post_msg)
            await log(post_msg + " to " + guild+" by --"+str(message.author))

        # Deleting command msg
        await message.delete()

        if post_channel_count > 0:
            # We detected a custom command so no need to check for others
            return

    # This makes bot.command() work and is the proper way to do commands
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    await log("\nERROR:"+str(error)+"\nMessage:"+str(ctx.message)+"\n")
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("It looks like you have no clue what you are doing\nPlease type !redbot help")


def get_channel_from_name(guild, name):
    for channel in guild.channels:
        if str(channel.type) == 'text' and channel.name == name:
            return bot.get_channel(channel.id)


bot.run(TOKEN)
