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
import time
import datetime

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
webhookFooter = f'FRIDAY.PY v{version} | coded by ebon#2020 | ETH'
footerUrl = 'https://cdn.discordapp.com/attachments/884302303648153641/964942745892454430/FridayAI.jpg'

#user agents for requests
software_names = [SoftwareName.CHROME.value]
operating_systems = [
    OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value
]
user_agent_rotator = UserAgent(software_names=software_names,
                               operating_systems=operating_systems,
                               limit=100)

#web3 client
w3 = Web3(Web3.HTTPProvider(f'{quickNodeEndpoint}'))

#NFT commands
ethCommands = {
    'seaScrape': 'Scrapes a collections statistics on OpenSea.',
    'ethStats <unit>': 'Returns ETH price and gas price in gwei/eth.',
    'createInvDatabase':
    'Creates a serverside database for user to store NFT investments.',
    'logInv <txHash>':
    'Logs an NFT investment into the user\'s investment database.',
    'logSale <txHash>':
    'Logs an NFT sale, removing NFT from database and logging profits.',
    'checkInvestments': 'Quickly check up on your logged invesments.'
}


#gwei to Eth conversion for Values from web3 api
def gweiToEth(gwei):
    return gwei * 0.000000001


#wei to Eth conversion for Values from web3 api
def weiToEth(wei):
    return wei / 1000000000000000000


#easy way to get a total transaction cost by simply inputting txHash
def getTotalTransactionCost(tx):
    transactionData = w3.eth.get_transaction(tx)
    transactionReceiptData = w3.eth.get_transaction_receipt(tx)
    price = w3.fromWei(int(transactionData['value']), 'ether')
    gasUsed = int(transactionReceiptData['gasUsed'])
    gasPrice = int(transactionReceiptData['effectiveGasPrice'])
    transactionFee = weiToEth(gasPrice * gasUsed)
    cutTransactionFee = round(transactionFee, 5)
    totalTransactionCost = float(price) + float(cutTransactionFee)
    return (totalTransactionCost)


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
def checkInDatabase(tx, path_to_user_list):
    investmentData = pd.read_csv(path_to_user_list)
    txList = investmentData.txHash.tolist()
    for transaction in txList:
        if tx in transaction:
            return True
    return False


#same but for sales
def checkInSaleDatabase(tx, path_to_user_list):
    investmentData = pd.read_csv(path_to_user_list)
    txList = investmentData.invTxHash.tolist()
    for transaction in txList:
        if tx in transaction:
            return True
    return False


#grabbing floor of OS collection
def findFloor(slug):
    openSeaStatsLink = f'https://api.opensea.io/api/v1/collection/{slug}/stats'
    slugStatsData = requests.get(openSeaStatsLink)
    slugStats = json.loads(slugStatsData.text)
    return float(slugStats['stats']['floor_price'])


#check if request was redirected
def requestRedirect(request):
    for item in request.history:
        if int(item.status_code) == 302:
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
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.guild_only()
    async def ethHelp(self, ctx):
        helpEmbed = nextcord.Embed(title='ETH Help!',
                                   description='Commands in the ETH cog:')
        for command in ethCommands:
            helpEmbed.add_field(name=f'`*{command}`',
                                value=f'{ethCommands[command]}')
        helpEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
        helpEmbed.set_thumbnail(url=footerUrl)

        await ctx.send(embed=helpEmbed)

    @commands.command()
    @commands.guild_only()
    async def createInvDatabase(self, ctx):
        author = ctx.author.name
        id = ctx.author.id
        path_to_investment_file = f'./NFTInvestments/Buying/{id}.csv'
        path_to_sale_file = f'./NFTInvestments/Selling/{id}.csv'
        path_to_users = './NFTInvestments/investmentUsers.csv'
        userHasList = checkUserInvList(id, path_to_users)
        if not userHasList:
            with open(path_to_users, 'a') as userLog:
                writer = csv.writer(userLog)
                writer.writerow([f'{id}'])
            userLog.close()

            with open(path_to_investment_file, 'w') as newUserInvList:
                writer = csv.writer(newUserInvList)
                headerRow = [
                    'nftName', 'txHash', 'slug', 'totalCost', 'price',
                    'floorAtLogging', 'contract', 'uniqueContractIdentifierID',
                    'transactionType', 'transDate'
                ]
                writer.writerow(headerRow)
            newUserInvList.close()

            with open(path_to_sale_file, 'w') as newUserSaleList:
                writer = csv.writer(newUserSaleList)
                headerRowSales = ['date', 'profit', 'txHash', 'invTxHash']
                writer.writerow(headerRowSales)
            newUserSaleList.close()

            affirmEmbed = nextcord.Embed(
                title=f'Database Created for user: `{author}`',
                description=
                'Run `*logInv` to start building your investment list!',
                color=affirm)
            affirmEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
            await ctx.channel.send(embed=affirmEmbed)
        else:
            await sendErrorMessage(ctx,
                                   f'{author}\'s database already exists!')

    @commands.command()
    async def logInv(self, ctx, txHash=None):
        if txHash != None:
            author = ctx.author
            id = author.id
            path_to_users = './NFTInvestments/investmentUsers.csv'

            userList = checkUserInvList(id, path_to_users)

            if userList:
                path_to_user_list = f'./NFTInvestments/Buying/{id}.csv'
                path_to_user_sales = f'./NFTInvestments/Selling/{id}.csv'
                #creating user agent so our scrape doesn't get blocked
                user_agent = user_agent_rotator.get_random_user_agent()

                #this is the base link for querying a transaction by txhash
                etherscanLink = f"https://etherscan.io/tx/{txHash}"

                #get requesting the page using the random user agent
                request = requests.get(etherscanLink,
                                       headers={'User-Agent': f'{user_agent}'})

                #seeing if we've been redirected from etherscan link indicating error

                txInList = checkInDatabase(txHash, path_to_user_list)
                loggedBefore = checkInSaleDatabase(txHash, path_to_user_sales)

                if not txInList and not loggedBefore:
                    #want to ensure we are not banned or redirected
                    if request.status_code == 200:
                        #initialize BS4 to analyze etherscan trans page
                        soup = BeautifulSoup(request.text, features="html5lib")

                        #find title of NFT collection
                        titleSpan = soup.find(
                            'span', {'class': 'hash-tag text-truncate mr-1'})
                        title = titleSpan['title']

                        #find transaction type
                        transactionTypeSpan = soup.find(
                            'span', {'class': 'mr-1 d-inline-block'})
                        transactionTypeWhole = transactionTypeSpan.text
                        if 'Mint' in transactionTypeWhole:
                            transactionType = '**Mint** :white_check_mark:'
                            loggedTransType = 'mint'
                        elif 'Transfer' in transactionTypeWhole:
                            transactionType = '**Transfer** :left_right_arrow:'
                            loggedTransType = 'transfer'

                        #find the original contract of the NFT
                        tokenClass = soup.find(
                            'a', {'class': 'mr-1 d-inline-block'})
                        etherscanContractPath = tokenClass['href']
                        etherscanContractPathSplit = etherscanContractPath.split(
                            '/')
                        contract = etherscanContractPathSplit[-1]

                        nftDict = {}
                        tokenClasses = soup.find_all(
                            'span', {'class': 'hash-tag text-truncate'})

                        for item in tokenClasses:
                            href = item.find('a').attrs['href']
                            href = str(href)
                            hrefSplit = href.split('/')
                            identifierSplit = href.split('=')
                            identifier = identifierSplit[-1]
                            contractIdentifier = hrefSplit[-1]
                            if '/' not in identifier:
                                nftDict[identifier] = contractIdentifier
                            else:
                                continue
                        amountOfNftsInTransaction = len(nftDict)

                        identifierString = ''
                        if amountOfNftsInTransaction == 1:
                            identifier = list(nftDict.keys())[0]
                        else:
                            for key in nftDict:
                                identifierString += f' #{key} |'
                            identifierString = identifierString[1:]

                        #these are used to get stats of single asset and contract to harvest slug -> get stats
                        if amountOfNftsInTransaction == 1:
                            openSeaAssetLink = f'https://api.opensea.io/api/v1/asset/{contract}/{identifier}/?include_orders=false'
                            openSeaContractLink = f'https://api.opensea.io/api/v1/asset_contract/{contract}'

                            openSeaAssetData = requests.get(
                                openSeaAssetLink,
                                headers={'X-API-KEY': f'{osAPIkey}'})
                            openSeaContractData = requests.get(
                                openSeaContractLink,
                                headers={'X-API-KEY': f'{osAPIkey}'})

                            openSeaAsset = json.loads(openSeaAssetData.text)
                            openSeaContract = json.loads(
                                openSeaContractData.text)
                            nftUrl = openSeaAsset['image_url']
                            slug = openSeaContract['collection']['slug']
                        else:
                            openSeaContractLink = f'https://api.opensea.io/api/v1/asset_contract/{contract}'
                            openSeaContractData = requests.get(
                                openSeaContractLink,
                                headers={'X-API-KEY': f'{osAPIkey}'})
                            openSeaContract = json.loads(
                                openSeaContractData.text)
                            slug = openSeaContract['collection']['slug']
                            nftUrl = openSeaContract['collection'][
                                'featured_image_url']

                        openSeaStatsLink = f'https://api.opensea.io/api/v1/collection/{slug}/stats'
                        slugStatsData = requests.get(openSeaStatsLink)
                        slugStats = json.loads(slugStatsData.text)
                        floorAtLogging = slugStats['stats']['floor_price']

                        #Web3 Section:

                        #Get price of acquisition
                        transactionData = w3.eth.get_transaction(txHash)
                        price = w3.fromWei(int(transactionData['value']),'ether')

                        #Get total cost of acquisition
                        cost = getTotalTransactionCost(txHash)

                        #get date of transaction
                        block = transactionData.blockNumber
                        timecode = w3.eth.get_block(block).timestamp
                        transDate = datetime.datetime.fromtimestamp(
                            timecode).isoformat()
                        transDateString = str(transDate)
                        dateList = transDateString.split('T')
                        transDate = dateList[0]

                        for nft in nftDict:
                            nftTitle = f'{title}#{nft}'
                            contractIdentifier = nftDict[nft]
                            investment = [
                                nftTitle, txHash, slug, cost / len(nftDict),
                                price / len(nftDict), floorAtLogging, contract,
                                contractIdentifier, loggedTransType, transDate
                            ]
                            with open(path_to_user_list,
                                      'a') as userInvestments:
                                writer = csv.writer(userInvestments)
                                writer.writerow(investment)
                            userInvestments.close()

                        #Build embed to relay information.
                        if amountOfNftsInTransaction == 1:
                            transactionEmbed = nextcord.Embed(
                                title=f'NFT Investment: `{title}#{identifier}`',
                                description=
                                f'Logging new investment for user: `{author}`',
                                color=affirm)
                            transactionEmbed.add_field(
                                name=f'Transaction type: {transactionType}',
                                value=f'Origin Contract: `{contract}`',
                                inline=False)
                            transactionEmbed.add_field(
                                name='Price:',
                                value=f'`{round(float(price),4)}` **Ξ**',
                                inline=True)
                            transactionEmbed.add_field(
                                name='Total Cost:',
                                value=f'`{round(float(cost),4)}` **Ξ**')
                            transactionEmbed.add_field(
                                name='Current Floor (OS):',
                                value=
                                f'`{round(float(floorAtLogging),4)}` **Ξ**',
                                inline=True)
                            transactionEmbed.add_field(
                                name='Transaction Date:',
                                value=f'`{transDate}`',
                                inline=False)
                            transactionEmbed.set_footer(text=webhookFooter,
                                                        icon_url=footerUrl)
                            transactionEmbed.set_thumbnail(url=nftUrl)
                        else:
                            transactionEmbed = nextcord.Embed(
                                title=f'NFT Investment: `{title} Collection`',
                                description=
                                f'Logging new investment for user: `{author}`',
                                color=affirm)
                            transactionEmbed.add_field(
                                name=f'Transaction type: {transactionType}',
                                value=f'Origin Contract: `{contract}`',
                                inline=False)
                            transactionEmbed.add_field(
                                name='Total Price:',
                                value=f'`{round(price,4)}` **Ξ**',
                                inline=True)
                            transactionEmbed.add_field(
                                name='Total Cost:',
                                value=f'`{round(cost,4)}` **Ξ**',
                                inline=True)
                            transactionEmbed.add_field(
                                name='Current Floor (OS)',
                                value=
                                f'`{round(float(floorAtLogging),4)}` **Ξ**',
                                inline=True)
                            transactionEmbed.add_field(
                                name='Total Minted:',
                                value=f'`{len(nftDict)}`',
                                inline=True)
                            transactionEmbed.add_field(
                                name='Total Cost per NFT:',
                                value=f'`{round((float(cost)/float(len(nftDict))), 4)}`',
                                inline=True)
                            transactionEmbed.add_field(
                                name='Transaction Date:',
                                value=f'`{transDate}`',
                                inline=True)
                            transactionEmbed.add_field(
                                name='Minted NFTs:',
                                value=f'```{identifierString}```')
                            transactionEmbed.set_thumbnail(url=nftUrl)
                            transactionEmbed.set_footer(text=webhookFooter,
                                                        icon_url=footerUrl)
                        await ctx.send(embed=transactionEmbed)
                else:
                    await sendErrorMessage(
                        ctx,
                        f'Transaction already logged in {author}\'s database.')
            else:
                await sendErrorMessage(
                    ctx,
                    'You cannot use this command without having a investment database.',
                    True, '*createInvDatabase')
        else:
            await sendErrorMessage(
                ctx, 'Transaction Hash must be included in command', True,
                '*logInv <txHash>')

    @commands.command()
    async def checkInvestments(self, ctx):
        user = ctx.author
        id = user.id
        path_to_users = './NFTInvestments/investmentUsers.csv'

        userHasList = checkUserInvList(id, path_to_users)

        if userHasList:
            path_to_user_list = f'./NFTInvestments/Buying/{id}.csv'
            data = pd.read_csv(path_to_user_list)
            nftNameList = data.nftName.tolist()
            costList = data.totalCost.tolist()
            slugList = data.slug.tolist()
            investmentString = ''
            currentFloorList = []
            currentProfitList = []

            nftNameListCounter = 0
            for item in nftNameList:
                investmentString += f'{item} ({round(costList[nftNameListCounter],4)}Ξ) \n'
                nftNameListCounter += 1

            for slug in slugList:
                currentFloorList.append(round(findFloor(slug),3))
                time.sleep(0.25)

            currentFloorString = '\n'
            for floor in currentFloorList:
                currentFloorString += f'{str(floor)}Ξ\n'

            currentFloorListCounter = 0
            for floor in currentFloorList:
                currentProfitList.append(
                    round(
                        float(floor) -
                        float(costList[currentFloorListCounter]), 3))
                currentFloorListCounter += 1

            currentProfitString = ''
            for profit in currentProfitList:
                if float(profit) < 0:
                    currentProfitString += f'🔴{str(profit)}🔴\n'
                if float(profit) > 0:
                    currentProfitString += f'🟢{str(profit)}🟢\n'

            investmentEmbed = nextcord.Embed(
                title=f'Investments: `{user}`',
                description=
                f'A brief insight into `{user}\'s` NFT investments.',
                color=blue)
            investmentEmbed.add_field(name='Investment (cost):',
                                      value=f'```{investmentString}```',
                                      inline=True)
            investmentEmbed.add_field(name='Current Floor:',
                                      value=f'```{currentFloorString}```',
                                      inline=True)
            investmentEmbed.add_field(name='Profit:',
                                      value=f'```{currentProfitString}```')
            investmentEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
            await ctx.send(embed=investmentEmbed)
        else:
            await sendErrorMessage(
                ctx,
                'You cannot use this command without having a investment database.',
                True, '*createInvDatabase')

    @commands.command()
    async def logSale(self, ctx, txHash=None):
        if txHash != None:
            user = ctx.author
            id = user.id
            path_to_user_list = './NFTInvestments/investmentUsers.csv'
            userHasList = checkUserInvList(id, path_to_user_list)

            if userHasList:
                path_to_user_sales = f'./NFTInvestments/Selling/{id}.csv'
                userLoggedSale = checkInDatabase(txHash, path_to_user_sales)
                if not userLoggedSale:
                    path_to_user_list = f'./NFTInvestments/Buying/{id}.csv'

                    #creating user agent so our scrape doesn't get blocked
                    user_agent = user_agent_rotator.get_random_user_agent()

                    #this is the base link for querying a transaction by txhash
                    etherscanLink = f"https://etherscan.io/tx/{txHash}"

                    #get requesting the page using the random user agent
                    request = requests.get(
                        etherscanLink, headers={'User-Agent': f'{user_agent}'})

                    #seeing if we've been redirected from etherscan link indicating error
                    redirectedToError = requestRedirect(request)

                    if redirectedToError == False:
                        userInvestments = pd.read_csv(path_to_user_list)
                        uniqueNFTKeys = userInvestments.uniqueContractIdentifierID.tolist(
                        )

                        soup = BeautifulSoup(request.text, features='html5lib')
                        #find the identifier tag of the NFT (e.g. #2907)
                        identifierSpan = soup.find(
                            'span', {'class': 'hash-tag text-truncate'})
                        identifierLink = identifierSpan.find('a').attrs['href']
                        contractIdentifierComboSplit = identifierLink.split('/')
                        uniqueContractIdentifierID = contractIdentifierComboSplit[-1]
                        userHasNFT = False
                        for item in uniqueNFTKeys:
                            if uniqueContractIdentifierID in item:
                                userHasNFT = True
                        if userHasNFT:
                            #finding the sellPrice via web3 and the buyPrice via stored data.
                            transactionData = w3.eth.get_transaction(txHash)
                            sellPrice = float(w3.fromWei(float(transactionData['value']), 'ether'))

                            #get date of transaction
                            block = transactionData.blockNumber
                            timecode = w3.eth.get_block(block).timestamp
                            saleDate = datetime.datetime.fromtimestamp(
                                timecode).isoformat()
                            saleDateString = str(saleDate)
                            dateList = saleDateString.split('T')
                            saleDate = dateList[0]
                          
                            nftData = userInvestments.loc[
                                userInvestments['uniqueContractIdentifierID']
                                == uniqueContractIdentifierID]
                            buyPrice = nftData['totalCost'].values[0]
                            investmentTransaction = nftData['txHash'].values[0]
                            floorAtLogging = float(nftData['floorAtLogging'].values[0])
                            slug = nftData['slug'].values[0]

                            #find current floor

                            currentFloor = findFloor(slug)

                            percentageFromFloor = ((sellPrice-currentFloor)/currentFloor)*100

                            percentageGrowth = ((currentFloor-floorAtLogging)/floorAtLogging)*100

                            #finding fees off OS platform.
                            contract = nftData['contract'].values[0]
                            openSeaContractLink = f'https://api.opensea.io/api/v1/asset_contract/{contract}'
                            contractDataResponse = requests.get(
                                openSeaContractLink,
                                headers={'X-API-KEY': f'{osAPIkey}'})
                            contractData = json.loads(contractDataResponse.text)
                            sellerFees = int(contractData['dev_seller_fee_basis_points']) / 100
                            totalFees = sellerFees + 2.5  #opensea takes 2.5 percent of every transaction
                            transactionMultiplier = 1 - (totalFees / 100)
                            totalEthToSeller = sellPrice * transactionMultiplier

                            totalProfit = totalEthToSeller - buyPrice

                            loggedTransactionType = nftData['transactionType'].values[0]
                            if str(loggedTransactionType) == 'mint':
                                buyIn = 'Mint Cost:'
                            elif str(loggedTransactionType) == 'transfer':
                                buyIn = 'Buy-in:'

                            nftTitleList = nftData.nftName.tolist()
                            nftTitle = nftTitleList[0]
                            nftIdentifierList = nftTitle.split('#')
                            nftIdentifier = nftIdentifierList[-1]

                            openSeaAssetLink = f'https://api.opensea.io/api/v1/asset/{contract}/{nftIdentifier}/?include_orders=false'
                            nftImageData = requests.get(openSeaAssetLink,headers={'X-API-KEY': f'{osAPIkey}'})
                            nftImageJSON =json.loads(nftImageData.text)
                            nftImage = nftImageJSON['image_url']                            

                            investmentIndex = userInvestments.index[
                                userInvestments["nftName"] == str(
                                    nftTitle)].tolist()
                            userInvestments = userInvestments.drop(
                                investmentIndex[0])
                            userInvestments.to_csv(f'{path_to_user_list}',
                                                   index=False)

                            loggingList = [
                                saleDate, totalProfit, txHash,
                                investmentTransaction
                            ]

                            with open(path_to_user_sales, 'a') as userSales:
                                writer = csv.writer(userSales)
                                writer.writerow(loggingList)
                            userSales.close()

                            loggedSaleEmbed = nextcord.Embed(
                                title='Sale Logged!',
                                description=
                                'FRIDAY has logged your sale and recorded your profit!',
                                color=blue)
                            loggedSaleEmbed.add_field(
                                name='Item:',
                                value=f'```{nftTitle}```',
                                inline=False)
                            loggedSaleEmbed.add_field(
                                name=buyIn,
                                value=f'`{round(buyPrice,4)}` **Ξ**',
                                inline=True)
                            loggedSaleEmbed.add_field(
                                name='Sold For:',
                                value=f'`{round(sellPrice,4)}` **Ξ**',
                                inline=True)
                            loggedSaleEmbed.add_field(
                                name='Profit (post fees):',
                                value=f'`{round(totalProfit,4)}` **Ξ**')
                            loggedSaleEmbed.add_field(name='Transaction Date:',
                                                      value=f'`{saleDate}`',
                                                      inline=True)
                            loggedSaleEmbed.add_field(name='Current Floor (OS):',value=f'`{currentFloor}` **Ξ**',inline=True)
                            loggedSaleEmbed.add_field(name='View TX:', value=f'[Etherscan]({etherscanLink})', inline=True)
                            if percentageGrowth < 0:
                              loggedSaleEmbed.add_field(name='Investment Summary:',value=f'```This collection\'s value decreased {round(percentageGrowth,4)}% from when you logged your transaction to when you logged your sale and you sold for {round(percentageFromFloor,4)}% from the current floor price.```',inline=False)
                            else:
                              loggedSaleEmbed.add_field(name='Investment Summary:',value=f'```This collection\'s value increased {round(percentageGrowth,4)}% from when you logged your transaction to when you logged your sale and you sold for {round(percentageFromFloor,4)}% from the current floor price.```', inline= False)
                            loggedSaleEmbed.set_thumbnail(url=nftImage)
                            loggedSaleEmbed.set_footer(text=webhookFooter,
                                                       icon_url=footerUrl)
                            await ctx.send(embed=loggedSaleEmbed)
                        else:
                          await sendErrorMessage(ctx, f'{user} does not own NFT in sale transaction.')
                    elif redirectedToError == True:
                        await sendErrorMessage(
                            ctx,
                            'Request redirected to Etherscan Error Page. Please ensure correctness of transaction hash and try again.'
                        )
                else:
                    await sendErrorMessage(
                        ctx,
                        'This sale transaction has already been recorded in your database.'
                    )
            else:
                await sendErrorMessage(
                    ctx,
                    'You cannot use this command without an investment database.',
                    True, '*createInvDatabase')
        else:
            await sendErrorMessage(
                ctx, 'Transaction Hash must be included in command', True,
                '*logSale <txHash>')

    @commands.command()
    @commands.guild_only()
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

        ethEmbed = nextcord.Embed(
            title='Ethereum Stats',
            description='Quick Ethereum stats from the Etherscan API.',
            color=blue)
        ethEmbed.set_thumbnail(
            url=
            'https://thumbs.gfycat.com/EqualPowerfulKoodoo-size_restricted.gif'
        )
        ethEmbed.add_field(name='Price:',
                           value=f'```{price} USD```',
                           inline=False)
        ethEmbed.add_field(name='Fast Gas: :rocket:',
                           value=f'`{fastGas}`',
                           inline=True)
        ethEmbed.add_field(name='Proposed Gas: :light_rail:',
                           value=f'`{proposedGas}`',
                           inline=True)
        ethEmbed.add_field(name='Safe Gas: :tractor:', value=f'`{safeGas}`')
        ethEmbed.set_footer(text=webhookFooter, icon_url=footerUrl)
        await ctx.send(embed=ethEmbed)

    @commands.command()
    @commands.guild_only()
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
                oneDayVolume = round(
                    float(collectionStats['stats']['one_day_volume']), 4)
                totalSupply = int(collectionStats['stats']['total_supply'])
                totalOwners = int(collectionStats['stats']['num_owners'])
                averagePrice = round(
                    float(collectionStats['stats']['average_price']), 4)

                collectionText = json.loads(collectionImageReq.text)
                for entry in collectionText['collection'][
                        'primary_asset_contracts']:
                    nftThumbnail = entry['image_url']
                    name = entry['name']

                collectionEmbed = nextcord.Embed(
                    title=f'OpenSea Scrape: `{name}`',
                    description=
                    f'A summary of the `{name}` collection on OpenSea.',
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
                collectionEmbed.set_footer(text=webhookFooter,
                                           icon_url=footerUrl)
                await ctx.channel.send(embed=collectionEmbed)
            else:
                await sendErrorMessage(
                    ctx, 'An unknown error occurred. Please try again later.')


def setup(client):
    client.add_cog(nfts(client))
