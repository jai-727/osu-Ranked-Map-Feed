#Ranked Map osu!Feed V4
#By Jplayz

#Collecting all the libraries
import os
import time
import json

#These ones need to be installed using pip so we check for the user
try:
    from bs4 import BeautifulSoup
except:
    raise RuntimeError("bs4 required: pip install bs4")
    time.sleep(10)

try:
    import requests
    from discord_hooks import Webhook
    
except:
    raise RuntimeError("requests required: pip install requests")
    time.sleep(10)

#The RSS Feed to read from
URL = "https://osu.ppy.sh/beatmapsets/events?user=&types%5B%5D=rank"
OldSplit = ""
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
        'Webhook': NewWebhook
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

#---------------------Checking for a new ranked map-------------------------
    
    #Starts a loop to contantly check if a new map is present
    FeedCheck = True

    while FeedCheck == True:

        try:
            r = requests.get(URL)
            #Seeing if a new beatmap has been ranked, using the URLs as identifiers
            soup = BeautifulSoup(r.text, 'html.parser')
            soup2 = soup.find("script", {"id":"json-events"}) #Gets information from the first ranked beatmap on the page
            SoupSplit = list(soup2) #Splits it so we can get the URL of the beatmap
            GetInfo = json.loads(SoupSplit[0]) #This cleans up the data and turns it into a json file to work with
            beatMapSetID = GetInfo[0]['beatmapset']['id'] #This gets us the ID of the beatmap

        except:
            print("Connection Failed")
            time.sleep(60)

        if beatMapSetID != OldSplit:
            OldSplit = beatMapSetID
            FeedCheck = False

        else:
            time.sleep(45)

#------------------Getting Beatmap info via osu!API--------------------------

    #Generating API access URL for the map
    MapURL = "http://osu.ppy.sh/api/get_beatmaps?k={}&s={}".format(APIKey, beatMapSetID)
    print(MapURL)
    r = requests.get(MapURL)
    ArrayMapURL = list(r.json())
    #Getting all the mapper information here
    Mapper = ArrayMapURL[0]['creator']
    MapperID = ArrayMapURL[0]['creator_id']

    #Map info
    Title = ArrayMapURL[0]['title']
    Artist = ArrayMapURL[0]['artist']
    BPM = ArrayMapURL[0]['bpm']
    TotalLength = int(ArrayMapURL[0]['total_length'])


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
    GMFormat = "hybrid" #this helps reduce lines of code later on
    if len(gamemode) == 1:
        GMFormat = GM

        if GM == "osu!standard":
            if std >= 1:
                GMFormat2 = "● {} {} difficulties".format(str(std), GM)
            else:
                GMFormat2 = "● {} {} difficulty".format(str(std), GM)
            
        elif GM == "osu!taiko":
            if tko >= 1:
                GMFormat2 = "● {} {} difficulties".format(str(tko), GM)
            else:
                GMFormat2 = "● {} {} difficulty".format(str(tko), GM)
        elif GM =="osu!catch":
            if ctb >= 1:
                GMFormat2 = "● {} {} difficulties".format(str(ctb), GM)
            else:
                GMFormat2 = "● {} {} difficulty".format(str(ctb), GM)
        elif GM =="osu!mania":
            if man >= 1:
                GMFormat2 = "● {} {} difficulties".format(str(man), GM)
            else:
                GMFormat2 = "● {} {} difficulty".format(str(man), GM)

    elif len(gamemode) == 2:
        GM1 = ""
        GM2 = ""
        if std >= 1:
            GM1 = "osu!standard"
            val1 = std

        if tko >= 1:
            if len(GM1) != 0:
                GM2 = "osu!taiko"
                val2 = tko
            else:
                GM1 = "osu!taiko"
                val1 = tko

        if ctb >= 1:
            if len(GM1) > 3:
                GM2 = "osu!catch"
                val2 = ctb
            else:
                GM1 = "osu!catch"
                val1 = ctb

        if man >= 1:
            GM2 = "osu!mania"
            val2 = man

        GMFormat2 = """● {} {}
● {} {}""".format(val1, GM1, val2, GM2)


    elif len(gamemode) == 3:
        GM1 = ""
        GM2 = ""
        GM3 = ""
        
        if std > 1:
            GM1 = "osu!standard"
            val1 = std

        if tko > 1:
            if len(GM1) > 3:
                GM2 = "osu!taiko"
                val2 = tko
            else:
                GM1 = "osu!taiko"
                val1 = tko

        if ctb > 1:
            if len(GM2) > 3:
                GM3 = "osu!catch"
                val3 = ctb
            else:
                GM2 = "osu!catch"
                val2 = ctb

        if man > 1:
            GM3 = "osu!mania"
            val3 = man

        GMFormat2 = """● {} {}
● {} {}
● {} {}""".format(val1, GM1, val2, GM2, val3, GM3)

    elif len(gamemode) == 4:
        GMFormat2 = """● {} osu!standard diffs
● {} osu!taiko diffs
● {} osu!catch diffs
● {} osu!mania diffs""".format(std,tko,ctb,man)

#----------------Getting info into the right format--------------------------
    #Putting the title in a better format
    EmbedTitle = "{} - {}".format(Artist, Title)

    #Getting the banner
    Banner = "https://assets.ppy.sh/beatmaps/{}/covers/list.jpg".format(beatMapSetID)

    #Getting Map Length
    Minutes = str(int(TotalLength//60)) #Converts to a string for later use
    Seconds = str(int(TotalLength%60))

    #Prevents map from ending up looking like 2:2 if it is 2 minutes and 2 seconds long
    if len(Seconds) != 2:
        Seconds = "0"+Seconds

    #Creates string to be used in the message
    Length = Minutes+":"+Seconds

    #Creating a URL straight to the beatmap
    MapLink = "https://osu.ppy.sh/beatmapsets/{}".format(beatMapSetID)

#------------------Printing the values to check it works---------------------------

    print('New {} map by {}'.format(GMFormat, Mapper))
    print('{}'.format(EmbedTitle))
    print("""**BPM:** {}
**Song Length:** {}
**Containing:**
{}
""".format(BPM, Length, GMFormat2))

#------------------Programming and sending the embed itself------------------
        
    embed = Webhook(webhook, color=0xFFB6C1)
    embed.set_author(name='New {} map by {}'.format(GMFormat, Mapper), icon='https://a.ppy.sh/{}'.format(MapperID), url='https://osu.ppy.sh/users/{}'.format(MapperID))
    embed.set_title(title='**__{}__**'.format(EmbedTitle),url=MapLink)
    embed.set_thumbnail(Banner)
    embed.set_desc("""**BPM:** {}
**Song Length:** {}
**Containing:**
{}
""".format(BPM, Length, GMFormat2))
    embed.set_footer(text='Ranked!',ts=True,icon='https://hypercyte.s-ul.eu/W4GBjy0M')
    embed.post()
