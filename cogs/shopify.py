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
version = os.environ['Version']

shopCommands = {
  'shopScrape <productLink>':'Scrape variants of a Shopify product.'
}

#credits, version number and bot Icon
webhookFooter = f'FRIDAY.PY v{version} | coded by ebon#7550 | Shopify'
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

class shopify(commands.Cog):
  def __init__(self,client):
    self.client = client

  @commands.command()
  async def shopifyHelp(self,ctx):
    helpEmbed = nextcord.Embed(title = 'NFT Help!', description = 'Commands in the NFT cog:')
    for command in shopCommands:
      helpEmbed.add_field(name = f'`*{command}`', value=f'{shopCommands[command]}')
    helpEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
    helpEmbed.set_thumbnail(url=footerUrl)
    
    await ctx.send(embed=helpEmbed)
    
  @commands.command()
  async def shopScrape(self, ctx, productLink=None):
      channel = ctx.channel
      commandMessage = await channel.fetch_message(channel.last_message_id)
  
      #this supresses the embed created by sending a link in the chat, simply to look better
      await commandMessage.edit(suppress=True)
  
      if productLink == None:
          await sendErrorMessage(ctx, 'Product link not included in command',
                                 True, '*shopScrape <link>')
  
      else:
          productSeparated = productLink.split("/")
          domain = productSeparated[2]
  
          productJson = f"{productLink}.json"
          """instead of parsing through the entire stock endpoint of the website, I simply use the json endpoint of
          the product itself to get more information/variants about it. This is quicker than loading an entire
          website"""
          webProducts = requests.get(productJson)
          if (webProducts.status_code != 200):
              await sendErrorMessage(
                  ctx,
                  'Product JSON not reachable at the moment, ensure that you\'ve entered a Shopify Product link and try again.'
              )
          else:
              shopJSON = json.loads(webProducts.text)
              varString = ''
              massVarString = '\n'
              stockString = '\n'
              title = shopJSON['product']['title']
              imageList = []
              stockList = []
  
              for thing in shopJSON['product']['images']:
                  
                  imageList.append(thing['src'])
  
              for size in shopJSON['product']['variants']:
                  variant = size['id']
                  varSize = size['title']
                  price = size['price']
                  varString += f'{varSize} - {variant}\n'
                  massVarString += f'{variant}\n'
                  if 'shoepalace' in domain:
                      stock = size['inventory_quantity']
                      stockList.append(int(stock))
                      stockString += f'{stock}\n'
  
              image = imageList[0]
              totalStock = sum(stockList)
              """if we do not find product info on the site and we are receiving good statuses, I assume that
              the variants simply are not loaded on the backend."""
              try:
                  varEmbed = nextcord.Embed(
                      title=f'**Shopify Scrape: **',
                      description=f'`{title}` - `${price}`',
                      color=blue)
                  varEmbed.add_field(name='Variants By Size:',
                                     value=f'```{varString}```')
                  if 'shoepalace' in domain:
                      varEmbed.add_field(name=f'Stock Numbers ({totalStock}):',
                                         value=f'```{stockString}```')
                      varEmbed.add_field(name='Mass Variants:',
                                         value=f'```{massVarString}```',
                                         inline=False)
                  else:
                      varEmbed.add_field(name='Mass Variants:',
                                         value=f'```{massVarString}```',
                                         inline=True)
                  varEmbed.set_thumbnail(url=image)
                  varEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
                  await ctx.channel.send(embed=varEmbed)
              except UnboundLocalError:
                  await sendErrorMessage(
                      ctx, 'Variants not loaded on Shopify JSON endpoint.')

def setup(client):
  client.add_cog(shopify(client))