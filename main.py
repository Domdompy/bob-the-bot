import discord
from discord.ext import commands
from discord import app_commands
import random
from list import lmessages
from list import images
import os
import json
import giphy_client
from giphy_client.rest import ApiException

api_instance = giphy_client.DefaultApi()

client = commands.Bot(command_prefix="^", intents=discord.Intents.all())


@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game(name="/help"))
  print("Your bot is ready")
  try:
    synced = await client.tree.sync()
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(e)




@client.tree.command(name="ping", description="Sends the latency of the bot.")
async def ping(interaction: discord.Interaction):
  await interaction.response.send_message(
    f"Bot Latency: {client.latency * 1000}")

# Function to open and retrieve the bank data
async def get_bank_data():
    with open("bank.json", "r") as f:
        users = json.load(f)
    return users


# Function to save the bank data
async def save_bank_data(users):
    with open("bank.json", "w") as f:
        json.dump(users, f)


# Function to open an account for a user
async def open_account(user_id):
    users = await get_bank_data()
    if str(user_id) not in users:
        users[str(user_id)] = {}
        users[str(user_id)]["wallet"] = 0
        users[str(user_id)]["bank"] = 0
        await save_bank_data(users)


# Function to get a user's wallet and bank balance
async def get_balance(user_id):
    users = await get_bank_data()
    wallet_amt = users[str(user_id)]["wallet"]
    bank_amt = users[str(user_id)]["bank"]
    return wallet_amt, bank_amt


# Function to update a user's wallet and bank balance
async def update_balance(user_id, wallet_amt, bank_amt):
    users = await get_bank_data()
    users[str(user_id)]["wallet"] = wallet_amt
    users[str(user_id)]["bank"] = bank_amt
    await save_bank_data(users)



# Command to check the user's balance
@client.tree.command(name="balance", description="Sends the amount of bananas you have!")
async def balance(interaction: discord.Interaction, user: discord.Member = None):
    if not user:
        user = interaction.user

    await open_account(user.id)
    wallet_amt, bank_amt = await get_balance(user.id)

    em = discord.Embed(color=discord.Color.yellow())
    em.add_field(name=f"🍌 {user.name}'s Balance", value=f"**Wallet Balance: **{wallet_amt}\n**Bank Balance: **{bank_amt}", inline=False)
    em.set_thumbnail(url=user.avatar)

    await interaction.response.send_message(embed=em)

# Command to earn bananas
@client.tree.command(name="earn", description="Gives you a random amount of bananas!")
@app_commands.checks.cooldown(1, 3600)
async def earn(interaction: discord.Interaction):
    await open_account(interaction.user.id)
    wallet_amt, bank_amt = await get_balance(interaction.user.id)

    earnings = random.randrange(10)

    em = discord.Embed(color=discord.Color.yellow())
    em.add_field(name="Banana Earnings", value=f"Someone gave you {earnings} 🍌!!")
    await interaction.response.send_message(embed=em)

    wallet_amt += earnings
    await update_balance(interaction.user.id, wallet_amt, bank_amt)


# Command to transfer bananas to another user
@client.tree.command(name="give", description="Bananananananananana")
async def give(interaction: discord.Interaction, recipient: discord.Member, amount: int):
    await open_account(interaction.user.id)
    await open_account(recipient.id)
    sender_wallet_amt, sender_bank_amt = await get_balance(interaction.user.id)
    recipient_wallet_amt, recipient_bank_amt = await get_balance(recipient.id)

    if amount <= 0:
        await interaction.response.send_message("Invalid amount. Please enter a positive value.", ephemeral=True)
        return

    if sender_wallet_amt < amount:
        await interaction.response.send_message("You do not have enough bananas in your wallet.", ephemeral=True)
        return

    sender_wallet_amt -= amount
    recipient_wallet_amt += amount

    await update_balance(interaction.user.id, sender_wallet_amt, sender_bank_amt)
    await update_balance(recipient.id, recipient_wallet_amt, recipient_bank_amt)

    em = discord.Embed(color=discord.Color.yellow())
    em.add_field(name="Banana gone", value=f"You have transferred {amount} 🍌 to {recipient.display_name}.")
    await interaction.response.send_message(embed=em)






@client.command(name='ban', pass_context=True)
@commands.has_permissions(ban_members=True)
async def ban(context, member: discord.Member, *, reason=None):
  await member.ban(reason=reason)
  await context.send('User ' + member.display_name +
                     ' has been yeeted from the server.')


@client.tree.command(name="help",
                     description="Shows a list of available commands.")
async def help(interaction: discord.Interaction):
  myEmbed = discord.Embed(
    title="Command List",
    description="To use TestBob use the following commands:",
    color=discord.Colour.from_rgb(247, 230, 127))
  myEmbed.set_thumbnail(url="https://i.imgur.com/Qusp5MX.png")
  myEmbed.add_field(name="🔨 Moderation", value="`/helpmod`", inline = False)
  myEmbed.add_field(name="📧 Direct Messaging", value="`/helpdm`", inline = False)
  myEmbed.add_field(name="😆 Memes", value="`/helpfun`", inline = False)
  myEmbed.set_footer(
    icon_url=
    "https://cdn.discordapp.com/avatars/1081418814882861066/e2271943f8c4d04c6efc723d972b36ef",
    text="Please dm Purpeal#1632 for more command suggestions!")

  await interaction.response.send_message(embed=myEmbed)


@client.tree.command(
  name="helpmod", description="Shows a list of available moderation commands.")
async def helpmod(interaction: discord.Interaction):
  myEmbed = discord.Embed(
    title="🔨 Moderation",
    description=
    "Here are some moderation commands you can use to moderate your server!",
    color=discord.Colour.from_rgb(247, 230, 127))
  myEmbed.set_thumbnail(url="https://i.imgur.com/Qusp5MX.png")
  myEmbed.add_field(
    name="`/kick`",
    value=
    "This kicks a specified player from the server. (Only for users with the kick/ban permissions)"
  )
  myEmbed.add_field(
    name="`/ban`",
    value=
    "This bans a specified player from the server. (Only for users with the kick/ban permissions)"
  )
  myEmbed.set_footer(
    icon_url=
    "https://cdn.discordapp.com/avatars/848916956169109535/e2271943f8c4d04c6efc723d972b36ef",
    text="Please dm Purpeal#6943 for more command suggestions!")

  await interaction.response.send_message(embed=myEmbed)

@client.tree.command(
  name="helpdm",
  description="Shows a list of available direct messaging commands.")
async def helpdm(interaction: discord.Interaction):
  myEmbed = discord.Embed(
    title="📧 Direct Messaging",
    description="Here are some cool direct messaging commands you can use!",
    color=discord.Colour.from_rgb(247, 230, 127))
  myEmbed.set_thumbnail(url="https://i.imgur.com/Qusp5MX.png")
  myEmbed.add_field(name="`/lonely`",
                    value="The bot dms you to make you not lonely!")
  myEmbed.set_footer(
    icon_url=
    "https://cdn.discordapp.com/avatars/848916956169109535/e2271943f8c4d04c6efc723d972b36ef",
    text="Please dm Purpeal#6943 for more command suggestions!")

  await interaction.response.send_message(embed=myEmbed)

@client.tree.command(name="helpfun",
                     description="Shows a list of available fun commands!")
async def helpfun(interaction: discord.Interaction):
  myEmbed = discord.Embed(
    title="😆 Memes",
    description="Here are some fun TestBob commands you can use!",
    color=discord.Colour.from_rgb(247, 230, 127))
  myEmbed.set_thumbnail(url="https://i.imgur.com/Qusp5MX.png")
  myEmbed.add_field(name="`/thumbsup`", value="Sends you some positivity!")
  myEmbed.set_footer(
    icon_url=
    "https://cdn.discordapp.com/avatars/848916956169109535/e2271943f8c4d04c6efc723d972b36ef",
    text="Please dm Purpeal#6943 for more command suggestions!")

  await interaction.response.send_message(embed=myEmbed)
  
# this command shows the information about the server
@client.tree.command(name="serverinfo",
                     description="Provides information about the server")
async def serverinfo(interaction: discord.Interaction):
  name = str(interaction.guild)
  owner = str(interaction.guild.owner)
  ID = str(interaction.guild_id)
  memberCount = str(interaction.guild.member_count)

  icon = str(interaction.guild.icon)

  myEmbed = discord.Embed(title=name,
                          description='This shows information about ' + name,
                          color=discord.Colour.from_rgb(247, 230, 127))
  myEmbed.set_thumbnail(url=icon)
  myEmbed.add_field(name="Owner: ", value=owner, inline=False)
  myEmbed.add_field(name="Server ID: ", value=ID, inline=False)
  myEmbed.add_field(name="Number of members: ", value=memberCount, inline=True)
  myEmbed.set_footer(icon_url=interaction.user.avatar,
                     text=f"Requested by {interaction.user.name}")

  await interaction.response.send_message(embed=myEmbed)


@client.tree.command(name="lonely",
                     description="The bot dms you to make you not lonely!")
async def lonely(interaction: discord.Interaction):
  random_lmes = random.choice(lmessages)
  myEmbed = discord.Embed(description=str(random_lmes),
                          color=discord.Colour.from_rgb(247, 230, 127))
  await interaction.response.send_message(embed=myEmbed)


@client.tree.command(name="thumbsup",
                     description="Sends you some positivity!")
async def thumbsup(interaction: discord.Interaction):
  embed = discord.Embed(title="Thumbs up to you!",
                        color=discord.Color.from_rgb(247, 230, 127))
  random_img = random.choice(images)
  embed.set_image(url=random_img)
  await interaction.response.send_message(embed=embed)


@client.event
async def on_raw_reaction_add(reaction):
  if reaction.emoji.name == '❌':
    m = await client.get_channel(reaction.channel_id
                               ).fetch_message(reaction.message_id)
    await m.delete()

  await client.get_channel(reaction.channel_id).send(
    f'{reaction.member.mention} just added the {reaction.emoji} emoji to a message.'
  )

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
  if isinstance(error, app_commands.CommandOnCooldown):
    if error.retry_after < 3600:
      hours = round(error.retry_after / 60, 1)
      await interaction.response.send_message(f"Please wait for {hours} minutes to use this command again!", ephemeral = True)
    elif error.retry_after < 60:
      await interaction.response.send_message(f"Please wait for {error.retry_after} seconds to use this command again!", ephemeral = True)
  else: raise error


client.run(os.environ['DISCORD_TOKEN'])