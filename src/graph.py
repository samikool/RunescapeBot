from math import sqrt
import heapq

class Vertex:
    def __init__(self,key,data):
        self.key = key
        self.data = data
        self.edges = {}

    def addNeighbor(self,nbr,weight=0):
        self.edges[nbr] = weight

    def connectedTo(self, vertex):
        if vertex in self.edges.keys():
            return True
        return False

    def __str__(self):
        return str(self.key +':'+str(self.data) + ' connectedTo:' + str([x.key for x in self.edges]))

    def getNeighbors(self):
        return [x for x in self.edges.keys()]

    def getWeight(self,nbr):
        return self.edges[nbr]

#this graph is undirected 
class Graph:
    def __init__(self):
        self.vertList = {}
        self.numVertices = 0

    def addVertex(self, v):
        if v.key not in self.vertList:
            self.vertList[v.key] = v
            self.numVertices += 1
            return True
        raise ValueError('Vertex'+str(v)+'is already in graph')
        
    def getV(self,k):
        if k in self.vertList:
            return self.vertList[k]
        else:
            return None

    def __contains__(self,n):
        return n in self.vertList

    def addEdge(self, v1: Vertex, v2: Vertex, weight=0):
        if(not (v1.key in self.vertList and v2.key in self.vertList)):
            raise ValueError('Either v1 or v2 have not been added to the graph')

        if not (v1.connectedTo(v2) or v2.connectedTo(v1)):
            v1.addNeighbor(v2,weight)
            v2.addNeighbor(v1,weight)
            return True
        return False
    
    def edgeWeight(self, v1, v2):
        return v1.getWeight(v2)

    def getVertices(self):
        return self.vertList.values()

    def __str__(self):
        s = ''
        for vert in self.vertList.values():
            s+=str(vert)+'\n'
        return  s

#override addEdge to compute our custom weights
class MapGraph(Graph):
    #this init will read our graph cfg file eventually
    def __init__(self):
        super().__init__()

    def load(self):        
        nodes = self.parseMapCfg()
        self.createGraph(nodes)


    def createGraph(self, mapnodes):
        #create each verticie and add it to graph
        for node in mapnodes.values():
            v = Vertex(node['name'],(int(node['x']),int(node['y'])))
            self.addVertex(v)

        #connecect verticies based on neighbors list
        for node in mapnodes.values():
            neighbors = node['neighbors'].split(',')

            for n in neighbors:
                self.addEdge(self.vertList[node['name']],self.vertList[n])


    #parse map cfg and return a graph
    def parseMapCfg(self):
        allMapNodes = dict()
        with open('mapnodes.cfg', 'r') as file:
            lines = file.readlines()
            
            curMapNode = dict()
            reading = False
            for line in lines:
                line = line.strip('\n')

                if line.startswith('#'):
                    continue

                if line == '':
                    continue

                if line.startswith('['):
                    if reading:
                        allMapNodes[curMapNode['name']] = curMapNode
                        curMapNode = dict()
                    reading = not reading
                    continue
                
                if reading:
                    key = line.split('=')[0]
                    value = line.split('=')[1]
                    curMapNode[key]=value
        return allMapNodes
    
    # TODO: eventually move this to utility function py file
    def dis(self, x1, y1, x2, y2):
        return sqrt((x2-x1)**2 + (y2-y1)**2)

    def addEdge(self, v1: Vertex, v2: Vertex):
        weight = self.dis(v1.data[0], v1.data[1], v2.data[0], v2.data[1])
        super().addEdge(v1,v2,weight)

    def getClosestVertex(self, data):
        x = data[0]
        y = data[1]
        minDis = float('inf')
        minV = None
        for v in self.vertList.values():
            testX = v.data[0]
            testY = v.data[1]
            dist = self.dis(x,y,testX,testY)
            if dist < minDis:
                minDis = dist
                minV = v
        return minV

    
    #TODO: switch to priority q with minHeap heapq library
    #TODO: probably can precalculate all of this on initialization
    def findPath(self, startV, endV):
        distance = {}
        parent = {}
        for v in self.vertList.keys():
            distance[v] = float('inf')
            parent[v] = None
        
        #find mst (dijkstra's) 
        q = list()
        distance[startV.key] = 0
        q.append(startV)
        while(len(q)):
            v = q.pop(0)
            for u in v.getNeighbors():
                du = distance[v.key]+v.getWeight(u)
                if(du < distance[u.key]):
                    distance[u.key] = du
                    parent[u.key] = v
                    q.append(u)

        path = list()
        path.append(endV)
        while(path[0].key != startV.key):
            cur = path[0]
            path.insert(0,parent[cur.key])
        return path