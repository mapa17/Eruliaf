#!/usr/bin/env python


###
# USAGE
###

#Call the script with ./[ScriptName] [PATH_TO_CSV_DATA_FILES] [ITERATION_START] [# of ITERATIONS] 
#e.g. ./createStatistics.py statsData/ 1 1  #Process iteration 1.csv
#e.g. ./createStatistics.py statsData/ 2 100 #process iteration 2.csv - 102s.csv

import os
import re
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')

def main():
    histFile = "hist_summary.csv"
    rScript = os.getcwd() + '/' + "Statistics.R"
    
    #logging.info('Generating Statistics: %s' % sys.argv )
    
    if(len(sys.argv) < 4):
        logging.error("Input error!")
        logging.error( usage() )
        sys.exit(1)
    
    dataDir = os.path.abspath( sys.argv[1] )
    workDir = dataDir + '/out'
    if( os.path.isdir   ( workDir ) == False ):
        os.mkdir(workDir) 
       
    itStart = int(sys.argv[2])
    nIterations = int(sys.argv[3]) 
    
    if (checkInput(dataDir, itStart, nIterations, rScript) == False):
        logging.error("Something was wrong with input arguments ...")
        sys.exit(1)
    
    #R CMD BATCH --slave "--args [STATS_FILE] [HISTORY_OUTPUT_FILE] [PREFIX] OR [HISTORY_FILE]" Statistics.R
    for i in range(nIterations):
        file = dataDir + '/' + str(itStart + i) + '.csv'
        args = "--args {0} {1} {2}".format(file, histFile, itStart +i )
        cmd = ["R", "CMD", "BATCH", "--slave", args, rScript ]
        print("Calling R script with {0}".format(cmd))
        call_command(cmd, workDir)
    
    #Now generate summary histogram
    args = "--args {0}".format( histFile )
    cmd = ["R", "CMD", "BATCH", "--slave", args, rScript ]
    call_command(cmd, workDir)
    print("Calling R script with {0}".format(cmd))    

def checkInput(dataDir, itStart, nIterations, rScript):
    
    if( os.path.isfile( rScript ) == False):
        logging.error("Could not find R Statistics script {0}", rScript)
        return False
    
    if( os.path.isdir(dataDir) == False):
        logging.error("{0} is no valid directory!".format(dataDir) )
        return False
    
    for i in range(nIterations):
        path = dataDir + "/" + str(itStart+i) + '.csv'
        if( os.path.isfile( path ) == False):
            logging.error("Statistics file {0} not found!".format(path) )
            return False
    
    return True
    

def usage():
    return ( "Usage: {0} [FOLDER_OF_STAT_FILES] [ITERATION_START] [# ITERATIONS]".format(sys.argv[0]) )
    
def call_command(command, cwd = os.getcwd() ):
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd = cwd
                               )
    stdout, stderr = process.communicate()
    
    return (process.returncode, stdout, stderr) 

if __name__ == "__main__":
    main()

