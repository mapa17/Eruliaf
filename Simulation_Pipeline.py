#!/usr/bin/env python


###
# USAGE
###

import os
import re
import sys
import subprocess
import logging

import configparser
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')

import threading
import queue
 


def main():
    if( len(sys.argv) < 2):
        logging.error("Error in Arguments!\nUsage {0}".format(usage()))
        sys.exit(1)
    
    configFile = os.path.abspath( sys.argv[1] )
    if( os.path.isfile(configFile) == False):
        logging.error("Config file {0} could not be read!".format(configFile))
        sys.exit(2)
    
    config = configparser.SafeConfigParser(allow_no_value=True)
    logging.debug("Reading config {0} ...".format(configFile))
    config.readfp(open(configFile))
    
    generateConfigs(config)
    
    runSimulations(config)

    generateStatistics(config)
    
    logging.info("Finished Simulation! ...")
    
def generateConfigs(config):
    
    #print("{0}".format(config.sections() ) )
    #print("{0}".format(config.items("General") ) )
    
    nIterations = int( config.get("General", "nIterations") )
    runDir = config.get("General", "runDirectory")
    runDir = os.path.abspath(runDir)
    prefix = config.get("General", "iterationPrefix")
    scenarioFile = config.get("General", "scenario")
    randSeedBase = int(config.get("General", "randSeedBase"))
    logCfg = config.get("General", "logCfg")
    logCfg = os.path.abspath(logCfg)
    scenario = configparser.SafeConfigParser(allow_no_value=True)
    scenario.readfp(open(scenarioFile))
    
    for i in  range(nIterations):
        cfgPath = "{0}/{1}{2}.cfg".format(runDir, prefix, i)
        logging.debug("Generating config {0}".format(cfgPath))
        
        statsFile = "{0}/{1}{2}.csv".format(runDir, prefix, i)
        scenario.set("General", "statsFile", statsFile )
        
        logFile = "{0}/{1}{2}.log".format(runDir, prefix, i)
        scenario.set("General", "logFile", logFile )
        
        scenario.set("General", "logCfg", logCfg )
        
        scenario.set("General", "randSeed", str(randSeedBase + i) )
        
        
        
        cfg = open(cfgPath , "w")
        scenario.write(cfg)
        cfg.close() 
        
    logging.info("Finished creating configs!")

q = queue.Queue()

def worker():
    while True:
        cfgFile = q.get()
        logging.info("Calling simulation with config {0}".format(cfgFile) )
        (rC,out,err) = call_command([sys.executable, "./Eruliaf.py", cfgFile], silent=True)
            
        q.task_done()

def runSimulations(config):
    
    logging.debug("Run simulations!")
    
    nThreads = int( config.get("General", "nThreads") )
    nIterations = int( config.get("General", "nIterations") )
    runDir = config.get("General", "runDirectory")
    prefix = config.get("General", "iterationPrefix")
    threadList = []
    for i in range(nThreads):
        threadList.append( threading.Thread(target=worker) )
        threadList[-1].daemon = True #Make them deamon threads so we dont care about cleaning up
        threadList[-1].start()

    for i in range(nIterations):
        cfgPath = "{0}/{1}{2}.cfg".format(runDir, prefix, i)
        #logging.debug("Adding instance on cfg {0}".format(cfgPath))
        q.put(cfgPath, False)
    
    logging.debug("Waiting for all simulations to finish!")
    q.join()
        
    logging.debug("All threads finished!")

def generateStatistics(config):
    nThreads = int( config.get("General", "nThreads") )
    nIterations = int( config.get("General", "nIterations") )
    runDir = config.get("General", "runDirectory")
    runDir = os.path.abspath(runDir)
    prefix = config.get("General", "iterationPrefix")
    statsScript = config.get("General", "statsScript")
    statsScript = os.path.abspath(statsScript)
    statsOutput = config.get("General", "statsOutput")
    statsOutput = os.path.abspath(statsOutput)
    statsSummaryFile = config.get("General", "statsSummaryFile")
    statsSummaryFile = os.path.abspath(statsSummaryFile)
    
    
    args = [sys.executable, statsScript, runDir, statsOutput, statsSummaryFile, prefix, str(nIterations) , str(nThreads) ]
    logging.debug("Generating statistics calling {0}!".format(args))
    
    call_command(args, cwd=os.path.dirname(statsScript) )
    
    logging.info("Finished creating statistics!")
    
def usage():
    return ( "{0} [SIMULATION_CONFIG] ".format(sys.argv[0]) )
    
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
#        if( process.returncode == 0):
#            logging.debug("Success {0}".format(out))
#        else:
##            logging.error("Failure! StdErr {0}\nStdout{1}".format(err,out))
        logging.debug("stdout {}\nstderr {}".format(out,err))
    
    return (process.returncode, out, err) 

if __name__ == "__main__":
    main()

