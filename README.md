# FRIDAY.PY
This is the first iteration of the FRIDAY discord bot, a bot meant to make SKU management, variant scraping and NFT information gathering intuitive and easy. 

Shoes
-
FRIDAY makes it easy to find variants of Shopify products via the Shopify Scraping feature. It also makes it easy to look up SKUs on footsites using the Footsite Scraping module, which will detect if Bot Protection is enabled on a certain SKU, indicating its impending release. Also, each user in your server can store their own automation SKU list via the Database Management system built into FRIDAY. These SKUs can be reached at any time, and can be kept private if the user wishes to do so. 

NFTs
-
Via the OpenSea API, FRIDAY has an NFT scraping feature, which will return useful statistics about any collection OpenSea has on their platform. Most recently, I've implemented a NFT investment tracker in order to help user's quickly check in on how their investment is doing. This is logged first by the transaction hash, and is logged later by using the hash of the sale. Upon logging of the sale, the user's profit will be recorded, and their investment will be summarized. This is using the web3 package in Python.

# Here's what's up for the future.
I'll be implementing an NFT collection floor monitor that will onboard collections as they are logged in user databases. This will allow the bot to ping as floors pump. Hopefully enabling the user to maximize their profit and sell at the correct time. Once I reach a state where I am satisfied with the current features, I will begin rewriting FRIDAY in Golang for various performance and speed upgrades.
