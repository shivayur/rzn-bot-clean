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

DATA_FILE = "levels.json"

# ─────────────────────────────
# DATA SYSTEM
# ─────────────────────────────
def load():
    try:
        return json.load(open(DATA_FILE))
    except:
        return {}

def save(data):
    json.dump(data, open(DATA_FILE, "w"))

def level_calc(xp):
    return int(xp ** 0.5 / 10)

# ─────────────────────────────
# ANTI SPAM XP
# ─────────────────────────────
cooldown = {}

# ─────────────────────────────
# XP SYSTEM
# ─────────────────────────────
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    uid = str(message.author.id)
    data = load()

    if uid not in data:
        data[uid] = {"xp": 0, "level": 0}

    now = datetime.datetime.utcnow().timestamp()

    if uid in cooldown and now - cooldown[uid] < 5:
        return

    cooldown[uid] = now

    data[uid]["xp"] += 5

    new_level = level_calc(data[uid]["xp"])

    if new_level > data[uid]["level"]:
        data[uid]["level"] = new_level
        await message.channel.send(f"🎉 {message.author.mention} reached Level {new_level}!")

    save(data)

    await bot.process_commands(message)

# ─────────────────────────────
# CLIPRATE SYSTEM
# ─────────────────────────────
@bot.tree.command(name="cliprate")
async def cliprate(interaction: discord.Interaction, clip: str):

    data = load()
    uid = str(interaction.user.id)

    if uid not in data:
        data[uid] = {"xp": 0, "level": 0}

    score = random.randint(3, 10)
    xp_gain = score * 12

    data[uid]["xp"] += xp_gain
    data[uid]["level"] = level_calc(data[uid]["xp"])

    save(data)

    embed = discord.Embed(title="🎬 Clip Rating", color=0x2ecc71)
    embed.add_field(name="Clip", value=clip, inline=False)
    embed.add_field(name="Rating", value=f"{score}/10")
    embed.add_field(name="XP", value=f"+{xp_gain}")

    await interaction.response.send_message(embed=embed)

# ─────────────────────────────
# LEVEL COMMAND
# ─────────────────────────────
@bot.tree.command(name="level")
async def level(interaction: discord.Interaction, member: discord.Member = None):

    data = load()
    member = member or interaction.user
    uid = str(member.id)

    if uid not in data:
        return await interaction.response.send_message("No data yet.")

    d = data[uid]

    embed = discord.Embed(title=f"{member.name}", color=0x2ecc71)
    embed.add_field(name="Level", value=d["level"])
    embed.add_field(name="XP", value=d["xp"])

    await interaction.response.send_message(embed=embed)

# ─────────────────────────────
# LEADERBOARD TOP 15
# ─────────────────────────────
@bot.tree.command(name="leaderboard")
async def leaderboard(interaction: discord.Interaction):

    data = load()

    top = sorted(data.items(), key=lambda x: x[1]["xp"], reverse=True)[:15]

    embed = discord.Embed(title="🏆 RZN LEADERBOARD", color=0x2ecc71)

    medals = ["🥇", "🥈", "🥉"]

    for i, (uid, d) in enumerate(top, start=1):
        try:
            user = await bot.fetch_user(int(uid))
            medal = medals[i-1] if i <= 3 else f"#{i}"

            embed.add_field(
                name=f"{medal} {user.name}",
                value=f"Level {d['level']} | XP {d['xp']}",
                inline=False
            )
        except:
            continue

    await interaction.response.send_message(embed=embed)

# ─────────────────────────────
# VERIFY SYSTEM (SETUP + BUTTON)
# ─────────────────────────────
class VerifyView(discord.ui.View):
    def __init__(self, role_id):
        super().__init__()
        self.role_id = role_id

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):

        role = interaction.guild.get_role(self.role_id)

        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Verified!", ephemeral=True)

@bot.tree.command(name="setup_verify")
async def setup_verify(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("No permission", ephemeral=True)

    role = discord.utils.get(interaction.guild.roles, name="Member")

    if not role:
        return await interaction.response.send_message("Create 'Member' role first", ephemeral=True)

    await interaction.channel.send(
        "Click to verify:",
        view=VerifyView(role.id)
    )

    await interaction.response.send_message("Setup done", ephemeral=True)

# ─────────────────────────────
# TICKETS SYSTEM
# ─────────────────────────────
class TicketView(discord.ui.View):

    @discord.ui.select(
        placeholder="Select ticket type",
        options=[
            discord.SelectOption(label="Support"),
            discord.SelectOption(label="Report"),
            discord.SelectOption(label="Admin Application")
        ]
    )
    async def select(self, interaction: discord.Interaction, select: discord.ui.Select):

        guild = interaction.guild
        cat = discord.utils.get(guild.categories, name="tickets")

        if not cat:
            cat = await guild.create_category("tickets")

        ch = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=cat,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True)
            }
        )

        await ch.send("Support will be with you soon.")
        await interaction.response.send_message(f"Created {ch.mention}", ephemeral=True)

@bot.tree.command(name="ticket_panel")
async def ticket_panel(interaction: discord.Interaction):

    await interaction.channel.send(
        "Open a ticket:",
        view=TicketView()
    )

    await interaction.response.send_message("Panel sent", ephemeral=True)

# ─────────────────────────────
# AD COMMAND
# ─────────────────────────────
@bot.tree.command(name="ad")
async def ad(interaction: discord.Interaction):

    embed = discord.Embed(
        title="JOIN RZN",
        description="PvP & Community Server",
        color=0x2ecc71
    )

    embed.add_field(name="Invite", value="https://discord.gg/PtP7sHwKJF")

    await interaction.response.send_message(embed=embed)

# ─────────────────────────────
# MODERATION
# ─────────────────────────────
@bot.tree.command(name="kick")
async def kick(interaction, member: discord.Member):
    await member.kick()
    await interaction.response.send_message("Kicked")

@bot.tree.command(name="ban")
async def ban(interaction, member: discord.Member):
    await member.ban()
    await interaction.response.send_message("Banned")

@bot.tree.command(name="clear")
async def clear(interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message("Cleared")

@bot.tree.command(name="warn")
async def warn(interaction, member: discord.Member, reason: str):
    await interaction.response.send_message(f"{member.mention} warned: {reason}")

# ─────────────────────────────
# MONTHLY WINNER
# ─────────────────────────────
async def monthly_loop():

    await bot.wait_until_ready()

    while not bot.is_closed():

        now = datetime.datetime.utcnow()

        if now.day == 1 and now.hour == 0:

            data = load()
            top = sorted(data.items(), key=lambda x: x[1]["xp"], reverse=True)

            if top:
                user = await bot.fetch_user(int(top[0][0]))

                ch = discord.utils.get(bot.guilds[0].text_channels, name="leaderboard")

                if ch:
                    await ch.send(f"🏆 Monthly Winner: {user.mention}")

            await asyncio.sleep(86400)

        await asyncio.sleep(3600)

# ─────────────────────────────
# READY
# ─────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.loop.create_task(monthly_loop())
    print(f"Bot online: {bot.user}")

# ─────────────────────────────
# RUN
# ─────────────────────────────
bot.run(TOKEN)
