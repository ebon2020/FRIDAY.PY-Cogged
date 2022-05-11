import os
import nextcord
from nextcord.ext import commands
from nextcord import Color as c
import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd

error = c.red()
affirm = c.green()
blue = c.blue()

#keeping track of version number
version = os.environ['Version']

#credits, version number and bot Icon
webhookFooter = f'FRIDAY.PY v{version} | coded by ebon#2020 | Footsites'
footerUrl = 'https://cdn.discordapp.com/attachments/884302303648153641/964942745892454430/FridayAI.jpg'

footsCommands = {
  'createSKUList':'Creates a serverside SKU list for the user.',
  'addSKU <sku>':'Adds a SKU to the user\'s serverside SKU list.',
  'delSKU <sku>':'Deletes a SKU from the user\' serverside SKU list.',
  'infoSKU <sku>':'Gathers info about a footsite SKU.',
  'listSKU <sku>':'Lists out a user\'s SKU list, add `True` to have it DM\'ed to you.'
}

pathToSKUUsers = './SKULists/userSKULists.csv'

def checkUserSKUList(id, pathToUserList):
    users = []
    userHasSKUList = False

    with open(pathToUserList, 'r') as userList:
        for row in userList:
            users.append(row)
        for user in users:
            if str(id) in user:
                userHasSKUList = True
    userList.close()

    if userHasSKUList:
        return True
    else:
        return False

def checkSKU(sku, pathToUserList):
  skuListData = pd.read_csv(pathToUserList)
  skuList = skuListData.SKU.tolist()
  for storedSKU in skuList:
    if sku in storedSKU:
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

class footsites(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  @commands.guild_only()
  async def footsitesHelp(self,ctx):
    helpEmbed = nextcord.Embed(title = 'Footsite Help!', description = 'Commands in the Footsite cog:')
    for command in footsCommands:
      helpEmbed.add_field(name = f'`*{command}`', value=f'{footsCommands[command]}')
    helpEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
    helpEmbed.set_thumbnail(url=footerUrl)
    
    await ctx.send(embed=helpEmbed)
  
  @commands.command()
  @commands.guild_only()
  async def createSKUList(self, ctx):
      author = ctx.author.name
      id = ctx.author.id
      path_to_file = f'./SKULists/{id}.csv'
      path_to_users = './SKULists/userSKULists.csv'
      #this switch will be flipped off if the user already has a list in the system
      userHasList = checkUserSKUList(id, path_to_users)
      if not userHasList:
          with open(path_to_users, 'a') as userLog:
              writer = csv.writer(userLog)
              writer.writerow([f'{id}'])
          userLog.close()
          #Once we've logged the user, we then create a new sku list with their disc id as their file title
          with open(path_to_file, 'w') as newUserSKUList:
              headerRow = ['SKU']
              writer = csv.writer(newUserSKUList)
              writer.writerow(headerRow)
          newUserSKUList.close()
          affirmEmbed = nextcord.Embed(
              title=f'Database Created for user: `{author}`',
              description='Run `*addSKU` to start building your SKU list!',
              color=affirm)
          affirmEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
          await ctx.channel.send(embed=affirmEmbed)
      else:
          await sendErrorMessage(ctx, f'{author}\'s database already exists!')
  
  
  #This is the command to add a specific footsite SKU to a user's database
  @commands.command()
  async def addSKU(self, ctx, sku=None):
      #catching possible user error
      if sku == None:
          await sendErrorMessage(ctx, 'No SKU provided.', True, '*addSKU <sku>')
      else:
          author = ctx.author
          id = author.id
          path_to_users = './SKULists/userSKULists.csv'
          imageLink = f"https://images.footlocker.com/is/image/EBFL2/{sku}_a1?wid=2000&hei=2000&fmt=png-alpha"
          userHasSKUList = checkUserSKUList(id, path_to_users)
  
          #first we need to ensure that the SKU does not already exist in the user's database to avoid duplication
          if userHasSKUList:
              path_to_file = f'./SKULists/{id}.csv'
  
              if not checkSKU(sku, path_to_file):
                  with open(path_to_file, 'a') as skuList2:
                      skuWriter = csv.writer(skuList2)
                      skuWriter.writerow([f"{sku}"])
                  skuList2.close()
                  affirmEmbed = nextcord.Embed(
                      title='Success!',
                      description=f"`{sku}` added to SKU `{author}'s` list!",
                      color=affirm)
                  affirmEmbed.set_thumbnail(url=imageLink)
                  affirmEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
                  await ctx.channel.send(embed=affirmEmbed)
              else:
                await sendErrorMessage(ctx,f'SKU already in {author}\'s list!')
          else:
              await sendErrorMessage(ctx, f'{author} has no SKU list!')
  
  
  """this is the other database managing command, allowing for users to delete SKUS that they no longer want
  in their database."""
  
  
  @commands.command()
  async def delSKU(self, ctx, sku=None):
      if sku != None:
        author = ctx.author
        id = author.id
        if checkUserSKUList(id, pathToSKUUsers):
          pathToUserList = f'./SKULists/{id}.csv'
          if checkSKU(sku,pathToUserList):
            imageLink = f"https://images.footlocker.com/is/image/EBFL2/{sku}_a1?wid=2000&hei=2000&fmt=png-alpha"
            skuListFrame = pd.read_csv(pathToUserList)
            skuList = skuListFrame.SKU.tolist()
            for item in skuList:
              if sku in item:
                skuList.remove(item)
            skuListRewrite = []
            for item in skuList:
              skuListRewrite.append([item])
            with open(pathToUserList, 'w') as newList:
              writer = csv.writer(newList)
              writer.writerow(['SKU'])
              writer.writerows(skuListRewrite)
            newList.close()
            deleteEmbed = nextcord.Embed(title='Success!', description=f'`{sku}` removed from `{author}\'s` SKU list!', color=error)
            deleteEmbed.set_thumbnail(url=imageLink)
            deleteEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)

            await ctx.send(embed=deleteEmbed)
          else:
            await sendErrorMessage(ctx, f'SKU not found in {author}\'s list!')
        else:
          await sendErrorMessage(ctx, 'You cannot use this command without a database.', True, '*createSKUList')
      else:
        await sendErrorMessage(ctx,'SKU not provided.', True, '*delSKU <sku>')
    
  
  
  #this command is used to list out what SKUs the specific user has added to their database
  @commands.command()
  async def listSKU(self, ctx, private=None):
      author = ctx.author
      id = author.id
    
      if checkUserSKUList(id, pathToSKUUsers):
        userList = f'./SKULists/{id}.csv'
        skuListDF = pd.read_csv(userList)
        skus = skuListDF.SKU.tolist()
        numSKUs = len(skus)
        skuString = ''
        for item in skus:
          skuString += f'{item} \n'
        
      #here I build and send the SKU list in an embed.
      
      skuEmbed = nextcord.Embed(
          title=f'**Current SKU List**',
          description=
          f"These are the current footsite SKUs stored in `{author}'s` database.",
          color=blue)
      skuEmbed.set_author(name='FRIDAY SKU Database', url='')
      skuEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
      skuEmbed.add_field(name=f'SKUs ({numSKUs} stored):',
                         value="```" + skuString + "```")
      
      #if the user wants to keep their list private, they add True to the command, and the list is DMed to them.
      if private:
          await author.send(embed=skuEmbed)
      else:
          await ctx.channel.send(embed=skuEmbed)
  
  """this command is used to gather information about a provided footsite SKU. It will grab an image of
  the product, check to see if it is available on the site, see if the SKU is in the user's database,
  provide links to the product, then it will then return all this information in an easy-to-read embed."""
  
  
  @commands.command()
  @commands.guild_only()
  async def infoSKU(self, ctx, sku=None):
      #catching obvious errors
      if sku == None:
          await sendErrorMessage(ctx, 'SKU not provided', True, '*infoSKU <sku>')
  
      else:
          inList = False
          skus = []
          id = ctx.author.id
          path_to_file = f'./SKULists/{id}.csv'
          loadedFTL = False
          loadedCS = False
          loadedEB = False
  
          #footsite link formats based on given SKU
          footlockerLink = f"https://www.footlocker.com/en/product/~/{sku}.html"
          champsLink = f"https://www.champssports.com/en/product/~/{sku}.html"
          eastbayLink = f"https://www.eastbay.com/en/product/~/{sku}.html"
          imageLink = f"https://images.footlocker.com/is/image/EBFL2/{sku}_a1?wid=2000&hei=2000&fmt=png-alpha"
          """here I use beautiful soup in order to scrape the product webpages - if the information is not found
          I assume that either the product is not loaded or we are blocked, and I use the requests status
          code to determine which. I do this site by site, and only build the soup if a product returns a
          200 status code in order to limit excessive parsing when unnecessary."""
          dataFTL = requests.get(footlockerLink)
          if '200' in str(dataFTL):
              soupFTL = BeautifulSoup(dataFTL.text, features="html5lib")
              productNameTagFTL = soupFTL.find('span',
                                               {'class': 'ProductName-primary'})
              priceTagFTL = soupFTL.find('span', {'class': 'ProductPrice'})
              try:
                  productNameFTL = productNameTagFTL.text
                  loadedFTL = True
              except AttributeError:
                  productNameFTL = sku
                  loadedFTL = False
              try:
                  productPriceFTL = priceTagFTL.text
              except AttributeError:
                  productPriceFTL = 'N/A'
          elif '403' in str(dataFTL):
              productNameFTL = sku
              productPriceFTL = 'N/A'
              loadedFTL = '<403> (BP)'
          elif '302' in str(dataFTL):
              productNameFTL = sku
              productPriceFTL = 'N/A'
              loadedFTL = 'Queue-It'
  
          #same process as the scrape above, simply for a different site (ChampsSports)
          dataCS = requests.get(champsLink)
          if '200' in str(dataCS):
              soupCS = BeautifulSoup(dataCS.text, features="html5lib")
              productNameTagCS = soupCS.find('span',
                                             {'class': 'ProductName-primary'})
              priceTagCS = soupCS.find('span', {'class': 'ProductPrice'})
              try:
                  productNameCS = productNameTagCS.text
                  loadedCS = True
              except AttributeError:
                  productNameCS = sku
                  loadedCS = False
              try:
                  productPriceCS = priceTagCS.text
              except AttributeError:
                  productPriceCS = 'N/A'
          elif '403' in str(dataCS):
              productNameCS = sku
              productPriceCS = 'N/A'
              loadedCS = '<403> (BP)'
          elif '302' in str(dataCS):
              productNameCS = sku
              productPriceCS = 'N/A'
              loadedCS = 'Queue-It'
  
          #Lastly, I use the same request process for EastBay. Footaction no longer exists RIP.
          dataEB = requests.get(eastbayLink)
          if '200' in str(dataEB):
              soupEB = BeautifulSoup(dataEB.text, features="html5lib")
              productNameTagEB = soupEB.find('span',
                                             {'class': 'ProductName-primary'})
              priceTagEB = soupEB.find('span', {'class': 'ProductPrice'})
              try:
                  productNameEB = productNameTagEB.text
                  loadedEB = True
              except AttributeError:
                  productNameEB = sku
                  loadedEB = False
              try:
                  productPriceEB = priceTagEB.text
              except AttributeError:
                  productPriceEB = 'N/A'
          elif '403' in str(dataEB):
              productNameEB = sku
              productPriceEB = 'N/A'
              loadedEB = '<403> (BP)'
          elif '302' in str(dataEB):
              productNameEB = sku
              productPriceEB = 'N/A'
              loadedEB = 'Queue-It'
  
          loadedListNames = {
              loadedFTL: productNameFTL,
              loadedCS: productNameCS,
              loadedEB: productNameEB
          }
  
          loadedListPrices = {
              loadedFTL: productPriceFTL,
              loadedCS: productPriceCS,
              loadedEB: productPriceEB
          }
  
          #iterating through and consolidating gathered info from sites.
          loadedString = f'Footlocker: `{loadedFTL}`\nChampsSports: `{loadedCS}`\nEastBay: `{loadedEB}`'
  
          if loadedFTL == False and loadedCS == False and loadedEB == False:
              productName = sku
              productPrice = 'N/A'
          else:
              for item in loadedListNames:
                  if item != False:
                      productName = loadedListNames[item]
                      productPrice = loadedListPrices[item]
  
          #checking to see if the sku appears in our database
          userHasSKUList = False
          users = []
          path_to_users = './SKULists/userSKULists.csv'
  
          with open(path_to_users, 'r') as userList:
              for row in userList:
                  users.append(row)
              for user in users:
                  if str(id) in user:
                      userHasSKUList = True
          userList.close()
  
          if userHasSKUList:
              with open(path_to_file, 'r') as skuList:
                  reader = csv.reader(skuList)
                  for row in reader:
                      skus.append(row)
                  for item in skus:
                      if sku in item:
                          inList = True
              skuList.close()
          else:
              inList = 'N/A'
  
          if inList == True:
              commandToRun = 'Run `*delSKU` to remove'
          else:
              commandToRun = 'Run `*addSKU` to add'
  
          #lastly, we build the embed
          infoEmbed = nextcord.Embed(
              title=f"**Footsite Product Information:** `{productName}`",
              color=blue)
          infoEmbed.add_field(name="Product Links:",
                              value=f"[Footlocker]({footlockerLink})\n" +
                              f"[ChampsSports]({champsLink})\n" +
                              f"[EastBay]({eastbayLink})")
          infoEmbed.add_field(name='Price:',
                              value=f"`{productPrice}`",
                              inline=True)
          infoEmbed.add_field(name="Loaded:",
                              value=f" {loadedString}",
                              inline=True)
          infoEmbed.add_field(name=f"In your SKU database: `{inList}`",
                              value=commandToRun,
                              inline=False)
          infoEmbed.set_image(url=imageLink)
          infoEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
          await ctx.channel.send(embed=infoEmbed)


def setup(client):
  client.add_cog(footsites(client))