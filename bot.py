import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

# 🔐 ZET HIER JOUW DISCORD USER ID
OWNER_ID = 1255555600293564417  # ← vervang dit

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# ─────────────────────────────
# PERMISSION CHECKS
# ─────────────────────────────
def is_owner(interaction: discord.Interaction):
    return interaction.user.id == OWNER_ID

def is_admin_or_owner(interaction: discord.Interaction):
    return (
        interaction.user.id == OWNER_ID or
        interaction.user.guild_permissions.administrator
    )

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
# SETUP (OWNER ONLY)
# ─────────────────────────────
@bot.tree.command(name="setup")
@discord.app_commands.check(is_owner)
async def setup(interaction: discord.Interaction):

    guild = interaction.guild

    for name in ["welcome", "📺│content", "🧾│logs"]:
        if not discord.utils.get(guild.text_channels, name=name):
            await guild.create_text_channel(name)

    if not discord.utils.get(guild.roles, name="Member"):
        await guild.create_role(name="Member")

    await interaction.response.send_message("✅ Setup complete", ephemeral=True)

# ─────────────────────────────
# VERIFY SETUP
# ─────────────────────────────
@bot.tree.command(name="setup_verify")
@discord.app_commands.check(is_admin_or_owner)
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
        "RZN is a competitive PvP community server.\n\n"
        "- Custom bot\n"
        "- Texture packs\n"
        "- Events\n"
        "- PvP clips & tips\n\n"
        "Owned by Shivayur\n\n"
        "https://discord.gg/PtP7sHwKJF"
    )

    await interaction.response.send_message(ad_text)

# ─────────────────────────────
# CONTENT
# ─────────────────────────────
@bot.tree.command(name="post")
@discord.app_commands.check(is_admin_or_owner)
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
@discord.app_commands.check(is_admin_or_owner)
async def kick(interaction: discord.Interaction, member: discord.Member):

    await member.kick()
    await interaction.response.send_message(f"Kicked {member}")

@bot.tree.command(name="ban")
@discord.app_commands.check(is_admin_or_owner)
async def ban(interaction: discord.Interaction, member: discord.Member):

    await member.ban()
    await interaction.response.send_message(f"Banned {member}")

@bot.tree.command(name="clear")
@discord.app_commands.check(is_admin_or_owner)
async def clear(interaction: discord.Interaction, amount: int):

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message("Cleared", ephemeral=True)

# ─────────────────────────────
# WELCOME + ROLE + LOGS + COUNTER
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

    await welcome.send(f"👋 Welcome {member.mention}!")

    role = discord.utils.get(guild.roles, name="Member")
    if role:
        await member.add_roles(role)

    await logs.send(f"📥 {member} joined")

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
# ERROR HANDLER
# ─────────────────────────────
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):

    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.",
            ephemeral=True
        )

# ─────────────────────────────
# READY
# ─────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} online (OWNER SYSTEM ACTIVE)")

bot.run(TOKEN)
