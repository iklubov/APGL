"""
Observe the effect in the perturbations of Laplacians 
"""

import sys 
import logging
import numpy
import scipy 
import itertools 
import copy
import matplotlib.pyplot as plt 
from apgl.graph import *
from apgl.util.PathDefaults import PathDefaults
from exp.sandbox.IterativeSpectralClustering import IterativeSpectralClustering
from apgl.graph.GraphUtils import GraphUtils
from apgl.generator.SmallWorldGenerator import SmallWorldGenerator
from apgl.generator.ErdosRenyiGenerator import ErdosRenyiGenerator
from apgl.util.Util import Util 

numpy.random.seed(21)
#numpy.seterr("raise")
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
numpy.set_printoptions(suppress=True, linewidth=200, precision=3)

class GraphIterator(object): 
    """
    Take 3 clusters generated by Erdos Renyi processes and then add random edges 
    successively to model "noise". 
    """
    def __init__(self): 
        self.changeEdges = 10 
        self.numGraphs = 100
        self.graphInd = 0
        numClusterVertices = 50 
        p = 0.3 
        generator = ErdosRenyiGenerator(p)
        
        graph1 = SparseGraph(GeneralVertexList(numClusterVertices))
        graph1 = generator.generate(graph1)
        
        graph2 = SparseGraph(GeneralVertexList(numClusterVertices))
        graph2 = generator.generate(graph2)
        
        graph3 = SparseGraph(GeneralVertexList(numClusterVertices))
        graph3 = generator.generate(graph3)
        
        graph = graph1.concat(graph2).concat(graph3) 
        self.graph = graph 
        
        self.realClustering = numpy.zeros(numClusterVertices*3)
        self.realClustering[numClusterVertices:2*numClusterVertices] = 1 
        self.realClustering[numClusterVertices*2:] = 2 
        
    def __iter__(self):
        return self
        
    def next(self):
        if self.graphInd == self.numGraphs: 
            raise StopIteration
        
        i = 0
        while i < self.changeEdges: 
            inds = numpy.random.randint(0, self.graph.size, 2)
            if self.graph[inds[0], inds[1]] == 0: 
                self.graph[inds[0], inds[1]] = 1
                i += 1 
        
        logging.debug(self.graph)        
        
        W = self.graph.getSparseWeightMatrix().tocsr()
        self.graphInd += 1 
        return W 
            
       
iterator = GraphIterator()

for W in iterator: 
    L = GraphUtils.shiftLaplacian(W)
    u, V = numpy.linalg.eig(L.todense())
    u = numpy.flipud(numpy.sort(u))
    
    #print(u)



k1 = 3
k2 = 3
logging.debug("k=" + str(k1))

iterator = GraphIterator()

clusterer = IterativeSpectralClustering(k1, k2)
clusterer.nb_iter_kmeans = 20
clusterer.computeBound = True 
logging.debug("Starting clustering")
clusterList, timeList, boundList = clusterer.clusterFromIterator(iterator, verbose=True, T=10)
boundList = numpy.array(boundList)
print(boundList)

errors = numpy.zeros(len(clusterList))

for i in range(len(clusterList)): 
    errors[i] = GraphUtils.randIndex(clusterList[i], iterator.realClustering)

print(clusterList[-1])

plt.figure(0)
plt.plot(boundList[:, 0], boundList[:, 1])
plt.plot(boundList[:, 0], boundList[:, 2])

plt.figure(1)
plt.plot(numpy.arange(errors.shape[0]), errors)

plt.show()


