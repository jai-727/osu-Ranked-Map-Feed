#Ranked Map osu!Feed V2
#By Jplayz

#Collecting all the libraries
import os
import time
import json

#These ones need to be installed using pip so we check for the user
try:
    import feedparser
except:
    raise RuntimeError("feedparser required: pip install feedparser")
    time.sleep(10)

try:
    import requests
    from discord_hooks import Webhook
    
except:
    raise RuntimeError("requests required: pip install requests")
    time.sleep(10)

#The RSS Feed to read from
RSS = "https://osu.ppy.sh/feed/ranked/"
OldRank = ""
#-----------------------------Checking Config File---------------------------

#Checks if a config file has been created
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

    #Dumps informfation into a file
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

#Starts the main program
while 0 < 1:

#---------------------Checking for a new update to the RSS Feed--------------
    
    #Starts a loop to contantly check if a new map is present
    FeedCheck = True

    while FeedCheck == True:
        #Try/Except to prevent the program crashing when internet connect is NOT present
        try:    
        #Using the maps as unique identifiers as each map has different ID
            ParsedRSS = feedparser.parse(RSS)
            RankedLink = ParsedRSS.entries[0].link
    
        except:
            print("Connection Failed")
            time.sleep(300)

        if RankedLink != OldRank:
            OldRank = RankedLink
            FeedCheck = False

        else:
            time.sleep(300)

#-----------------Gathering information from the RSS feed--------------------

    Title = ParsedRSS.entries[0].title #Map Title
    Author = ParsedRSS.entries[0].author #Mapper of song

    #Getting the map banner
    Desc = ParsedRSS.entries[0].description #The description contains the map banner as a part of it
    DescSplit = Desc.split("'") #There is a ' present in the split
    Banner = DescSplit[3]

#----------------------Getting User info through osu!Api----------------------
    
    #Generating the URL used to read from the API
    UserURL = "http://osu.ppy.sh/api/get_user?k={}&u={}".format(APIKey, Author)

    #Requests the URL
    r = requests.get(UserURL)
    #Turns it into a list
    AuthorProfile = list(r.json())
    #Gets the userID
    AuthorID = AuthorProfile[0]['user_id']

#------------------Getting Beatmap info via osu!API--------------------------

    #Generating API access URL for the map
    #This is similar to getting user info
    MapID = RankedLink.replace('http://osu.ppy.sh/s/','')
    MapURL = "http://osu.ppy.sh/api/get_beatmaps?k={}&s={}".format(APIKey, MapID)
    r = requests.get(MapURL)
    ArrayMapURL = list(r.json())
    #This gets the BPM of the map
    BPM = ArrayMapURL[0]['bpm']

    #Getting Map Length
    RawLength = int(ArrayMapURL[0]['total_length'])
    Minutes = str(int(RawLength//60)) #Converts to a string for later use
    Seconds = str(int(RawLength%60))

    #Prevents map from ending up looking like 2:2 if it is 2 minutes and 2 seconds long
    if len(Seconds) != 2:
        Seconds = "0"+Seconds

    #Creates string to be used in the message
    Length = Minutes+":"+Seconds    

#-----------------Getting the gamemodes avaliable to play--------------------               

    #Set all values to 0
    std = tko = ctb= man = 0

    #Getting all gamemodes avaliable
    for x in range(0,len(ArrayMapURL)):
        Mode = ArrayMapURL[x]['mode']

        if Mode == "0": #Standard
            std += 1

        if Mode == "1": #Taiko
            tko += 1

        if Mode =="2": #CTB
            ctb += 1

        if Mode == "3": #Mania
            man += 1

    #Create an array for the gamemodes
    gamemode = []
    gamemode = list(gamemode)

    #Adding each gamemode to the array if its present in mapset
    if man >= 1:
        gamemode.insert(0,"osu!mania")

    if ctb >= 1:
        gamemode.insert(0,"osu!catch")

    if tko >= 1:
        gamemode.insert(0,"osu!taiko")

    if std >= 1:
        gamemode.insert(0,"osu!standard")

    #This takes it out of a list and turns it into a usable format without the square brackets
    GM = ", ".join(gamemode)
    #Sets up format for if there is 1 gamemode present
    if len(gamemode) == 1:
        GMFormat = GM

        if GM == "osu!standard":
            if std > 1:
                GMFormat2 = "● {} {} difficulties".format(str(std), GM)
            else:
                GMFormat2 = "● {} {} difficulty".format(str(std), GM)
            
        elif GM == "osu!taiko":
            if tko > 1:
                GMFormat2 = "● {} {} difficulties".format(str(tko), GM)
            else:
                GMFormat2 = "● {} {} difficulty".format(str(tko), GM)
        elif GM =="osu!catch":
            if ctb > 1:
                GMFormat2 = "● {} {} difficulties".format(str(ctb), GM)
            else:
                GMFormat2 = "● {} {} difficulty".format(str(ctb), GM)
        elif GM =="osu!mania":
            if man > 1:
                GMFormat2 = "● {} {} difficulties".format(str(man), GM)
            else:
                GMFormat2 = "● {} {} difficulty".format(str(man), GM)
    
    elif len(gamemode) >= 2:
        GMFormat = 'Hybrid'
        GMFormat2 = """● {} osu!standard diffs
● {} osu!taiko diffs
● {} osu!catch diffs
● {} osu!mania diffs""".format(std,tko,ctb,man)

#------------------Programming and sending the embed itself------------------
        
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

