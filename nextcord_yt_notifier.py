from re import search
from nextcord import ChannelType, Embed, Interaction, SlashOption
from nextcord.abc import GuildChannel
from os import getenv
from sqlite3 import connect
from nextcord.ext import commands, tasks
from dotenv import load_dotenv
from requests import get

bot = commands.Bot(command_prefix="?")
db = connect('youtubedata.db')

load_dotenv()
TOKEN=getenv('token')


@bot.event
async def on_ready():
    print("Bot Now Online!")

    #starting checking for vidoes everytime the bot's go online
    checkforvideos.start()

#checking for videos every minute


@tasks.loop(minutes=1)
async def checkforvideos():

  #printing here to show
  print("Now Checking!")

  #checking for all the channels in youtubedata.db file
  channel_ids = db.execute("SELECT channel_id FROM youtube").fetchall()
  for i in channel_ids:
    print(f"Now Checking For {i[0]}")

    #getting youtube channel's url
    channel = f"https://www.youtube.com/channel/{i[0]}"

    #getting html of the /videos page
    html = get(channel+"/videos").text

    #getting the latest video's url
    #put this line in try and except block cause it can give error some time if no video is uploaded on the channel
    try:
      latest_video_url = "https://www.youtube.com/watch?v=" + \
          search('(?<="videoId":").*?(?=")', html).group()
    except:
      continue

    #checking if url in youtubedata.db file is not equals to latest_video_url

    latest_video = db.execute(
        "SELECT latest_video FROM youtube WHERE channel_id = ?", (i[0],)).fetchone()[0]

    if not str(latest_video) == latest_video_url:

      #changing the latest_video_url
      db.execute("UPDATE youtube SET latest_video = ? WHERE channel_id = ?",
                 (latest_video_url, i[0],))
      db.commit()

      #getting the channel to send the message
      discord_channel_id = db.execute(
          "SELECT notifier_channel FROM youtube WHERE channel_id = ?", (i[0],)).fetchone()
      discord_channel = bot.get_channel(int(discord_channel_id[0]))

      #sending the msg in discord channel
      #you can mention any role like this if you want
      channel_name = db.execute(
          "SELECT channel_name FROM youtube WHERE channel_id = ?", (i[0],)).fetchone()

      mention = db.execute(
          "SELECT mention FROM youtube WHERE channel_id = ?", (i[0],)).fetchone()

      if mention[0] == "None":
        msg = f"{channel_name[0]} just uploaded a new video!\nCheck it out: {latest_video_url}"
      else:
        msg = f"{mention[0]}\n{channel_name[0]} just uploaded a new video!\nCheck it out: {latest_video_url}"
      #if you'll send the url discord will automaitacly create embed for it
      #if you don't want to send embed for it then do <{latest_video_url}>

      await discord_channel.send(msg)

#creating command to add more youtube accounds data in youtubedata.db file


@bot.slash_command()
@commands.has_permissions(manage_guild=True)
async def add_youtube_notification_data(ctx: Interaction, channel_id=SlashOption(description="Add a YouTube channel ID", required=True), channel_name=SlashOption(description="Add the name of the YouTube channel"), notifier_channel: GuildChannel = SlashOption(description="Which channel do you want the updates to be posted", channel_types=[ChannelType.text, ChannelType.news], required=True), mention=SlashOption(description="What role or ping should be mentioned?", required=False)):

  if mention == None:
    mention = "None"

  db.execute("INSERT OR IGNORE INTO youtube (channel_id, channel_name, latest_video, notifier_channel, mention) VALUES (?,?,?,?,?)",
             (channel_id, channel_name, 'None', notifier_channel.id, mention))
  db.commit()

  await ctx.send("Added Your Account Data!")

#you can also create this command if you ever want to stop notifying


@bot.slash_command(description="Stops notifying")
async def stop_notifying(ctx: Interaction):
  checkforvideos.stop()
  await ctx.send("Stoped Notifying")

#you can also create this command to start notifying but we're gonna do so that everytime the bot goes online it will automaitacly starts notifying


@bot.slash_command(description="Start notifying (on by default)")
async def start_notifying(ctx: Interaction):
  checkforvideos.start()
  await ctx.send("Now Notifying")

bot.run(TOKEN)
