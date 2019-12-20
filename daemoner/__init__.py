#!/usr/bin/env python3

import os
import sys
import signal
import time
import json
import urllib
import datetime as dt
import psutil

def log(*args,file=None):
    args = [dt.datetime.now()] + list(args)
    if file == None:
        print(*args,file=sys.stdout,flush=True)
    else:
        if type(file) != str:
            raise TypeError("'file' argument must be a string")
        with open(file,'a') as f:
            print(*args,file=f,flush=True)

def g():
    pass
            
def main(**kwargs):
    
    
    log("Default main loop")
    while True:
        
        log("10 second loop....")
        time.sleep(10)


class Daemon(object):
    def __init__(self,f=main,fkwargs={},pidfilename='./daemon.pid',g=g,gkwargs={}):
        
        self.pidfilename = os.path.abspath(pidfilename)
        self.f = f
        self.fkwargs = fkwargs
        self.g = g
        self.gkwargs = gkwargs

    def run(self):
        if sys.argv[1] == '--start':
            log('Starting...')
            self.start()

        elif sys.argv[1] == '--stop':
            self.stop()

        elif sys.argv[1] == '--restart':
            log("Stopping...")
            self.stop()
            log("Restarting...")
            self.start()    
            
        else:
            log("Please provide one of the following options: --start --stop --restart")
            sys.exit()
            
    def graceful_exit(self,e=None):
        
        self.g(**self.gkwargs)
        
        try:
            os.remove(self.pidfilename) 
            log("Exiting daemon gracefully....")

        except FileNotFoundError:
            log("pid file is missing. Exiting anyways")

        if e is not None:
            raise e
        else:
            sys.exit()


    def catch_signal(self,sig,frame):
        self.graceful_exit()


    def start(self):

        # If the PID file exists, exit without doing anything
        # because the daemon is already running
        if os.path.isfile(self.pidfilename):
            log(self.pidfilename)
            log("Daemon is already running")
            sys.exit()

        # If the PID files doesn't exist...
        else:

            # Setup signal handlers 
            signal.signal(signal.SIGINT, self.catch_signal)
            signal.signal(signal.SIGTERM, self.catch_signal)

            # Get PID of current process
            pid = os.getpid()
            now = dt.datetime.now().isoformat()
            
            # Open the PID file and write the PID
            with open(self.pidfilename,'w') as pidfile:                   
                pidcontent = {'pid':pid,'time':now}
                json.dump(pidcontent,pidfile)

            try:
                self.f(**self.fkwargs)
            except Exception as e:
                self.graceful_exit(e)
            
            
    def stop(self):

        """
        This stops a *separate* running daemon process
        """
        

        if os.path.isfile(self.pidfilename):

            with open(self.pidfilename) as f:
                    data = json.load(f)
                    pid = data['pid']
            os.kill(int(pid), signal.SIGTERM)

            # Check that the process has been killed
            # Give up after 15 seconds
            for i in range(15):
                if int(pid) not in psutil.pids():

                    return True
                time.sleep(1)
            return False

        # If the daemon is not currently running, do nothing
        else:
            log("The daemon is not currently running")   
    


        
        

