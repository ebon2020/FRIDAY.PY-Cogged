import os
import nextcord
from nextcord.ext import commands
from nextcord import Color as c
import requests
import json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

error = c.red()
affirm = c.green()
blue = c.blue()

etherscanAPIkey = os.environ['etherscan_api_key']

#keeping track of version number
version = os.environ['Version']

#credits, version number and bot Icon
webhookFooter = f'FRIDAY.PY v{version} | coded by ebon#7550 | NFTs'
footerUrl = 'https://cdn.discordapp.com/attachments/884302303648153641/964942745892454430/FridayAI.jpg'

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)


def gweiToEth(gwei):
  return gwei*0.000000000862

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
  async def logInvestment(self, ctx, txHash):
    author = ctx.author
    id = author.id
    
    #creating user agent so our scrape doesn't get blocked
    user_agent = user_agent_rotator.get_random_user_agent()

    #this is the base link for querying a transaction by txhash
    etherscanLink = f"https://etherscan.io/tx/{txHash}"

    #get requesting the page using the random user agent
    request = requests.get(etherscanLink, headers={'User-Agent':f'{user_agent}'})

    #want to ensure we are not banned, so we won't proceed with any kind of analysis if our request doesnt go thru
    if request.status_code == 200:
      soup = BeautifulSoup(request.text, features="html5lib")
      
      titleSpan = soup.find('span',{'class':'hash-tag text-truncate mr-1'})
      title = titleSpan['title']
      
      transactionTypeSpan = soup.find('span',{'class':'mr-1 d-inline-block'})
      transactionType = transactionTypeSpan.text
      
      mediaBodySpan = soup.find('div',{'class':'media-body'})
      image = f"https://etherscan.io{mediaBodySpan.find('img').attrs['src']}"
      
      tokenClass = soup.find('a',{'class':'mr-1 d-inline-block'})
      etherscanContractPath = tokenClass['href']
      etherscanContractPathSplit = etherscanContractPath.split('/')
      contract = etherscanContractPathSplit[-1]

      identifierSpan = soup.find('span',{'class':'hash-tag text-truncate'})
      identifierLink = identifierSpan.find('a').attrs['href']
      identifierSplit = identifierLink.split('=')
      identifier = identifierSplit[-1]
      print(identifier)

      transactionEmbed = nextcord.Embed(title='NFT Investment!', description = f'Logging new investment for user: `{author}`', color = affirm)
      transactionEmbed.set_thumbnail(url=image)
      transactionEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)

      await ctx.send(embed=transactionEmbed)
      
      

      
  
  @commands.command()
  async def ethStats(self, ctx, ethVGwei = None):
    if ethVGwei == None:
      await sendErrorMessage(ctx, 'Choose gas price unit (either ETH or Gwei)', True, '*ethStats <unit> (unit either \'eth\' or \'gwei\')')
    
    elif ethVGwei.lower() != 'eth' and ethVGwei.lower() != 'gwei':
      await sendErrorMessage(ctx, 'Enter a valid gas price unit (either ETH or Gwei)', True, '*ethStats <unit> (unit either \'eth\' or \'gwei\')')

    else:
      choice = ethVGwei.lower()
      etherscanAPIprice = f'https://api.etherscan.io/api?module=stats&action=ethprice&apikey={etherscanAPIkey}'
  
      etherscanPriceResponse = requests.get(etherscanAPIprice)
      priceJSON = json.loads(etherscanPriceResponse.text)
      results = priceJSON['result']
      price = results['ethusd']
  
      etherscanGasPrice = f'https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={etherscanAPIkey}'
      etherscanGasPriceResponse = requests.get(etherscanGasPrice)
      gasPriceJSON = json.loads(etherscanGasPriceResponse.text)
      results = gasPriceJSON['result']

      if choice == 'gwei':
        safeGas = f"{results['SafeGasPrice']} gwei"
        proposedGas = f"{results['ProposeGasPrice']} gwei"
        fastGas = f"{results['FastGasPrice']} gwei"
      elif choice == 'eth':
        safeGas = f"{gweiToEth(int(results['SafeGasPrice']))} eth"
        proposedGas = f"{gweiToEth(int(results['ProposeGasPrice']))} eth"
        fastGas = f"{gweiToEth(int(results['FastGasPrice']))} eth"
  
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