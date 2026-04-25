import discord
from discord.ext import commands
import sqlite3
import os

# ─────────────────────────────
# 🔐 TOKEN (VEILIG VIA ENV)
# ─────────────────────────────
TOKEN = os.getenv("TOKEN")

# ─────────────────────────────
# INTENTS
# ─────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# ─────────────────────────────
# DATABASE
# ─────────────────────────────
conn = sqlite3.connect("rzn.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    messages INTEGER DEFAULT 0,
    level INTEGER DEFAULT 0
)
""")
conn.commit()

# ─────────────────────────────
# LEVEL SYSTEM
# ─────────────────────────────
def get_level(msgs):
    if msgs >= 1000: return 5
    if msgs >= 600: return 4
    if msgs >= 300: return 3
    if msgs >= 150: return 2
    if msgs >= 50: return 1
    return 0

# ─────────────────────────────
# MESSAGE SYSTEM
# ─────────────────────────────
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    uid = str(message.author.id)

    c.execute("INSERT OR IGNORE INTO users VALUES (?, 0, 0)", (uid,))
    conn.commit()

    c.execute("SELECT messages, level FROM users WHERE user_id=?", (uid,))
    msgs, lvl = c.fetchone()

    msgs += 1
    new_lvl = get_level(msgs)

    if new_lvl > lvl:
        await message.channel.send(f"🎉 {message.author.mention} reached Level {new_lvl}")

    c.execute("UPDATE users SET messages=?, level=? WHERE user_id=?", (msgs, new_lvl, uid))
    conn.commit()

    await bot.process_commands(message)

# ─────────────────────────────
# LEADERBOARD
# ─────────────────────────────
@bot.tree.command(name="leaderboard")
async def leaderboard(interaction: discord.Interaction):

    c.execute("SELECT * FROM users ORDER BY messages DESC LIMIT 15")
    rows = c.fetchall()

    embed = discord.Embed(title="🏆 Leaderboard", color=0x2ecc71)

    for i, r in enumerate(rows, 1):
        user = await bot.fetch_user(int(r[0]))
        embed.add_field(
            name=f"#{i} {user.name}",
            value=f"{r[1]} msgs | Level {r[2]}",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

# ─────────────────────────────
# PROFILE
# ─────────────────────────────
@bot.tree.command(name="profile")
async def profile(interaction: discord.Interaction, member: discord.Member = None):

    member = member or interaction.user
    uid = str(member.id)

    c.execute("SELECT messages, level FROM users WHERE user_id=?", (uid,))
    data = c.fetchone()

    if not data:
        return await interaction.response.send_message("No data yet.")

    await interaction.response.send_message(
        f"👤 {member.name}\nMessages: {data[0]}\nLevel: {data[1]}"
    )

# ─────────────────────────────
# VERIFY SYSTEM
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

        await interaction.response.send_message("Verified!", ephemeral=True)

@bot.tree.command(name="setup_verify")
async def setup_verify(interaction: discord.Interaction):

    role = discord.utils.get(interaction.guild.roles, name="Member")

    if not role:
        role = await interaction.guild.create_role(name="Member")

    await interaction.channel.send("Click to verify:", view=VerifyView(role.id))

    await interaction.response.send_message("Verify ready", ephemeral=True)

# ─────────────────────────────
# TICKETS
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
        user = interaction.user

        category = discord.utils.get(guild.categories, name="tickets")
        if not category:
            category = await guild.create_category("tickets")

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }
        )

        choice = select.values[0]

        if choice == "Admin Application":

            await channel.send(
"""📋 ADMIN APPLICATION

1. Username
2. Age
3. Why staff?
4. Experience
5. Motivation
6. Scenario handling
7. Activity hours
8. Questions

Be honest and detailed.
"""
            )

        else:
            await channel.send(f"🎫 {choice} ticket created.")

        await interaction.response.send_message(f"Created {channel.mention}", ephemeral=True)

# ─────────────────────────────
# TIKTOK
# ─────────────────────────────
@bot.tree.command(name="tiktok")
async def tiktok(interaction: discord.Interaction, link: str):

    channel = discord.utils.get(interaction.guild.text_channels, name="announcements")

    if not channel:
        channel = await interaction.guild.create_text_channel("announcements")

    embed = discord.Embed(title="📢 New TikTok", description=link)

    await channel.send(embed=embed)

    await interaction.response.send_message("Posted", ephemeral=True)

# ─────────────────────────────
# MODERATION
# ─────────────────────────────
@bot.tree.command(name="kick", default_member_permissions=discord.Permissions(kick_members=True))
async def kick(interaction, member: discord.Member):
    await member.kick()
    await interaction.response.send_message("Kicked")

@bot.tree.command(name="ban", default_member_permissions=discord.Permissions(ban_members=True))
async def ban(interaction, member: discord.Member):
    await member.ban()
    await interaction.response.send_message("Banned")

# ─────────────────────────────
# READY
# ─────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot online (secure mode)")

bot.run(TOKEN)
