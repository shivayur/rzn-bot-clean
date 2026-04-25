import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─────────────────────────────
# BOT READY
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
# VERIFY SYSTEM
# ─────────────────────────────

class VerifyButtonView(discord.ui.View):
    def __init__(self, role: discord.Role):
        super().__init__(timeout=None)
        self.role = role

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.user.add_roles(self.role)
        await interaction.response.send_message("✅ You are now verified!", ephemeral=True)


class VerifySetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.selected_role = None

        self.role_select = discord.ui.Select(
            placeholder="Select a verification role...",
            min_values=1,
            max_values=1,
            options=[]
        )

        self.role_select.callback = self.select_callback
        self.add_item(self.role_select)

    async def select_callback(self, interaction: discord.Interaction):
        role_id = int(self.role_select.values[0])
        self.selected_role = interaction.guild.get_role(role_id)

        await interaction.response.send_message(
            f"✅ Selected role: {self.selected_role.name}",
            ephemeral=True
        )

    @discord.ui.button(label="Send Verify Message", style=discord.ButtonStyle.green)
    async def send_verify(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.selected_role is None:
            return await interaction.response.send_message(
                "❌ Please select a role first",
                ephemeral=True
            )

        embed = discord.Embed(
            title="🔐 Verify to enter the server",
            description="Click the button below to get access.",
            color=0x2ecc71
        )

        await interaction.channel.send(
            embed=embed,
            view=VerifyButtonView(self.selected_role)
        )

        await interaction.response.send_message("✅ Verify message sent!", ephemeral=True)

# ─────────────────────────────
# SETUP VERIFY COMMAND
# ─────────────────────────────

@bot.tree.command(name="setup_verify", description="Setup verification system")
async def setup_verify(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    view = VerifySetupView()

    for role in interaction.guild.roles:
        if role.name != "@everyone":
            view.role_select.options.append(
                discord.SelectOption(label=role.name, value=str(role.id))
            )

    await interaction.response.send_message(
        "⚙️ Select a role and send verify message:",
        view=view,
        ephemeral=True
    )

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
        color=0x2ecc71
    )

    embed.add_field(
        name="🟢 Behavior",
        value="Be respectful, no bullying or toxicity",
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

@bot.tree.command(name="kick", description="Kick a member")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member} kicked.")

@bot.tree.command(name="ban", description="Ban a member")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    await member.ban(reason=reason)
    await interaction.response.send_message(f"⛔ {member} banned.")

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
