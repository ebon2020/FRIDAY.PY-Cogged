# UPDATES


1.1.1 Updates:
  - reworked shopScrape Logic to include stock numbers of products on ShoePalace.
  - added FRIDAY logo and bot embed footer in order to relay proper version number and author.

1.1.2 Updates:
  - Wrote Opensea API interation.

1.1.3 Updates:
  - Rewrote SKU storing logic, specifically to move into a subfolder.

1.1.4 Updates:
  - Upgraded from Discord.PY which has since reached EOL. Now using Nextcord for any Discord API/asynchronous programming.
  - Also changed backend enviroments for Host, as Discord.PY is incompatible with Nextcord (this meant changing repositories)

-------------------

1.2 Updates:
  - Reached all goals for 1.1 version (OpenSea API interactions, better file structure, more extensive commenting...)
  - Added cog implementation (run *loadCog, *unloadCog, and *reloadCog to manage loaded features). This means I can make changes and edits to the code without having to restart the bot, instead I can simply refresh the cog.

-------------------

1.3 Updates:
  - Added NFT investment logging + creation of user databases.

1.3.1 Updates:
  - added safeguards against duplication of investments and database files.
  - added credits.

1.3.2 Updates:
  - Officially implemented *checkInvestment - this returns a quick summary (sans rarity implementation) of current logged investments.
  - Optimizations of requests (specifically timing to avoid rate limits on OpenSea API).

1.3.3 Updates:
  - Officially implemented *logSale - which removes the NFT from the investment database of the user, and returns the profit of the investment. The logSale embed will become more complicated to include more information in the future.
  - Improved error handling in various areas, ensuring the best experience for the user.

1.3.4 Updates:
  - Added logging for sales, and restricted data entry to forbid past transactions from being reentered. This assures that one user cannot inflate their perceived profit by entering the same profitable investment multiple times.
  - Slight reworks to request timing in order to avoid API rate limits from OpenSea.
  - Added more error logging.

1.3.5 Updates
  - Added support for multi-nft mints. Now, no matter what, FRIDAY will pick up all NFTs traded in a transaction. Each NFT that is minted in a group will have a percentage price of the total cost of the transaction and is logged as such.
  - Tweaked data logging, and shifted NFT image url requesting to per-logging basis, whether that be selling or investing, this is so that each time the NFT is mentioned in a transaction, the most recent image is grabbed from the OpenSea API, it's better that than storing an outdated image.
  - There are now two types of investment embeds - accounting for multi-NFT transactions. These embeds will grab the image url for the collection rather than the url of all the different NFT's, simply because it's better this way.

1.3.6 Updates
  - Rewrote SKU storing commands to use Pandas versus iterating through with csv reader. It's lighter weight, and improves performance + it normalizes the csv parsing software I use throughout the project.
  - Rewrote *listSKU to use Pandas as well.
  - Began implementation of a link storing database to store Shopify restock links for each user, making them readily accessible so long as the user has access to Discord. *delLink and *listLink will be implemented in 1.3.7
    
---------
1.3 Updates to do:
  - implement a viewSales command which will show you whether or not you should have held in your past investments 🔴
  - implement a viewNFTs command which will allow you to quickly see what NFTs you have logged 🔴
  - Add a storage system for shopify restock links 🟡

1.4 Targets:
  - implement a NFT collection floor monitor, which adds new floors to monitor with stored investments.
  - Add multi-nft mint support on *logInvestment without need for differentiation from user. (Done)
  - all 1.3 updates to do.

1.5 Targets:
  - Add profit tracking implementation
  - Add NFT autolist feature?