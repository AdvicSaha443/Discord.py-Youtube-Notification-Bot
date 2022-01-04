import json
import requests
import re
import os

from discord.ext import commands, tasks

bot = commands.Bot(command_prefix = "?")

@bot.event
async def on_ready():
    print("Bot Now Online!")

    #starting checking for vidoes everytime the bot's go online
    checkforvideos.start()

#checking for vidoes every 30 seconds
#you can check for vidoes every 10 seconds also but i would prefer to keep 30 seconds
@tasks.loop(seconds=30)
async def checkforvideos():
  with open("youtubedata.json", "r") as f:
    data=json.load(f)
  
  #printing here to show
  print("Now Checking!")

  #checking for all the channels in youtubedata.json file
  for youtube_channel in data:
    print(f"Now Checking For {data[youtube_channel]['channel_name']}")
    #getting youtube channel's url
    channel = f"https://www.youtube.com/channel/{youtube_channel}"

    #getting html of the /videos page
    html = requests.get(channel+"/videos").text

    #getting the latest video's url
    #put this line in try and except block cause it can give error some time if no video is uploaded on the channel
    try:
      latest_video_url = "https://www.youtube.com/watch?v=" + re.search('(?<="videoId":").*?(?=")', html).group()
    except:
      continue

    #checking if url in youtubedata.json file is not equals to latest_video_url
    if not str(data[youtube_channel]["latest_video_url"]) == latest_video_url:

      #changing the latest_video_url
      data[str(youtube_channel)]['latest_video_url'] = latest_video_url

      #dumping the data
      with open("youtubedata.json", "w") as f:
        json.dump(data, f)

      #getting the channel to send the message
      discord_channel_id = data[str(youtube_channel)]['notifying_discord_channel']
      discord_channel = bot.get_channel(int(discord_channel_id))

      #sending the msg in discord channel
      #you can mention any role like this if you want
      msg = f"@everone {data[str(youtube_channel)]['channel_name']} Just Uploaded A Video Or He is Live Go Check It Out: {latest_video_url}"
      #if you'll send the url discord will automaitacly create embed for it
      #if you don't want to send embed for it then do <{latest_video_url}>

      await discord_channel.send(msg)
      
#creating command to add more youtube accounds data in youtubedata.json file
#you can also use has_role if you don't want to allow everyone to use this command
@bot.command()
@commands.has_role("Youtube")
async def add_youtube_notification_data(ctx, channel_id: str, *, channel_name: str):
  with open("youtubedata.json", "r") as f:
    data = json.load(f)
  
  data[str(channel_id)]={}
  data[str(channel_id)]["channel_name"]=channel_name
  data[str(channel_id)]["latest_video_url"]="none"

  #you can also get discord_channe id from the command 
  #but if the channel is same then you can also do directly
  data[str(channel_id)]["notifying_discord_channel"]="890293434856914964"

  with open("youtubedata.json", "w") as f:
    json.dump(data, f)

  await ctx.send("Added Your Account Data!")

#you can also create this command if you ever want to stop notifying
@bot.command()
@commands.has_role("Youtube")
async def stop_notifying(ctx):
  checkforvideos.stop()
  await ctx.send("Stoped Notifying")

#you can also create this command to start notifying but we're gonna do so that everytime the bot goes online it will automaitacly starts notifying
@bot.command()
@commands.has_role("Youtube")
async def start_notifying(ctx):
  checkforvideos.start()
  await ctx.send("Now Notifying")
