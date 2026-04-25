import discord
from discord.ext import commands
import os
import json
import random
import asyncio
import datetime

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

LEVEL_FILE = "levels.json"

# ─────────────────────────────
# DATA SYSTEM
# ─────────────────────────────
def load_data():
    try:
        with open(LEVEL_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(LEVEL_FILE, "w") as f:
        json.dump(data, f)

def get_level(xp):
    return int(xp ** 0.5 / 10)

# ─────────────────────────────
# XP SYSTEM (CHAT)
# ─────────────────────────────
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    data = load_data()
    user_id = str(message.author.id)

    if user_id not in data:
        data[user_id] = {"xp": 0, "level": 0}

    data[user_id]["xp"] += 5

    new_level = get_level(data[user_id]["xp"])

    if new_level > data[user_id]["level"]:
        data[user_id]["level"] = new_level
        await message.channel.send(f"🎉 {message.author.mention} reached Level {new_level}!")

    save_data(data)

    await bot.process_commands(message)

# ─────────────────────────────
# CLIPRATE SYSTEM
# ─────────────────────────────
@bot.tree.command(name="cliprate")
async def cliprate(interaction: discord.Interaction, clip: str):

    data = load_data()
    user_id = str(interaction.user.id)

    if user_id not in data:
        data[user_id] = {"xp": 0, "level": 0}

    score = random.randint(1, 10)
    xp_gain = score * 10

    data[user_id]["xp"] += xp_gain
    data[user_id]["level"] = get_level(data[user_id]["xp"])

    save_data(data)

    embed = discord.Embed(
        title="🎬 Clip Rating",
        color=0x2ecc71
    )

    embed.add_field(name="Clip", value=clip, inline=False)
    embed.add_field(name="Rating", value=f"{score}/10", inline=True)
    embed.add_field(name="XP Gained", value=f"+{xp_gain}", inline=True)

    await interaction.response.send_message(embed=embed)

# ─────────────────────────────
# LEVEL COMMAND
# ─────────────────────────────
@bot.tree.command(name="level")
async def level(interaction: discord.Interaction, member: discord.Member = None):

    data = load_data()
    member = member or interaction.user
    user_id = str(member.id)

    if user_id not in data:
        return await interaction.response.send_message("No data yet.")

    embed = discord.Embed(
        title=f"{member.name} Stats",
        color=0x2ecc71
    )

    embed.add_field(name="Level", value=data[user_id]["level"])
    embed.add_field(name="XP", value=data[user_id]["xp"])

    await interaction.response.send_message(embed=embed)

# ─────────────────────────────
# FANCY LEADERBOARD (TOP 15)
# ─────────────────────────────
@bot.tree.command(name="leaderboard")
async def leaderboard(interaction: discord.Interaction):

    data = load_data()

    sorted_users = sorted(
        data.items(),
        key=lambda x: x[1]["xp"],
        reverse=True
    )[:15]

    embed = discord.Embed(
        title="🏆 RZN LEADERBOARD",
        color=0x2ecc71
    )

    medals = ["🥇", "🥈", "🥉"]

    for i, (user_id, stats) in enumerate(sorted_users, start=1):

        try:
            user = await bot.fetch_user(int(user_id))
            medal = medals[i-1] if i <= 3 else f"#{i}"

            embed.add_field(
                name=f"{medal} {user.name}",
                value=f"Level {stats['level']} | XP {stats['xp']}",
                inline=False
            )

        except:
            continue

    await interaction.response.send_message(embed=embed)

# ─────────────────────────────
# MONTHLY WINNER
# ─────────────────────────────
async def monthly_reward():

    data = load_data()

    sorted_users = sorted(
        data.items(),
        key=lambda x: x[1]["xp"],
        reverse=True
    )

    if not sorted_users:
        return

    top_user_id, _ = sorted_users[0]
    user = await bot.fetch_user(int(top_user_id))

    guild = bot.guilds[0]
    channel = discord.utils.get(guild.text_channels, name="leaderboard")

    if channel:
        await channel.send(
            f"🏆 Monthly Winner: {user.mention}\n"
            f"🎁 Reward: Special Role / Shoutout"
        )

async def monthly_loop():
    await bot.wait_until_ready()

    while not bot.is_closed():

        now = datetime.datetime.utcnow()

        if now.day == 1 and now.hour == 0:
            await monthly_reward()
            await asyncio.sleep(86400)

        await asyncio.sleep(3600)

# ─────────────────────────────
# AD COMMAND
# ─────────────────────────────
@bot.tree.command(name="ad")
async def ad(interaction: discord.Interaction):

    embed = discord.Embed(
        title="JOIN RZN",
        description="PvP & community server focused on improvement, competition and social interaction.",
        color=0x2ecc71
    )

    embed.add_field(name="Features", value="PvP clips, events, community, bots", inline=False)
    embed.add_field(name="Invite", value="https://discord.gg/PtP7sHwKJF", inline=False)

    await interaction.response.send_message(embed=embed)

# ─────────────────────────────
# BASIC COMMANDS
# ─────────────────────────────
@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

# ─────────────────────────────
# READY
# ─────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.loop.create_task(monthly_loop())
    print(f"Bot online als {bot.user}")

# ─────────────────────────────
# RUN
# ─────────────────────────────
bot.run(TOKEN)
