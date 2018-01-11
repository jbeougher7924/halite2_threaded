import os
import time
import argparse
import math
import sys

ship_requirement = 10
damage_requirement = 1000
# original code created by: Harrison Kinsley
# Updated  by: Jeff Beougher

# run this from the root directory .\Halite2_Python3_Windows "python appendData.py"
# the program handles the rest of the processing of data

def ensure_dir(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def makeTrainingFolder():
    working_des = os.getcwd() + "\\train_data"
    ensure_dir(working_des,)

def get_ships(data):
    return int(data.split("producing ")[1].split(" ships")[0])

def get_damage(data):
    return int(data.split("dealing ")[1].split(" damage")[0])


def get_rank(data):
    return int(data.split("rank #")[1].split(" and")[0])

def readContents(player1_cont, player2_cont, dir, trin, trout):
    CharlesBot1 = player1_cont
    CharlesBot2 =player2_cont
    print(CharlesBot1)
    print(CharlesBot2)

    CharlesBot1_ships = get_ships(CharlesBot1)
    CharlesBot1_dmg = get_damage(CharlesBot1)
    CharlesBot1_rank = get_rank(CharlesBot1)

    CharlesBot2_ships = get_ships(CharlesBot2)
    CharlesBot2_dmg = get_damage(CharlesBot2)
    CharlesBot2_rank = get_rank(CharlesBot2)

    print("Charles1 rank: {} ships: {} dmg: {}".format(CharlesBot1_rank, CharlesBot1_ships, CharlesBot1_dmg))
    print("Charles2 rank: {} ships: {} dmg: {}".format(CharlesBot2_rank, CharlesBot2_ships, CharlesBot2_dmg))
    if CharlesBot1_rank == 1:
        if CharlesBot1_ships >= ship_requirement and CharlesBot1_dmg >= damage_requirement:
            with open(dir + "\\c1_input.vec", "r") as f:
                # read the c1_input.vec file located in the current thread_folder_# and write its entire contents to trin "train.in"
               trin.write(f.read())

            with open(dir + "\\c1_out.vec", "r") as f:
                # read the c1_out.vec file located in the current thread_folder_# and write its entire contents to trout "train.out"
                trout.write(f.read())

    elif CharlesBot2_rank == 1:
        if CharlesBot2_ships >= ship_requirement and CharlesBot2_dmg >= damage_requirement:
            with open(dir + "\\c2_input.vec", "r") as f:
                # read the c1_input.vec file located in the current thread_folder_# and write its entire contents to trin "train.in"
                trin.write(f.read())

            with open(dir + "\\c2_out.vec", "r") as f:
                # read the c1_out.vec file located in the current thread_folder_# and write its entire contents to trout "train.out"
                trout.write(f.read())

def appedBadRunNumber(bad_run_at):
    with open(os.getcwd() + "\\train_data\\badrun.brf", "a") as f:
        # write out every bad run number to the badrun.brf file "brf bad run file" though prouncing it as barf does sound about right.
         f.write("Error on run: " + str(bad_run_at) + "\n")


def appendData(dir, currentRun, trin, trout):
    # keep track of the number of failed runs
    bad_run_count = 0

    try:
        print("\n\n\nCurrently on: " + str(currentRun))

        with open(dir + '\\data.gameout', 'r') as f:
            contents = f.readlines()
            # check if the last two lines of dead written to them if not then something went wrong during that run
            if "dead" in contents[-1] and "dead" in contents[-2]:
                CharlesBot1 = contents[-4]
                CharlesBot2 = contents[-3]
                # output the data to trin and trout
                readContents(CharlesBot1, CharlesBot2, dir, trin, trout)
            else:
                print("Bad file")
                # append the bad run the the badrun.brf file for later review
                appedBadRunNumber(currentRun)
                return bad_run_count

        # time.sleep(2) only needed if append data while opening and closing the file since the file is kept open data will be fine.
        return bad_run_count
    except Exception as e:
        print(str(e))
        time.sleep(2)
        return  bad_run_count

def logDirList(trin,trout):
    currentRun = 0
    # data will not be in order such as 1-2-3 but will write the correct runs to train.in and train.out.  such as thread_folder_0 thread_folder_1 thread_folder_10 thread_folder_2 thread_folder_20  thread_folder_300 so on this is due to serial reading of each folder
    # before reading the next
    for dir in listdir_fullpath(os.getcwd()+"\\logs"):
        appendData(dir, currentRun,trin,trout)
        # keep track of current run
        currentRun += 1

def openTrainingFiles(in_file, out_file):
    trin = open(os.getcwd() + "\\train_data\\" + in_file, "w")
    trout = open(os.getcwd() + "\\train_data\\" + out_file, "w")
    return trin, trout


# ensure the training folder exist
makeTrainingFolder()

# create two instance of training files to be passed to other function to quickly write data to train.in and train.out.
trin, trout = openTrainingFiles("train.in", "train.out")

# get a list of all the thread folder in the log directory and write the data to train.in and train.out
logDirList(trin, trout)

# close the files after appending data
trin.close()
trout.close()

