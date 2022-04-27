import os
import nextcord
from nextcord.ext import commands
from nextcord import Color as c
import random


error = c.red()
affirm = c.green()
blue = c.blue()

#keeping track of version number
version = os.environ['Version']

#credits, version number and bot Icon
webhookFooter = f'FRIDAY.PY v{version} | coded by ebon#7550 | SNKRS'
footerUrl = 'https://cdn.discordapp.com/attachments/884302303648153641/964942745892454430/FridayAI.jpg'

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

class snkrs(commands.Cog):
  def __init__(self,client):
    self.client = client

  @commands.command()
  async def pickForMe(ctx, drop=None, cwkNum=None, hmNum=None):
      if drop == None:
          title = '**SNKRS Accounts to Use:**'
      else:
          title = f'**SNKRS Accounts to Use:** {drop}'
  
      accountsDict = {
          'cwkMA': [1, 2, 3, 4, 5],
          'cwkNY': [1, 2, 3, 4, 5],
          'hmMA': [1, 2, 3, 4, 5],
          'hmNY': [1, 2, 3, 4, 5]
      }
      if cwkNum == None:
          cwkNum = 3
      if hmNum == None:
          hmNum = 2
  
      for key in accountsDict:
          if 'cwk' in key:
              if 'MA' in key:
                  cwkMAList = random.sample(accountsDict[key], int(cwkNum))
              if 'NY' in key:
                  cwkNYList = random.sample(accountsDict[key], int(cwkNum))
          if 'hm' in key:
              if 'MA' in key:
                  hmMAList = random.sample(accountsDict[key], int(hmNum))
              if 'NY' in key:
                  hmNYList = random.sample(accountsDict[key], int(hmNum))
  
      embed = nextcord.Embed(
          title=title,
          description=
          'Randomly chosen SNKRS accounts groups for rotation purposes.',
          color=blue)
  
      accountsStringMA = "CWK MA: " + str(cwkMAList) + "\nHandmade MA: " + str(
          hmMAList)
      accountsStringNY = "CWK NY: " + str(cwkNYList) + "\nHandmade NY: " + str(
          hmNYList)
  
      embed.add_field(name='MA Accounts to use:',
                      value=f'```{accountsStringMA}```')
      embed.add_field(name='NY Accounts to use:',
                      value=f'```{accountsStringNY}```')
      embed.set_footer(text=webhookFooter, icon_url=footerUrl)
  
      await ctx.channel.send(embed=embed)

def setup(client):
  client.add_cog(snkrs(client))