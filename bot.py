import discord
from discord.ext import commands
from config import TOKEN
from db import *
from safe import safe

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# ───────── LEVEL SYSTEM ─────────
def get_level(msgs):
    if msgs >= 1000: return 5
    if msgs >= 600: return 4
    if msgs >= 300: return 3
    if msgs >= 150: return 2
    if msgs >= 50: return 1
    return 0

# ───────── MESSAGE TRACKING ─────────
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    uid = str(message.author.id)
    create_user(uid)

    user = get_user(uid)
    msgs = user[1]
    lvl = user[2]

    msgs += 1
    new_lvl = get_level(msgs)

    if new_lvl > lvl:
        await message.channel.send(f"🎉 {message.author.mention} reached Level {new_lvl}")

    update_user(uid, msgs, new_lvl)

    await bot.process_commands(message)

# ───────── LEADERBOARD ─────────
@bot.tree.command(name="leaderboard")
async def leaderboard(interaction: discord.Interaction):

    await interaction.response.defer()

    c.execute("SELECT * FROM users ORDER BY messages DESC LIMIT 15")
    rows = c.fetchall()

    embed = discord.Embed(title="🏆 Leaderboard", color=0x2ecc71)

    for i, r in enumerate(rows, 1):
        user = await bot.fetch_user(int(r[0]))
        embed.add_field(name=f"#{i} {user.name}", value=f"{r[1]} msgs | lvl {r[2]}", inline=False)

    await interaction.followup.send(embed=embed)

# ───────── VERIFY (SAFE) ─────────
class Verify(discord.ui.View):
    def __init__(self, role_id):
        super().__init__()
        self.role_id = role_id

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def verify(self, interaction, button):

        role = interaction.guild.get_role(self.role_id)

        if role:
            await interaction.user.add_roles(role)

        await interaction.response.send_message("Verified", ephemeral=True)

@bot.tree.command(name="setup_verify")
async def setup_verify(interaction):

    role = discord.utils.get(interaction.guild.roles, name="Member")

    if not role:
        role = await interaction.guild.create_role(name="Member")

    await interaction.channel.send("Click verify", view=Verify(role.id))

    await interaction.response.send_message("OK", ephemeral=True)

# ───────── ERROR HANDLER (CRASH STOPPER) ─────────
@bot.tree.error
async def on_error(interaction, error):
    print("ERROR:", error)
    try:
        await interaction.response.send_message("⚠️ Error occurred.", ephemeral=True)
    except:
        pass

# ───────── READY ─────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("BOT STABLE ONLINE")

bot.run(TOKEN)
