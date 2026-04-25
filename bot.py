import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─────────────────────────────
# BOT READY
# ─────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot online als {bot.user}")

# ─────────────────────────────
# SLASH COMMANDS
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
        description="Please follow the rules below to keep the server safe and fun.",
        color=0x2ecc71
    )

    embed.add_field(
        name="🟢 Behavior & Respect",
        value=(
            "• Be respectful to everyone\n"
            "• No bullying, hate, or toxicity\n"
            "• Follow staff instructions\n"
            "• Respect moderators"
        ),
        inline=False
    )

    embed.add_field(
        name="🟢 Communication",
        value=(
            "• English only in chat\n"
            "• Stay on topic in channels\n"
            "• No mic spam or loud/annoying audio\n"
            "• No unnecessary pings"
        ),
        inline=False
    )

    embed.add_field(
        name="🟡 Spam & Activity",
        value=(
            "• No spam or floods\n"
            "• No abuse of bots\n"
            "• Don’t spam permission requests"
        ),
        inline=False
    )

    embed.add_field(
        name="🔴 Safety Rules",
        value=(
            "• No NSFW, illegal, or harmful content\n"
            "• No racism or discrimination\n"
            "• No doxxing or sharing private info\n"
            "• No threats, hacking, DDOS, or raids"
        ),
        inline=False
    )

    embed.add_field(
        name="📩 Reports",
        value="Report issues directly to staff or moderators.",
        inline=False
    )

    embed.set_footer(text="Follow Discord Terms of Service at all times.")

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Rules posted!", ephemeral=True)

# ─────────────────────────────
# RUN BOT
# ─────────────────────────────
bot.run(TOKEN)
