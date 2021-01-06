import asyncio
import sys
from distest import TestCollector
from distest import run_interactive_bot, run_dtest_bot
from discord import Embed

test_collector = TestCollector()
created_channel = None

@test_collector()
async def combineTest(interface):
    await interface.assert_reply_contains("!combine earth rain", "earth+rain=Plant") #change args everytime
    await interface.assert_reply_contains("!combine zzzzz, zzzzz", "Invalid combination")
    
@test_collector()
async def suggestTest(interface):
    await interface.assert_reply_contains("!suggest fire earth Lava", "That combination already exists.")
    #await interface.assert_reply_contains("!suggest plant earth yard", "Someone has already suggested that. Use !voteup to vote for it.") #change args everytime
    await interface.assert_reply_contains("!suggest invalid valid noComb", "Succesfully suggested the combination invalid + valid = noComb") #change args everytime
    
#@test_collector()
#async def collectionTest(interface):
    #await interface.assert_reply_contains("!collection", "User Elemental-D#8317 created: ")
    
@test_collector()
async def unknownCmdTest(interface):
    await interface.assert_reply_contains("!hello", "Unknown command.")
    
@test_collector()
async def voteupTest(interface):
    await interface.assert_reply_contains("!voteup", "Syntax: voteup element1 element2 product")
    await interface.assert_reply_contains("!voteup invalid valid noComb", "You've already voted for this.") #change args according to suggestTest
    await interface.assert_reply_contains("!voteup fire earth Lava", "Nobody has suggested that combination. Perhaps you made a typo, or you meant to use the \"suggest\" command.")

@test_collector()
async def hintTest(interface):
    response=await interface.wait_for_reply("!hint")
    responseWords=response.content.split()[-2:]
    await interface.assert_reply_contains("!combine "+" ".join(responseWords),"+".join(responseWords))

@test_collector()
async def removeTest(interface):
    await interface.assert_reply_contains("!remove air fire", "sucessfully removed air+earth=Energy from csv file") #change args everytime





if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)
