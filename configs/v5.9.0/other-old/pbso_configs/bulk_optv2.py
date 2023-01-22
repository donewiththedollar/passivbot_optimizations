# sample run : 
# python3 bulk_optimisation.py bulk_optimisation.json   
# coin by coin
#       will create a fake configuration in : ../configs/optimize/_*.hjson
#       will run the harmony optimisation
#       will use choose the good config with inspect_opt_results.py (PAD 0.02)
#       then backtest the config
#       After, save the config in configs/live/PBSO/COIN_DIRECTORY/config.json (the best config)
#       After, save the backtest result in configs/live/PBSO/COIN_DIRECTORY/result.txt (the Backtest of best config)

# @TODO : Create a Lock, to avoid multiples run at same time.
# @TODO : in high level folder, add the difference between, recursive or static grid (or neat)
# @TODO : Where to add the PNL 
# @TODO : create a parameter to only backtest a strategy ?

import argparse
from hashlib import md5
import os
from pickle import FALSE, TRUE
from textwrap import indent
import hjson
import subprocess
import glob
import shutil
import re
import time
import datetime
from datetime import timedelta
import glob
import hashlib

# testing_mode = True
testing_mode = False

if testing_mode:
    print('Testing mode ACTIVATED')


def convertStringPercent(string):
    if not isinstance(string, str):
        return string
    if string[-1] != "%":
        return string
    prct = float(string[0:-1])

    return prct / 100

def convertHJsonToHumanReadable(filename):
    # Read in the file
    with open(filename, 'r') as file :
        filedata = file.read()

    # Replace the target string
    filedata = re.sub('\[\r?\n[ ]*', '[', filedata ) 
    filedata = re.sub('[ ]*\r?\n[ ]*\]', ']', filedata ) 
    filedata = re.sub('([0-9]+),\r?\n[ ]*([0-9]+)', r'\1,\2', filedata ) 

    # Write the file out again
    with open(filename, 'w') as file:
        file.write(filedata)




# run timing
e = datetime.datetime.now()
starting_script = e.strftime("%Y%m%d%H%M%S")

# ------------------------------------------------------------
#             Manage command line parameters  
# ------------------------------------------------------------
parser = argparse.ArgumentParser( description="This script will loop on coins to optimize and backtest",
epilog="",
usage="python3 " + __file__ + " ./bulk_opt.hjson "
)

parser.add_argument("bo_config", type=str, help="file path to the bulk optimize config (hjson)")
args = parser.parse_args()
if not os.path.exists(args.bo_config) :
    print("bo_config doesn't exist")
    exit()

# ------------------------------------------------------------
#             Load  Bulk config  
# ------------------------------------------------------------
bo_config = hjson.load(open(args.bo_config, encoding="utf-8"))
# check exist configs
harmony_config_file = ""
if not os.path.exists(bo_config['harmony_config_file']):
    exit("ERROR : harmony_config_file doesn't exist")
else:
    harmony_config_file = bo_config['harmony_config_file'] = os.path.realpath(bo_config['harmony_config_file'])

backtest_config_file = ""
if not os.path.exists(bo_config['backtest_config_file']):
    exit("ERROR : backtest_config_file doesn't exist")
else:
    backtest_config_file = bo_config['backtest_config_file'] = os.path.realpath(bo_config['backtest_config_file'])


# -----------------------------------------------------------
#              Generate the name of the harmony config name (only name)
# -----------------------------------------------------------
md5_name = hashlib.md5(hjson.dumps(bo_config).encode('utf-8')).hexdigest()
harmony_config = os.path.dirname(bo_config['harmony_config_file']) + '/_harmony_' + md5_name + ".hjson"
print("We will use this auto generated and OVERIDED config : ", harmony_config)

# -----------------------------------------------------------
#              Generate the name of the backtest_config config name (only name)
# -----------------------------------------------------------
backtest_config = os.path.dirname(bo_config['backtest_config_file']) + '/_backtest_' + md5_name + ".hjson"
print("We will use this auto generated and OVERIDED config : ", backtest_config)

# -----------------------------------------------------------
#              Generate start_date & end_date 
# -----------------------------------------------------------
if ('nb_days' in bo_config['override_bt_and_opti']):
    today = datetime.date.today()
    bo_config['override_bt_and_opti']['start_date'] = str(today - timedelta(days=bo_config['override_bt_and_opti']['nb_days']))
    bo_config['override_bt_and_opti']['end_date'] = str(today)

print('Period :', bo_config['override_bt_and_opti']['start_date'], ' to ', bo_config['override_bt_and_opti']['end_date'])


# -----------------------------------------------------------
#              Generate the new backtest config OVERRIDE IT
# -----------------------------------------------------------
new_config_hjson = hjson.load(open(bo_config['backtest_config_file'], encoding="utf-8"))

# override from "override_bt_and_opti"
for key in bo_config['override_bt_and_opti']:
    if (key in new_config_hjson):
        new_config_hjson[key]  = bo_config['override_bt_and_opti'][key]

with open(backtest_config, 'w') as outfile:
    hjson.dumpJSON(new_config_hjson, outfile, indent=True)

convertHJsonToHumanReadable(backtest_config)


# -----------------------------------------------------------
#              Generate the new harmony config OVERRIDE IT
# -----------------------------------------------------------
new_config_hjson = hjson.load(open(bo_config['harmony_config_file'], encoding="utf-8"))
new_config_hjson['symbols'] = ['NOTSET']

# override from "override_bt_and_opti"
for key in bo_config['override_bt_and_opti']:
    if (key in new_config_hjson):
        new_config_hjson[key]  = bo_config['override_bt_and_opti'][key]

#strategies group, not main config
bo_strat_groups = ["strategies_long_and_short","strategies_long","strategies_short"]


# override basic setting in "override_harmony_config"
for key in bo_config['override_harmony_config']:
    if (key in bo_strat_groups):
        continue
    if (key in new_config_hjson):
        new_config_hjson[key]  = bo_config['override_harmony_config'][key]

# override section "strategies_long_and_short" "strategies_long" "strategies_short"
pb_grids = ['bounds_static_grid', 'bounds_recursive_grid', 'bounds_neat_grid']

for bo_strat_group in bo_strat_groups: # loop in strategie bulk group 
    if bo_strat_group in bo_config['override_harmony_config']: # if group exist
        for key in bo_config['override_harmony_config'][bo_strat_group]: # loop on key / value of the group
            value = bo_config['override_harmony_config'][bo_strat_group][key]

            # manage percent string value possible
            if isinstance(value, str):
                value = convertStringPercent(value)
            if isinstance(value, list):
                for k, v in enumerate(value):
                    if isinstance(v, str):
                        value[k] = convertStringPercent(v)

            for grid in pb_grids: # loop on the passivbot possible grids
                if (grid in new_config_hjson): # grid finded
                    if bo_strat_group in ["strategies_long_and_short","strategies_long"]: # For short ?
                        new_config_hjson[grid]['long'][key] = value # update value
                    if bo_strat_group in ["strategies_long_and_short","strategies_short"]: # For long ?
                        new_config_hjson[grid]['short'][key] = value # update value

with open(harmony_config, 'w') as outfile:
    hjson.dumpJSON(new_config_hjson, outfile, indent=True)

convertHJsonToHumanReadable(harmony_config)


# ------------------------------------------------------------
#             Name of this bulk version  
# ------------------------------------------------------------
bulk_version = input('How to name this bulk ? ')
bulk_version = re.sub('[^a-zA-Z0-9_.]', '_', bulk_version)

print("Name of the subdirectory => ", bulk_version)


# ------------------------------------------------------------
#             CREATE THE configs/live/PBSO/ directory  
# ------------------------------------------------------------
pbso_dir  = os.path.realpath("./../configs/live/PBSO/"+bulk_version)
if not os.path.exists(pbso_dir):
     os.makedirs(pbso_dir)

# ------------------------------------------------------------
#             End if testing mode  
# ------------------------------------------------------------
if testing_mode:
    print('END Because Testing ENABLED')
    exit()

try:
    # -----------------------------------------------------------
    #              Load coin List
    # -----------------------------------------------------------
    print("Coin List :")
    coin_list = bo_config['coin_list']
    for a_coin in coin_list:
        print(a_coin['coin'] + " / Harmony start config : " +  
                (a_coin['harmony_starting_config'] if 'harmony_starting_config' in a_coin else "None")
            )

    if len(coin_list) == 0 :
        exit('ERROR : No coin finded with the program arguments.')



    # -----------------------------------------------------------
    #              Loop on coin 
    # -----------------------------------------------------------
    for coin in coin_list:
        print('Start Optimize loop', coin['coin'])

        #python3 harmony_search.py -o config --oh -sd startdat -ed enddate -s SYMBOL
        command_line = [
                                "python3", "harmony_search.py", 
                                "-o", harmony_config,
                                "-s", coin['coin'],
                                "-b", backtest_config,
                             #   "-t configs/live/neat_grid.json"
                                ]
        if ('harmony_starting_config' in coin):

            coin['harmony_starting_config'] = coin['harmony_starting_config'].replace('%COIN%', coin['coin'])

            if not os.path.exists(coin['harmony_starting_config']):
                print("Sorry but this file doesn't exist : " , coin['harmony_starting_config'])
                exit()

            coin['harmony_starting_config'] = os.path.realpath(coin['harmony_starting_config'])
            print('harmony_starting_config renamed in :', coin['harmony_starting_config'])

            command_line.append("-t")
            command_line.append(coin['harmony_starting_config'])    

        if bo_config['override_bt_and_opti']['ohlc']:
            command_line.append("-oh") 

        print(' '.join(command_line))
        
        try:
            subprocess.run(command_line, cwd="..")
            # print("othing")
        except subprocess.TimeoutExpired:
            print('Timeout Reached  seconds)')



        # find the last file all_results.txt (must be the new one created)
        list_of_files = glob.glob("./../results_harmony_*/*_" + coin['coin'].upper() + "/all_results.txt", recursive=True)
        latest_file = max(list_of_files, key=os.path.getctime)
        latest_file = os.path.realpath(latest_file)

        print("Last result file is : ", latest_file)

        #         Findd the best strategy with inspect_opt_results.py
        #                     -p 0.02
        #                             [PAD around 0.02]

        #python3 inspect_opt_results.py results_harmony_search_recursive_grid/2022-07-10T18-32-36_XRPUSDT/all_results.txt -p 0.02 -d
        command_line = [
                                "python3", "inspect_opt_results.py", 
                                latest_file,
                                "-p", "0.02",  
                                "-d"
                                ]
        try:
            print(' '.join(command_line))
            subprocess.run(command_line, cwd="..")
        except subprocess.TimeoutExpired:
            print('Timeout Reached  seconds)')

        dir_to_save = pbso_dir + "/" + coin['coin'] + "_" + starting_script + "_" + md5_name[0:5] + "/"
        if not os.path.exists(dir_to_save):
            os.makedirs(dir_to_save)

        best_config_dest = dir_to_save + "/config.json"
        shutil.copy(os.path.dirname(latest_file) + "/all_results_best_config.json", best_config_dest)

        command_line = [
                                    "python3", "backtest.py", 
                                    "-s", coin['coin'],
                                    "-b", backtest_config
                                    ]

        if bo_config['override_bt_and_opti']['ohlc']:
            command_line.append("-oh") 
        
        command_line.append(best_config_dest) 


        try:
            print(' '.join(command_line))
            subprocess.run(command_line, cwd="..")
        except subprocess.TimeoutExpired:
            print('Timeout Reached  seconds)')


        #         Copy the backtest configuration
        #             change the config 
        #                 start_date: => now lower than 900 days [nb_days]
        #                   end_date: => now 
        #         run the backtest with this configs
        #         Copy the strategy in 
        #             /configs/live/PBSO/900d_1000i_0.02,0.4gs_0.02,0.4mm_0.02,0.4mr/config.json
        #         Copy the backtest result in 
        #             /configs/live/PBSO/900d_1000i_0.02,0.4gs_0.02,0.4mm_0.02,0.4mr/result.txt

        # find the last file  (must be the new one created)
        list_of_files = glob.glob("./../backtests/*/*" + coin['coin'].upper() + "*/plots/*/backtest_result.txt", recursive=True)
        latest_result = max(list_of_files, key=os.path.getctime)
        latest_result = os.path.realpath(latest_result)

        shutil.copy(latest_result, dir_to_save + '/result.txt')


        other_files_to_copy = [
                            'balance_and_equity_sampled_long.png',
                            'balance_and_equity_sampled_short.png',
                            'whole_backtest_long.png',
                            'whole_backtest_short.png',
        ]

        for src in other_files_to_copy:
            src_file = os.path.dirname(latest_result) + '/' + src
            if os.path.exists(src_file):
                shutil.copy(src_file, dir_to_save + '/' + src)
        
        shutil.copy(harmony_config, dir_to_save + '/')
        shutil.copy(backtest_config, dir_to_save + '/')
        shutil.copy(args.bo_config, dir_to_save + '/')

    print('All Results files are stored in this directory : ', pbso_dir)

except KeyboardInterrupt:
    print("End of process")
finally:
    print("Deleting unused files")
    os.unlink(harmony_config)
    os.unlink(backtest_config)


