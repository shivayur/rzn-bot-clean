import discord
from discord.ext import commands
import os

# ─────────────────────────────
# 🔐 TOKEN (ENV SAFE)
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
# VERIFY COMMAND
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

    await interaction.response.send_message("Posted!", ephemeral=True)

# ─────────────────────────────
# PERMISSION SAFE CHECK (FIX VOOR JOUW ERROR)
# ─────────────────────────────
@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, member: discord.Member):

    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.kick()
    await interaction.response.send_message(f"Kicked {member.name}")

# ─────────────────────────────
@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, member: discord.Member):

    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.ban()
    await interaction.response.send_message(f"Banned {member.name}")

# ─────────────────────────────
@bot.tree.command(name="clear")
async def clear(interaction: discord.Interaction, amount: int):

    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await interaction.channel.purge(limit=amount)

    await interaction.response.send_message(f"Cleared {amount} messages", ephemeral=True)

# ─────────────────────────────
# READY
# ─────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("RZN compatible bot online")

bot.run(TOKEN)
