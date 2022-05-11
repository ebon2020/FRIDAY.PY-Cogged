import os
import nextcord
from nextcord.ext import commands
from nextcord import Color as c
import requests
import json
import csv
import validators
import pandas as pd

error = c.red()
affirm = c.green()
blue = c.blue()

#keeping track of version number
version = os.environ['Version']

#universal shop user dest
path_to_user_list = './ShopifyLists/userShopLists.csv'


#commands
shopCommands = {
  'shopScrape <productLink>':'Scrape variants of a Shopify product.',
  'createShopList':'Create a serverside database of Shopify restock links.',
  'addLink <link>':'Add a link to your serverside database.',
  'delLink <link>':'Delete a link from your serverside database.',
  'listLinks':'Returns the links stored in your database.'
}

#credits, version number and bot Icon
webhookFooter = f'FRIDAY.PY v{version} | coded by ebon#2020 | Shopify'
footerUrl = 'https://cdn.discordapp.com/attachments/884302303648153641/964942745892454430/FridayAI.jpg'

#check for shop list
def checkUserShopList(id, pathToUserList):
    users = []
    with open(pathToUserList, 'r') as userList:
        for row in userList:
            users.append(row)
        for user in users:
            if str(id) in user:
                return True
    userList.close()
    return False

def checkInList(pathToList, link):
  linkedList = pd.read_csv(pathToList)
  linkList = linkedList.links.tolist()
  for storedLink in linkList:
    if link in storedLink:
      return True
  return False

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
    helpEmbed = nextcord.Embed(title = 'Shopify Help!', description = 'Commands in the Shopify cog:')
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

  @commands.command()
  async def createShopList(self, ctx):
    author = ctx.author
    id = author.id

    path_to_user_list = './ShopifyLists/userShopLists.csv'

    if checkUserShopList(id, path_to_user_list):
      await sendErrorMessage(ctx, f'{author}\'s database already exists!')
    else:
      path_to_user_shop_list = f'./ShopifyLists/{id}.csv'
      with open(path_to_user_list,'a') as userList:
        writer = csv.writer(userList)
        writer.writerow([f'{id}'])
      userList.close()
      headerRow = ['links']
      with open(path_to_user_shop_list,'w') as newUserList:
        writer = csv.writer(newUserList)
        writer.writerow(headerRow)
      newUserList.close()

      affirmEmbed = nextcord.Embed(
              title=f'Database Created for user: `{author}`',
              description='Run `*addLink` to start building your link list!',
              color=affirm)
      affirmEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
      await ctx.channel.send(embed=affirmEmbed)
    
  @commands.command()
  async def addLink(self, ctx, link=None):
    author = ctx.author
    id = author.id
    channel = ctx.channel
    commandMessage = await channel.fetch_message(channel.last_message_id)
    await commandMessage.edit(suppress=True)
    
    if link == None:
      await sendErrorMessage(ctx,'No link provided', True, '*addLink <link>')
    if checkUserShopList(id, path_to_user_list):
      if validators.url(link):
        path_to_user_shop_list = f'./ShopifyLists/{id}.csv'
        if checkInList(path_to_user_shop_list, link):
          await sendErrorMessage(ctx,'Link already stored.')
        else:
          with open(path_to_user_shop_list, 'a') as userList:
            writer = csv.writer(userList)
            writer.writerow([f"{link}"])
          userList.close()
          linkAddedEmbed = nextcord.Embed(title='Success!', description=f'[New link]({link}) added to `{author}`\'s link list!', color=affirm)
          linkAddedEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
          await ctx.send(embed=linkAddedEmbed)
      else:
        await sendErrorMessage(ctx,'Link not valid.')
    else:
      await sendErrorMessage(ctx, 'Cannot use this command without a database.', True, '*createShopList')
def setup(client):
  client.add_cog(shopify(client))