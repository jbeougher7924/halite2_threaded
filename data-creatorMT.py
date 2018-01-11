import os
import time
import argparse
import pp
import math
import sys

# original Script created by: Harrison Kinsley
# Threading added by: Jeff Beougher

# run this script from the .\Halite2_Python3_Windows\logs as python ..\data-creatorMT.py --runs # --workers # --cycles #
# you will need to create a logs directory as a child of the Halite2_Python3_Windows
# "#" needs to be an integer
# parellel python will need to be installed and a change to pp.py will need to be added  for python 3 on windows see pp forums for help
# https://www.parallelpython.com/component/option,com_smf/Itemid,29/topic,786.msg2038#msg2038
# https://www.parallelpython.com/

ship_requirement = 10
damage_requirement = 1000

# below are set will cli argumnets
number_of_runs = 1 #constant for number of run to do
number_of_workers = 0 # set to 0 if not set 0 will tell pp to use all available cpu's
number_of_cycles = 1 # constant for total run = runs * cycles

parser = argparse.ArgumentParser(description='Run halite 2 a number of times to create training data.')

parser.add_argument('--runs', default=1, nargs=1
                    , dest='runs_arg'
                    , help='how many times to run the halite2.exe'
                    )

parser.add_argument('--workers', default=0, nargs=1
                    , dest='workers_arg'
                    , help='how many cpu workers to create')

parser.add_argument('--cycles', default=1, nargs=1
                    , dest='cycles_arg'
                    , help='total runs = cycles * runs "used for cpu testing"')

args = parser.parse_args()

if args.runs_arg != 1:
    number_of_runs = int(args.runs_arg[0])

if args.workers_arg != 0:
    number_of_workers = int(args.workers_arg[0])

if args.cycles_arg != 1:
    number_of_cycles = int(args.cycles_arg[0])

print("Number of runs: " + str(number_of_runs))

def ensure_dir(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)

def makeThreadDir(num_threads):
    dir_name ="thread_folder_"
    for i in range(num_threads):
        ensure_dir(dir_name + str(i))

def get_ships(data):
    return int(data.split("producing ")[1].split(" ships")[0])


def get_damage(data):
    return int(data.split("dealing ")[1].split(" damage")[0])


def get_rank(data):
    return int(data.split("rank #")[1].split(" and")[0])


player_1_wins = 0
player_2_wins = 0

def do_run(num,player_1_wins,player_2_wins,damage_requirement,ship_requirement,root_dir):
    try:

       # uncomment to see which run the script is at
        #print("Currently on: " + str(num))

       # setup the working directory name
        dir_name = "thread_folder_" + str(num)
        working_des =  root_dir + "\\" + dir_name

        # set the working directory to .\thread_folder_"num" for halite.exe to process data in
        os.chdir(working_des)
        # Code from original script but no output is currently being used.
        if player_1_wins > 0 or player_2_wins > 0:
            p1_pct = round(player_1_wins / (player_1_wins + player_2_wins) * 100.0, 2)
            p2_pct = round(player_2_wins / (player_1_wins + player_2_wins) * 100.0, 2)
            print("Player 1 win: {}%; Player 2 win: {}%.".format(p1_pct, p2_pct))

        os.system('..\..\halite.exe -d "360 240" "python ..\..\MyBot-1.py" "python ..\..\MyBot-2.py" >>' + "data.gameout")

        # set this to true if you want each thread to write it own traininng data files.  Not needed if you run appendData.py which is really fast
        read_file = False
        if read_file:
            with open('data.gameout', 'r') as f:
                contents = f.readlines()
                CharlesBot1 = contents[-4]
                CharlesBot2 = contents[-3]
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
                print("c1 won")
                player_1_wins += 1
                if CharlesBot1_ships >= ship_requirement and CharlesBot1_dmg >= damage_requirement:
                    with open("c1_input.vec", "r") as f:
                        input_lines = f.readlines()
                    with open("train.in", "a") as f:
                        for l in input_lines:
                            f.write(l)

                    with open("c1_out.vec", "r") as f:
                        output_lines = f.readlines()
                    with open("train.out", "a") as f:
                        for l in output_lines:
                            f.write(l)

            elif CharlesBot2_rank == 1:
                print("c2 won")
                player_2_wins += 1
                if CharlesBot2_ships >= ship_requirement and CharlesBot2_dmg >= damage_requirement:
                    with open("c2_input.vec", "r") as f:
                        input_lines = f.readlines()
                    with open("train.in", "a") as f:
                        for l in input_lines:
                            f.write(l)

                    with open("c2_out.vec", "r") as f:
                        output_lines = f.readlines()
                    with open("train.out", "a") as f:
                        for l in output_lines:
                            f.write(l)

        time.sleep(2)
        return player_1_wins,player_2_wins
    except Exception as e:
        print(str(e))
        time.sleep(2)


# how many cycles to process used to test performance of physical cores to hyper threads
for i in range(number_of_cycles):
    # create a parellel python server tuple
    ppservers = ()

    # this defines how many workers to create max based on CPU it not set will be max cpu
    if number_of_workers > 0:
        ncpus = int(number_of_workers)
        # Creates jobserver with ncpus workers
        job_server = pp.Server(ncpus, ppservers=ppservers)
    else:
        # Creates jobserver with automatically detected number of workers
        job_server = pp.Server(ppservers=ppservers)

    print("Starting pp with %s workers" % job_server.get_ncpus())
    # get the root directory where the script is running
    root_dir = os.getcwd()

    # for threading purpose create a single directory to run the  os.system('..\..\halite.exe -d "360 240" "python ..\..\MyBot-1.py" "python ..\..\MyBot-2.py" >>' + "data.gameout") command in and will save all output to this dir
    for num in range(number_of_runs):
        dir_name = "thread_folder_" + str(num)
        working_des = root_dir + "\\" + dir_name
        #print(working_des)
        ensure_dir(dir_name)


    # create the job to run see parellel python for explanation
    jobs = [(input,job_server.submit(do_run, (input,player_1_wins,player_2_wins,damage_requirement,ship_requirement,root_dir ), (get_ships,get_damage,get_rank,ensure_dir ),
                             ("time","os" ))) for input in range(number_of_runs)]
    # now run each job
    for input, job in jobs:
        job()
        #print("Player 1 win: {0} Player 2 wins: {1}".format(player1,player2))

    # output the status of the completed jobs
    job_server.print_stats()

