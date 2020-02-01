import os
import random
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta
import csv
import traceback

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='&')


@bot.command(name='rozdajo', brief='Tworzy nowe losowanie', help='Tworzy nowe losowanie', usage ='"Gra" "Platforma" "Czas do losowania w godzinach"')
async def giveaway(ctx, game: str, platform: str, time:int):
    try:
        embed=discord.Embed(title="Rozdawanko ", description="Cebule w dłoń!", color=0xff0000)
        embed.add_field(name="Gra:", value="{}".format(game), inline=True)
        embed.add_field(name="Platforma:", value="{}".format(platform), inline=True)
        embed.add_field(name="Rozdający:", value="{}".format(ctx.author.display_name), inline=True)
        embed.add_field(name="Koniec za:", value="{} godzin od posta do losowania".format(str(time)), inline=True)
        embed.set_footer(text="Jeśli jesteś zainteresowany kliknij ikonkę polskiej trufli")
        mesg = await ctx.send(embed=embed)
        print(ctx.message.id)
        emoji = "🧅"
        await mesg.add_reaction(emoji)
        end_date = datetime.now() + timedelta(hours=time)
        with open('data.csv', mode='a', newline='') as data_file:
            data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            fields = ['{}'.format(game), '{}'.format(platform), '{}'.format(end_date.isoformat()),'{}'.format(mesg.id),'{}'.format(ctx.message.id),'{}'.format(ctx.author.display_name)]
            data_writer.writerow(fields)
        await mesg.pin()
    except:
        await ctx.send('Ups, coś poszło nie tak, sprawdź "!help rozdajo" żeby wiedzieć w jaki sposób utworzyć losowanie!')


@bot.command(name='kasu', help='Kasuje twoje ostatnie losowanie')
async def del_giveaway(ctx):
    with open('data.csv', mode='r') as data_file:
        data_reader = csv.DictReader(data_file)
        new_data = [line for line in data_reader]
        for row in new_data[::-1]:
            if row["santa"] == ctx.author.display_name:
                row["time"] = "FINISHED"
                break

    with open('data2.csv', mode='w+', newline='') as data_file2:
        print('check')
        fieldnames = ['game','platform','time','id','santaid','santa']
        data_writer = csv.DictWriter(data_file2, fieldnames = fieldnames)
        print('check2')
        data_writer.writeheader()
        for new_row in new_data:
            data_writer.writerow(new_row)

    os.remove("data.csv")
    os.rename("data2.csv","data.csv")
    channel = bot.get_channel(640335135144935429)
    message = await channel.fetch_message(int(row["id"]))
    await message.unpin()
    await channel.send("Skasowałem i odpiąłem twoje ostatnie losowanie!")


# @bot.event
# async def on_command_error(ctx, error):
#     channel = bot.get_channel(640335135144935429)
#     print(error)
#     await channel.send('Ups, coś poszło nie tak! Sprawdź "!help rozdajo" żeby zobaczyć jak dodać losowanie!') 

class Check(commands.Cog):
    def __init__(self,bot):
        self.index = 0
        self.printer.start()
        self.bot = bot

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(minutes=1)
    async def printer(self):
        try:        
            print(datetime.now().isoformat())
            new_data=[]
            with open('data.csv', mode='r') as data_file:
                data_reader = csv.DictReader(data_file)
                for row in data_reader:
                    try:
                        if datetime.now() > datetime.fromisoformat(row["time"]):
                            row["time"] = "FINISHED"
                            channel = bot.get_channel(640335135144935429)
                            message = await channel.fetch_message(int(row["id"]))
                            reaction = message.reactions[0]
                            losu_losu = await reaction.users().flatten()
                            if len(losu_losu) == 1:
                                await channel.send("🧅Nikt się nie zgłosił do losowania : {}. Straciliście prawo do miana cebularzy! 🧅".format(row["game"]))
                                await message.unpin()
                                break
                            winner = random.choice(losu_losu)
                            while winner.bot == True:
                                winner = random.choice(losu_losu)
                            santamessage = await channel.fetch_message(int(row["santaid"]))
                            santa = santamessage.author
                            await channel.send("🧅Losowanie {} zakończone! Gratulacje {}, napisz do {} w celu dobioru nagrody 🧅".format(row["game"], winner.mention, santa.mention))
                            await message.unpin()
                    except:
                        pass                    
                    new_data.append(row)
                    print(row)

            with open('data2.csv', mode='w+', newline='') as data_file2:
                print('check')
                fieldnames = ['game','platform','time','id','santaid','santa']
                data_writer = csv.DictWriter(data_file2, fieldnames = fieldnames)
                print('check2')
                data_writer.writeheader()
                for new_row in new_data:
                    data_writer.writerow(new_row)

            os.remove("data.csv")
            os.rename("data2.csv","data.csv")
        except Exception as e:
            print(e)
            print(e.message)            

    @tasks.loop(hours=12.0)
    async def check(self):
        giveaway_count = 0
        with open('data.csv', mode='r') as data_file:
            data_reader = csv.DictReader(data_file)
            for row in data_reader:
                if row["time"] != "FINISHED":
                    giveaway_count += 1
            if giveaway_count > 0:
                channel = bot.get_channel(640335135144935429)
                await  channel.send("🧅Hej, w tej chwili odbywa się następująca liczba głosowań : {}. Sprawdźcie przypięte wiadomości!🧅".format(giveaway_count))
    

bot.add_cog(Check(bot))
bot.run(token)