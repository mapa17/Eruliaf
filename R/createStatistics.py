#!/usr/bin/env python


###
# USAGE
###

#Call the script with ./[ScriptName] [PATH_TO_CSV_DATA_FILES] [WORK_DIR] [SUMMARY_DIR] [PREFIX] [# of ITERATIONS] [NUM_THREADS]
#e.g. ./createStatistics.py statsData/ 1 1  #Process iteration 1.csv
#e.g. ./createStatistics.py statsData/ 2 100 #process iteration 2.csv - 102s.csv

import os
import re
import sys
import subprocess
import logging
import threading
import queue

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')

#rScript = os.path.abspath("./Statistics.R")
#rScript = "/work/Eigene/uni/Erasmus/Thesis/Eruliaf/statistics/Statistics.R"
#dataDir = ""
#workDir = ""
#statsSummary = ""  
#prefix = ""
#nIterations = 0 
#nThreads = 0

q = queue.Queue()

def worker():
    while(q.empty() == False):
        i = q.get()
        
        #Generate tables using R script file
        file2 = dataDir + '/' + prefix + str(i) + '.csv'
        scenario_summary2 = workDir + '/' + prefix + str(i) + '_summary.csv'
        args2 = "Rscript {} {} {} {} {}".format( rScript, file2, workDir, scenario_summary2, prefix + str(i))
        cmd2 = args2.split(" ")
        logging.debug("Calling R script with {} in {}".format(cmd2, workDir))
        call_command(cmd2, cwd=workDir)
    
        #Generate summary pdf for this scenario out of the different png files
        args2 = "convert {} {}".format( prefix + str(i) + "_*.png", prefix + str(i) + "_summary.pdf" )
        cmd2 = args2.split(" ")
        logging.debug("Calling convert with {0}".format(cmd2))
        call_command(cmd2, workDir)
        
        q.task_done()

def main():
    logging.info('Being called to generate Statistics: {0}'.format(sys.argv) )
    
    #print('Being called to generate Statistics: {0}'.format(sys.argv) )
    #sys.exit(0)
    
    if(len(sys.argv) != 7):
        logging.error("Input error!")
        logging.error( usage() )
        sys.exit(1)
    
    #Make variables global so that they can be accessed in worker function
    #rScript = os.path.abspath("./Statistics.R")
    global rScript
    global dataDir
    global workDir
    global statsSummaryDir  
    global prefix
    global nIterations 
    global nThreads
    
    rScript = os.path.abspath("./Statistics.R")
    #rScript = "/work/Eigene/uni/Erasmus/Thesis/Eruliaf/statistics/Statistics.R"
    dataDir = os.path.abspath( sys.argv[1] )
    workDir = os.path.abspath( sys.argv[2] )
    if( os.path.isdir   ( workDir ) == False ):
        os.mkdir(workDir) 
    statsSummaryDir = os.path.abspath( sys.argv[3] )  
    prefix = sys.argv[4]
    nIterations = int(sys.argv[5]) 
    nThreads = int(sys.argv[6])
    statsSummaryFile = os.path.dirname(statsSummaryDir) + "/" + prefix + "summary.csv"
    
    if (checkInput(dataDir, prefix, nIterations, rScript) == False):
        logging.error("Something was wrong with input arguments ...")
        sys.exit(1)

    for i in range(nIterations):
        q.put(i, False)
    
    threadList = []
    #Use the worker function
    for i in range(nThreads):
        threadList.append( threading.Thread(target=worker) )
        threadList[-1].daemon = True #Make them daemon threads so we dont care about cleaning up
        threadList[-1].start()

    logging.debug("Waiting for all simulations to finish!")
    q.join()
       
    #Unify the different scenario summaries
    args = "/bin/cat {} > {}".format( workDir+"/" + prefix + "*_summary.csv", statsSummaryFile)
    #args = "cat {} > {}".format( "*.csv", statsSummaryDir)
    #cmd = args.split(" ")
    cmd = args #Execution will hang if cmd is passed as array!
    logging.debug("Calling subprocess with {0}".format(cmd))
    
    #(rV,out,err) = call_command(cmd, workDir )
    #Dont use normal call_command because we dont want to redirect std-output to file!
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, cwd = workDir , shell=True) #Have to enable Shell or * will not be expanded!
    stdout, stderr = process.communicate()
    #print(stderr)
    
    #Now generate summary histogram 
    args = "Rscript {} {} {} {}".format( rScript, statsSummaryFile , statsSummaryDir, prefix)
    cmd = args.split(" ")
    logging.debug("Calling subprocess with {0}".format(cmd))
    (rV,out,err) = call_command(cmd, workDir)
        
        
    logging.info("Finished script with exit value {0}".format(0))
    sys.exit(0)
        
        

def checkInput(dataDir, itStart, nIterations, rScript):
    
    if( os.path.isfile( rScript ) == False):
        logging.error("Could not find R Statistics script {0}", rScript)
        return False
    
    if( os.path.isdir(dataDir) == False):
        logging.error("{0} is no valid directory!".format(dataDir) )
        return False
    
    for i in range(nIterations):
        path = dataDir + "/" + itStart + str(i) + '.csv'
        if( os.path.isfile( path ) == False):
            logging.error("Statistics file {0} not found!".format(path) )
            return False
    
    return True
    

def usage():
    return ( "Usage: {0} [PATH_TO_CSV_DATA_FILES] [WORK_DIR] [SUMMARY_DIR] [PREFIX] [# of ITERATIONS] [NUM_THREADS]".format(sys.argv[0]) )
    
def call_command(command, cwd = os.getcwd() , silent = False, shell=False):
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd = cwd,
                               shell = shell
                               )
    stdout, stderr = process.communicate()
    
    #Transform the output into an array, containing the lines produced as elements
    out = stdout.decode("utf-8").split('\n')
    err = stderr.decode("utf-8").split('\n')
    for idx,v in enumerate(out):
        out[idx] = v.strip()
    for idx,v in enumerate(err):
        err[idx] = v.strip()
        
    if(silent == False):
        logging.debug("stdout {}\nstderr {}".format(out,err))
    
    return (process.returncode, out, err) 

if __name__ == "__main__":
    main()

