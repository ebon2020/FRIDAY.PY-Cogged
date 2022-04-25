import os
import nextcord
from nextcord.ext import commands
from nextcord import Color as c
import requests
import json

error = c.red()
affirm = c.green()
blue = c.blue()

#keeping track of version number
version = '1.2.0'

#credits, version number and bot Icon
webhookFooter = f'FRIDAY.PY v{version} | coded by ebon#7550'
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

class nfts(commands.Cog):
  def __init__(self,client):
    self.client = client

  @commands.command()
  async def seaScrape(self, ctx, collection=None):
      if collection == None:
          await sendErrorMessage(ctx, 'No collection provided!', True,
                                 '*seaScrape <collection>')
      else:
          osLink = f'https://api.opensea.io/api/v1/collection/{collection}/stats'
          osIMGLink = f'https://api.opensea.io/api/v1/collection/{collection}'
          collectionData = requests.get(osLink)
          collectionImageReq = requests.get(osIMGLink)
          if collectionData.status_code == 404:
              await sendErrorMessage(
                  ctx, 'Collection does not exist on OpenSea API.')
          elif collectionData.status_code == 200:
              collectionStats = json.loads(collectionData.text)
              floorPrice = collectionStats['stats']['floor_price']
              oneDaySales = int(collectionStats['stats']['one_day_sales'])
              oneDayVolume = float(collectionStats['stats']['one_day_volume'])
              totalSupply = int(collectionStats['stats']['total_supply'])
              totalOwners = int(collectionStats['stats']['num_owners'])
              averagePrice = float(collectionStats['stats']['average_price'])
  
              collectionText = json.loads(collectionImageReq.text)
              for entry in collectionText['collection'][
                      'primary_asset_contracts']:
                  nftThumbnail = entry['image_url']
                  name = entry['name']
  
              collectionEmbed = nextcord.Embed(
                  title=f'OpenSea Scrape: `{name}`',
                  description=f'A summary of the `{name}` collection on OpenSea.',
                  color=blue)
              collectionEmbed.set_thumbnail(url=nftThumbnail)
              collectionEmbed.add_field(name='Floor Price: ',
                                        value=f'`{floorPrice}`')
              collectionEmbed.add_field(name='Average Price: ',
                                        value=f'`{float(averagePrice)}`',
                                        inline=True)
              collectionEmbed.add_field(name='One Day Sales: ',
                                        value=f'`{oneDaySales}`',
                                        inline=True)
              collectionEmbed.add_field(name='One Day Volume: ',
                                        value=f'`{oneDayVolume}`',
                                        inline=True)
              collectionEmbed.add_field(name='Total Supply: ',
                                        value=f'`{totalSupply}`',
                                        inline=True)
              collectionEmbed.add_field(name='Total Owners: ',
                                        value=f'`{totalOwners}`',
                                        inline=True)
              collectionEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
              await ctx.channel.send(embed=collectionEmbed)
          else:
              await sendErrorMessage(
                  ctx, 'An unknown error occurred. Please try again later.')

def setup(client):
  client.add_cog(nfts(client))