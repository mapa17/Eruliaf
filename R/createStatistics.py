'''
    Created on Feb 2, 2012

    @author: Pasieka Manuel , mapa17@posgrado.upv.es
    
    Copyright (C) 2012  Pasieka Manuel , mapa17@posgrado.upv.es

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

#!/usr/bin/env python

###
# USAGE
###

#Call the script with ./[ScriptName] RScript PATH_TO_CSV_DATA_FILES WORK_DIR SUMMARY_DIR PREFIX #ofITERATIONS NUM_THREADS

import os
import re
import sys
import subprocess
import logging
import threading
import queue

logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')

q = queue.Queue()

def worker():
    while(q.empty() == False):
        i = q.get()
        
        #Generate tables using R script file
        file2 = os.path.join(dataDir , prefix + str(i) + '.csv')
        scenario_summary2 = os.path.join(workDir , prefix + str(i) + '_summary.csv')
        args2 = "Rscript {} {} {} {} {}".format( rScript, file2, workDir, scenario_summary2, prefix + str(i))
        cmd2 = args2.split(" ")
        logging.info("Calling R script with {} in {}".format(cmd2, workDir))
        (rV,out,err) = call_command(cmd2, cwd=workDir)
        logging.debug( "Rscript finished with stdout {} \n stderr {} ".format(out,err) )
        
        if( rV > 0):
            logging.error("Generating scenario statistics failed!\n{}".format(err))
            q.task_done()
            return
        else:
            #Generate summary pdf for this scenario out of the different png files
            args2 = "convert {} {}".format( prefix + str(i) + "_*.png", os.path.join(statsSummaryDir , prefix + str(i) + "_summary.pdf" ) )
            cmd2 = args2.split(" ")
            logging.debug("Calling convert with {0}".format(cmd2))
            (rV,out,err) = call_command(cmd2, workDir)
        
            if( rV > 0):
                logging.error("Calling convert failed!\n{}".format(err))
                q.task_done()
                return
            else:
                q.task_done()

def main():
    logging.info('Being called to generate Statistics: {0}'.format(sys.argv) )
    
    #print('Being called to generate Statistics: {0}'.format(sys.argv) )
    #sys.exit(0)
    
    if(len(sys.argv) != 8):
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
    
    
    #rScript = "/work/Eigene/uni/Erasmus/Thesis/Eruliaf/R/Statistics.R"
    
    rScript = os.path.abspath( sys.argv[1])
    dataDir = os.path.abspath( sys.argv[2] )
    workDir = os.path.abspath( sys.argv[3] )
    if( os.path.isdir   ( workDir ) == False ):
        os.mkdir(workDir) 
    statsSummaryDir = os.path.abspath( sys.argv[4] )  
    prefix = sys.argv[5]
    nIterations = int(sys.argv[6]) 
    nThreads = int(sys.argv[7])
    statsSummaryFile = os.path.join(statsSummaryDir, prefix + "summary.csv")
    
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

    logging.info("Waiting for all scripts to finish!")
    q.join()
       
    #Unify the different scenario summaries
    args = "cat {} > {}".format( os.path.join( workDir, prefix + "*_summary.csv"), statsSummaryFile)
    #cmd = args.split(" ")
    cmd = args #Execution will hang if cmd is passed as array!
    logging.debug("Calling subprocess with {0}".format(cmd))
    
    #(rV,out,err) = call_command(cmd, workDir )
    #Dont use normal call_command because we dont want to redirect std-output to file!
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, cwd = workDir , shell=True) #Have to enable Shell or * will not be expanded!
    stdout, stderr = process.communicate()
    if(process.returncode > 0):
        logging.error("Collecting summary failed!\n{}".format(stderr))
        sys.exit(1)
    
    logging.info("Finished processing scenarios, start to fuse data to create summary ... ".format())    
    
    #Now generate summary histogram 
    args = "Rscript {} {} {} {}".format( rScript, statsSummaryFile , statsSummaryDir, prefix)
    cmd = args.split(" ")
    logging.debug("Calling subprocess with {0}".format(cmd))
    (rV,out,err) = call_command(cmd, workDir)
    if( rV > 0):
        logging.error("Creating summary statistics failed!\n{}".format(err))
        sys.exit(1)
        
    logging.info("Finished script".format())
    sys.exit(0)
        
        

def checkInput(dataDir, itStart, nIterations, rScript):
   
    #Generate Dir
    d = os.path.abspath(statsSummaryDir)
    if not os.path.exists(d):
        os.makedirs( d )
    
    if( os.path.isfile( rScript ) == False):
        logging.error("Could not find R Statistics script {0}", rScript)
        return False
    
    if( os.path.isdir(dataDir) == False):
        logging.error("{0} is no valid directory!".format(dataDir) )
        return False
    
    for i in range(nIterations):
        path = os.path.join(dataDir, itStart + str(i) + '.csv')
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

