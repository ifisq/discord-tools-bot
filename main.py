import discord
from discord.ext import commands
import json
import requests
import random
import urllib3
import asyncio
from proxybroker import Broker
import time
import extruct
from w3lib.html import get_base_url
from bs4 import BeautifulSoup
import tweepy
import os

urllib3.disable_warnings()

with open('config.json') as f:
	json_file = json.load(f)

auth = tweepy.OAuthHandler(str(json_file["twitter_consumer_key"]), str(json_file["twitter_consumer_secret"]))
auth.set_access_token(str(json_file["twitter_access_token"]), str(json_file["twitter_access_token_secret"]))
twitter_api = tweepy.API(auth)

bot = commands.Bot(command_prefix=json_file["bot_prefix"])
bot_embed_color = 0x00a8ff	

bot.remove_command('help')

@bot.event
async def on_ready():

    print("Bot running with:")
    print("User ID: " + str(bot.user.id))
    print("User Name: " + str(bot.user.name))

def find_url(attachment):
	soup = BeautifulSoup(attachment, 'html.parser')
	link = soup.find("attachment")["url"]
	return link

bot.success_users = []
bot.success_messages_str = []
bot.tweet_ids = []
bot.success_messages = []
bot.success_user_messages = []

@bot.event
async def on_message(message):
	if message.channel == bot.get_channel(id=602677420495208471) and message.author != bot.user:
		if message.attachments != []:
			filename = "temp.jpg"
			attachment = str(message.attachments[0])
			url = find_url(attachment)
			request = requests.get(url, stream=True)
			if request.status_code == 200:
				with open(filename, 'wb') as image:
					for chunk in request:
						image.write(chunk)
				tweet = twitter_api.update_with_media(filename, status="Success by {} in Blue Development \n{}".format(message.author, message.content), auto_populate_reply_metadata=True)
				os.remove(filename)
				em = discord.Embed(title="**Success posted on Twitter!**", description = "Did you leave any sensitive information? Click :wastebasket: to delete the tweet!", color = bot_embed_color, url="https://twitter.com/bluecantcode/status/{}".format(str(tweet.id)))
				em.add_field(name="User ", value="<@{}>".format(message.author.id))
				em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))
				em.set_author(name="Blue Success", url="https://twitter.com/bluecantcode")
				sent_message = await bot.get_channel(id=602677420495208471).send(embed = em)
				await sent_message.add_reaction("🗑")
				bot.success_users.append(str(message.author.name) + "#" + str(message.author.discriminator))
				bot.success_messages_str.append(str(sent_message))
				bot.success_messages.append(sent_message)
				bot.success_user_messages.append(message)
				bot.tweet_ids.append(tweet.id)
			else:
				await bot.get_channel(id=602677112494751763).send("Couldn't download the image.")

	await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
	if str(user) in bot.success_users:
		if str(reaction.message) in bot.success_messages_str:
			if user != bot.user:
				index = bot.success_messages_str.index(str(reaction.message))
				twitter_api.destroy_status(id=bot.tweet_ids[index])
				em = discord.Embed(title="Deleted {}'s success!".format(user), color = bot_embed_color)
				em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))
				em.set_author(name="Blue Success", url="https://twitter.com/bluecantcode")
				await bot.success_user_messages[index].delete()
				await bot.success_messages[index].edit(embed=em)
				del bot.success_users[index]
				del bot.success_messages_str[index]
				del bot.success_messages[index]
				del bot.success_user_messages[index]
				del bot.tweet_ids[index]
	
	#await bot.get_channel(602676776803631115).send(bot.get_channel(604902071111778314).fetch_message(604903231201738783))
	#if reaction.message == bot.get_channel(604902071111778314).fetch_message(604903231201738783):
		#print("Reaction detected!")
		#await user.add_roles(roles=[(reaction.message.guild).get_role(604902245980569619)])
	
@bot.command()
async def update_msg(ctx):
	em = discord.Embed(title="React for Updates!", description="React to this message with the ✅ emote to be pinged for updates! Unreact if you'd like the role removed.", color=bot_embed_color)
	em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))
	await ctx.send(embed=em)


@bot.command()
async def help(ctx):
	em = discord.Embed(title="Blue Help", description="", color = bot_embed_color)
	em.add_field(name="Address", value = "Creates alternative addresses for the specified address. \n `!address <address>`", inline=False)
	em.add_field(name="Delay Calculator", value = "Specifies recommended delay that should be used for your proxy and task count. \n `!delay <number of tasks> <number of proxies>`", inline=False)
	em.add_field(name="Downloads", value = "Displays a list of bot/software downloads. \n `!downloads`", inline=False)
	em.add_field(name="Fee Calculator", value = "Calculates seller fees for certain sites. \n `!fees <amount>`", inline=False)
	em.add_field(name="Gmail Dot Trick", value = "Applies the Gmail dot trick to an email address. \n `!gmail <email>`", inline=False)
	em.add_field(name="Goat Search", value = "Searches Goat and displays a search result. \n `!goat <keywords>`", inline=False)
	em.add_field(name="PopPriceGuide Search", value = "Searches PopPriceGuide and return stats for the specified search term. \n `!pop <keywords>`", inline=False)
	em.add_field(name="Proxy Scraper", value = "Scrapes a specified amount of usable proxies (limited to 50 per command). \n `!proxies <amount>`", inline=False)
	em.add_field(name="Shoe Size Converter", value = "Converts shoe sizes (men) for the following regions: US, UK, and EU. `!size <size> <region>`", inline=False)
	em.add_field(name="Shopify Variants", value = "Creates add-to-cart links for the specified Shopify product link. \n `!shopify <link>`", inline=False)
	em.add_field(name="StockX Search", value = "Searches StockX and displays a search result. \n `!stockx <keywords>`", inline=False)
	em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))

	await ctx.send(embed=em)

@bot.command(pass_context=True)
async def fees(ctx, price):

	price = float(price)
	paypal_price = price - (price*0.029) + .30
	ebay_price = price - (price*0.129)
	goat_price = price - (price * 0.095) + 5
	grailed_price = price - (price*0.089)
	flightclub_price = price * 0.80
	stockx_level_1 = price - (price*0.095)
	stockx_level_2 = price - (price*0.09)
	stockx_level_3 = price - (price*0.085)
	stockx_level_4 = price - (price*0.08)

	em = discord.Embed(title="Blue Fee Calculator", description="", color= bot_embed_color)
	em.add_field(name="Ebay", value= "${}".format('%.2f' % round(ebay_price, 2)), inline=False)
	em.add_field(name="PayPal", value="${}".format('%.2f' % round(paypal_price, 2)), inline=False)
	em.add_field(name="Goat", value="${}".format('%.2f' % round(goat_price, 2)), inline=False)
	em.add_field(name="Grailed", value="${}".format('%.2f' % round(grailed_price, 2)), inline=False)
	em.add_field(name="Flight Club", value="${}".format('%.2f' % round(flightclub_price, 2)), inline=False)
	em.add_field(name="StockX", inline=False, value="Level 1 | ${} \n Level 2 | ${} \n Level 3 | ${} \n Level 4 | ${}".format(
		'%.2f' % round(stockx_level_1, 2), 
		'%.2f' % round(stockx_level_2, 2), 
		'%.2f' % round(stockx_level_3, 2), 
		'%.2f' % round(stockx_level_4, 2)))
	em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))
	await ctx.send(embed=em)

@bot.command(pass_context=True)
async def delay(ctx, task_count: int, proxy_count: int):
	delay_number = 3500/(proxy_count/task_count)

	em = discord.Embed(title="Blue Delay Calculator", description="", color= bot_embed_color)
	em.add_field(name="Task Count", value = "{}".format(task_count), inline=False)
	em.add_field(name="Proxy Count", value = "{}".format(proxy_count), inline=False)
	em.add_field(name="Recommended Delay", value = "{} ms".format(round(delay_number)), inline=False)
	em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))
	await ctx.send(embed=em)

@bot.command(pass_context=True)
async def size(ctx, shoe_size: float, region):
	em = discord.Embed(title="Blue Size Converter", description="", color= bot_embed_color)
	em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))

	if region.lower() == "us":
		if shoe_size == int(shoe_size):
			em.add_field(name="US", value = "{}".format(shoe_size), inline=False)
			em.add_field(name="UK", value = "{}".format(shoe_size-0.5), inline=False)
			em.add_field(name="EU", value = "{}".format(shoe_size+33), inline=False)
		
		else:
			eu_lower_bound = shoe_size + 32.5
			eu_higher_bound = shoe_size + 33.5
			em.add_field(name="US", value = "{}".format(shoe_size), inline=False)
			em.add_field(name="UK", value = "{}".format(shoe_size-0.5), inline=False)
			em.add_field(name="EU", value = "{}-{}".format(eu_lower_bound, eu_higher_bound), inline=False)

	if region.lower() == "uk":
		if shoe_size == int(shoe_size):
			em.add_field(name="US", value = "{}".format(shoe_size+0.5), inline=False)
			em.add_field(name="UK", value = "{}".format(shoe_size), inline=False)
			em.add_field(name="EU", value = "{}".format(shoe_size+33.5), inline=False)
		
		else:
			eu_lower_bound = shoe_size + 33
			eu_higher_bound = shoe_size + 34
			em.add_field(name="US", value = "{}".format(shoe_size+0.5), inline=False)
			em.add_field(name="UK", value = "{}".format(shoe_size), inline=False)
			em.add_field(name="EU", value = "{}-{}".format(eu_lower_bound, eu_higher_bound), inline=False)

	if region.lower() == "eu":
		em.add_field(name="US", value = "{}".format(shoe_size-33), inline=False)
		em.add_field(name="UK", value = "{}".format(shoe_size-33.5), inline=False)
		em.add_field(name="EU", value = "{}".format(shoe_size), inline=False)
	
	await ctx.send(embed=em)
		
@bot.command(pass_context=True)
async def gmail(ctx, account):
	length = len(account) - 10
	i = 0
	final_str = ""
	while i < 10:
		amount_of_periods = random.randint(0, length - 1)
		period_count = 0
		new_account = account
		index_arr=[]

		while period_count < amount_of_periods:
			index = random.randint(1, length - 1)
			temp_index = index
			if index in index_arr:
				while temp_index in index_arr:
					temp_index = random.randint(1, length - 1)
				index = temp_index
			
			new_account = new_account[:index] + "." + new_account[index:]
			for arr_index, item in enumerate(index_arr):
				if item > index:
					index_arr[arr_index] += 1

			index_arr.append(index)
			print(index_arr)
			period_count += 1

		final_str = final_str + new_account + "\n"
		i+=1

	final_str = remove_duplicates(final_str)

	em = discord.Embed(title="Blue Gmail Generator", description= "", color= bot_embed_color)
	em.add_field(name=account, value=final_str, inline=False)
	em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))
	await ctx.send(embed=em)
	
def remove_duplicates(string):
    for i, (a, b) in enumerate(zip(string, string[1:])):
        if a == b and a == ".":
            return string[:i] + remove_duplicates(string[i+1:])
    return string

bot.proxy_array = []

async def show(proxies):
	while True:
		proxy = await proxies.get()
		if proxy is None: break
		#print("Proxy found: {}".format(proxy))
		bot.proxy_array.append(proxy)

@bot.command(pass_context=True)
async def proxies(ctx, amount: int):
	em = discord.Embed(title="Blue Proxy Scraper", description = "Note - Proxies are scraped from public sources, so all may not be secure or fully functional.", color = 0x00a8ff)
	proxies = asyncio.Queue()
	broker = Broker(proxies)
	if amount < 50:
		await asyncio.gather(broker.find(types=['HTTP', 'HTTPS'], limit=amount), show(proxies))
	else:
		await asyncio.gather(broker.find(types=['HTTP', 'HTTPS'], limit=50), show(proxies))

	proxies_str = ""
	for item in bot.proxy_array:
		item = str(item).split(']')[1][:-1]
		proxies_str += item + "\n"
	
	em.add_field(name="Proxies", value= proxies_str)
	em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))
	await ctx.send(embed=em)

	bot.proxy_array = []

@bot.command(pass_context=True)
async def build(ctx, link):
	vars = []
	titles = []
	site = link.split('/')
	site = site[2]
	r = requests.get(link + ".json")
	r = r.json()
	prodname = r["product"] ["title"]
	for i in r["product"] ["variants"]:
		id = i['id']
		vars.append(id)
		title = i['title']
		titles.append(title)
	em = discord.Embed(title="Blue Link Builder", description=prodname, color=bot_embed_color)
	x = 0
	for i in titles:
		em.add_field(name=str(i), value="[Download](https://{}/cart/{}:1)".format(site, str(vars[x])), inline=False)
		x = x+1
		
	em.set_thumbnail(url=r["product"]["image"]["src"].replace("{}".format("\ "), ""))
	em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))

	await ctx.send(embed=em)

@bot.command(pass_context=True)
async def downloads(ctx):
	em = discord.Embed(title="Blue Downloads", description="", color = 0x00a8ff)
	em.add_field(name="ANB AIO", value="[Download](http://bit.ly/ANB-AIO-Setup)")
	em.add_field(name="ANB AIO V2", value="[Download](http://downloadsv2.aiobot.com/)")
	em.add_field(name="BNB", value="[Download](http://bnba.io/download-bnb)")
	em.add_field(name="CyberAIO", value="[Download](https://cdn.cybersole.io/installer/installer.exe)")
	em.add_field(name="Dashe", value="[Download](https://dashe-updater.herokuapp.com/)")
	em.add_field(name="EveAIO", value="[Download](http://eve-robotics.com/release/EveAIO_setup.exe)")
	em.add_field(name="EveCaptcha (Mac)", value="[Download](https://updates.shhhh3dots.com/download/latest&platform=mac)")
	em.add_field(name="EveCaptcha (Windows)", value="[Download](https://updates.shhhh3dots.com/download/latest&platform=win)")
	em.add_field(name="Ghost Phantom", value="[Download](https://ghost.shoes/l/phantom)")
	em.add_field(name="Ghost SNKRS", value="[Download](https://update.ghostaio.com/)")
	em.add_field(name="HasteyIO", value="[Download](https://update.hastey.io/)")
	em.add_field(name="Latchkey", value="[Download](http://download.latchkeybots.io/)")
	em.add_field(name="NikeShoeBot", value="[Download](https://nsb.nyc3.digitaloceanspaces.com/NSB-win-latest.exe)")
	em.add_field(name="PD", value="[Download](https://shopify.projectdestroyer.com/download)")
	em.add_field(name="TheKickStation", value="[Download](http://thekickstationapi.com/downloads/Installer.msi.)")
	em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))

	await ctx.send(embed=em)

@bot.command(pass_context=True)
async def pop(ctx, *args):
	args = " ".join(args)
	args = str(args).replace(" ", "+")
	r = requests.get("https://www.poppriceguide.com/guide/searchresults.php?search={}".format(args))
	soup = BeautifulSoup(r.content, 'html.parser')
	first_answer = soup.find("div", {"class": "itemrow"})
	link = first_answer.find("a")["href"]
	item_name = first_answer.find("div", {"class": "itemname"}).contents[0]
	image = first_answer.find("img", {"class": "itemlistimg-ext"})["src"]
	price = first_answer.find("div", {"class": "itemvalue"}).contents[0]

	description_req = requests.get("https://www.poppriceguide.com" + str(link))

	em = discord.Embed(title="Blue Funko Pricer", description="[{}](https://www.poppriceguide.com{})".format(str(item_name), str(link)), color=bot_embed_color)
	em.add_field(name="Estimated Value", value= str(price))
	em.set_thumbnail(url=image)
	em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))
	await ctx.send(embed=em)

@bot.command(pass_context=True)
async def stockx(ctx, *args):
	keywords = ''
	for word in args:
		keywords += word + '%20'
	json_string = json.dumps({"params": f"query={keywords}&hitsPerPage=20&facets=*"})
	byte_payload = bytes(json_string, 'utf-8')
	algolia = {"x-algolia-agent": "Algolia for vanilla JavaScript 3.32.0", "x-algolia-application-id": "XW7SBCT9V6", "x-algolia-api-key": "6bfb5abee4dcd8cea8f0ca1ca085c2b3"}
	with requests.Session() as session:
		r = session.post("https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query", params=algolia, verify=False, data=byte_payload, timeout=30)
		results = r.json()["hits"][0]
		apiurl = f"https://stockx.com/api/products/{results['url']}?includes=market,360&currency=USD"
		header = {
			'accept': '*/*',
			'accept-encoding': 'gzip, deflate, br',
			'accept-language': 'en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7,la;q=0.6',
			'appos': 'web',
			'appversion': '0.1',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
		}
		response = requests.get(apiurl, verify=False, headers=header)

	prices = response.json()
	general = prices['Product']
	market = prices['Product']['market']
	sizes = prices['Product']['children']
   
	bidasks = ''
	for size in sizes:
		bidasks +=f"Size {sizes[size]['shoeSize']} | Low Ask ${sizes[size]['market']['lowestAsk']} | High Bid ${sizes[size]['market']['highestBid']}\n"

	embed = discord.Embed(title="Blue StockX", description = "[{}](https://stockx.com/{})".format(str(general['title']), str(general['urlKey'])), color=bot_embed_color)
	embed.set_thumbnail(url=results['thumbnail_url'])
	embed.set_footer(text='Blue Utilities', icon_url = bot.user.avatar_url)
	if 'styleId' in general:
		embed.add_field(name='SKU/PID:', value=general['styleId'], inline=True)
	else:
		embed.add_field(name='SKU/PID:', value='None', inline=True)
	if 'colorway' in general:
		embed.add_field(name='Colorway:', value=general['colorway'], inline=True)
	else:
		embed.add_field(name='Colorway:', value='None', inline=True)
	if 'retailPrice' in general:
		embed.add_field(name='Retail Price:', value=f"${general['retailPrice']}", inline=True)
	else:
		for trait in general['traits']:
			try:
				embed.add_field(name='Retail Price:', value=f"${int(trait['value'])}")
			except:
				pass
	embed.add_field(name='Release Date:', value=general['releaseDate'], inline=True)
	embed.add_field(name='Highest Bid:', value=f"${market['highestBid']} Size {market['highestBidSize']}", inline=True)
	embed.add_field(name='Lowest Ask:', value=f"${market['lowestAsk']} Size {market['lowestAskSize']}", inline=True)
	embed.add_field(name='Total Asks:', value=market['numberOfAsks'], inline=True)
	embed.add_field(name='Total Bids:', value=market['numberOfBids'], inline=True)
	embed.add_field(name='Total Sold:', value=market['deadstockSold'], inline=True)
	embed.add_field(name='Sales last 72 hrs:', value=market['salesLast72Hours'], inline=True)
	embed.add_field(name='Last Sale:', value=f"${market['lastSale']} Size {market['lastSaleSize']}", inline=True)
	#embed.add_field(name='Sizes:', value=bidasks, inline=False)
	embed.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))
	await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def goat(ctx, *query):
	headers = {
			#'User-Agent': user_agent
		}

	params = {
			'x-algolia-agent': 'Algolia for vanilla JavaScript 3.25.1',
			'x-algolia-api-key': 'ac96de6fef0e02bb95d433d8d5c7038a',
			'x-algolia-application-id': '2FWOTDVM2O',
        }

	data = {
			"params": "query={}&facetFilters=(status%3Aactive%2C%20status%3Aactive_edit)%2C%20()&page=0&hitsPerPage=20"
			.format(query)
		}

	response = requests.post(url="https://2fwotdvm2o-dsn.algolia.net/1/indexes/ProductTemplateSearch/query", headers=headers, params=params, json=data)

	output = json.loads(response.text)

	image = output['hits'][0]['picture_url']
	name = output['hits'][0]['name']
	new_lowest_price_cents = int(output['hits'][0]['new_lowest_price_cents'] / 100)
	maximum_offer = int(output['hits'][0]['maximum_offer_cents'] / 100)
	minimum_offer = int(output['hits'][0]['minimum_offer_cents'] / 100)
	url = 'https://www.goat.com/sneakers/' + output['hits'][0]['slug']
	used_lowest_price_cents = int(output['hits'][0]['used_lowest_price_cents'] / 100)
	want_count = output['hits'][0]['want_count']
	want_count_three = output['hits'][0]['three_day_rolling_want_count']

	em = discord.Embed(title="Blue GOAT Price Checker", description="", color=bot_embed_color)
	em.set_thumbnail(url=image)
	em.add_field(name="Product Name", value="[{}]({})".format(name, url), inline=False)
	em.add_field(name="Lowest Bid", value="${}".format(minimum_offer), inline=True)
	em.add_field(name="Highest Bid", value="${}".format(maximum_offer), inline=True)
	em.add_field(name="Used Lowest Price", value="${}".format(used_lowest_price_cents), inline=True)
	em.add_field(name="New Lowest Price", value="${}".format(new_lowest_price_cents), inline=True)
	em.add_field(name="Want Count in Last 3 Days", value="{}".format(want_count_three), inline=True)
	em.add_field(name="Total Want Count", value="{}".format(want_count), inline=True)
	em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))

	await ctx.send(embed=em)

def gen_address(addy: str):

	letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	four_char = ''.join(random.choice(letters) for _ in range(4))
	should_abbreviate = random.randint(0,1)
	if should_abbreviate == 0:
		if "street" in addy.lower():
			addy = addy.replace("Street", "St.")
			addy = addy.replace("street", "St.")
		elif "st." in addy.lower():
			addy = addy.replace("st.", "Street")
			addy = addy.replace("St.", "Street")
		if "court" in addy.lower():
			addy = addy.replace("court", "Ct.")
			addy = addy.replace("Court", "Ct.")
		elif "ct." in addy.lower():
			addy = addy.replace("ct.", "Court")
			addy = addy.replace("Ct.", "Court")
		if "rd." in addy.lower():
			addy = addy.replace("rd.", "Road")
			addy = addy.replace("Rd.", "Road")
		elif "road" in addy.lower():
			addy = addy.replace("road", "Rd.")
			addy = addy.replace("Road", "Rd.")
		if "dr." in addy.lower():
			addy = addy.replace("dr.", "Drive")
			addy = addy.replace("Dr.", "Drive")
		elif "drive" in addy.lower():
			addy = addy.replace("drive", "Dr.")
			addy = addy.replace("Drive", "Dr.")
		if "ln." in addy.lower():
			addy = addy.replace("ln.", "Lane")
			addy = addy.replace("Ln.", "Lane")
		elif "lane" in addy.lower():
			addy = addy.replace("lane", "Ln.")
			addy = addy.replace("lane", "Ln.")
	
	random_number = random.randint(1,99)
	extra_list = ["Apartment", "Unit", "Room"]
	random_extra = random.choice(extra_list)
	return four_char + " " + addy + " " + random_extra + " " + str(random_number)


@bot.command(pass_context=True)
async def address(ctx, *args):
	addy = ' '.join(args)
	address_array = []
	i = 0
	while i < 10:
		address_array.append(gen_address(addy))
		i+=1
	
	final_str = "\n".join(address_array)
	em = discord.Embed(title = "Blue Address Generator", description="{}".format(final_str), color=bot_embed_color)
	em.set_footer(text=str(json_file["bot_embed_footer_text"]), icon_url = str(json_file["bot_embed_logo"]))
	await ctx.send(embed=em)

bot.run(json_file["bot_token"])