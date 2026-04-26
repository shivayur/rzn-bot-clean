import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# ─────────────────────────────
# VERIFY BUTTON
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
# SETUP COMMAND (FULL SERVER SETUP)
# ─────────────────────────────
@bot.tree.command(name="setup")
async def setup(interaction: discord.Interaction):

    guild = interaction.guild

    # channels
    for name in ["welcome", "📺│content", "🧾│logs"]:
        if not discord.utils.get(guild.text_channels, name=name):
            await guild.create_text_channel(name)

    # role
    if not discord.utils.get(guild.roles, name="Member"):
        await guild.create_role(name="Member")

    await interaction.response.send_message("✅ Server setup complete", ephemeral=True)

# ─────────────────────────────
# SETUP VERIFY
# ─────────────────────────────
@bot.tree.command(name="setup_verify")
async def setup_verify(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🔐 Verification",
        description="Click below to verify",
        color=0x2ecc71
    )

    await interaction.channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message("Verify message sent", ephemeral=True)

# ─────────────────────────────
# /AD
# ─────────────────────────────
@bot.tree.command(name="ad")
async def ad(interaction: discord.Interaction):

    ad_text = (
        "**JOIN RZN**\n\n"
        "RZN is a competitive PvP community server where players improve and share clips.\n\n"
        "- Custom bot\n"
        "- Texture packs\n"
        "- Events\n"
        "- PvP clips & tips\n"
        "- Active community\n\n"
        "Owned by Shivayur\n\n"
        "https://discord.gg/PtP7sHwKJF"
    )

    await interaction.response.send_message(ad_text)

# ─────────────────────────────
# CONTENT
# ─────────────────────────────
@bot.tree.command(name="post")
async def post(interaction: discord.Interaction, link: str):

    channel = discord.utils.get(interaction.guild.text_channels, name="📺│content")

    if not channel:
        channel = await interaction.guild.create_text_channel("📺│content")

    await channel.send(link)
    await interaction.response.send_message("Posted", ephemeral=True)

# ─────────────────────────────
# MODERATION
# ─────────────────────────────
@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, member: discord.Member):

    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("No permission", ephemeral=True)

    await member.kick()
    await interaction.response.send_message(f"Kicked {member}")

@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, member: discord.Member):

    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("No permission", ephemeral=True)

    await member.ban()
    await interaction.response.send_message(f"Banned {member}")

@bot.tree.command(name="clear")
async def clear(interaction: discord.Interaction, amount: int):

    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("No permission", ephemeral=True)

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message("Cleared", ephemeral=True)

# ─────────────────────────────
# WELCOME + AUTO ROLE + LOGS + COUNTER
# ─────────────────────────────
@bot.event
async def on_member_join(member):

    guild = member.guild

    welcome = discord.utils.get(guild.text_channels, name="welcome")
    logs = discord.utils.get(guild.text_channels, name="🧾│logs")

    if not welcome:
        welcome = await guild.create_text_channel("welcome")

    if not logs:
        logs = await guild.create_text_channel("🧾│logs")

    # welcome message
    await welcome.send(f"👋 Welcome {member.mention}!")

    # auto role
    role = discord.utils.get(guild.roles, name="Member")
    if role:
        await member.add_roles(role)

    # logs
    await logs.send(f"📥 {member} joined")

    # counter
    counter = discord.utils.get(guild.voice_channels, name="👥 Members")

    if not counter:
        await guild.create_voice_channel(f"👥 Members: {guild.member_count}")
    else:
        await counter.edit(name=f"👥 Members: {guild.member_count}")

@bot.event
async def on_member_remove(member):

    guild = member.guild

    logs = discord.utils.get(guild.text_channels, name="🧾│logs")
    if logs:
        await logs.send(f"📤 {member} left")

    counter = discord.utils.get(guild.voice_channels, name="👥 Members")
    if counter:
        await counter.edit(name=f"👥 Members: {guild.member_count}")

# ─────────────────────────────
# READY
# ─────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} online (PRO STABLE BOT)")

bot.run(TOKEN)
