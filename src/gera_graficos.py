#!/bin/python
import re
import sys
import json
import math
import warnings
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pyproj import Proj, transform

# ignore weird warnings from pyproj
warnings.filterwarnings('ignore')

# shorcuts
cos = math.cos
sin = math.sin
acos = math.acos
asin = math.asin
degrees = math.degrees
radians = math.radians

# globals
EARTH_RADIUS = 6371000
PI = math.pi

## PROJECTION

def get_point_coords_proj(a):
    lat = a['lat']
    lng = a['lng']
    p = np.array((lng, lat))
    return transform(Proj(init='epsg:4326'), Proj(init='epsg:3857'), p[0], p[1])

def get_dist_proj(a, b):
    pa = get_point_coords_proj(a)
    pb = get_point_coords_proj(b)
    return ((pa[0] - pb[0])**2 + (pa[1] - pb[1])**2)**(1/2)


## SPHERICAL TRIGONOMETRY

def get_angular_distance(a, b):
    latA = a["lat"]
    latB = b["lat"]
    lngA = a["lng"]
    lngB = b["lng"]

    # for didatic purposes, I will calculate the
    # angle's complement. But this is not necessary,
    # since cos(x) = sin(90 - x). I did this to make
    # it easier for reading the formula

    # point C is north pole (could be south pole too,
    # it doesn't matter)
    AC = radians(90 - latA)
    BC = radians(90 - latB)
    gamma = radians(abs(lngA - lngB))

    cosAB = cos(AC) * cos(BC) + sin(AC) * sin(BC) * cos(gamma)
    AB = acos(cosAB)
    return AB

def get_dist_spherical_trigonometry(a, b):
    return EARTH_RADIUS * get_angular_distance(a, b)

## HAVERSINA FORMULA

def haversine(a, b):
    latA = radians(a["lat"])
    latB = radians(b["lat"])
    lngA = radians(a["lng"])
    lngB = radians(b["lng"])
    return sin((latA - latB)/2)**2 + cos(latA) * cos(latB)* (sin((lngA - lngB)/2)**2)

def get_dist_haversine(a, b):
    s = haversine(a, b)
    return 2 * EARTH_RADIUS * asin(s**(1/2))

## PLOT HELPERS

# single plot
def plot(x, y, fname, title, xlabel, ylabel, label):
    plt.plot(x, y, label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(loc = "upper left")
    plt.savefig(fname)
    plt.clf()

# multiple plots together
def plots(x, ys, fnames, title, xlab, ylab, labels):
    l = len(ys)

    # generate single plot for each dataset
    for i in range(0, l):
        plot(x, ys[i], fnames[i], title, xlab, ylab, labels[i])

    # plot all datasets together
    fname = fnames[-1]
    for i in range(0, l):
        plt.plot(x, ys[i], label = labels[i])
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.title(title)
    plt.legend(loc = "upper left")
    plt.savefig(fname)
    plt.clf()

## MAIN

def main():
    # extract data from the file
    file_path = sys.argv[1]

    with open(file_path, "r") as f:
        text = f.read()
        data = json.loads(text)
        if (isinstance(data, dict)):
            data = data['photos']

    # variables used in loops
    L = len(data)
    l = L - 1
    indexes0l = range(0, l)
    indexes1L = range(1, L)
    indexes0L = range(0, L)

    # convert string to float
    for point in data:
        point["lat"] = float(point["lat"])
        point["lng"] = float(point["lng"])

    ## CONSECUTIVE DISTANCE
    dist_proj = [0]*l
    dist_trig = [0]*l
    dist_hav = [0]*l

    # calculate distance between consecutive points
    for i in indexes0l:
        a = data[i]
        b = data[i + 1]
        dist_proj[i] = get_dist_proj(a, b)
        dist_hav[i] = get_dist_haversine(a, b)
        dist_trig[i] = get_dist_spherical_trigonometry(a, b)

    ## TOTAL DISTANCE
    dist_proj_ac = [0] * L
    dist_trig_ac = [0] * L
    dist_hav_ac = [0] * L

    # calculate total distance up to the given point
    for i in indexes1L:
        a = data[i]
        b = data[i - 1]
        dist_proj_ac[i] = get_dist_proj(a, b) + dist_proj_ac[i -1]
        dist_hav_ac[i] = get_dist_haversine(a, b) + dist_hav_ac[i - 1]
        dist_trig_ac[i] = get_dist_spherical_trigonometry(a, b) + dist_trig_ac[i - 1]

    ## TIME DIFERENCE
    times = [0] * l
    FMT = '%Y-%m-%d %H:%M:%S'

    for d in data:
        # convert string time to date object
        d["time"] = datetime.strptime(d["shot_date"], FMT)

    for i in indexes0l:
        # calculate time difference
        times[i] = (data[i + 1]["time"] - data[i]["time"]).seconds

    ## INSTANT SPEED
    v_proj = [0]*l
    v_trig = [0]*l
    v_hav = [0]*l
    for i in indexes0l:
        tdelta = times[i]
        v_proj[i] = dist_proj[i]/tdelta
        v_trig[i] = dist_trig[i]/tdelta
        v_hav[i] = dist_hav[i]/tdelta

    ### PLOTS ###

    # prefix for saving the figure
    file_basename = re.split("/", file_path)[-1]
    fig_prefix = re.search("(.*)\\..*$", file_basename)[1] + "-"

    if (len(sys.argv) > 2):
        # if specified, save the fig to custom dir
        directory = re.sub("/$", "", sys.argv[2])
        fig_prefix = directory + "/" + fig_prefix

    # label for the plots
    labels = [
        "Método da projeção",
        "Método da fórmula de Haversine",
        "Método da trigonometria esférica",
    ]
    xlab = "pontos"

    # fig names
    v_fnames = [
        fig_prefix + "velocidades-proj.png",
        fig_prefix + "velocidades-hav.png",
        fig_prefix + "velocidades-trig.png",
        fig_prefix + "velocidades.png"
    ]
    dist_fnames = [
        fig_prefix + "distancias-proj.png",
        fig_prefix + "distancias-hav.png",
        fig_prefix + "distancias-trig.png",
        fig_prefix + "distancias.png"
    ]
    dist_ac_fnames = [
        fig_prefix + "distancia-total-proj.png",
        fig_prefix + "distancia-total-hav.png",
        fig_prefix + "distancia-total-trig.png",
        fig_prefix + "distancia-total"
    ]

    # y values
    v_ys = [v_proj, v_hav, v_trig]
    dist_ys = [dist_proj, dist_hav, dist_trig]
    dist_ac_ys = [dist_proj_ac, dist_hav_ac, dist_trig_ac]

    # plot time difference
    x = indexes0l
    y = times
    fname =  fig_prefix + "tempos.png"
    title = "Tempo decorrido entre pontos consecutivos"
    ylab = "tempo (s)"
    plot(x, y, fname, title, xlab, ylab, ylab)

    # plot speeds
    title = "Velocidade entre pares de pontos consecutivos"
    ylab = "velocidade (m/s)"
    plots(x, v_ys, v_fnames, title, xlab, ylab, labels)

    # plot consecutive distances
    title = "Distância entre pares de pontos consecutivos"
    ylab = "distância (m)"
    plots(x, dist_ys, dist_fnames, title, xlab, ylab, labels)

    # plot total distance
    title = "Distância total percorrida"
    x = indexes0L
    plots(x, dist_ac_ys, dist_ac_fnames, title, xlab, ylab, labels)

# call main
main()
exit(0)
