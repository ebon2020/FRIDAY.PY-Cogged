import os
import nextcord
from nextcord.ext import commands
from nextcord import Color as c

activity = nextcord.Activity(type=nextcord.ActivityType.listening, name = '*FRIDAYhelp')

client = commands.Bot(command_prefix='*', activity=activity)

error = c.red()
affirm = c.green()
blue = c.blue()

#keeping track of version number
version = os.environ['Version']

#credits, version number and bot Icon
webhookFooter = f'FRIDAY.PY v{version} | coded by ebon#7550'
footerUrl = 'https://cdn.discordapp.com/attachments/884302303648153641/964942745892454430/FridayAI.jpg'

#secrets (bot token etc.)
my_secret = os.environ['token']

#This is a dictionary of available commands for the user. This is used for the help command.
orders = {
    'createSKUList':
    'Have FRIDAY instantiate a SKU list for you in our database!',
    'addSKU':
    'Add a SKU to your database by using: `*addSKU <sku>`',
    'delSKU':
    'Delete a SKU from your database by using `*delSKU <sku>`.',
    'listSKU':
    'List the SKUs currently contained in your database by using `*listSKUs`. Add "True" to the end of your command in order to keep your list private.',
    'infoSKU':
    'Gather helpful info about a footsite SKU by using `*infoSKU <sku>`',
    'direct':
    'Have FRIDAY send you a test DM',
    'pickForMe':
    'Have FRIDAY tell you which SNKRS account groups to use by using `*pickForMe <dropname> <cwk#> <hm#>`',
    'shopScrape':
    'Have FRIDAY scrape the variants of a given product link by using `*shopScrape <link>`',
    'seaScrape':
    'Have FRIDAY scrape the useful stats about any collection on OpenSea.',
    'ethStats':
    'Gather quick statistics about the Ethereum blockchain (gas prices, eth->USD) by using `*ethStats <gas unit>`'
}

cogs = {
  'footsites':True, 
  'nfts':True, 
  'shopify':True, 
  'snkrs':True
}

async def sendErrorMessage(ctx, message, command_needed=False, command=None):
    #initiating the error embed
    embed = nextcord.Embed(
        title="**Error!**",
        description=
        "Something went wrong with your command! See below for more info.",
        color=error)
    embed.add_field(name="Error Message: ", value=f"```{message}```")
    embed.set_footer(text=webhookFooter, icon_url=footerUrl)
    """if I use the function with "True" as their third argument, then the error embed will include
    a provided example command."""
    if (command_needed):
        embed.add_field(name="Example command:",
                        value=f"```{command}```",
                        inline=False)
    await ctx.channel.send(embed=embed)

@client.event
async def on_ready():
    print('FRIDAY online!')

    for fn in os.listdir('./cogs'):
      if fn.endswith('.py'):
        client.load_extension(f"cogs.{fn[:-3]}")

@client.command()
async def FRIDAYhelp(ctx):
    #initializing the help embed
    helpEmbed = nextcord.Embed(
        title="Help!",
        description='Here are the list of commands you can use with FRIDAY',
        color=blue)
    """here we iterate through the command dictionary, making the key of each entry the name of the field
    #and the value of the key:value pair the text of the field"""
    for key in orders:
        helpEmbed.add_field(name=f'`*{key}`: ',
                            value=f'{orders[key]}',
                            inline=False)
    helpEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
    helpEmbed.set_thumbnail(url=footerUrl)
    await ctx.channel.send(embed=helpEmbed)

@client.command()
async def loadCog(ctx, extension = None):
  if extension==None:
    await sendErrorMessage(ctx, 'No cog provided.')
  
  else:  
    client.load_extension(f'cogs.{extension}')
  
    cogs[f'{extension}'] = True
    
    affirmEmbed = nextcord.Embed(title=f'Success!', description = f'`{extension}` cog loaded into FRIDAY.PY', color = affirm)
    affirmEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
    affirmEmbed.set_thumbnail(url=footerUrl)
    await ctx.send(embed=affirmEmbed)

@loadCog.error
async def loadCog_error(ctx, error):
  if isinstance(error, commands.CommandInvokeError):
    await sendErrorMessage(ctx, f'{error}')
  
@client.command()
async def unloadCog(ctx, extension):
  client.unload_extension(f'cogs.{extension}')

  cogs[f'{extension}'] = False
  
  affirmEmbed = nextcord.Embed(title=f'Success!', description = f'`{extension}` cog unloaded from FRIDAY.PY', color = error)
  affirmEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
  affirmEmbed.set_thumbnail(url=footerUrl)
  await ctx.send(embed=affirmEmbed)

@unloadCog.error
async def unloadCog_error(ctx, error):
  if isinstance(error, commands.CommandInvokeError):
    await sendErrorMessage(ctx, f'{error}')

@client.command()
async def reloadCog(ctx, extension):
  client.reload_extension(f'cogs.{extension}')
  affirmEmbed = nextcord.Embed(title=f'Success!', description = f'`{extension}` cog reloaded into FRIDAY.PY', color = blue)
  affirmEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
  affirmEmbed.set_thumbnail(url=footerUrl)
  await ctx.send(embed=affirmEmbed)

@reloadCog.error
async def reloadCog_error(ctx, error):
  if isinstance(error, commands.CommandInvokeError):
    await sendErrorMessage(ctx, f'{error}')

@client.command()
async def loaded(ctx):
  printString = ''
  for key in cogs:
    printString += f'{key}: {cogs[key]}\n'

  infoEmbed = nextcord.Embed(title = 'FRIDAY Cogs:', description = 'What cogs are loaded into FRIDAY right now?', color = blue)
  infoEmbed.add_field(name = 'Cogs:', value = f'```{printString}```')
  infoEmbed.set_thumbnail(url = footerUrl)
  infoEmbed.set_footer(text = webhookFooter, icon_url = footerUrl)
  await ctx.send(embed=infoEmbed)

client.run(my_secret)