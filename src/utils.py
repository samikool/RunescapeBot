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

def parseTaskLoops():
    taskLoops = dict()
    with open('taskLoops.cfg', 'r') as file: 
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
                    taskLoops[curTask['name']] = curTask
                    curTask = dict()
                reading = not reading
                continue
                
            if reading:
                key = line.split('=')[0]
                value = line.split('=')[1]
                curTask[key] = value

    prepTaskLoops(taskLoops)
    return taskLoops

def cleanTask(task_name, params:list=None):
    #key to replace #value to replace with
    def replaceInDict(d,key,value):
        for k in d:
            d[k] = d[k].replace(key,value)
            while d[k].endswith(' '):
                d[k] = d[k][:-1]

    task = parseTasks()[task_name]
    if task.get('required'):
        req = task.get('required').split(',')
        opt = task.get('optional').split(',') if task.get('optional') else None

        if len(req) > len(params):
            raise AssertionError('There are required parameters not present')
        for i,var in enumerate(req):
            replaceInDict(task,var,params[i])
        if opt:
            numLeft = len(params) - len(req)
            if(numLeft):
                params = params[len(req):]
                for i,var in enumerate(opt):
                    replaceInDict(task,var,params[i])
            else:
                for i,var in enumerate(opt):
                    replaceInDict(task,var,'')
            replaceInDict(task,' ,',',')
    
    return task

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

def prepTaskLoops(taskLoops):
    for loop in taskLoops.values():
        l = list()
        preloop = loop['preloop'].split(',')
        for t in preloop:
            t = t.split(' ')

            n = t[0]
            p = t[1:] if t[1:] else None

            l.append(cleanTask(n,p))

        loop['preloop'] = l

        l = list()
        mloop = loop['loop'].split(',')
        for t in mloop:
            t = t.split(' ')

            n = t[0]
            p = t[1:] if t[1:] else None

            l.append(cleanTask(n,p)) 
        
        loop['loop'] = l

        l = list()
        poloop = loop['postloop'].split(',')
        for t in poloop:
            t = t.split(' ')

            n = t[0]
            p = t[1:] if t[1:] else None

            l.append(cleanTask(n,p))
        
        loop['postloop'] = l

def getLoginDetails():
    lines = None
    e = None
    p = None
    u = None
    v = None

    with open('login.deets', 'r') as f:
        lines = f.readlines()
        
        for i,l in enumerate(lines):
            if l.startswith('#'):
                continue
            li = l.strip('\n')
            li = l.split(' ')

            v = int(li[3])

            if not v:
                e = li[0]
                p = li[1]
                u = li[2]

                # l = l[:-2]
                # l += '1\n'
                # lines[i] = l
                break

    # with open('login.deets', 'w') as f:
    #     f.writelines(lines)
    
    v = None
    w = None
    
    with open('worlds.deets', 'r') as f:
        lines = f.readlines()

        for i,l in enumerate(lines):
            if l.startswith('#'):
                continue
            li = l.strip('\n')
            li = l.split(' ')

            v = int(li[1])

            if not v:
                w = li[0]
                
                # l = l[:-2]
                # l += '1\n'
                # lines[i] = l
                break

    # with open('worlds.deets', 'w') as f:
    #     f.writelines(lines)

    return e,p,w

# print(getLoginDetails())            