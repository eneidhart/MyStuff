# -*- coding: utf-8 -*-
"""
Created on Mon Jul 06 14:59:54 2015

@author: eneidhart
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import csv
from scipy.signal import savgol_filter as savgol

anode_width = np.linspace(43.830769230769230769230769230769, -34.938461538461538461538461538462, 801).tolist()
anode_height = np.linspace(-66.31818181818181, 65.1969696969697, 1401).tolist()

cathode_width = np.linspace(45.66929133858268, -32.44094488188976, 801).tolist()
cathode_height = np.linspace(-65.81686046511628, 66.85755813953489, 1401).tolist()


def main():
    global anode_width, anode_height, cathode_width, cathode_height
    
    rootpath = r'C:\Users\eneidhart\Documents\Laser Test Data\150805-UlyssesVsAcuGage'
    filename = '22707_Raw_unpivot.csv'
    filepath = os.path.join(rootpath, filename)
    
    anodes = ["22707", "22713", "22725", "22733", "22741"]
    cathodes = ["22717", "22720", "22728", "22738", "22748"]
    
    myfile = open(filepath, 'rb')
    reader = csv.reader(myfile)
    allpoints = []
    x = []
    y = []
    z = []
    
    x2 = []
    y2 = []
    data = []
    
    acugage = []
    
    for row in reader:
        if 'X' in str(row[1]):
            print "Skipping headers"
            continue
        allpoints.append([float(row[1]), float(row[2]), float(row[3])])
        x.append(int(row[1]))
        y.append(int(row[2]))
        z.append(float(row[3]))
    
    myfile.close()
    del reader
    
    print "Getting AcuGage data"
    
    filename2 = "150805-BotHorz-Anode%s.csv" % (filename.split("_")[0])
    filepath2 = os.path.join(rootpath, filename2)
    myfile = open(filepath2, 'rb')
    reader = csv.reader(myfile)
    
    for row in reader:
        acugage.append([float(row[5]), float(row[4]), float(row[6])])
    
    myfile.close()
    del reader
        
    print "converting Ulysses data"
    
    if filename.split("_")[0] in anodes:
        anode = True
    elif filename.split("_")[0] in cathodes:
        anode = False
    else:
        raise
    
    for i in x:
        if anode:
            j = anode_width[i]
        else:
            j = cathode_width[i]
        x2.append(j)
        
    for i in y:
        if anode:
            j = anode_height[i]
        else:
            j = cathode_height[i]
        y2.append(j)
        
    for i in xrange(len(y2)):
        data.append([x2[i], y2[i], z[i]])
    
    if "Bot" in filename2:
        h = 42.65
    elif "Top" in filename2:
        h = -51.24
    elif "Left" in filename2:
        h = -20.62
    elif "Right" in filename2:
        h  = 19.1
    elif "MidHorz" in filename2:
        h = -3.45
    elif "MidVert" in filename2:
        h = 0.39
    else:
        raise
    pltdata = [[xval, yval, zval] for [xval, yval, zval] in data if h - 0.05 < xval < h + 0.05]
    
    print "Getting raw Ulysses data"
    
    filename3 = "%s.csv" % filename.split("_")[0]
    filepath3 = os.path.join(rootpath, filename3)
    
    raw = np.loadtxt(filepath3, delimiter=",", skiprows=2, unpack=True)
    
    if anode:
        xval = anode_height.index(pltdata[0][0])
    else:
        xval = cathode_height.index(pltdata[0][0])
    
    rawz = raw[xval]
    rawx = []
    
    for i in xrange(len(rawz)):
        if anode:
            j = anode_width[i]
        else:
            j = cathode_width[i]
        rawx.append(j)
    
    
    
    #filt = savgol([z1 for [x1, y1, z1] in pltdata], 15, 8)
    
    uy = [y1 for [x1, y1, z1] in pltdata]
    uz = [z1 for [x1, y1, z1] in pltdata]
    
    ay = [y1 for [x1, y1, z1] in acugage]
    az = [z1 for [x1, y1, z1] in acugage]
    
    acutop = [z1 for z1 in az if z1 > 0.17]
    
    if anode:
        l = 
        r = 
    else:
        l = 
        r = 
    
    title = "%s %s %s" % (filename.split("_")[0], filename2.split("-")[1], filename2.split("-")[2][:-9])
    
    u0 = "Zeroed Ulysses:\nmin: %5.3f     max: %5.3f     dev: %5.3f" % (np.min(uz[l:r]), np.max(uz[l:r]), np.std(uz[l:r]))
    u1 = "Standard Ulysses:\nmin: %5.3f     max: %5.3f     dev: %5.3f" % (np.min(rawz[l:r]), np.max(rawz[l:r]), np.std(rawz[l:r]))
    ag = "Acu-Gage:\nmin: %5.3f      max: %5.3f     dev: %5.3f" % (np.min(acutop), np.max(acutop), np.std(acutop))
    
    #lbl = headers + u0 + u1+ ag
    
    print "plotting", len(pltdata), len(data)
    
    f = plt.figure(1)
    g = plt.figure(2)
    
    a = f.add_subplot(111)
    a.set_title(title)
    f.text(0.12, 0.05, u0)
    f.text(0.44, 0.05, u1)
    f.text(0.77, 0.05, ag)
    #a.set_ylim([0.2, 0.4])
    a.plot(rawx, rawz, 'g.')
    a.plot(uy, uz, 'b.')
    a.plot(ay, az, 'r.')
    
    a1 = g.add_subplot(111)
    a1.set_title(title)
    g.text(0.12, 0.05, u0)
    g.text(0.44, 0.05, u1)
    g.text(0.77, 0.05, ag)
    a1.set_ylim([0.3, 0.5])
    a1.plot(rawx, rawz, 'g.')
    a1.plot(uy, uz, 'b.')
    a1.plot(ay, az, 'r.')
    
    plt.show()

## set up filenames
#filename = '22707_Raw_unpivot.csv'
#rootpath = r'C:\Users\eneidhart\Documents\Laser Test Data\150805-UlyssesVsAcuGage'
##filename = '21539.csv'
##rootpath = r'C:\Users\tdoherty\Documents\Work\Projects\Sandbox Python'
#filepath = os.path.join(rootpath, filename)
#
##load raw data
#print '---------Read File---------'
#myfile = open(filepath, 'rb')
#reader = csv.reader(myfile)
#data = []
#x = []
#y = []
#z = []
#
#for row in reader:
#    if 'X' in str(row[1]) or 'X' in str(row[2]):
#        continue
#    data.append(row[1:4])
#
#for row in data:
#    x.append(float(row[0]))
#    y.append(float(row[1]))
#    z.append(float(row[2]))
#
#threedee = plt.figure().gca(projection='3d')
#threedee.set_xlim(-300,1100)
#threedee.set_ylim(0,1400)
#threedee.set_zlim(-.2,.8)
#threedee.scatter(x, y, z, c = z, marker = '.')
#plt.show()

#x = np.NaN
#
#y = np.NaN
#
#if x is y:
#    print 'yes'
#else:
#    print 'no'

if __name__ == "__main__":
    main()
    
