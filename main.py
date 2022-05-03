import os
import nextcord
from nextcord.ext import commands
from nextcord import Color as c

#setting activity to help command
activity = nextcord.Activity(type=nextcord.ActivityType.listening,
                             name='*FRIDAYhelp')

#initialize bot
client = commands.Bot(command_prefix='*', activity=activity)

#useful colors
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

#cog descriptions
cogDescriptions = {
    'Footsites':
    'Commands that give info about footsites/store footsite SKUs.',
    'ETH': 'Commands that scrape ETH info/store investment transactions.',
    'Shopify': 'Commands that scrape info about Shopify products.'
}

#loading commands
mainCommands = {
    'loadCog <cog>': 'Load a cog into FRIDAY',
    'unloadCog <cog>': 'Unload a cog from FRIDAY',
    'reloadCog <cog>': 'Reload a cog into FRIDAY',
    'loaded':'See which cogs are loaded into FRIDAY'
}

cogs = {'footsites': True, 'eth': True, 'shopify': True}

async def sendErrorMessage(ctx, message, command_needed=False, command=None):
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
    helloEmbed = nextcord.Embed(
        title="Help!",
        description=
        'Here is the list of Cogs available in FRIDAY. Run `*<cog>Help` to get each Cog\'s individual commands!',
        color=blue)
    for key in cogDescriptions:
        helloEmbed.add_field(name=f'{key}: ',
                             value=f'```{cogDescriptions[key]}```',
                             inline=False)
    for command in mainCommands:
        helloEmbed.add_field(name=f'`*{command}`:',
                             value=f'`{mainCommands[command]}`',
                             inline=True)
    helloEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
    helloEmbed.set_thumbnail(url=footerUrl)
    await ctx.send(embed=helloEmbed)


@client.command()
async def loadCog(ctx, extension=None):
    if extension == None:
        await sendErrorMessage(ctx, 'No cog provided.')

    else:
        client.load_extension(f'cogs.{extension}')

        cogs[f'{extension}'] = True

        affirmEmbed = nextcord.Embed(
            title=f'Success!',
            description=f'`{extension}` cog loaded into FRIDAY.PY',
            color=affirm)
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

    affirmEmbed = nextcord.Embed(
        title=f'Success!',
        description=f'`{extension}` cog unloaded from FRIDAY.PY',
        color=error)
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
    affirmEmbed = nextcord.Embed(
        title=f'Success!',
        description=f'`{extension}` cog reloaded into FRIDAY.PY',
        color=blue)
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

    infoEmbed = nextcord.Embed(
        title='FRIDAY Cogs:',
        description='What cogs are loaded into FRIDAY right now?',
        color=blue)
    infoEmbed.add_field(name='Cogs:', value=f'```{printString}```')
    infoEmbed.set_thumbnail(url=footerUrl)
    infoEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
    await ctx.send(embed=infoEmbed)

@client.command()
async def credits(ctx):
  creditsEmbed = nextcord.Embed(
      title=':heart: Credits :heart:',
      url='https://github.com/ebon2020/FRIDAY.PY-Cogged',
      description='Coded with love by ebon#7550',
  )
  creditsEmbed.add_field(name='Github:',value='[click here](https://github.com/ebon2020)', inline=True)
  creditsEmbed.add_field(name='Twitter:', value='[click here](https://twitter.com/ebon0001)', inline=True)
  creditsEmbed.add_field(name='Instagram:', value='[click here](https://www.instagram.com/ebon2020)', inline=True)

  creditsEmbed.set_thumbnail(url=footerUrl)
  creditsEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)

  await ctx.send(embed=creditsEmbed)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await sendErrorMessage(
            ctx,
            'Command not found. Run *FRIDAYhelp to find your appropriate command.'
        )


client.run(my_secret)
