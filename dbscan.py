# -*- coding: utf-8 -*-

# A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise
# Martin Ester, Hans-Peter Kriegel, Jörg Sander, Xiaowei Xu
# dbscan: density based spatial clustering of applications with noise

import numpy as np
import math
from time import time

UNCLASSIFIED = False
NOISE = None

def _distLoc(p, q):
    #delta 0.0001 = 11m
    deltaLat = q[0] - p[0]
    deltaLong = q[1] - p[1]

    deltaLat = 11 * (deltaLat / 0.0001)
    deltaLong = 11 * (deltaLong / 0.0001)

    distance = math.sqrt(math.pow(deltaLat, 2) + math.pow(deltaLong, 2))
    return distance

def _dist(p,q):
	return math.sqrt(np.power(p-q,2).sum())

def _eps_neighborhood(p,q,eps):
	return _distLoc(p,q) < eps

def _region_query(m, point_id, eps):
    n_points = m.shape[1]
    seeds = []
    for i in range(0, n_points):
        if _eps_neighborhood(m[:,point_id], m[:,i], eps):
            seeds.append(i)
    return seeds

def _add_point_to_avr(cluster_avr, m, cluster_id, point_id):
    cluster_avr[cluster_id - 1][0] += m.item(0, point_id)
    cluster_avr[cluster_id - 1][1] += m.item(1, point_id)
    cluster_avr[cluster_id - 1][2] += 1

def _expand_cluster(m, classifications, point_id, cluster_id, eps, min_points, clustersList, cluster_avr):
    numPoints = 0
    seeds = _region_query(m, point_id, eps)
    if len(seeds) < min_points:
        classifications[point_id] = NOISE
        return False
    else:
        clustersList.append([])
        cluster_avr.append([0, 0, 0])

        #classifications[point_id] = cluster_id Not necessary as it is already in seeds
    
        for seed_id in seeds:
            #print(seed_id)
            classifications[seed_id] = cluster_id
            clustersList[cluster_id - 1].append(seed_id)

            _add_point_to_avr(cluster_avr, m, cluster_id, seed_id)
            numPoints += 1
            
        while len(seeds) > 0:
            current_point = seeds[0]
            results = _region_query(m, current_point, eps)
            if len(results) >= min_points:
                for i in range(0, len(results)):
                    result_point = results[i]
                    if classifications[result_point] == UNCLASSIFIED or \
                       classifications[result_point] == NOISE:
                        if classifications[result_point] == UNCLASSIFIED:
                            seeds.append(result_point)

                        classifications[result_point] = cluster_id
                        clustersList[cluster_id - 1].append(result_point)

                        _add_point_to_avr(cluster_avr, m, cluster_id, result_point)
                        numPoints += 1
                        
            seeds = seeds[1:]

        #Make the average
        cluster_avr[cluster_id - 1][0] /= numPoints
        cluster_avr[cluster_id - 1][1] /= numPoints

        return True
        
def dbscan(m, eps, min_points):
    """Implementation of Density Based Spatial Clustering of Applications with Noise
    See https://en.wikipedia.org/wiki/DBSCAN
    
    scikit-learn probably has a better implementation
    
    Uses Euclidean Distance as the measure
    
    INPUTS
    m - A matrix whose columns are feature vectors
    eps - Maximum distance two points can be to be regionally related
    min_points - The minimum number of points to make a cluster
    
    OUTPUTS

    classifications:
    An array with either a cluster id number or dbscan.NOISE (None) for each
    column vector in m.

    clustersList: 
    A list of clusters which cotains the ids of the points in each cluster

    cluster_avr: 
    A list of points which contains the center os the cluster and the number 
    of points
    """
    clustersList = []
    cluster_avr = []
    

    cluster_id = 1
    n_points = m.shape[1]
    classifications = [UNCLASSIFIED] * n_points
    for point_id in range(0, n_points):
        point = m[:,point_id]
        
        if classifications[point_id] == UNCLASSIFIED:
            if _expand_cluster(m, classifications, point_id, cluster_id, eps, min_points, clustersList, cluster_avr):
                cluster_id = cluster_id + 1
                
    return cluster_avr

def test_dbscan():
    init_time = time()

    m = np.matrix("""1.0 3.8 0.8 3.7 3.9 3.6 10.1 10.4 10.7; 
                     1.1 4.3 1.0 4.0 3.9 4.1 10.1 10.4 10.7""")
    eps = 4
    min_points = 2
    
    result = dbscan(m, eps, min_points)
    finish_time = time()
    print("El tiempo fue: " + str(finish_time - init_time))
    print(result)
