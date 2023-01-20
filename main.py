from icmplib import async_ping
from enum import Enum
import asyncio, sys, os, time, schedule
import threading
import time
from concurrent import futures

class hostStates(Enum):
    IDLE = 'idle'
    PINGING = 'pinging'
    REJECTED = 'rejected'
    ACCEPTED = 'accepted'

class programStates(Enum):
    STARTING = 'starting'
    GATERING = 'getting'
    RUNNING_THREADS = 'running_threads'
    DISPLAYING_DATA = 'displaying_data'
    IDLE = 'idle'

class HostClass:
    def __init__(self, address):
        self.state = hostStates.IDLE.name
        self.address = address
        self.up = False
        self.time = 0
        self.uptime = 0
        self.downtime = 0
        self.error = 0
    
    async def is_alive(self): 
        self.state = hostStates.PINGING.name

        try:
            host = await async_ping(self.address, count=1, interval=0.2, timeout = 0.3)
        
        except:
            self.state = hostStates.REJECTED.name
            self.updateDead()
            return

        if host.is_alive:
            self.state = hostStates.ACCEPTED.name
            self.uptateAlife()
        else:
            self.state = hostStates.REJECTED.name
            self.updateDead()
    
    def updateDead(self):
        self.up = False
        self.time = self.time + 1
        self.downtime = self.downtime + 1
        self.error = self.downtime / self.time

    def uptateAlife(self):
        self.up = True
        self.time = self.time + 1
        self.uptime = self.uptime + 1
        self.error = self.downtime / self.time

    def displaySelf(self):
        print(self.address,'|', self.up, '|', self.time, '|', self.uptime, '|', self.downtime, '|', self.error, '|', self.state)

class program:      # START PROGRAMU
    def __init__(self, host):   
        self.state = programStates.STARTING.name    # INICJALIZACJA PROGRAMU
        self.hosts = []
        self.args = []
        self.gatherHost(host)
        self.setState(programStates.RUNNING_THREADS.name)   # USTAWIENIE STANU O URUCHOMIENIU WĄTKÓW
        self.main_loop()
                    
    def setArgs(self, args):
        self.args = args

    def setState(self, state):
        self.state = state

    def gatherHost(self, host):     # GATHERING HOST
        self.setState(programStates.GATERING.name)
        self.setArgs(host)
    
    def startThread(self, address):
        host = HostClass(address)
        self.hosts.append(host)
        schedule.every(0).seconds.do(self.check_run, host) # URUCHOMIĆ GO ASYNCHRONICZNIE, ABY NIE BLOKOWAŁ INNYCH WĄTKÓW

    def check_run(self, host):
        return asyncio.run(host.is_alive())

    def main_loop(self):    # główna pętla programu
        schedule.every(0).seconds.do(self.display)
        for host in self.args:
           self.startThread(host)       
        self.setState(programStates.IDLE.name)

    def display(self):
        self.setState(programStates.DISPLAYING_DATA.name)
        clear = lambda: os.system('clear')
        clear()
        print("Host | Online | Time | Uptime | Downtime | Probability | Host current machine state")
        for host in self.hosts:
           host.displaySelf()

        self.setState(programStates.IDLE.name)
 

args = sys.argv     # odczytuje wszystkie podane argumenty w terminalu
args.pop(0)

program = program(args)

#############################

while True:
    start = time.time()
    schedule.run_pending()  #URUCHAMIA ZAKOLEJKOWANE WĄTKI
    end = time.time()
    if end - start > 0:
        time.sleep(1-(end-start))

