import os
import nextcord
from nextcord.ext import commands
from nextcord import Color as c
import requests
import json
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from web3 import Web3
import csv
import pandas as pd

error = c.red()
affirm = c.green()
blue = c.blue()

#secret EtherScan key
etherscanAPIkey = os.environ['etherscan_api_key']

#secret OpenSea key
osAPIkey = os.environ['os_api_key']

#secret quickNode endpoint
quickNodeEndpoint = os.environ['quickNode Endpoint']

#keeping track of version number
version = os.environ['Version']

#credits, version number and bot Icon
webhookFooter = f'FRIDAY.PY v{version} | coded by ebon#7550 | NFTs'
footerUrl = 'https://cdn.discordapp.com/attachments/884302303648153641/964942745892454430/FridayAI.jpg'

#user agents for requests
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

#web3 client
w3 = Web3(Web3.HTTPProvider(f'{quickNodeEndpoint}'))

#NFT commands
nftCommands = {
  'seaScrape':'Scrapes a collections statistics on OpenSea.',
  'ethStats <unit>':'Returns ETH price and gas price in gwei/eth.',
  'createInvDatabase':'Creates a serverside database for user to store NFT investments.',
  'logInvestment <txHash>':'Logs an NFT investment into the user\'s database.',
  'logSale <txHash>':'Logs an NFT sale, removing NFT from database and logging profits.'
}

#gwei to Eth conversion for Values from web3 api
def gweiToEth(gwei):
  return gwei*0.000000001

#wei to Eth conversion for Values from web3 api
def weiToEth(wei):
  return wei/1000000000000000000

#easy way to get a total transaction cost by simply inputting txHash
def getTotalTransactionCost(tx):
  transactionData = w3.eth.get_transaction(tx)
  transactionReceiptData = w3.eth.get_transaction_receipt(tx)
  price = w3.fromWei(int(transactionData['value']), 'ether')
  gasUsed = int(transactionReceiptData['gasUsed'])
  gasPrice = int(transactionReceiptData['effectiveGasPrice'])
  transactionFee = weiToEth(gasPrice*gasUsed)
  cutTransactionFee=round(transactionFee, 5)
  totalTransactionCost = float(price)+float(cutTransactionFee)
  return(totalTransactionCost)

#gateway function for nft investment database functions
def checkUserInvList(id, pathToUserList):
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

#checking for a transaction in a user database
def checkTxInDatabase(tx, path_to_user_list):
  investmentData = pd.read_csv(path_to_user_list)
  txList = investmentData.txHash.tolist()
  for transaction in txList:
    if tx in transaction:
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

class nfts(commands.Cog):
  def __init__(self,client):
    self.client = client

  @commands.command()
  async def nftsHelp(self,ctx):
    helpEmbed = nextcord.Embed(title = 'NFT Help!', description = 'Commands in the NFT cog:')
    for command in nftCommands:
      helpEmbed.add_field(name = f'`*{command}`', value=f'{nftCommands[command]}')
    helpEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
    helpEmbed.set_thumbnail(url=footerUrl)
    
    await ctx.send(embed=helpEmbed)

  @commands.command()
  async def createInvDatabase(self, ctx):
    author = ctx.author.name
    id = ctx.author.id
    path_to_file = f'./NFTInvestments/{id}.csv'
    path_to_users = './NFTInvestments/investmentUsers.csv'
    userHasList = checkUserInvList(id, path_to_users)
    if not userHasList:
        with open(path_to_users, 'a') as userLog:
            writer = csv.writer(userLog)
            writer.writerow([f'{id}'])
        userLog.close()
      
        with open(path_to_file, 'w') as newUserInvList:
            writer = csv.writer(newUserInvList)
            headerRow=['txHash','nftName','slug','totalCost','price','floorAtLogging','contract', 'uniqueContractIdentifierID']
            writer.writerow(headerRow)
        newUserInvList.close()
      
        affirmEmbed = nextcord.Embed(
            title=f'Database Created for user: `{author}`',
            description='Run `*logInvestment` to start building your investment list!',
            color=affirm)
        affirmEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
        await ctx.channel.send(embed=affirmEmbed)
    else:
        await sendErrorMessage(ctx, f'{author}\'s database already exists!')
  
  @commands.command()
  async def logInvestment(self, ctx, txHash):
    author = ctx.author
    id = author.id
    userPFP = author.avatar.url
    path_to_users = './NFTInvestments/investmentUsers.csv'

    userList = checkUserInvList(id, path_to_users)

    if userList:
      path_to_user_list = f'./NFTInvestments/{id}.csv'
      #creating user agent so our scrape doesn't get blocked
      user_agent = user_agent_rotator.get_random_user_agent()
  
      #this is the base link for querying a transaction by txhash
      etherscanLink = f"https://etherscan.io/tx/{txHash}"
  
      #get requesting the page using the random user agent
      request = requests.get(etherscanLink, headers={'User-Agent':f'{user_agent}'})

      txInList = checkTxInDatabase(txHash, path_to_user_list)

      if not txInList:
        #want to ensure we are not banned, so we won't proceed with any kind of analysis if our request doesnt go thru
        if request.status_code == 200:
          #initialize BS4 to analyze etherscan trans page
          soup = BeautifulSoup(request.text, features="html5lib")
  
          #find title of NFT collection
          titleSpan = soup.find('span',{'class':'hash-tag text-truncate mr-1'})
          title = titleSpan['title']
  
          #find transaction type
          transactionTypeSpan = soup.find('span',{'class':'mr-1 d-inline-block'})
          transactionTypeWhole = transactionTypeSpan.text
          if 'Mint' in transactionTypeWhole:
            transactionType='**Mint** :white_check_mark:'
          elif 'Transfer' in transactionTypeWhole:
            transactionType='**Transfer** :left_right_arrow:'
  
          #find the original contract of the NFT
          tokenClass = soup.find('a',{'class':'mr-1 d-inline-block'})
          etherscanContractPath = tokenClass['href']
          etherscanContractPathSplit = etherscanContractPath.split('/')
          contract = etherscanContractPathSplit[-1]
  
          #find the identifier tag of the NFT (e.g. #2907)
          identifierSpan = soup.find('span',{'class':'hash-tag text-truncate'})
          identifierLink = identifierSpan.find('a').attrs['href']
          identifierSplit = identifierLink.split('=')
          contractIdentifierComboSplit = identifierLink.split('/')
          identifier = identifierSplit[-1]
          uniqueContractIdentifierID = contractIdentifierComboSplit[-1]
  
          nftTitle = f'{title}#{identifier}'
  
          #these are used to get stats of single asset and contract to harvest slug -> get stats
          openSeaAssetLink = f'https://api.opensea.io/api/v1/asset/{contract}/{identifier}/?include_orders=false'
          openSeaContractLink = f'https://api.opensea.io/api/v1/asset_contract/{contract}'
  
          #unusable until API key is delivered
          openSeaAssetData = requests.get(openSeaAssetLink, headers={'X-API-KEY':f'{osAPIkey}'})
          openSeaContractData = requests.get(openSeaContractLink, headers={'X-API-KEY':f'{osAPIkey}'})
          slug = 'N/A'
          floorAtLogging = 'N/A'
  
          #Web3 Section:
          
          #Get price of acquisition
          transactionData = w3.eth.get_transaction(txHash)
          price = w3.fromWei(int(transactionData['value']), 'ether')
  
          #Get total cost of acquisition
          cost = getTotalTransactionCost(txHash)
  
          investment = [txHash, nftTitle, slug, cost, price, floorAtLogging, contract, uniqueContractIdentifierID]
          
          with open(path_to_user_list, 'a') as userList:
            writer = csv.writer(userList)
            writer.writerow(investment)
          userList.close()

        #Build embed to relay information.
          transactionEmbed = nextcord.Embed(title=f'NFT Investment: `{nftTitle}`', description = f'Logging new investment for user: `{author}`', color = affirm)
          transactionEmbed.add_field(name=f'Transaction type: {transactionType}', value = f'Origin Contract: `{contract}`', inline=False)
          transactionEmbed.add_field(name='Price:', value=f'`{price}` **Ξ**', inline=True)
          transactionEmbed.add_field(name='Total Cost:', value=f'`{cost}` **Ξ**')
          transactionEmbed.add_field(name='Current Floor (OS):', value=f'`not implemented`', inline=True)
          transactionEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
          transactionEmbed.set_thumbnail(url=userPFP)
    
          await ctx.send(embed=transactionEmbed)

      else:
        await sendErrorMessage(ctx, f'Transaction already logged in {author}\'s database.')
       
  
  @commands.command()
  async def ethStats(self, ctx):
      etherscanAPIprice = f'https://api.etherscan.io/api?module=stats&action=ethprice&apikey={etherscanAPIkey}'
  
      etherscanPriceResponse = requests.get(etherscanAPIprice)
      priceJSON = json.loads(etherscanPriceResponse.text)
      results = priceJSON['result']
      price = results['ethusd']
  
      etherscanGasPrice = f'https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={etherscanAPIkey}'
      etherscanGasPriceResponse = requests.get(etherscanGasPrice)
      gasPriceJSON = json.loads(etherscanGasPriceResponse.text)
      results = gasPriceJSON['result']

      safeGas = f"{results['SafeGasPrice']} gwei"
      proposedGas = f"{results['ProposeGasPrice']} gwei"
      fastGas = f"{results['FastGasPrice']} gwei"
  
      ethEmbed = nextcord.Embed(title = 'Ethereum Stats', description = 'Quick Ethereum stats from the Etherscan API.', color = blue)
      ethEmbed.set_thumbnail(url = 'https://thumbs.gfycat.com/EqualPowerfulKoodoo-size_restricted.gif')
      ethEmbed.add_field(name='Price:', value = f'```{price} USD```', inline = False)
      ethEmbed.add_field(name='Fast Gas: :rocket:', value = f'`{fastGas}`', inline = True)
      ethEmbed.add_field(name='Proposed Gas: :light_rail:', value=f'`{proposedGas}`', inline = True)
      ethEmbed.add_field(name='Safe Gas: :tractor:', value = f'`{safeGas}`')
      ethEmbed.set_footer(text = webhookFooter, icon_url = footerUrl)
      await ctx.send(embed = ethEmbed)

  
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
              oneDayVolume = round(float(collectionStats['stats']['one_day_volume']),4)
              totalSupply = int(collectionStats['stats']['total_supply'])
              totalOwners = int(collectionStats['stats']['num_owners'])
              averagePrice = round(float(collectionStats['stats']['average_price']),4)
  
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