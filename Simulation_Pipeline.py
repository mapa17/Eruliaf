#!/usr/bin/env python


###
# USAGE
###

import os
import re
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')

def main():
    pass

def usage():
    return ( "".format(sys.argv[0]) )
    
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

