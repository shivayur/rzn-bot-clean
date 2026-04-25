import discord
from discord.ext import commands
import os

# ─────────────────────────────
# 🔐 TOKEN
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
# VERIFY SYSTEM
# ─────────────────────────────
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):

        role = discord.utils.get(interaction.guild.roles, name="Member")

        if not role:
            role = await interaction.guild.create_role(name="Member")

        await interaction.user.add_roles(role)

        await interaction.response.send_message("✅ Verified!", ephemeral=True)

# ─────────────────────────────
# SETUP VERIFY MESSAGE
# ─────────────────────────────
@bot.tree.command(name="setup_verify")
async def setup_verify(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🔐 Verification",
        description="Click the button below to verify yourself.",
        color=0x2ecc71
    )

    await interaction.channel.send(embed=embed, view=VerifyView())

    await interaction.response.send_message("Verify system created.", ephemeral=True)

# ─────────────────────────────
# CONTENT POST (📺│content)
# ─────────────────────────────
@bot.tree.command(name="post")
async def post(interaction: discord.Interaction, link: str):

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
# KICK
# ─────────────────────────────
@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, member: discord.Member):

    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.kick()
    await interaction.response.send_message(f"Kicked {member.name}")

# ─────────────────────────────
# BAN
# ─────────────────────────────
@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, member: discord.Member):

    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.ban()
    await interaction.response.send_message(f"Banned {member.name}")

# ─────────────────────────────
# CLEAR
# ─────────────────────────────
@bot.tree.command(name="clear")
async def clear(interaction: discord.Interaction, amount: int):

    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await interaction.channel.purge(limit=amount)

    await interaction.response.send_message(f"Cleared {amount} messages", ephemeral=True)

# ─────────────────────────────
# TIMEOUT
# ─────────────────────────────
@bot.tree.command(name="timeout")
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int):

    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    try:
        duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)

        await member.edit(timed_out_until=duration)

        await interaction.response.send_message(
            f"⏱️ {member.name} timed out for {minutes} minutes"
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ Timeout failed: {e}",
            ephemeral=True
        )

# ─────────────────────────────
# READY
# ─────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is online (stable full moderation bot)")

bot.run(TOKEN)
