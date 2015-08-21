# -*- coding: utf-8 -*-
"""
Created on Mon Jul 06 14:59:54 2015

@author: eneidhart
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import csv
import pyodbc

anode_width = np.linspace(43.830769230769230769230769230769, -34.938461538461538461538461538462, 801).tolist()
anode_height = np.linspace(-66.31818181818181, 65.1969696969697, 1401).tolist()

cathode_width = np.linspace(45.66929133858268, -32.44094488188976, 801).tolist()
cathode_height = np.linspace(-65.81686046511628, 66.85755813953489, 1401).tolist()

def residual(a, b):
    # used with map() to subtract one data set from another
    if a == []:
        if b == []:
            return np.NaN
        else:
            return b
    elif b == []:
        return a
    else:
        return a - b

def main():
    global anode_width, anode_height, cathode_width, cathode_height
    
    cnxn_str =    """
    Driver={SQL Server Native Client 11.0};
    Server=24m-data01;
    Database=CellTestData;
    UID=sa;
    PWD=Welcome!;
    """
    
    cnxn = pyodbc.connect(cnxn_str)
    cnxn.autocommit = True
    cursor = cnxn.cursor()
    
    rootpath = r'C:\Users\eneidhart\Documents\Laser Test Data\150805-UlyssesVsAcuGage'
    filename = '22707_Raw_unpivot.csv'
    filepath = os.path.join(rootpath, filename)
    
    eid = filename.split("_")[0]
    
    anodes = ["22707", "22713", "22725", "22733", "22741"]
    cathodes = ["22717", "22720", "22728", "22738", "22745"]
    
    #scale for whole plot
    wpltMin = -0.2
    wpltMax = 0.6
    
    if eid in anodes:
        anode = True
        t = "Anode"
        #scale for "top" plot
        pltMin = 0.2
        pltMax = 0.4
        #edges
        l = 120
        r = 750
    elif eid in cathodes:
        anode = False
        t = "Cathode"
        pltMin = 0.3
        pltMax = 0.5
        l = 150
        r = 765
    else:
        #error
        raise
    
    print "Getting unpivoted Ulysses data"
    # Data files created by Tristan's script
    
    myfile = open(filepath, 'rb')
    reader = csv.reader(myfile)
    
    # all the data lists we'll use
    
    # stores x, y, z data from unpivoted Ulysses data
    x = []
    y = []
    z = []
    
    # stores Ulysses data retrieved from the database
    dx = []
    dz = []
    
    for row in reader:
        if 'X' in str(row[1]):
            print "Skipping headers"
            continue
        x.append(int(row[1]))
        y.append(int(row[2]))
        z.append(float(row[3]))
    
    myfile.close()
    del reader
    
    print len(x), len(y), len(z)
    print "Getting original Ulysses data"
    
    filename3 = "%s.csv" % eid
    filepath3 = os.path.join(rootpath, filename3)
    
    # One big 800 x 1400 array of Ulysses data
    raw = np.loadtxt(filepath3, delimiter=",", skiprows=2, unpack=True)
    
    # Keep plots from showing
    plt.ioff()
    
    print "Getting filtered Ulysses data from database"
    
    q = cursor.execute("SELECT LaserProfileID FROM ElectrodeLaserProfile WHERE UlyssesElectrodeID = ?", eid).fetchone()
    lpid = q.LaserProfileID
    
    q = cursor.execute("SELECT * FROM ElectrodeLaserSideProfileTD WHERE LaserProfileID = ?", lpid).fetchall()
    for row in q:
        if anode:
            dx.append(anode_width[int(row.Pos)])
        else:
            dx.append(cathode_width[int(row.Pos)])
        dz.append(row.Height)
    
    # This is where all the plot pictures are going to end up being saved
    fdir = r"C:\Users\eneidhart\Documents\Laser Test Data\Horizontal"
    
    for mid in ["Bot", "Mid", "Top"]:
        # once for each Acu-Gage scan
        
        # x2 and y2 are going to store the values in x and y, converted to mm
        # data is x2, y2, and z zipped together
        x2 = []
        y2 = []
        data = []    
        
        # acugage holds a zipped list of acugage x, y, and z coordinates
        acugage = []
    
        print "Getting AcuGage data"
        
        #construct filepath to acugage data
        filename21 = "150805-"
        filename22 = "Horz-"
        filename23 = "%s%s.csv" % (t, eid)
        filename2 = filename21 + mid + filename22 + filename23
        filepath2 = os.path.join(rootpath, filename2)
        myfile = open(filepath2, 'rb')
        reader = csv.reader(myfile)
        
        # read in acugage data as a zipped list
        # acugage xy coordinates need to be swapped; acugage x == ulysses Y
        for row in reader:
            acugage.append([float(row[5]), float(row[4]), float(row[6])])
        
        myfile.close()
        del reader
            
        print "converting Ulysses data"
        # convert ulysses x, y coordinates to mm
        
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
            try:
                data.append([x2[i], y2[i], z[i]])
            except:
                print len(x2), len(y2), len(z)
                print i
                raise
        
        # define position of acugage scan line
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
            
        # reduce Ulysses data to zipped x, y, z list of points that correspond with the acugage data
        pltdata = [[xval, yval, zval] for [xval, yval, zval] in data if h - 0.05 < yval < h + 0.05]
        
        # reduce original ulysses data to the row that corresponds best with the acugage data
        # rawx and rawz will be the original ulysses data to plot
        if anode:
            yval = anode_height.index(pltdata[0][1])
        else:
            yval = cathode_height.index(pltdata[0][1])
        
        
        rawz = [row[yval] for row in raw]
        rawx = []
        
        # convert original Ulysses data to mm
        for i in xrange(len(rawz)):
            if anode:
                j = anode_width[i]
            else:
                j = cathode_width[i]
            rawx.append(j)
        
        # unpivoted ulysses data to plot
        ux = [x1 for [x1, y1, z1] in pltdata]
        uz = [z1 for [x1, y1, z1] in pltdata]
        
        # acugage data to plot
        ax = [x1 for [x1, y1, z1] in acugage]
        az = [z1 for [x1, y1, z1] in acugage]
        
        # acugage data trimmed to edges, used for stats and correction
        acutop_plot = [[x1, z1] for [x1, y1, z1] in acugage if z1 > 0.17]
        if len(acutop_plot) >= r - l:
            print "Yes"
        else:
            print "Uh-oh"
        
        # ulysses data trimmed to edges, used for stats and correction
        ulysses_top = [[x1, z1] for [x1, y1, z1] in pltdata[l:r]]
        
        # unzipping
        utx = [x1 for [x1, z1] in ulysses_top]
        utz = [z1 for [x1, z1] in ulysses_top]
        
        bins = [[] for a in ulysses_top]
        agz = [[] for a in ulysses_top]
        
        # sorting acugage data into bins for easy correction
        for [x1, z1] in acutop_plot:
            bins[utx.index(min(utx, key = lambda c: abs(c - x1)))].append(z1)
        
        # taking mean of each bin
        for n, b in enumerate(bins):
            if len(b) >= 1:
                agz[n] = np.mean(b)
        
#        for num in agz:
#            if num == []:
#                print "Y:", num
#            else:
#                print "X:", num
        
        # subtract plots for correction, then apply correction
        residual_plot = map(residual, utz, agz)
        
        fixed_ulysses = map(residual, utz, residual_plot)
        
        acutop = [z1 for [x1, z1] in acutop_plot]
        
        title = "%s %s %s" % (eid, filename2.split("-")[1], filename2.split("-")[2][:-9])
        
        # stats for plots
        u0 = "Zeroed Ulysses:\nmin: %5.3f     max: %5.3f     dev: %5.3f" % (np.min(uz[l:r]), np.max(uz[l:r]), np.std(uz[l:r]))
        u1 = "Standard Ulysses:\nmin: %5.3f     max: %5.3f     dev: %5.3f" % (np.min(rawz[l:r]), np.max(rawz[l:r]), np.std(rawz[l:r]))
        ag = "Acu-Gage:\nmin: %5.3f      max: %5.3f     dev: %5.3f" % (np.min(acutop), np.max(acutop), np.std(acutop))
        
        #lbl = headers + u0 + u1+ ag
        
        print "plotting", len(pltdata), len(data)
        
        f = plt.figure(1)
        plt.clf()
        fname = "%s_%sHorz_%s_Whole.png" % (eid, mid, t)
        fpath = os.path.join(fdir, fname)
        
        a = f.add_subplot(111)
        a.set_title(title)
        f.text(0.0, 0.0, u0)
        f.text(0.5, 0.0, u1)
        f.text(1.0, 0.0, ag)
        #a.set_ylim([wpltMin, wpltMax])
        a.plot(rawx, rawz, 'g.')
        a.plot(ux, uz, 'b.')
        a.plot(ax, az, 'r.')
        a.plot(utx, fixed_ulysses, 'yo')
        a.plot(dx, dz, 'wd', mec = "k", mew = 2)
        
        plt.savefig(fpath, bbox_inches='tight')
        
        g = plt.figure(2)
        plt.clf()
        fname = "%s_%sHorz_%s_Top.png" % (eid, mid, t)
        fpath = os.path.join(fdir, fname)
        
        a1 = g.add_subplot(111)
        a1.set_title(title)
        g.text(0.0, 0.0, u0)
        g.text(0.5, 0.0, u1)
        g.text(1.0, 0.0, ag)
        a1.set_ylim([pltMin, pltMax])
        a1.plot(rawx, rawz, 'g.')
        a1.plot(ux, uz, 'b.')
        a1.plot(ax, az, 'r.')
        a1.plot(utx, fixed_ulysses, 'yo')
        a1.plot(dx, dz, 'wd', mec = "k", mew = 2)
        
        plt.savefig(fpath, bbox_inches='tight')
        

if __name__ == "__main__":
    main()
    