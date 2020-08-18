import subprocess
from time import sleep

def loadFile(file):
    with open(file,'r') as f:
        return [x.strip('\n') for x in f.readlines() if not x == '\n']

def getTaskGroup(group_name):
    lines = loadFile('taskGroups.cfg')
    l = findTask(group_name, lines)
    return prepTaskGroup(l)

def prepTaskGroup(group):
    def dictStrToList(key):
        t_list = list()
        for t in group[key].split(','):
            l = t.split(' ')
            n = l[0] #name
            p = l[1:] #params

            t_list.append(getTask(n,p))
        group[key] = t_list

    dictStrToList('preloop')
    dictStrToList('loop')
    dictStrToList('postloop')
    return group

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

    req_p = params[:nreq]
    opt_p = params[nreq:]+[' ']*((nreq+nopt)-nparam) if opt else []

    s = str(t)

    for k,v in zip(req,req_p):
        s = s.replace(k,v)

    for k,v in zip(opt,opt_p):
        s = s.replace(k,v)

    s = s.replace('  ','')
    s = s.replace(' ,',',')

    s = eval(s)

    if s.get('preloop'): s['preloop'] = s['preloop'].split(',')
    if s.get('loop'): s['loop'] = s['loop'].split(',')
    if s.get('postloop'): s['postloop'] = s['postloop'].split(',')

    return s

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