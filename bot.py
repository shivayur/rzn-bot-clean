import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─────────────────────────────
# BOT READY + SLASH SYNC
# ─────────────────────────────
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Bot online als {bot.user}")
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Sync error: {e}")

# ─────────────────────────────
# BASIC COMMANDS
# ─────────────────────────────

@bot.tree.command(name="hello", description="Say hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("👋 Hello!")

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

@bot.tree.command(name="rules", description="Show server rules")
async def rules(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📜 Server Rules",
        description="Please follow these rules to keep the server safe.",
        color=0x2ecc71
    )

    embed.add_field(
        name="🟢 Behavior & Respect",
        value="Be respectful, no bullying or toxicity, follow staff",
        inline=False
    )

    embed.add_field(
        name="🟢 Communication",
        value="English only, stay on topic, no spam or mic spam",
        inline=False
    )

    embed.add_field(
        name="🔴 Safety",
        value="No NSFW, racism, doxxing, threats, hacking or raids",
        inline=False
    )

    embed.set_footer(text="Follow Discord Terms of Service")

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Rules posted!", ephemeral=True)

# ─────────────────────────────
# MODERATION COMMANDS
# ─────────────────────────────

@bot.tree.command(name="kick", description="Kick a member")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member} kicked. Reason: {reason}")

@bot.tree.command(name="ban", description="Ban a member")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.ban(reason=reason)
    await interaction.response.send_message(f"⛔ {member} banned. Reason: {reason}")

@bot.tree.command(name="clear", description="Delete messages")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Deleted {amount} messages", ephemeral=True)

@bot.tree.command(name="warn", description="Warn a user")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await interaction.response.send_message(
        f"⚠️ {member.mention} warned. Reason: {reason}"
    )

# ─────────────────────────────
# RUN BOT
# ─────────────────────────────
bot.run(TOKEN)
