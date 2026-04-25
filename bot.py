import discord
from discord.ext import commands
import os

# ─────────────────────────────
# 🔐 TOKEN (VEILIG)
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
# VERIFY
# ─────────────────────────────
@bot.tree.command(name="verify")
async def verify(interaction: discord.Interaction):

    role = discord.utils.get(interaction.guild.roles, name="Member")

    if not role:
        role = await interaction.guild.create_role(name="Member")

    await interaction.user.add_roles(role)

    await interaction.response.send_message("✅ Verified!", ephemeral=True)

# ─────────────────────────────
# TIKTOK / CONTENT POST
# ─────────────────────────────
@bot.tree.command(name="tiktok")
async def tiktok(interaction: discord.Interaction, link: str):

    channel = discord.utils.get(interaction.guild.text_channels, name="📺│content")

    if not channel:
        channel = await interaction.guild.create_text_channel("📺│content")

    embed = discord.Embed(
        title="📢 New Content",
        description=link,
        color=0x2ecc71
    )

    await channel.send(embed=embed)

    await interaction.response.send_message("Posted in 📺│content", ephemeral=True)

# ─────────────────────────────
# MODERATION
# ─────────────────────────────
@bot.tree.command(name="kick", default_member_permissions=discord.Permissions(kick_members=True))
async def kick(interaction: discord.Interaction, member: discord.Member):
    await member.kick()
    await interaction.response.send_message(f"Kicked {member.name}")

@bot.tree.command(name="ban", default_member_permissions=discord.Permissions(ban_members=True))
async def ban(interaction: discord.Interaction, member: discord.Member):
    await member.ban()
    await interaction.response.send_message(f"Banned {member.name}")

# ─────────────────────────────
# SERVER SETUP
# ─────────────────────────────
@bot.tree.command(name="setup")
@discord.app_commands.default_permissions(administrator=True)
async def setup(interaction: discord.Interaction):

    guild = interaction.guild

    # ── ROLE ──
    member_role = discord.utils.get(guild.roles, name="Member")
    if not member_role:
        member_role = await guild.create_role(name="Member")

    # ── CHANNELS ──
    content = discord.utils.get(guild.text_channels, name="📺│content")
    if not content:
        await guild.create_text_channel("📺│content")

    announcements = discord.utils.get(guild.text_channels, name="📢│announcements")
    if not announcements:
        await guild.create_text_channel("📢│announcements")

    logs = discord.utils.get(guild.text_channels, name="🧾│logs")
    if not logs:
        await guild.create_text_channel("🧾│logs")

    # ── CATEGORY ──
    category = discord.utils.get(guild.categories, name="🎫 tickets")
    if not category:
        await guild.create_category("🎫 tickets")

    await interaction.response.send_message(
        "✅ Setup complete:\n"
        "📺│content\n"
        "📢│announcements\n"
        "🧾│logs\n"
        "🎫 tickets category\n"
        "Member role created",
        ephemeral=True
    )

# ─────────────────────────────
# READY
# ─────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("RZN stable bot online")

bot.run(TOKEN)
