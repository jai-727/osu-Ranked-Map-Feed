#Ranked Map osu!Feed V1
#Initial Release
import os
import time
import json
try:
    import feedparser
except:
    raise RuntimeError("feedparser required: pip install feedparser")
try:
    from discord_hooks import Webhook
    import requests
    time.sleep(10)
except:
    raise RuntimeError("discord_hooks required: pip install discord_hooks")
    time.sleep(10)

#The feed the program will be getting all its information from
RSS = "https://osu.ppy.sh/feed/ranked/"
OldRank = ""

#---------------------Checking for a new update to the RSS Feed--------------
def NewRanked():
    global RSS
    global RankedLink
    global OldRank
    global ParsedRSS

    #Using the maps links as unique identifiers
    ParsedRSS = feedparser.parse(RSS)
    RankedLink = ParsedRSS.entries[0].link
    if RankedLink != OldRank:
        OldRank = RankedLink
        RSSInfo()

    else:
        time.sleep(300)
        NewRanked()
    
#-----------------Gathering all the information needed from the RSS feed-------
def RSSInfo():
    global ParsedRSS
    global Title
    global Author
    global Banner

    Title = ParsedRSS.entries[0].title
    Author = ParsedRSS.entries[0].author

    #Getting the map banner
    Desc = ParsedRSS.entries[0].description
    DescSplit = Desc.split("'")
    Banner = DescSplit[3]

    ApiUser()


#----------------------Getting User info through osu!Api----------------------
def ApiUser():
    global APIKey
    global Author
    global AuthorID
    #Generating UserURl
    UserURL = "http://osu.ppy.sh/api/get_user?k={}&u={}".format(APIKey, Author)
    r = requests.get(UserURL)
    AuthorProfile = list(r.json())
    AuthorID = AuthorProfile[0]['user_id']

    ApiBeatmap()

#------------------Getting Beatmap info via osu!API--------------------------
def ApiBeatmap():
    global APIKey
    global RankedLink
    global BPM
    global Length
    global ArrayMapURL
    
    #Generating API access url for the map
    MapID = RankedLink.replace('http://osu.ppy.sh/s/','')
    MapURL = "http://osu.ppy.sh/api/get_beatmaps?k={}&s={}".format(APIKey, MapID)
    r = requests.get(MapURL)
    ArrayMapURL = list(r.json())
    BPM = ArrayMapURL[0]['bpm']
    RawLength = int(ArrayMapURL[0]['total_length'])
    Length = str(int(RawLength)//60)+":"+str(int(RawLength%60))
    Minutes = str(int(RawLength)//60)
    Seconds = str(int(RawLength)%60)
    if len(Seconds) != 2:
        Seconds = "0"+Seconds
    Length = Minutes+":"+Seconds
    
    Gamemodes()
    
#-----------------Getting the gamemodes avaliable to play--------------------
def Gamemodes():
    global ArrayMapURL   
    global GMFormat
    global GMFormat2

    #Sets all these values to 0
    std = taiko = ctb = mania = 0

    #Getting all gamemodes avaliable
    for x in range(0,len(ArrayMapURL)):
        Mode = ArrayMapURL[x]['mode']

    #Standard
        if Mode == "0":
            std += 1

    #Taiko
        if Mode == "1":
            taiko += 1

    #CTB
        if Mode =="2":
            ctb += 1

    #Mania
        if Mode == "3":
            mania += 1

    #Create an array for the gamemodes
    gamemode = []
    gamemode = list(gamemode)

    #Adding each gamemode to the array if its present in mapset
    if mania >= 1:
        gamemode.insert(0,"osu!mania")

    if ctb >= 1:
        gamemode.insert(0,"osu!catch")

    if taiko >= 1:
        gamemode.insert(0,"osu!taiko")

    if std >= 1:
        gamemode.insert(0,"osu!standard")

#Formatting the gamemodes for the embed            
    GM = ", ".join(gamemode)
    if len(gamemode) == 1:
        GMFormat = GM

        if GM == "osu!standard":
            if std > 1:
                GMFormat2 = "● {} {} difficulties".format(str(std), GM)
            else:
                GMFormat2 = "● {} {} difficulty".format(str(std), GM)
            
        elif GM == "osu!taiko":
            if taiko > 1:
                GMFormat2 = "● {} {} difficulties".format(str(taiko), GM)
            else:
                GMFormat2 = "● {} {} difficulty".format(str(taiko), GM)
        elif GM =="osu!catch":
            if ctb > 1:
                GMFormat2 = "● {} {} difficulties".format(str(ctb), GM)
            else:
                GMFormat2 = "● {} {} difficulty".format(str(ctb), GM)
        elif GM =="osu!mania":
            if mania > 1:
                GMFormat2 = "● {} {} difficulties".format(str(mania), GM)
            else:
                GMFormat2 = "● {} {} difficulty".format(str(mania), GM)
    
    elif len(gamemode) >= 2:
        GMFormat = 'Hybrid'
        GMFormat2 = """● {} osu!standard diffs
● {} osu!taiko diffs
● {} osu!catch diffs
● {} osu!mania diffs""".format(std,taiko,ctb,mania)

    EmbedMsg()
#------------------Programming and sending the embed itself------------------
def EmbedMsg():
    global Author
    global AuthorID
    global Title
    global Banner
    global RankedLink
    global Length
    global BPM
    global GMFormat
    global GMFormat2
    
    embed = Webhook(webhook, color=0x0098f9)
    embed.set_author(name='New {} map by {}'.format(GMFormat, Author), icon='https://a.ppy.sh/{}'.format(AuthorID), url='https://osu.ppy.sh/users/{}'.format(AuthorID))
    embed.set_title(title='**__{}__**'.format(Title),url=RankedLink)
    embed.set_thumbnail(Banner)
    embed.set_desc("""**BPM:** {}
**Song Length:** {}
**Containing:**
{}
""".format(BPM, Length, GMFormat2))
    embed.set_footer(text='Ranked!',ts=True,icon='https://hypercyte.s-ul.eu/W4GBjy0M')
    embed.post()

    NewRanked()
    
#-----------------------------Main Program---------------------------

#Checking for if a config file is present
if os.path.exists("config.txt"):
    print("Config file is present")

#If it doesn't, generate one
else:
    print("No config file found")
    NewKey = input("What is your osu!Api Key?:")
    NewWebhook = input("What is your Discord webhook?:")
    #Putting the information into an array
    data = {}  
    data[''] = []  
    data[''].append({  
        'Osu!Key': NewKey,
        'Webhook': NewWebhook,
    })

    #Dumps information into a file
    with open('config.txt', 'w') as outfile:  
        json.dump(data, outfile)
        outfile.close()

#Gathering all variables to be used later
with open('config.txt','r') as config_file:
    config = json.load(config_file)
    for info in config['']:
        APIKey = info['Osu!Key']
        webhook = info['Webhook']
config_file.close()


NewRanked()
    

    
    



