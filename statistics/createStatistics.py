#!/usr/bin/env python


import os
import re
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')

def main():
    #logging.info('Generating Statistics: %s' % sys.argv )
    
    if(len(sys.argv) < 4):
        logging.error("Input error!")
        logging.error( usage() )
        sys.exit(1)
    
    dataDir = sys.argv[1]
    itStart = int(sys.argv[2])
    nIterations = int(sys.argv[3])
    
    if (checkInput(dataDir, itStart, nIterations) == False):
        logging.error("Something was wrong with input arguments ...")
        sys.exit(1)
    
    #R CMD BATCH --slave "--args [STATS_FILE] [HISTORY_OUTPUT_FILE] [PREFIX] OR [HISTORY_FILE]" Statistics.R
    for i in range(nIterations):
        file = dataDir + '/' + str(itStart + i) + '.csv'
        args = "--args {0} {1} {2}".format(file, "hist_summary.csv", itStart +i )
        cmd = ["R", "CMD", "BATCH", "--slave", args, "Statistics.R" ]
        print("Calling with arguments {0}".format(cmd))
        call_command(cmd)
    
    

def checkInput(dataDir, itStart, nIterations):
    if( os.path.isdir(dataDir) == False):
        logging.error("{0} is no valid directory!".format(dataDir) )
    
    for i in range(nIterations):
        path = dataDir + "/" + str(itStart+i) + '.csv'
        if( os.path.isfile( path ) == False):
            logging.error("Statistics file {0} not found!".format(path) )
            return False
    

def usage():
    return ( "Usage: {0} [FOLDER_OF_STAT_FILES] [ITERATION_START] [# ITERATIONS]".format(sys.argv[0]) )
    
def call_command(command):
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    return (process.returncode, stdout, stderr) 

if __name__ == "__main__":
    main()

