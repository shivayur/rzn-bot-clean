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
# MODERATION
# ─────────────────────────────
@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, member: discord.Member):

    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.kick()
    await interaction.response.send_message(f"Kicked {member.name}")

@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, member: discord.Member):

    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.ban()
    await interaction.response.send_message(f"Banned {member.name}")

@bot.tree.command(name="clear")
async def clear(interaction: discord.Interaction, amount: int):

    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await interaction.channel.purge(limit=amount)

    await interaction.response.send_message(f"Cleared {amount} messages", ephemeral=True)

# ─────────────────────────────
# WELCOME + COUNTER SYSTEM
# ─────────────────────────────
@bot.event
async def on_member_join(member):

    guild = member.guild

    # ── WELCOME CHANNEL ──
    welcome_channel = discord.utils.get(guild.text_channels, name="welcome")

    if not welcome_channel:
        welcome_channel = await guild.create_text_channel("welcome")

    embed = discord.Embed(
        title="👋 Welcome!",
        description=f"Welcome {member.mention} to **{guild.name}**!",
        color=0x2ecc71
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    await welcome_channel.send(embed=embed)

    # ── MEMBER COUNTER ──
    counter_channel = discord.utils.get(guild.voice_channels, name="👥 Members")

    if not counter_channel:
        counter_channel = await guild.create_voice_channel(
            f"👥 Members: {guild.member_count}"
        )
    else:
        await counter_channel.edit(
            name=f"👥 Members: {guild.member_count}"
        )

# ─────────────────────────────
# MEMBER LEAVE (COUNTER UPDATE)
# ─────────────────────────────
@bot.event
async def on_member_remove(member):

    guild = member.guild

    counter_channel = discord.utils.get(guild.voice_channels, name="👥 Members")

    if counter_channel:
        await counter_channel.edit(
            name=f"👥 Members: {guild.member_count}"
        )

# ─────────────────────────────
# READY EVENT
# ─────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is online (stable full bot)")

bot.run(TOKEN)
