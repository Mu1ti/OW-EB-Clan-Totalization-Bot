import datetime
import discord
import json
import os

from discord.ext import commands
from discord.ext import tasks

from modules.ebro_bot import EBRO_bot
from modules.log import Log

intents = discord.Intents.all()
driver = commands.Bot(command_prefix='/', intents=intents)
config = json.loads(open('config.json', 'r', encoding='utf-8-sig').read())
bot = EBRO_bot(driver, config)
logger = Log()


####################
#      Commands    #
####################


@driver.command()
async def 스태프추가(message):
    nickname = message.author.display_name + "#" + message.author.discriminator
    if not message.channel.type.name == "private":
       return

    if not nickname in config['staff_list']:
        await message.send("😴 잘자영")
        return

    target_nickname = message.message.content.replace('/스태프추가', '').strip()

    if target_nickname == "":
        await message.send("🤔 아무것도 입력하지 않으신 것 같습니다.")
        return

    config['staff_list'] = config['staff_list'] + [target_nickname]
    filecontent = json.dumps(config, indent=4, ensure_ascii=False)
    open('config.json', 'w', encoding='utf-8').write(filecontent)

    await message.send("😎 스태프 추가를 완료했습니다.")


@driver.command()
async def 스태프제외(message):
    nickname = message.author.display_name + "#" + message.author.discriminator
    if not message.channel.type.name == "private":
       return

    if not nickname in config['staff_list']:
        await message.send("😴 잘자영")
        return

    target_nickname = message.message.content.replace('/스태프제외', '').strip()

    if target_nickname == "":
        await message.send("🤔 아무것도 입력하지 않으신 것 같습니다.")
        return

    config['staff_list'].remove(target_nickname)
    filecontent = json.dumps(config, indent=4, ensure_ascii=False)
    open('config.json', 'w', encoding='utf-8').write(filecontent)

    await message.send("😎 스태프 제외를 완료했습니다.")


@driver.command()
async def 집계(message):
    nickname = message.author.display_name + "#" + message.author.discriminator
    if not message.channel.type.name == "private":
       return

    if not nickname in config['staff_list']:
        await message.send("😴 잘자영")
        return

    target_date = message.message.content.replace('/집계', '').strip()

    if target_date == "":
        await message.send("🤔 아무것도 입력하지 않으신 것 같습니다.")
        return

    try:
        datetime.datetime.strptime(target_date, "%Y-%m")

        if not len(target_date.split('-')[1]) == 2:
            await message.send("🤔 20XX-12와 같은 방식으로 알려주세요.")
            return

    except Exception:
        await message.send("🤔 20XX-12와 같은 방식으로 알려주세요.")
        return

    total = logger.load(target_date)
    response = ""

    if total['status']:
        data = total['data']
        for player in data:
            response = response + player + "," + str(data[player]) + "\n"

    else:
        if total['message'] == "no data":
            await message.send("🤔 그 날짜에 해당하는 집계정보가 없습니다. 날짜를 다시 확인 해 주세요!")

        return

    await message.send("😎 집계정보를 찾았습니다!\n"+"```"+response+"```")

    tmpfilename = "tmp.csv"

    with open(tmpfilename, 'w', encoding='utf-8-sig') as filedescriptor:
        filedescriptor.write(response)

    with open(tmpfilename, 'rb') as filedescriptor:
        await message.send(target_date+"일자 집계결과", file=discord.File(filedescriptor, target_date+".csv"))

    os.remove(tmpfilename)
    return


@driver.command()
async def 저장하기(message):
    player_list = bot.player
    logger.save(player_list)
    bot.player = {}

    print("[*] 저장을 완료했습니다.")

    return


####################
#       Events     #
####################

@driver.event
async def on_ready():
    bot.init()
    return

"""
@driver.event
async def on_raw_reaction_add(payload):
    member = await driver.fetch_user(payload.user_id)
    if not bot.inited and payload.channel_id in bot.channel_id_list:
        return
    bot.activate_detect('on', member, payload)
"""


@driver.event
async def on_raw_reaction_remove(payload):
    guild = await driver.fetch_guild(payload.guild_id)
    member = await guild.fetch_member(payload.user_id)

    if not bot.inited and payload.channel_id in bot.channel_id_list:
        return
    # bot.activate_detect('off', member, payload)
    bot.new_activate_detect(member, payload)
    return


####################
#     scheduler    #
####################


@tasks.loop(seconds=1)
async def scheduler():
    now = datetime.datetime.now().strftime("%H:%M:%S")

    if now == "23:59:50":
        print("[*] 자동저장을 완료했습니다.")
        player_list = bot.player
        logger.save(player_list)
        bot.player = {}


####################
#        Run.      #
####################


if __name__ == "__main__":
    scheduler.start()
    driver.run(config['token'])
