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

def loadFile(file):
    with open(file,'r') as f:
        return [x.strip('\n') for x in f.readlines() if not x == '\n']

def getTaskLoop(loop_name):
    lines = loadFile('taskLoops.cfg')
    l = findTask(loop_name, lines)
    return prepTaskLoopp(l)

def prepTaskLoopp(loop):
    def makeList(k,loop):
        t_list = list()
        for t in loop[k].split(','):
            l = t.split(' ')
            n = l[0] #name
            p = l[1:] #params

            t_list.append(getTask(n,p))
        loop[k] = t_list

    makeList('preloop',loop)
    makeList('loop',loop)
    makeList('postloop',loop)
    return loop

def getTask(task_name, params:list=[]):
    lines = loadFile('tasks.cfg')    
    t = findTask(task_name, lines)
    return prepTask(t, params)

def findTask(task_name, lines:list):
    reading = False
    task = dict()
    for i,l in enumerate(lines):
        if l.endswith(task_name):
            reading = True
        if reading:
            if l.startswith('['):
                break
            k,v = l.split('=')
            task[k] = v
    return task

def prepTask(t, params:list=[]):
    req = t.get('required').split(',') if t.get('required') else []
    opt = t.get('optional').split(',') if t.get('optional') else []

    nreq = len(req) if req else 0
    nopt = len(opt) if opt else 0
    nparam = len(params)

    if nparam < nreq:
        raise ValueError('task has required parameters, but some were not provided')

    if nparam > nreq+nopt:
        raise ValueError('too many parameters provided for task')

    if not req and not opt:
        return t

    req_p = params[:nreq]
    opt_p = params[nreq:]+[' ']*((nreq+nopt)-nparam) if opt else []

    s = str(t)

    for k,v in zip(req,req_p):
        s = s.replace(k,v)

    for k,v in zip(opt,opt_p):
        s = s.replace(k,v)

    s = s.replace('  ','')
    s = s.replace(' ,',',')

    return eval(s)
    
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

