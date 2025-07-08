#!/usr/bin/env python
# Haversine formula example in Python
# Author: Wayne Dyck

import math

import numpy as np


def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d
    
def nearest_point(origin, latpoints, lonpoints, grid='1d'):
    
    if grid == '1d':
        dist = np.zeros((np.shape(latpoints)[0], np.shape(lonpoints)[0]))

        for i, lat in enumerate(latpoints):
            for j, lon in enumerate(lonpoints):
                dist[i,j] = distance(origin,[lat,lon])

        lati, loni = np.where(dist == dist.min())
        return (dist.min(), latpoints[lati[0]], lonpoints[loni[0]], lati[0], loni[0] )

    elif grid == '2d':
        dist = np.zeros_like(latpoints)

        for i, latrow in enumerate(latpoints):
            for j, lonrow in enumerate(latrow):
                dist[i,j] = distance(origin,[latpoints[i,j],lonpoints[i,j]])

        lati, loni = np.where(dist == dist.min())
        
        return (dist.min(), latpoints[lati[0]][loni[0]], lonpoints[lati[0]][loni[0]], lati[0], loni[0] )
    else:
        raise Exception("not a valid grid")