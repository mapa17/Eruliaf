#!/usr/bin/env python


###
# USAGE
###

import os
import re
import sys
import subprocess
import logging
import argparse


import configparser
logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')

import threading
import queue

def main():
    
    global nIterations
    global rScript
    global runDir
    global prefix
    global scenarioFile
    global randSeedBase
    global logCfg
    global logLevel
    global scenario
    global nThreads
    global statsScript
    global statsOutput
    global statsSummaryDir
    
#    if( len(sys.argv) < 2):
#        logging.error("Error in Arguments!\nUsage {0}".format(usage()))
#        sys.exit(1)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prefix", help="Prefix used for simulation results" , default="", type=str)
    parser.add_argument("-s", "--StatsOnly", help="Use already available simulation data and generate statistics only", action="store_true")
    parser.add_argument("-l", "--noLogs", help="Do not create log files", action="store_true")
    parser.add_argument("SimulationFile", help="Specified the Simulation file")
    args = parser.parse_args()
    
    configFile = os.path.abspath( args.SimulationFile )
    prefix = args.prefix
    generateStatsOnly = args.StatsOnly
    noLogs = args.noLogs
    
    print("Running Simulation [{}] with Prefix \"{}\"".format(configFile, prefix))
    if(generateStatsOnly):
        print("Generating only statistics!!")
    if(noLogs):
        print("Will not generate Log files!")
    
    if( os.path.isfile(configFile) == False):
        logging.error("Config file {0} could not be read!".format(configFile))
        sys.exit(2)

    #Read config values
    config = configparser.SafeConfigParser(allow_no_value=True)
    logging.debug("Reading config {0} ...".format(configFile))
    config.readfp(open(configFile))
    
    nIterations = int( config.get("General", "nIterations") )
    runDir = config.get("General", "runDirectory")
    runDir = os.path.abspath(runDir)
    if(prefix == ""): 
        prefix = config.get("General", "iterationPrefix")
    scenarioFile = config.get("General", "scenario")
    randSeedBase = int(config.get("General", "randSeedBase"))
    logCfg = config.get("General", "logCfg")
    logCfg = os.path.abspath(logCfg)
    logLevel = config.get("General", "logLevel")
    if(noLogs):
        logLevel = "NONE"
    scenario = configparser.SafeConfigParser(allow_no_value=True)
    scenario.readfp(open(scenarioFile))   
    nThreads = int( config.get("General", "nThreads") )
    statsScript = config.get("General", "statsScript")
    statsScript = os.path.abspath(statsScript)
    rScript = config.get("General", "rScript")
    rScript = os.path.abspath(rScript)
    statsOutput = config.get("General", "statsOutput")
    statsOutput = os.path.abspath(statsOutput)
    statsSummaryDir = config.get("General", "statsSummaryDir")
    statsSummaryDir = os.path.abspath(statsSummaryDir)
   
    if(generateStatsOnly == False):
        #Generate Dir
        d = os.path.abspath(config.get("General", "runDirectory"))
        if not os.path.exists(d):
            os.makedirs( d )
        
        d = os.path.abspath(config.get("General", "statsOutput"))
        if not os.path.exists(d):
            os.makedirs( d )
        
        d = os.path.abspath(config.get("General", "statsSummaryDir"))
        if not os.path.exists(d):
            os.makedirs( d )
    
        #Generate Configs    
        generateConfigs(config)
        
        runSimulations(config)

    generateStatistics(config)
    
    logging.info("Finished Simulation! ...")
    
def generateConfigs(config):
    
    #print("{0}".format(config.sections() ) )
    #print("{0}".format(config.items("General") ) )
    
    for i in  range(nIterations):
        #cfgPath = "{0}/{1}{2}.cfg".format(runDir, prefix, i)
        cfgPath = os.path.join(runDir,prefix+str(i)+".cfg")
        logging.debug("Generating config {0}".format(cfgPath))
        
        #statsFile = "{0}/{1}{2}.csv".format(runDir, prefix, i)
        statsFile = os.path.join(runDir,prefix+str(i)+".csv")
        scenario.set("General", "statsFile", statsFile )
        
        #logFile = "{0}/{1}{2}.log".format(runDir, prefix, i)
        logFile = os.path.join(runDir,prefix+str(i)+".log")
        scenario.set("General", "logFile", logFile )
        
        scenario.set("General", "logCfg", logCfg )
        
        scenario.set("General", "logLevel", logLevel)
        
        scenario.set("General", "randSeed", str(randSeedBase + i) )
        
        cfg = open(cfgPath , "w")
        scenario.write(cfg)
        cfg.close() 
        
    logging.info("Finished creating configs!")

q = queue.Queue()

def worker():
    while True:
        cfgFile = q.get()
        rC = 1
        retryCnt = 0
        while(retryCnt < 1):
            
            logging.info("Calling simulation with config {0}".format(cfgFile) )
            (rC,out,err) = call_command([sys.executable, "Eruliaf.py", cfgFile], silent=True)
            
            if( (rC != 0) and (retryCnt < 1) ):
                logging.error("Simulation failed! With [out:{} , err:{}]".format(out, err))
                if(getLogLevel(cfgFile) != "NONE"):
                    logging.info("Scenario already created a log file. Look for errors there.")
                    retryCnt = 1
                else:
                    logging.info("Will run the simulation again with log level set to INFO ...")
                    adaptLogLevel(cfgFile, "INFO" )
            
        q.task_done()

def runSimulations(config):
    
    logging.debug("Run simulations!")
    
    threadList = []
    for i in range(nThreads):
        threadList.append( threading.Thread(target=worker) )
        threadList[-1].daemon = True #Make them daemon threads so we dont care about cleaning up
        threadList[-1].start()

    for i in range(nIterations):
        #cfgPath = "{0}/{1}{2}.cfg".format(runDir, prefix, i)
        cfgPath = os.path.join(runDir, prefix+str(i)+".cfg")
        #logging.debug("Adding instance on cfg {0}".format(cfgPath))
        q.put(cfgPath, False)
    
    logging.debug("Waiting for all simulations to finish!")
    q.join()
        
    logging.debug("All threads finished!")

def generateStatistics(config):
    args = [sys.executable, statsScript, rScript, runDir, statsOutput, statsSummaryDir, prefix, str(nIterations) , str(nThreads) ]
    logging.info("Generating statistics calling {0}!".format(args))
    
    #call_command(args, cwd=os.path.dirname(statsScript) )
    args = '{} {} {} {} {} {} "{}" {} {}'.format(sys.executable, statsScript, rScript, runDir, statsOutput, statsSummaryDir, prefix, str(nIterations) , str(nThreads))
    (status,output) = subprocess.getstatusoutput(args)
    if(status != 0):
        logging.info("Generating statistics failed!\n{}".format(output))
        return status
    else:
        logging.info("Finished creating statistics!")
        return 0


def adaptLogLevel(cfgFile, logLevel):
    cfg = configparser.SafeConfigParser(allow_no_value=True)
    cfg.readfp(open(cfgFile))
    cfg.set("General", "logLevel", logLevel)
    cfg.write(cfgFile)    

def getLogLevel(cfgFile):
    cfg = configparser.SafeConfigParser(allow_no_value=True)
    cfg.readfp(open(cfgFile))
    return cfg.get("General", "logLevel")
    
def usage():
    return ( "{0} [SIMULATION_PREFIX] SIMULATION_CONFIG ".format(sys.argv[0]) )
    
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

