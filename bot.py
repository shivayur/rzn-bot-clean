import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

member_count = 0

TICKET_CATEGORY = "tickets"

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
# WELCOME
# ─────────────────────────────
@bot.event
async def on_member_join(member):
    global member_count

    member_count += 1

    channel = discord.utils.get(member.guild.text_channels, name="welcome")

    if channel:
        embed = discord.Embed(
            title="👋 Welcome!",
            description=f"Member #{member_count} joined!\nWelcome to **{member.guild.name}** 🎉",
            color=0x2ecc71
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await channel.send(embed=embed)

# ─────────────────────────────
# VERIFY
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
                return await interaction.followup.send("❌ Role not found", ephemeral=True)

            await interaction.user.add_roles(role)

            await interaction.followup.send("✅ You are now verified!", ephemeral=True)

        except discord.Forbidden:
            await interaction.followup.send("❌ Missing permissions", ephemeral=True)

# ─────────────────────────────
# VERIFY SETUP
# ─────────────────────────────
@bot.tree.command(name="setup_verify")
async def setup_verify(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    role = discord.utils.get(interaction.guild.roles, name="Member")

    if not role:
        return await interaction.response.send_message("❌ Create role 'Member'", ephemeral=True)

    embed = discord.Embed(
        title="🔐 Verify System",
        description="Click verify to get access",
        color=0x2ecc71
    )

    await interaction.channel.send(embed=embed, view=VerifyButtonView(role.id))

    await interaction.response.send_message("✅ Verify sent", ephemeral=True)

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
    embed.add_field(name="Spam", value="No spam", inline=False)
    embed.add_field(name="Safety", value="No NSFW, hacking, doxxing", inline=False)

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Rules sent", ephemeral=True)

# ─────────────────────────────
# ADMIN APPLICATION EMBED
# ─────────────────────────────
def get_admin_application_embed():
    embed = discord.Embed(
        title="📝 Admin Application Form",
        description="Please answer all questions clearly and honestly.",
        color=0x2ecc71
    )

    embed.add_field(name="1. Username", value="What is your in-game username?", inline=False)
    embed.add_field(name="2. Age", value="What is your age?", inline=False)
    embed.add_field(name="3. Motivation", value="Why do you want to become an administrator?", inline=False)
    embed.add_field(name="4. Experience", value="Do you have previous staff experience? Explain.", inline=False)
    embed.add_field(name="5. Skills", value="What makes you suitable for staff?", inline=False)
    embed.add_field(name="6. Situations", value="How would you handle rule breakers?", inline=False)
    embed.add_field(name="7. Motivation", value="What motivates you?", inline=False)
    embed.add_field(name="8. Responsibility", value="Do you understand staff responsibilities?", inline=False)
    embed.add_field(name="9. Questions", value="Any questions for staff?", inline=False)

    return embed

# ─────────────────────────────
# CLOSE TICKET
# ─────────────────────────────
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❌ Close Ticket", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message("🔒 Closing ticket...", ephemeral=True)
        await interaction.channel.delete()

# ─────────────────────────────
# TICKET SYSTEM
# ─────────────────────────────
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Choose ticket type...",
        options=[
            discord.SelectOption(label="Support", emoji="🛠️"),
            discord.SelectOption(label="Report User", emoji="🚨"),
            discord.SelectOption(label="Admin Application", emoji="📝"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):

        guild = interaction.guild
        user = interaction.user

        category = discord.utils.get(guild.categories, name=TICKET_CATEGORY)

        if category is None:
            category = await guild.create_category(TICKET_CATEGORY)

        for channel in category.channels:
            if channel.name.endswith(str(user.id)):
                return await interaction.response.send_message(
                    "❌ You already have a ticket!",
                    ephemeral=True
                )

        ticket_type = select.values[0]
        auto_embed = None

        if ticket_type == "Support":
            prefix = "support"

        elif ticket_type == "Report User":
            prefix = "report"

        else:
            prefix = "application"
            auto_embed = get_admin_application_embed()

        channel = await guild.create_text_channel(
            name=f"{prefix}-{user.name.lower().replace(' ', '-')}",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }
        )

        embed = discord.Embed(
            title=f"🎫 {ticket_type}",
            description="Please explain your request below.",
            color=0x2ecc71
        )

        await channel.send(embed=embed, view=CloseTicketView())

        if auto_embed:
            await channel.send(embed=auto_embed)

        await interaction.response.send_message(
            f"✅ Ticket created: {channel.mention}",
            ephemeral=True
        )

# ─────────────────────────────
# TICKET PANEL
# ─────────────────────────────
@bot.tree.command(name="ticket_panel")
async def ticket_panel(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ No permission", ephemeral=True)

    embed = discord.Embed(
        title="🎫 Ticket System",
        description="Select a ticket type below",
        color=0x2ecc71
    )

    await interaction.channel.send(embed=embed, view=TicketView())

    await interaction.response.send_message("✅ Ticket panel sent", ephemeral=True)

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
