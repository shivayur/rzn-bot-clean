import discord
from discord.ext import commands
import os

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
        print(f"Sync error: {e}")

# ─────────────────────────────
# WELCOME CHANNEL MESSAGE
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
# VERIFY SYSTEM (FIXED - NO INTERACTION FAIL)
# ─────────────────────────────
class VerifyButtonView(discord.ui.View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            await interaction.response.defer(ephemeral=True)

            role = interaction.guild.get_role(self.role_id)

            if role is None:
                return await interaction.followup.send("❌ Role not found")

            # check role hierarchy
            if role >= interaction.guild.me.top_role:
                return await interaction.followup.send(
                    "❌ Bot role is too low to assign this role"
                )

            await interaction.user.add_roles(role)

            await interaction.followup.send("✅ You are now verified!")

        except discord.Forbidden:
            await interaction.followup.send("❌ Missing permissions (Manage Roles or role hierarchy)")

        except Exception as e:
            print(f"VERIFY ERROR: {e}")
            try:
                await interaction.followup.send("❌ Unexpected error (check logs)")
            except:
                pass

# ─────────────────────────────
# SETUP VERIFY
# ─────────────────────────────
@bot.tree.command(name="setup_verify", description="Setup verify system")
async def setup_verify(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    role = discord.utils.get(interaction.guild.roles, name="Member")

    if not role:
        return await interaction.response.send_message(
            "❌ Create a role named 'Member'",
            ephemeral=True
        )

    embed = discord.Embed(
        title="🔐 Verify System",
        description="Click the button below to get access",
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
@bot.tree.command(name="rules", description="Show rules")
async def rules(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📜 Server Rules",
        color=0x2ecc71
    )

    embed.add_field(name="Respect", value="Be respectful, no bullying", inline=False)
    embed.add_field(name="Chat", value="No spam, stay on topic", inline=False)
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
    await interaction.response.send_message(f"👢 Kicked {member}")

@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):

    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.ban(reason=reason)
    await interaction.response.send_message(f"⛔ Banned {member}")

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

    await interaction.response.send_message(f"⚠️ {member.mention} warned: {reason}")

# ─────────────────────────────
# RUN BOT
# ─────────────────────────────
bot.run(TOKEN)
