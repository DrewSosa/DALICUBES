""""This module reads in RBSP Ephemeris files produced by ECT LANL team
and plots magnetic conjunctions of the payloads on a given date
 and the Van Allen Probes (Mageis), saves them to
a local disk, and produces a document listing the conjunctions.
Dartmouth Balloon Group
@Andrew Sosanya, Dartmouth '20.~~~Email Sosa.20@dartmouth.edu with any questions."""
import os
import time
import bisect
import datetime
import urllib

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import numpy.ma as ma
from spacepy import pycdf
from scipy import interpolate
import globalvariables



 # ---- Andrew's plot of magnetic conjunctions -----
#
#
# --------------------------------------------------#

def generalX(balloon, mageis_a, mageis_b, payload, date):
    global jointcounter
    """Function to plot data from the balloons and Van Allen Probes"""

    mageis = [mageis_a, mageis_b]

    graphed = [balloon, mageis_a, mageis_b]

    cdf = pycdf.CDF(graphed[0])

    #then grab the data we want
    time = cdf['Epoch'][...]
    L_Balloon = cdf['L_Kp2'][...]

    #[start_ind:stop_ind]
    mlt_3A = cdf['MLT_Kp2_T89c'][...]
    cdf.close()



    myFmt = mdates.DateFormatter('%H:%M')
    axis = plt.subplot2grid((2, 1), (0, 0))
    axis1 = plt.subplot2grid((2, 1), (1, 0))
    plots = [axis, axis1]
    plots[0].xaxis.set_major_formatter(myFmt)
    plots[1].xaxis.set_major_formatter(myFmt)
    plots[0].set_title(payload +"--" +str(date))


    #-----for the general case, shall we keep the limits the same, or generalize it

    plots[0].set_ylim(3, 10)
    plots[1].set_ylim(0, 24)

    #====

    plots[0].plot(time, L_Balloon, 'r.', label='balloon') # Balloon L-values in red
    plots[0].set_xlabel('UT')
    plots[0].set_ylabel('L-T89', color='red')

    plots[1].plot(time, mlt_3A, 'r.') # Balloon MLT in red
    plots[1].set_ylabel('MLT-T89', color='blue')

    for j in range(1, 3):
        #read in CDF

        cdf = pycdf.CDF(graphed[j])


        # then grab the data we want


        # get time range indices for this file
        start = datetime.datetime(2015, 8, 10, 14, 0, 0, 0)
        stop = datetime.datetime(2015, 8, 10, 18, 0, 0, 0)
        start_ind = bisect.bisect_left(cdf['Epoch'], start)
        stop_ind = bisect.bisect_left(cdf['Epoch'], stop)

        time_m = cdf['Epoch'][...]
        l_mageis = cdf['L'][...]

        mlt_mageis = cdf['MLT'][...]
        cdf.close()

        myFmt = mdates.DateFormatter('%H:%M')

        #mageis A in green
        if j == 1:
            plots[0].plot(time_m, l_mageis, 'g.')
            plots[1].plot(time_m, mlt_mageis, 'g.')
            #mageis B in yellow
        if j == 2:

            plots[0].plot(time_m, l_mageis, 'y.')
            plots[1].plot(time_m, mlt_mageis, 'y.')

         #===========L=============#

        l_intersection = intersection_L(time_m, time, l_mageis, L_Balloon)
        #plot the intersecting L -values in blue

        if l_intersection != None: # make sure we have a value
            for pair in range(0, len(l_intersection) - 1):
            #access the tuple and plot the intersections in blue
                # First Van Allen probe MLT plot intersections in blue dots.
                if j == 1:
                    plots[0].plot(l_intersection[pair][0], l_intersection[pair][1], 'b.')

                if j == 2:
                # second Van Allen probe MLT plot intesection in blue pluses
                    plots[0].plot(l_intersection[pair][0], l_intersection[pair][1], 'b+')

         #===========MLT=============#

        #plot the intersecting MLT -values in purple
        mlt_intersection = intersection_MLT(time_m, time, mlt_mageis, mlt_3A)
        if mlt_intersection != None: # make sure we have a value
            for pair in range(0, len(mlt_intersection) - 1):
                #access the tuple and plot the intersections in blue
                if j == 1:
                    plots[1].plot(mlt_intersection[pair][0], mlt_intersection[pair][1], 'b.')
                if j == 2:
                    plots[1].plot(mlt_intersection[pair][0], mlt_intersection[pair][1], 'b+')


        pair = joint_intersection(time_m, time, L_Balloon, l_mageis, mlt_3A, mlt_mageis)
        pair.spliced()
        joint_report(j, pair, date, payload, "joint.txt")

        if len(xsplicer(l_intersection)) > 1:

            spliced_report(j, xsplicer(l_intersection), date, payload, "multitest.txt", "L")
            spliced_report(j, xsplicer(l_intersection), date, payload, "Lconj.txt", "L")
        else:

            report(j, l_intersection, date, payload, "multitest.txt", "L")
            report(j, l_intersection, date, payload, "Lconj.txt", "L")
        if len(xsplicer(mlt_intersection)) > 1:

            spliced_report(j, xsplicer(mlt_intersection), date, payload, "multitest.txt", "MLT")
            spliced_report(j, xsplicer(mlt_intersection), date, payload, "MLTconj.txt", "MLT")
        else:

            report(j, mlt_intersection, date, payload, "multitest.txt", "MLT")
            report(j, mlt_intersection, date, payload, "MLTconj.txt", "MLT")


  #========making the plots ===========#
    plots[0].legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)
    plt.draw()
    newpath = r'/Users/sosa/research/plots/'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    plt.savefig(newpath+str(date)+"-"+payload)
    #have it so that it saves the image only and does not show it.
    #plt.show(block=False)



#==========intersection functions==============

def xsplicer(intersection_list):
    """Function that splices a list of conjunction using the criteria
    that conjunctions should be 60 minutes or more apart one another
    to be considered seperate."""

    if len(intersection_list) < 14:
        return []
    spliced = []
    last_splice_index = 0
    for i in xrange(len(intersection_list)-2):

        if (intersection_list[i+1][0]-intersection_list[i][0]).seconds > 3600:
            spliced.append(intersection_list[last_splice_index:i])
            last_splice_index = i+1
    # add last portion of the list

    spliced.append(intersection_list[last_splice_index:])
    if len(spliced) > 1:
        return spliced
    else:
        return []
    #after this,when plotting , one should do a for-loop that plots the spliced list



def intersection_L(time, time_3A, L1, L2):
    """looks for times and valueswithin a certain threshold of each other respectively;
    returns a list of tuples that contain points of approximate intersections"""
    points = []
    for t_time in range(0, len(time) - 1, 30):
        for  t_time3A in range(0, len(time_3A) - 1, 30):
            if abs(time[t_time] - time_3A[t_time3A]).seconds < 300:
                if abs(L1[t_time] - L2[t_time3A]) < .25:
                    point = (time[t_time], L1[t_time])
                    points.append(point)
    return points

def intersection_MLT(time, time_3A, MLT1, MLT2):
    """looks for times within a certain threshold of each other,
     and checks if their values are within a certain thershold of each other.
     returns a list of tuples that contain points of approximate intersections"""
    points = []
    for t_time in range(0, len(time) - 1, 30):
        for  t_time3A in range(0, len(time_3A) - 1, 30):
            if abs(time[t_time] - time_3A[t_time3A]).seconds < 300:

                if abs(MLT1[t_time] - MLT2[t_time3A]) < 1:
                    point = (time[t_time], MLT1[t_time])
                    points.append(point)

    return points



#create a list to hold all of these joint points
class JointPoint(object):

    """How JointPoint works: three lists, to record time,
    L values, and MLT values. Append puts the points in their corres-
    ponding lists, and splice officiates each conjunction"""

    def __init__(self):
        self.time_list = []
        self.mlt_list = []
        self.l_list = []

        self.spliced_time_conj = []
        self.spliced_l_conj = []
        self.spliced_mlt_conj = []

    def append(self, time, l_value, mlt_value):
        """keeps three seperate lists"""
        self.time_list.append(time)
        self.l_list.append(l_value)
        self.mlt_list.append(mlt_value)

    def isSpliced(self):
        if len(self.spliced_time_conj) != 0:
            return True
        else:
            return False

    def spliced(self):

        if len(self.time_list) < 14:
            return -1
        spliced = []
        last_splice_index = 0
        for i in xrange(len(self.time_list)-2):

            if (self.time_list[i+1]- self.time_list[i]).seconds > 3600:
                self.spliced_time_conj.append(self.time_list[last_splice_index:i])
                self.spliced_l_conj.append(self.l_list[last_splice_index:i])
                self.spliced_mlt_conj.append(self.mlt_list[last_splice_index:i])
                last_splice_index = i+1


        # add last portion of the list

        self.spliced_time_conj.append(self.time_list[last_splice_index:i])
        self.spliced_l_conj.append(self.l_list[last_splice_index:i])
        self.spliced_mlt_conj.append(self.mlt_list[last_splice_index:i])


    def conj_elapsed_seconds(self, conj):
        """elapsed seconds"""
        return (conj[-1]-conj[0]).seconds
    def elapsed_seconds(self):
        """elapsed seconds"""
        return (self.time_list[-1] - self.time_list[0]).seconds

def joint_intersection(time, time_3A, l_balloon, l_mageis, mlt_balloon, mlt_mageis):

    """looks for times within a certain threshold of each other L and MLT values
    and checks if their values are within a certain thershold of each other.
    returns a JointPoint that contains the list of joint conjunctions"""
    joint_point = JointPoint()
    for t_time in range(len(time)-2):
        for  t_time3A in range(len(time_3A)-2):
            if abs(time[t_time] - time_3A[t_time3A]).seconds < 300:
                if abs(mlt_mageis[t_time] - mlt_balloon[t_time3A]) < 1 \
                      and abs(l_mageis[t_time] - l_balloon[t_time3A]) < .25:

                        joint_point.append(time[t_time], l_balloon[t_time], mlt_balloon[t_time])



    return joint_point


def joint_report(j, jointpoint, date, payload, filename):

    """To a given file, prints out conjunctions where there are both MLT and L conjunctions.
    Utilizes the JointPoint class."""
    file = open(filename, "a")

    if jointpoint.spliced_l_conj > 1:
        globalvariables.joint_conj_counter += len(jointpoint.spliced_l_conj)

        for time_conj, l_conj, mlt_conj in \
        zip(jointpoint.spliced_time_conj, jointpoint.spliced_l_conj, jointpoint.spliced_mlt_conj):

            if j == 1:
                column = [date, payload, "Mageis-A", "L & MLT", str(l_conj[0]),
                        str(l_conj[-1]), str(mlt_conj[0]),
                        str(mlt_conj[-1]), str(time_conj[0].time().hour) + ":" +
                        str(time_conj[0].time().minute) +" TO "+
                        str(time_conj[-1].time().hour) + ":" +
                        str(time_conj[-1].time().minute),
                        str(jointpoint.conj_elapsed_seconds(time_conj))]

            else:
                column = [date, payload, "Mageis-B", "L & MLT", str(l_conj[0]),
                        str(l_conj[-1]), str(mlt_conj[0]),
                        str(mlt_conj[-1]), str(time_conj[0].time().hour) + ":" +
                        str(time_conj[0].time().minute) +" TO "+
                        str(time_conj[-1].time().hour) + ":" +
                        str(time_conj[-1].time().minute),
                        str(jointpoint.conj_elapsed_seconds(time_conj))]

            for i in xrange(len(column)):
                file.write(column[i] + "\t")
            file.write("\n")
    else:
        print "does not enter spliced"
        globalvariables.joint_conj_counter += 1
        if j == 1:
            column = [date, payload, "Mageis-A", "Range: L & MLT", str(jointpoint.l_list[0]),
                      str(jointpoint.l_list[-1]), str(jointpoint.mlt_list[0]),
                      str(jointpoint.mlt_list[-1]), str(jointpoint.time_list[0].time().hour) + ":" +
                      str(jointpoint.time_list[0].time().minute) + " TO " +
                      str(jointpoint.time_list[-1].time().hour) + ":" +
                      str(jointpoint.time_list[-1].time().minute),
                      str(jointpoint.elapsed_seconds())]

        else:
            column = [date, payload, "Mageis-B", "Range: L & MLT", str(jointpoint.l_list[0]),
                      str(jointpoint.l_list[-1]), str(jointpoint.mlt_list[0]),
                      str(jointpoint.mlt_list[-1]), str(jointpoint.time_list[0].time().hour) + ":" +
                      str(jointpoint.time_list[0].time().minute) + " TO " +
                      str(jointpoint.time_list[-1].time().hour) + ":" +
                      str(jointpoint.time_list[-1].time().minute),
                      str(jointpoint.elapsed_seconds())]



        for i in xrange(len(column)):
            file.write(column[i] + "\t")
        file.write("\n")




    file.close()


def elapsedsecs(conj):
    """ returns number of elapsed seconds of a conjunction """
    return (conj[len(conj)-2][0]-conj[0][0]).seconds


def report(j, list, date, payload, filename, valname):
    """prints out a transposed column of data to desired file"""

    if len(list) > 1:
        if j == 1:
            column = [date, payload, "Mageis-A", valname, str(list[0][1]),
                      str(list[len(list)-1][1]), str(list[0][0].time().hour) + ":" +
                      str(list[0][0].time().minute) + " TO " +
                      str(list[len(list)-1][0].time().hour) + ":" +
                      str(list[len(list)-1][0].time().minute), str(elapsedsecs(list))]

        else:
            column = [date, payload, "Mageis-B", valname, str(list[0][1]),
                      str(list[len(list)-1][1]), str(list[0][0].time().hour) + ":" +
                      str(list[0][0].time().minute) +" TO "+
                      str(list[len(list)-1][0].time().hour) + ":" +
                      str(list[len(list)-1][0].time().minute), str(elapsedsecs(list))]

        file = open(filename, "a")
        for i in xrange(len(column)):
            file.write(column[i] + "\t")
        file.write("\n")
        file.close()


def spliced_report(j, spliced, date, payload, filename, valname):
    """FOr multiple conjunctions: prints out a transposed column of data to desired file """
    file = open(filename, "a")

    for conj in spliced:
    #prints out a transposed column of data.

        if len(conj) > 1:
            if j == 1:
                column = [date, payload, "Mageis-A", valname, str(conj[0][1]), str(conj[-1][1]),
                          str(conj[0][0].time().hour) + ":" + str(conj[0][0].time().minute) +" TO "+
                          str(conj[-1][0].time().hour) + ":" + str(conj[-1][0].time().minute),
                          str(elapsedsecs(conj))]

            else:
                column = [date, payload, "Mageis-B", valname, str(conj[0][1]),
                          str(conj[len(conj)-1][1]), str(conj[0][0].time().hour) + ":" +
                          str(conj[0][0].time().minute) + " TO "+
                          str(conj[len(conj)-1][0].time().hour) + ":" +
                          str(conj[len(conj)-1][0].time().minute),
                          str(elapsedsecs(conj))]

            for i in xrange(len(column)):
                file.write(column[i]+ "\t")
            file.write("\n")
    file.close()
