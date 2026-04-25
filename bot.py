import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─────────────────────────────
# READY
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
# WELCOME DM + OPTIONAL ROLE
# ─────────────────────────────
@bot.event
async def on_member_join(member):

    role = discord.utils.get(member.guild.roles, name="Unverified")

    if role:
        try:
            await member.add_roles(role)
        except:
            pass

    try:
        embed = discord.Embed(
            title="👋 Welcome!",
            description=(
                "Welcome to the server!\n\n"
                "🔐 Go to #verify and click the button\n"
                "to get full access."
            ),
            color=0x2ecc71
        )

        await member.send(embed=embed)

    except discord.Forbidden:
        pass

# ─────────────────────────────
# VERIFY SYSTEM
# ─────────────────────────────
class VerifyButtonView(discord.ui.View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):

        role = interaction.guild.get_role(self.role_id)

        if role is None:
            return await interaction.response.send_message(
                "❌ Role not found",
                ephemeral=True
            )

        try:
            await interaction.user.add_roles(role)

            await interaction.response.send_message(
                "✅ You are now verified!",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I can't give roles (check permissions)",
                ephemeral=True
            )

# ─────────────────────────────
# SETUP VERIFY COMMAND
# ─────────────────────────────
@bot.tree.command(name="setup_verify", description="Create verify message")
async def setup_verify(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    role = discord.utils.get(interaction.guild.roles, name="Member")

    if role is None:
        return await interaction.response.send_message(
            "❌ Create a role named 'Member'",
            ephemeral=True
        )

    embed = discord.Embed(
        title="🔐 Verify to enter the server",
        description="Click the button below to get access.",
        color=0x2ecc71
    )

    await interaction.channel.send(
        embed=embed,
        view=VerifyButtonView(role.id)
    )

    await interaction.response.send_message("✅ Verify system sent!", ephemeral=True)

# ─────────────────────────────
# BASIC COMMANDS
# ─────────────────────────────
@bot.tree.command(name="hello", description="Say hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("👋 Hello!")

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

@bot.tree.command(name="rules", description="Show rules")
async def rules(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📜 Server Rules",
        color=0x2ecc71
    )

    embed.add_field(
        name="🟢 Behavior",
        value="Be respectful, no bullying or hate",
        inline=False
    )

    embed.add_field(
        name="🟢 Chat",
        value="No spam, stay on topic, English only",
        inline=False
    )

    embed.add_field(
        name="🔴 Safety",
        value="No NSFW, racism, doxxing, hacking or raids",
        inline=False
    )

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Rules posted!", ephemeral=True)

# ─────────────────────────────
# MODERATION
# ─────────────────────────────
@bot.tree.command(name="kick", description="Kick a user")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):

    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 Kicked {member}")

@bot.tree.command(name="ban", description="Ban a user")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):

    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.ban(reason=reason)
    await interaction.response.send_message(f"⛔ Banned {member}")

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

    await interaction.response.send_message(f"⚠️ {member.mention} warned: {reason}")

# ─────────────────────────────
# RUN BOT
# ─────────────────────────────
bot.run(TOKEN)
