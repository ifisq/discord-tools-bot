Blue's Tools Bot

This is an open source discord tools bot geared towards the sneaker community! It has a ton of features, including a twitter success poster, fee calculator, delay calculator, size converter, alternate gmail generator, proxy scraper, shopify link builder, bot download links, funko price searcher, stockx price searcher, goat price searcher, and an alternate address generator. 

Please feel free to message me on discord at Blue#9588 if you have any questions!


To run:

Install python from https://python.org

Once installed, run:
pip install discord.py requests urllib3 asyncio proxybroker extruct w3lib.html beautifulsoup4 tweepy

Once you've done all of that, create a twitter developer account at https://developer.twitter.com/ and get your twitter consumer key, twitter consumer secret, twitter access token, and twitter access token secret. Paste these into their respective fields in config.json.

Once you've done all that, go to line 62 on the code for main.py and change the field from url="https://twitter.com/bluecantcode/status/{}" to your twitter account's username. 

Notes:

For all of the code under async def on_message(message), make sure that you change the channel id in bot.get_channel(id=602677420495208471) to whichever success channel you're trying to post to.

Credits:

StockX command compiled and edited from: https://github.com/kxvxnc/Stockx-Discord-Bot/blob/master/stockx.py

Goat command's source was taken down from github.
