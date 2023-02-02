import json
import string
import sqlite3

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("Я на старте")
    global base, cursor
    base = sqlite3.connect("bot.db")
    cursor = base.cursor()
    if base:
        print("База данных подключена")


@bot.command()
async def test(ctx):
    await ctx.send("Я на месте, и я работаю!")


# @bot.command()
# async def info(ctx, arg):
#     await ctx.send(arg)

# @bot.command()
# async def info(ctx, *, arg):
#     await ctx.send(arg)

@bot.command()
async def rules(ctx):
    await ctx.send("Наши великие умы придумывают правила. Давайте не будем им мешать.")


@bot.command()
async def info(ctx, arg=None):
    author = ctx.message.author
    if arg is None:
        await ctx.send(f"```\n"
                       f"{author}, enter:\n"
                       f"!info general\n"
                       f"!info commands\n"
                       f"```")
    elif arg == "general":
        await ctx.send(f"```\n"
                       f"{author}\n"
                       f"Здравствуйте. Я ваш личный бот по чему то там (мне не объяснили)\n"
                       f"```")
    elif arg == "commands":
        await ctx.send(f"{author.mention}\n"
                       f"!test - команда для проверки бота на его готовность\n"
                       f"(Так же если вы лентяй, то можете посмотреть на на мой профиль. "
                       f"Если горит зеленая точка, то я с вами)\n"
                       f"!rules - правила сервера"
                       f"!send \"ник\"- отправить сообщение в личные сообщения"
                       f"!clear - удаление предыдущего сообщения")
    else:
        await ctx.send("Таких команд в списке нет, поэтому обратитесь к нему\n"
                       "Команда списка !info commands")


@bot.event
async def on_message(message):
    if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.content.split(" ")} \
            .intersection(set(json.load(open("words.json")))) != set():
        await message.channel.send(f"{message.author.mention}, нельзя так выражаться! ")
        await message.delete()

        base.execute("CREATE TABLE IF NOT EXISTS warnings (user_id INT, count INT)")
        base.commit()

        warnings = cursor.execute("SELECT * FROM warnings WHERE user_id ==?", (message.author.id,)).fetchone()
        if warnings is None:
            cursor.execute("INSERT INTO warnings VALUES (?,?)", (message.author.id, 1))
            base.commit()
            await message.channel.send(f"{message.author.mention}, тебя где учили говорить, балбес. "
                                       f"Первое предупреждение. На четвертое отправим тебя в школу под названием \"БАН\"")
        elif warnings[1] == 1:
            cursor.execute("UPDATE warnings SET count ==? WHERE user_id ==?", (2, message.author.id))
            base.commit()
            await message.channel.send(f"{message.author.mention}, Я вижу ты бессмертный. "
                                       f"Второе предупреждение. Давай, кощей, покажи свое бессмертие")
        elif warnings[1] == 2:
            cursor.execute("UPDATE warnings SET count ==? WHERE user_id ==?", (3, message.author.id))
            base.commit()
            await message.channel.send(f"{message.author.mention}, Это был сарказм... "
                                       f"Третье предупреждение. Ты меня вынудил взять телефон.")
        elif warnings[1] == 3:
            cursor.execute("UPDATE warnings SET count ==? WHERE user_id ==?", (4, message.author.id))
            base.commit()
            await message.author.send(f"{message.author.mention}, ты доигрался. Выгляни в окно.\n"
                                      f"**К вашему двору "
                                      f"подъехала машина, из которой выбежало несколько крепких парней. "
                                      f"Они ворвались к вам в дом и связали вас, а затем спустили к машине и "
                                      f"закинули в багажник, после чего сели в нее и уехали. "
                                      f"Вас больше никто не видел** ")
            await message.author.ban(reason="Язык слишком длинный")
            await message.channel.send(f"{message.author.mention}, отправлен в конслагерь \"БАН\"")

    if "Как дела?" in message.content:
        await message.channel.send(f"{message.author.mention}, все хорошо")
    await bot.process_commands(message)


@bot.command()
async def send(ctx):
    await ctx.author.send(f"{ctx.author.mention}. Привет, бездельник.")


@bot.command()
async def send_member(ctx, member: discord.Member):
    await member.send(f"{member.name}. Привет, бездельник.\n"
                      f"Сообщение от {ctx.author.name}")


@bot.command()
async def clear(ctx, amount=2):
    if ctx.message.author.guild_permissions.administrator:
        await ctx.channel.purge(limit=amount)


@bot.command()
async def hello(ctx, amount=1):
    await ctx.channel.purge(limit=amount)
    author = ctx.message.author
    await ctx.send(f"Привет, {author.mention}")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member):
    Talk = discord.utils.get(member.guild.roles, name="Разговорчивый")
    Mute = discord.utils.get(member.guild.roles, name="Мьют")
    await member.add_roles(Mute)
    await member.remove_roles(Talk)
    await ctx.send(f"{member.mention}, держи мьют, заслужил. А теперь посиди и подумай над своим поведением")
    await member.send(f"Лови мьют на сервере {ctx.guild.name}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
    Talk = discord.utils.get(member.guild.roles, name="Разговорчивый")
    Mute = discord.utils.get(member.guild.roles, name="Мьют")
    await member.add_roles(Talk)
    await member.remove_roles(Mute)
    await ctx.send(f"{member.mention} был размьючен!")

@bot.event
async def on_member_join(member):
    Talk = discord.utils.get(member.guild.roles, name="Разговорчивый")
    await member.add_roles(Talk)
    await member.send(f"Добро пожаловать на сервер. Я БОТинок, который следит за порядком в чате, а так же имею еще"
                      f"пару функций")


@bot.command()
async def clear_all(ctx, amount=1001):
    await ctx.channel.purge(limit=amount)


@bot.event
async def on_member_remove(member):
    for ch in bot.get_guild(member.guild.id).channels:
        if ch.name == "общее":
            await bot.get_channel(ch.id).send(f"{member}, подлец и предатель.")


bot.run("MTA1ODAxODAxMzUwNjQ0NTMxNA.G2iH4S.XP4FRtSUXeb8V4CZdKKzpe5l1_RP8s_aKWUpQs")
