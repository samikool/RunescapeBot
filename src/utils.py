import subprocess
from time import sleep

#function will read tasks from cfg file
def parseTasks():
    allTasks = dict()
    with open('tasks.cfg', 'r') as file: 
        lines = file.readlines()
        curTask = dict()
        reading=False
        for line in lines:
            line = line.strip('\n')
            if line.startswith('#'):
                continue
            if line == '':
                continue

            if line.startswith('['):
                if reading:
                    allTasks[curTask['name']] = curTask
                    curTask = dict()
                reading = not reading
                continue
                
            if reading:
                key = line.split('=')[0]
                value = line.split('=')[1]
                curTask[key] = value
    return allTasks

 
def stopDisplay(d):
    subprocess.call([''])

def createDisplay(d):
    cmd = './scripts/createDisplay.sh :'+str(d)
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)

    while proc.poll() == None:
        sleep(0.1)
    
    if(proc.returncode):
        return None,None

    out = proc.stdout
    out = out.peek().decode('utf8')
    out = out.split('\n')
    
    dispPID = None
    deskPID = None
    for line in out:
        if line.startswith('dispPID'):
            dispPID = int(line.split('=')[1])
        elif line.startswith('deskPID'):
            deskPID = int(line.split('=')[1])

    return dispPID,deskPID

def startClient(d):
    cmd = './scripts/startClient.sh :'+str(d)
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)

    while proc.poll() == None:
        sleep(0.1)

    if proc.returncode:
        return None

    out = proc.stdout
    out = out.peek().decode('utf8')
    out = out.split('\n')

    clientPID = None

    for line in out:
        if line.startswith('clientPID'):
            clientPID = int(line.split('=')[1])

    return clientPID

def startVNC(d):
    cmd = './scripts/startVNC.sh :'+str(d)
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)

    while proc.poll() == None:
        sleep(0.1)
    
    if(proc.returncode):
        return None,None

    out = proc.stdout
    out = out.peek().decode('utf8')
    out = out.split('\n')

    port = None
    vncPID = None
    for line in out:
        if line.startswith('PORT'):
            port = int(line.split('=')[1])
        elif line.startswith('vncPID'):
            vncPID = int(line.split('=')[1])

    return port,vncPID

def killBot(bot):
    pids = ''
    for k in bot:
        if k.endswith('PID'): 
            pids += str(bot[k])+' '

    pids = pids[:-1] # take of last space

    cmd = 'kill '+pids
    subprocess.Popen(cmd,shell=True)