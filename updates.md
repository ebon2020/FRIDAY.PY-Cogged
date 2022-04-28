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

1.2 Updates:
  - Reached all goals for 1.1 version (OpenSea API interactions, better file structure, more extensive commenting...)
  - Added cog implementation (run *loadCog, *unloadCog, and *reloagCog to manage loaded features). This means I can make changes and edits to the code without having to restart the bot, instead I can simply refresh the cog.

1.3 Updates:
  - Added NFT investment logging + creation of user databases.

1.3.1 Updates:
  - added safeguards against duplication of investments and database files.
  - added credits.
---------
1.4 Targets:
  - implement a NFT collection floor monitor, which adds new floors to monitor with stored investments.