import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─────────────────────────────
# READY EVENT
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
# VERIFY SYSTEM (FIXED)
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
                "❌ I don't have permission to give roles",
                ephemeral=True
            )

class VerifySetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.selected_role_id = None

        options = []
        for role in interaction_cache["guild"].roles:
            if role.name != "@everyone":
                options.append(
                    discord.SelectOption(label=role.name, value=str(role.id))
                )

        self.select = discord.ui.Select(
            placeholder="Select verification role...",
            options=options,
            min_values=1,
            max_values=1
        )

        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        self.selected_role_id = int(self.select.values[0])

        role = interaction.guild.get_role(self.selected_role_id)

        await interaction.response.send_message(
            f"✅ Selected role: {role.name}",
            ephemeral=True
        )

    @discord.ui.button(label="Send Verify Message", style=discord.ButtonStyle.green)
    async def send_verify(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.selected_role_id is None:
            return await interaction.response.send_message(
                "❌ Select a role first",
                ephemeral=True
            )

        embed = discord.Embed(
            title="🔐 Verify to enter the server",
            description="Click the button below to get access.",
            color=0x2ecc71
        )

        await interaction.channel.send(
            embed=embed,
            view=VerifyButtonView(self.selected_role_id)
        )

        await interaction.response.send_message(
            "✅ Verify message sent!",
            ephemeral=True
        )

# ─────────────────────────────
# TEMP CACHE (fix voor dropdown context)
# ─────────────────────────────
interaction_cache = {}

# ─────────────────────────────
# SETUP VERIFY COMMAND
# ─────────────────────────────
@bot.tree.command(name="setup_verify", description="Setup verification system")
async def setup_verify(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    interaction_cache["guild"] = interaction.guild

    view = VerifySetupView()

    await interaction.response.send_message(
        "⚙️ Select role and send verify message:",
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
        name="🟢 Respect",
        value="Be respectful, no bullying or hate",
        inline=False
    )

    embed.add_field(
        name="🟢 Chat Rules",
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
