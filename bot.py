# bot.py
import os, csv, json
import random

import shutil
from tempfile import NamedTemporaryFile

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PREFIX = "!" #TODO: Make this not hard-coded.
THRESHOLD = 2 #the number of votes necessary to add a new element.

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

class CustomClient(discord.Client):
    combinations={}
    #Key: tuple of 2 elements "(element1, element2)"
    #Value: Product
    async def on_ready(self):
        print(f'{client.user} has connected to Discord!')
        guild = discord.utils.get(client.guilds, name=GUILD)
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )
        
    #async def on_member_join(self, member):
        #print("New member joined.")
        #channel = client.get_channel(762006658611937280)
        #for channel in member.guild.channels:
         #   if(channel.name == "general"):
        #await channel.send(f"Welcome to the server {member.mention}!")
        #await member.create_dm()
        #await member.dm_channel.send(f'Welcome to my Discord Server {member.mention}!')
        
    async def on_connect(self):
        print("on_connect")
        with open("combinations.csv","r") as combinationsFile:
            combinationsreader=csv.reader(combinationsFile)
            for combination in combinationsreader:
                self.combinations[(combination[1],combination[2])]=combination[0]
    
    async def on_message(self,message):
        content=message.content
        channel=message.channel
        if(content.startswith(PREFIX)):
            args=content.split(" ")
            command=args[0][len(PREFIX):]#remove the prefix from the command
            #print(args)
            if(command=="combine"):
                if((args[1],args[2]) in self.combinations):
                    print("user "+str(message.author)+" successfully combined "+args[1]+" with "+args[2]+" to get "+self.combinations[(args[1],args[2])])
                    await channel.send(args[1]+"+"+args[2]+"="+self.combinations[(args[1]),(args[2])])
                    with open(f"combinations_{message.author}.txt", "a+") as userCombFile:
                        userCombFile.seek(0)
                        for element in userCombFile.readlines():
                            if element.strip("\n") == self.combinations[(args[1]),(args[2])]:
                                await channel.send("(You already created this element.)")
                                break
                        else:
                            userCombFile.write(self.combinations[(args[1]),(args[2])]+"\n")
                else:
                    print("user "+str(message.author)+" made an invalid combination")    
                    await channel.send("Invalid combination")
            elif(command=="remove"):
                with open("admin.txt","r+") as adminFile:
                    adminFile.seek(0)
                    for element in adminFile.readlines():
                        if element.strip("\n") == str(message.author):
                            if((args[1],args[2]) in self.combinations):
                                print("user "+str(message.author)+" successfully removed"+args[1]+" with "+args[2]+" to get "+self.combinations[(args[1],args[2])])
                                await channel.send("sucessfully removed "+args[1]+"+"+args[2]+"="+self.combinations[(args[1]),(args[2])]+" from csv file")
                                new=open('combinations.csv','r+')
                                old=open('newCsv.csv','w+')
                                reader=csv.reader(new)
                                writer=csv.writer(old)
                                for row in reader:
                                    if ((row[0] !=self.combinations[(args[1],args[2])])):
                                        writer.writerow(row)
                                new.close()
                                old.close()
                                shutil.move('newCsv.csv','combinations.csv')
            elif(command=="hint"):
                combFile=open('combinations.csv','r+')
                userFile=open(f"combinations_{message.author}.txt",'r+')
                reader = csv.reader(combFile)
                count=1
                while(count >= 1):
                    chosen_row = random.choice(list(reader))
                    for element in userFile.readlines():
                        if chosen_row[0] == element.strip("\n"):
                            count=count+1
                    if count == 1:
                        count=-1
                        print("user can try this combination"+chosen_row[1]+ " " + chosen_row[2])
                        await channel.send("try this combination: "+ chosen_row[1]+" " +chosen_row[2])
            elif(command=="suggest"):
                if(len(args)<4):
                    await channel.send("Syntax: suggest element1 element2 product")
                elif((args[1],args[2]) in self.combinations):
                    await channel.send("That combination already exists.")
                else:                      
                    with open("suggestions.json","r") as suggestionsFile:
                        for line in suggestionsFile:
                            cur_suggestion=json.loads(line)
                            if(cur_suggestion["factors"]==[args[1],args[2]] and cur_suggestion["product"]==args[3]):
                                await channel.send("Someone has already suggested that. Use !voteup to vote for it.")
                                return
                    suggestion = {
                        "product":args[3],
                        "factors":(args[1],args[2]),
                        "upvotes":[str(message.author)],
                        "downvotes":{}
                    }
                    with open("suggestions.json","a") as suggestionsFile:
                        suggestionsFile.write(json.dumps(suggestion)+"\n")
                    await channel.send("Succesfully suggested the combination "+args[1]+" + "+args[2]+" = "+args[3])
            elif(command=="voteup"):
                if(len(args)<4):
                    await channel.send("Syntax: voteup element1 element2 product")
                suggestions=[]
                suggestion = {}
                suggested=False
                with open("suggestions.json","r") as suggestionsFile:
                    for line in suggestionsFile:
                        cur_suggestion=json.loads(line)
                        if(not(suggested) and cur_suggestion["factors"]==[args[1],args[2]] and cur_suggestion["product"]==args[3]):
                            if(str(message.author) not in cur_suggestion["upvotes"]):
                                cur_suggestion["upvotes"].append(str(message.author))
                                suggestion=cur_suggestion
                            else:
                                await channel.send("You've already voted for this.")
                                return
                            suggested=True
                        else:
                            suggestions.append(cur_suggestion)
                if(not(suggested)):
                    await channel.send("Nobody has suggested that combination. Perhaps you made a typo, or you meant to use the \"suggest\" command.")
                    return
                await channel.send("Succesfully upvoted. Currently there are "+str(len(suggestion["upvotes"]))+" upvotes, out of a necessary "+str(THRESHOLD)+" to get added.")
                if(len(suggestion["upvotes"])>=THRESHOLD):
                    self.combinations[(args[1],args[2])]=args[3]
                    with open("combinations.csv","a") as outputFile:#"a" means "open for appending"
                        combinationswriter=csv.writer(outputFile)
                        combinationswriter.writerow((args[3],args[1],args[2]))
                        await channel.send("Combination created! "+args[1]+" + "+args[2]+" = "+args[3])                
                else:
                    suggestions.insert(0,suggestion)#insert in front because newer suggestions are more likely to get more votes sooner.
                with open("suggestions.json","w") as suggestionsFile:
                    for suggestion in suggestions:
                        suggestionsFile.write(json.dumps(suggestion)+"\n")
            elif(command=="upcoming"):
                
                total=65535#how many suggestions the user wants to see
                if(len(args)>1):
                    try:
                        total=int(args[1])
                    except Exception:
                        await channel.send("Syntax: upcoming [number]")
                count=total
                with open("suggestions.json","r") as suggestionsFile:
                    for line in suggestionsFile:
                        suggestion = json.loads(line)
                        if(len(suggestion["upvotes"])>=THRESHOLD/2):
                            await channel.send("Upcoming suggestion: "+suggestion["factors"][0]+" + "+suggestion["factors"][1]+" = "+suggestion["product"])
                            count-=1
                            if(count <= 0):
                                return
                if(total==count):
                    with open("suggestions.json","r") as suggestionsFile:
                        for line in suggestionsFile:
                            suggestion = json.loads(line)
                            await channel.send("Upcoming suggestion: "+suggestion["factors"][0]+" + "+suggestion["factors"][1]+" = "+suggestion["product"])
                            count-=1
                            if(count <= 0):
                                return
                if(total==count):
                    await channel.send("No upcoming suggestions")
            elif(command == "collection"):
                numElementsCreated = 0
                totalNumElements = 0
                with open(f"combinations_{message.author}.txt", "r") as userCombFile:
                    await channel.send(f"User {message.author} created: ")
                    for element in userCombFile.readlines():
                        numElementsCreated += 1
                        element = element.strip("\n")
                        await channel.send(element)
                with open("combinations.csv", "r") as combinationsFile:
                    for el in combinationsFile.readlines():
                        totalNumElements += 1
                percentElementsCreated = (numElementsCreated/totalNumElements) * 100
                await channel.send("Percentage of total elements created: {:0.2f}%".format(percentElementsCreated))
            else:
                await channel.send("Unknown command.")



                      

client = CustomClient()
client.run(TOKEN)
