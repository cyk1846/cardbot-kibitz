import discord
import asyncio
import aiohttp
import json
import datetime
import os
import sys
import time
import platform
import random
import datetime

import keep_alive

from discord.ext.commands import Bot
from discord.ext import commands
from platform import python_version
from random import randint
from disputils import BotEmbedPaginator
from datetime import timedelta

import numpy as np

gacha_currency = ':gem:'
prefix = '~'

#bot = commands.Bot(command_prefix = '~')
bot = Bot(prefix)

def check(author):
	def inner_check(message): 
		if message.author != author:
			return False
		try: 
			int(message.content) 
			return True 
		except ValueError: 
			return False
	return inner_check

async def status_task():
	while True:
		await bot.change_presence(activity=discord.Game('Try and break me!'))
		await asyncio.sleep(10)
		await bot.change_presence(activity=discord.Game('Beta v0.5'))
		await asyncio.sleep(10)

class AbortWait(Exception):
    pass

def checkm(m):
    if m.content == 'cancel':
        raise AbortWait
    return m.content == m.content and m.channel == m.channel and m.author == m.author

def random_card(result):
	#after randomizing a result level, reference it to open the correct json and pull a card from there
	#should also add the card to user's inventory
	file_suffix = ".json"
	file_name = result + file_suffix
	#print(file_name)
	with open(file_name) as fp:
		card_data = json.load(fp)
		#result referencable
	card_list = card_data[result]
	#print(card_list)
	card_list_pick_code = random.choice(list(card_list.keys()))
	#print(card_list_pick_code)
	cardname = card_list[card_list_pick_code]['name']
	cardsource = card_list[card_list_pick_code]['source']
	cardimg = card_list[card_list_pick_code]['img']
	cardvar = card_list[card_list_pick_code]['event_variant']
	cardcode = card_list_pick_code
	#print("Made it here without issue?") #debug
	#print(cardname, cardsource, cardimg, cardvar, cardcode)
	return(cardname, cardsource, cardimg, cardvar, cardcode)

def draw(ratio_mod):
	if ratio_mod == "a":
		a = 1
		b = 1
		c = 1
		d = 1
		e = 1
		f = 1

	elif ratio_mod == "b":
		#special event draw, weekly draw; increased chance of rarer cards
		a = 8
		b = 18
		c = 6
		d = 0.75
		e = 0.5
		f = 0.25

	else:
		a = 10
		b = 90
		c = 0
		d = 0
		e = 0
		f = 0
        
	random_number = np.random.randint(low=0, high=100, size=1)
	#print(random_number) #DEBUG

	if random_number <= 0.5*a:
		result = "legendary"
		text_result = "LEGENDARY"
	elif 0.5*a < random_number <= (0.5*a + 1.5*b):
		result = "ultra_rare"
		text_result = "ULTRA_RARE"
	elif (0.5*a + 1.5*b) < random_number <= (0.5*a + 1.5*b + 5*c):
		result = "super_rare"
		text_result = "SUPER_RARE"
	elif (0.5*a + 1.5*b + 5*c) < random_number <= (0.5*a + 1.5*b + 5*c + 15*d):
		result = "rare"
		text_result = "RARE"
	elif (0.5*a + 1.5*b + 5*c + 15*d) < random_number <= (0.5*a + 1.5*b + 5*c + 15*d + 33*e):
		result = "uncommon"
		text_result = "UNCOMMON"
	else:
		result = "common"
		text_result = "COMMON"

	#print(result) #DEBUG
	return(result, text_result)

def add_card(ctx, cardcode):
	with open('users.json','r') as f:
		users = json.load(f)
	id_string = str(ctx.author.id)
	users[id_string]['cards'].append(cardcode)

	with open('users.json','w') as f:
		json.dump(users,f)

def add_cooldown(ctx, cd_type):
    with open('users.json', 'r') as f:
        users = json.load(f)
    id_string = str(ctx.author.id)
    dateTimeObj = datetime.date.today()
    timestr = dateTimeObj.strftime("%d-%b-%Y")

    cd_type_num_list = ['allowance','daily','weekly']
    cd_type_num = cd_type_num_list.index(cd_type)
    cd_timestr = users[id_string]['cooldown'][cd_type_num]
    cd_date = datetime.datetime.strptime(cd_timestr,"%d-%b-%Y")
    cd_date = cd_date.date()
    today=datetime.date.today()
    day_diff = int(abs(cd_date-today).days)

    print(cd_type_num)
    print(timestr)
    if (cd_type == "allowance") or (cd_type == "daily"):
        if day_diff > 0:
            cd_status = True
            users[id_string]['cooldown'][cd_type_num] = timestr
            print(users[id_string]['cooldown'][cd_type_num])
        else:
            cd_status = False
    elif (cd_type == "weekly"):
        if day_diff >= 7:
            cd_status = True
            users[id_string]['cooldown'][cd_type_num] = timestr
        else:
            cd_status = False
    else:
        print(cd_type)
        print("Minor error. Discrepency has been recorded.")
    
    with open('users.json','w') as f:
        json.dump(users,f)

    print(cd_type)
    print(cd_status)
    
    return(cd_status)


@bot.event
async def on_ready():
	print('Log on successful!'.format(bot))
	#channel = bot.get_channel(541052582647562250)
	#await channel.send('Kibitz is online!')
	print('---')
	bot.loop.create_task(status_task())

#@bot.event
#async def on_member_join(member):
#	with open('users.json', 'r') as f:
#		users = json.load(f)

	#await update_data(users, member)

#	with open('users.json', 'w') as f:
#		json.dump(users,f)

@bot.command()
async def info(ctx):
	e = discord.Embed(description="My name's Kibitz. Here to collect?")
	e.set_author(name="Bot Information")
	await ctx.message.channel.send(embed=e)

@bot.command()
async def ping(ctx):
	embed = discord.Embed(color=0x00FF00)
	embed.set_footer(text='Pong request by {0}'.format(ctx.message.author))
	embed.add_field(name='Pong! {}'.format(round(bot.latency, 1)), value=':ping_pong:', inline=True)
	await ctx.message.channel.send(embed=embed)

@bot.command()
async def die(ctx):
	if ctx.author.guild_permissions.administrator:
		await ctx.send(':gun: Until next time! :boom:')
		await bot.logout()
	else:
		await ctx.send('You cannot kill me.')

@bot.command()
async def admin_give(ctx, amount, other: discord.Member):
	if ctx.author.guild_permissions.administrator:
		#primary_id = str(ctx.message.author.id)
		giftee = str(other.id)
		with open('users.json', 'r') as f:
			users = json.load(f)
		amt_var = int(amount)
		users[giftee]['gems']+= amt_var
		await ctx.send("{} has been entered in the following user's account: {}".format(amount,other))
		with open('users.json', 'w') as f:
			json.dump(users,f)
	else:
		await ctx.send('Sorry; only admins may use this command.')

@bot.command()
async def suggest(ctx):
    with open('suggestions.json','r') as f:
        s_file = json.load(f)

    id_string = str(ctx.author.id)
    await ctx.send('At any time you can type and send "cancel" if you would like to exit this command.')
    await ctx.send('First, provide the "Character Name". Please provide the full name as accurately as possible, with correct syntax.')
    msg_n = await bot.wait_for('message', check=checkm)
    await ctx.send('Thanks! Now enter the series or source of the "Character". Please provide the full name as accurately as possible, with correct syntax.')
    msg_s = await bot.wait_for('message', check=checkm)
    await ctx.send('Your suggestion has been recorded. Thank you!')
    msg_name = msg_n.content
    msg_series = msg_s.content

    if id_string in s_file:
        count = str(len(s_file[id_string])+1)
        s_file[id_string][count] = [msg_name, msg_series]
    else:
        s_file[id_string] = {}
        s_file[id_string]['0'] = [msg_name, msg_series]
       

    with open('suggestions.json','w') as f:
        json.dump(s_file,f)

@bot.command()
async def gems(ctx):
	with open('users.json','r') as f:
		users = json.load(f)
	id_string=str(ctx.author.id)
	#await update_data(users, ctx)
	#print(users) #DEBUG
	await ctx.send("{}, your vault currently holds {}:gem:.".format(ctx.author.mention,users[id_string]['gems']))
	with open('users.json', 'w') as f:
		json.dump(users,f)

@bot.command()
async def inv(ctx):
	id_string = str(ctx.author.id)
	with open('users.json', 'r') as f:
		users = json.load(f)
	if not users[id_string]['cards']:
		await ctx.send("You don't seem to have any cards yet!")
	else:
		embeds = []
		#print(users[id_string]["cards"])
		for card in users[id_string]["cards"]:
			#print(card)
			if card[-1] == "1":
				with open('common.json','r') as co:
					commonfile = json.load(co)
				card_name = commonfile['common'][card]['name']
				card_source =commonfile['common'][card]['source']
				card_image = commonfile['common'][card]['img']
				card_var = commonfile['common'][card]['event_variant']
			elif card[-1] == "2":
				with open('uncommon.json','r') as co:
					commonfile = json.load(co)
				card_name = commonfile['uncommon'][card]['name']
				card_source =commonfile['uncommon'][card]['source']
				card_image = commonfile['uncommon'][card]['img']
				card_var = commonfile['uncommon'][card]['event_variant']
			elif card[-1] == "3":
				with open('rare.json','r') as co:
					commonfile = json.load(co)
				card_name = commonfile['rare'][card]['name']
				card_source =commonfile['rare'][card]['source']
				card_image = commonfile['rare'][card]['img']
				card_var = commonfile['rare'][card]['event_variant']
			elif card[-1] == "4":
				with open('super_rare.json','r') as co:
					commonfile = json.load(co)
				card_name = commonfile['super_rare'][card]['name']
				card_source =commonfile['super_rare'][card]['source']
				card_image = commonfile['super_rare'][card]['img']
				card_var = commonfile['super_rare'][card]['event_variant']
			elif card[-1] == "5":
				with open('ultra_rare.json','r') as co:
					commonfile = json.load(co)
				card_name = commonfile['ultra_rare'][card]['name']
				card_source =commonfile['ultra_rare'][card]['source']
				card_image = commonfile['ultra_rare'][card]['img']
				card_var = commonfile['ultra_rare'][card]['event_variant']
			else:
				with open('legendary.json','r') as co:
					commonfile = json.load(co)
				card_name = commonfile['legendary'][card]['name']
				card_source =commonfile['legendary'][card]['source']
				card_image = commonfile['legendary'][card]['img']
				card_var = commonfile['legendary'][card]['event_variant']
			#print(card_name, card_source, card_image, card_var)
			embeds.append(discord.Embed(title="{}".format(card_name),description="SERIES: {}".format(card_source)).set_image(url=card_image))
		paginator = BotEmbedPaginator(ctx,embeds)
		return await paginator.run()

@bot.command()
async def buy(ctx):
    with open('users.json','r') as f:
        users = json.load(f)
    id_string=str(ctx.author.id)
    if not users[id_string]:
        await ctx.message.channel.send("Hey there! I don't know you yet. Why don't you use `~register` to get your tab going before you go snatching any cards?")
    elif users[id_string]['gems']<(1000):
        await ctx.send("You don't have enough gems for that.")
    else:
        newtotalgems = users[id_string]['gems'] - 1000
        await ctx.send("Congratulations! You have purchased a booster pack. 1000:gem: has been wired from your account as payment.")
        users[id_string]['gems']=newtotalgems
        with open('users.json', 'w') as f:
            json.dump(users,f)
        result, text_result = draw("c")
        rarity = result
        cardname, cardsource, cardimg, cardvar, cardcode = random_card(result)
        add_card(ctx, cardcode)
        e = discord.Embed()
        e.set_image(url=cardimg)
        await ctx.message.channel.send('You have pulled a(n) {} card! Congratulations!\nSERIES: {}\nCARD: {}'.format(text_result, cardsource, cardname),embed=e)
        result, text_result = draw("a")
        rarity = result
        cardname, cardsource, cardimg, cardvar, cardcode = random_card(result)
        add_card(ctx, cardcode)
        e = discord.Embed()
        e.set_image(url=cardimg)
        await ctx.message.channel.send('You have pulled a(n) {} card! Congratulations!\nSERIES: {}\nCARD: {}'.format(text_result, cardsource, cardname),embed=e)
        result, text_result = draw("a")
        rarity = result
        cardname, cardsource, cardimg, cardvar, cardcode = random_card(result)
        add_card(ctx, cardcode)
        e = discord.Embed()
        e.set_image(url=cardimg)
        await ctx.message.channel.send('You have pulled a(n) {} card! Congratulations!\nSERIES: {}\nCARD: {}'.format(text_result, cardsource, cardname),embed=e)

#async def update_data(users, ctx):
#	id_string=str(ctx.author.id)
#	if id_string in users:
#		pass
#	else:
#		users[id_string] = {}
#		users[id_string]['gems'] = 0
#		users[id_string]['cards'] = []

async def add_allowance(users, ctx, gems):
	id_string=str(ctx.author.id)
	startinggems = users[id_string]['gems']
	totalgems = int(startinggems + gems)
	await ctx.send("{}, here is your allowance of {}:gem:. Your account total is now {}:gem:.".format(ctx.author.mention,gems,totalgems))
	users[id_string]['gems'] += 100
	#print("lolll", users[ctx.author.id]['gems'])

@bot.command()
async def register(ctx):
	id_string=str(ctx.author.id)
	with open('users.json', 'r') as f:
		users = json.load(f)
	if id_string in users:
		await ctx.send("I appreciate the enthusiasm, but you already have a tab open with me here. You can use `~help` to see what other actions are available to you.")
	else:
		dateTimeObj = datetime.date.today()
		timestr = dateTimeObj.strftime("%d-%b-%Y")
		users[id_string] = {}
		users[id_string]['gems'] = 0
		users[id_string]['cards'] = []
		users[id_string]['cooldown'] = ["01-Jan-2020", "01-Jan-2020", "01-Jan-2020"]
        # order is: allowance, daily, weekly
		await ctx.send("You've been registered. Have fun! You can use `~help` to see a full list of commands.")
		with open('users.json', 'w') as f:
			json.dump(users,f)
@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	if message.content.startswith('~hello'):
		await message.channel.send("Hello! My name is Kibitz, and I'm your local card peddler. The shop is currently under construction, so check back later to see what I've got for sale!")

	await bot.process_commands(message)

######################## ERROR EXCEPTIONING OR WHATEVER THIS PART OF THE CODE IS CALLED #############
@bot.event
async def on_command_error(ctx, error):
	if isinstance(error,commands.CommandOnCooldown):
		#time_in_seconds = error.retry_after
		#converted_time = datetime.timedelta(seconds = error.retry_after)
		await ctx.send("Slow your roll, {}! That command is still on cooldown for you.".format(ctx.author.mention))
	#elif isinstance(error, commands.CommandInvokeError):
		#ctx.command.reset_cooldown(ctx)
		#await ctx.send("Hey there! I don't know you yet. Why don't you use `~register` to get your tab going before you go snatching any cards?")
	elif isinstance(error,commands.CommandInvokeError):
		await ctx.send("Fatal error. Please refer to error log for details.")
		raise error


@bot.command()
#@commands.cooldown(1, 86400, BucketType.user)
async def daily(ctx, *args):
	id_string=str(ctx.author.id)
	with open('users.json', 'r') as f:
		users = json.load(f)    
	if id_string in users:
		cd_status = add_cooldown(ctx,"daily")
		print(cd_status)
		if cd_status:
			result, text_result = draw("a")
			cardname, cardsource, cardimg, cardvar, cardcode = random_card(result)
			add_card(ctx, cardcode)
			e = discord.Embed()
			e.set_image(url=cardimg)
			await ctx.message.channel.send('You have pulled a(n) {} card! Congratulations!\nSERIES: {}\nCARD: {}'.format(text_result, cardsource, cardname),embed=e)
		else:
			await ctx.send("Slow your roll, {}! That command is still on cooldown for you.".format(ctx.author.mention))
	else:
		#ctx.command.reset_cooldown(ctx)
		await ctx.send("Hey there! I don't know you yet. Why don't you use `~register` to get your tab going before you go snatching any cards?")
	

@bot.command()
#@commands.cooldown(1, 604800, BucketType.user)
async def weekly(ctx, *args):
	id_string=str(ctx.author.id)
	with open('users.json', 'r') as f:
		users = json.load(f)
	if id_string in users:
		cd_status = add_cooldown(ctx,"weekly")
		if cd_status:
			result, text_result =draw("b")
			cardname, cardsource, cardimg, cardvar, cardcode = random_card(result)
			add_card(ctx, cardcode)
			e = discord.Embed()
			e.set_image(url=cardimg)
			await ctx.message.channel.send('You have pulled a(n) {} card! Congratulations!\nSERIES: {}\nCARD: {}'.format(text_result, cardsource, cardname),embed=e)
		else:
			await ctx.send("Slow your roll, {}! That command is still on cooldown for you.".format(ctx.author.mention))
	else:
		#ctx.command.reset_cooldown(ctx)
		await ctx.send("Hey there! I don't know you yet. Why don't you use `~register` to get your tab going before you go snatching any cards?")

@bot.command()
#@commands.cooldown(1, 60*60*24, commands.BucketType.user)
async def allowance(ctx):
	with open('users.json', 'r') as f:
		users = json.load(f)
	#await update_data(users, ctx)
	#print("AFTER CHECKING FOR USER EXISTENCE:",users) #DEBUG
	cd_status = add_cooldown(ctx, "allowance")
	#print("IN ALLOWANCE PRINT",cd_status)
	if cd_status:
        
		await add_allowance(users, ctx, 100)
		dateTimeObj = datetime.date.today()
		timestr = dateTimeObj.strftime("%d-%b-%Y")
		id_string = str(ctx.author.id)
		users[id_string]['cooldown'][0] = timestr
		#print("AFTER ADDING ALLOWANCE:",users) #DEBUG

		with open('users.json', 'w') as f:
			json.dump(users,f)
	else:
		await ctx.send("Slow your roll, {}! That command is still on cooldown for you.".format(ctx.author.mention))


keep_alive.keep_alive()
bot.run(os.environ['TOKEN'])
