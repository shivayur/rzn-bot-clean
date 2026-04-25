import discord
from discord.ext import commands
import os
import random

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

member_count = 0

# ─────────────────────────────
# READY
# ─────────────────────────────
@bot.event
async def on_ready():
    global member_count

    for guild in bot.guilds:
        member_count = guild.member_count

    try:
        synced = await bot.tree.sync()
        print(f"Bot online als {bot.user}")
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# ─────────────────────────────
# WELCOME CHANNEL
# ─────────────────────────────
@bot.event
async def on_member_join(member):
    global member_count

    member_count += 1

    channel = discord.utils.get(member.guild.text_channels, name="welcome")

    if channel:
        embed = discord.Embed(
            title="👋 Welcome!",
            description=(
                f"Member #{member_count} joined!\n"
                f"Welcome to **{member.guild.name}** 🎉"
            ),
            color=0x2ecc71
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await channel.send(embed=embed)

# ─────────────────────────────
# CAPTCHA VERIFY SYSTEM
# ─────────────────────────────
class VerifyButtonView(discord.ui.View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id

        self.emojis = ["🍎", "🍌", "🍇", "🍒", "🍉"]
        self.correct = random.choice(self.emojis)

    @discord.ui.button(label="Start Verify", style=discord.ButtonStyle.green)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):

        view = discord.ui.View(timeout=60)

        for emoji in self.emojis:
            view.add_item(CaptchaButton(self.role_id, self.correct, emoji))

        embed = discord.Embed(
            title="🔐 CAPTCHA VERIFY",
            description=f"Click the correct emoji:\n\n**{self.correct}**",
            color=0x2ecc71
        )

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# ─────────────────────────────
# CAPTCHA BUTTONS
# ─────────────────────────────
class CaptchaButton(discord.ui.Button):
    def __init__(self, role_id, correct, emoji):
        super().__init__(label=emoji, style=discord.ButtonStyle.secondary)
        self.role_id = role_id
        self.correct = correct
        self.emoji = emoji

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        if self.emoji != self.correct:
            return await interaction.followup.send("❌ Wrong emoji, try again.")

        role = interaction.guild.get_role(self.role_id)

        if role is None:
            return await interaction.followup.send("❌ Role not found")

        try:
            await interaction.user.add_roles(role)
            await interaction.followup.send("✅ Verified successfully!")

        except discord.Forbidden:
            await interaction.followup.send("❌ Missing permissions")

# ─────────────────────────────
# SETUP VERIFY COMMAND
# ─────────────────────────────
@bot.tree.command(name="setup_verify", description="Setup captcha verify")
async def setup_verify(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    role = discord.utils.get(interaction.guild.roles, name="Member")

    if not role:
        return await interaction.response.send_message(
            "❌ Create role 'Member'",
            ephemeral=True
        )

    embed = discord.Embed(
        title="🔐 Verify System",
        description="Click Start Verify to begin captcha",
        color=0x2ecc71
    )

    await interaction.channel.send(
        embed=embed,
        view=VerifyButtonView(role.id)
    )

    await interaction.response.send_message("✅ Verify system sent", ephemeral=True)

# ─────────────────────────────
# RULES
# ─────────────────────────────
@bot.tree.command(name="rules")
async def rules(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📜 Rules",
        color=0x2ecc71
    )

    embed.add_field(name="Respect", value="Be respectful", inline=False)
    embed.add_field(name="Spam", value="No spam or flooding", inline=False)
    embed.add_field(name="Safety", value="No NSFW, hacking, doxxing", inline=False)

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Rules sent", ephemeral=True)

# ─────────────────────────────
# BASIC COMMANDS
# ─────────────────────────────
@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("👋 Hello!")

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# ─────────────────────────────
# MODERATION
# ─────────────────────────────
@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):

    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 Kicked {member}", ephemeral=True)

@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):

    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.ban(reason=reason)
    await interaction.response.send_message(f"⛔ Banned {member}", ephemeral=True)

@bot.tree.command(name="clear")
async def clear(interaction: discord.Interaction, amount: int):

    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Deleted {amount}", ephemeral=True)

@bot.tree.command(name="warn")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):

    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await interaction.response.send_message(f"⚠️ {member.mention} warned: {reason}", ephemeral=True)

# ─────────────────────────────
# RUN BOT
# ─────────────────────────────
bot.run(TOKEN)
