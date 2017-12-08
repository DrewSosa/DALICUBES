"""This module plots the FSPC Values for the payloads of the BARREL Campaign
@Andrew Sosanya, Dartmouth' 20 ~~~Email Sosa.20@dartmouth.edu with any questions."""

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


#we could probably just lump everything into one function.
def fspc_plot(balloon, payload, date):
    """Function to plot data from the balloons and Van Allen Probes"""
    print "WTF"

    cdf = pycdf.CDF(balloon)

    #then grab the data we want
    time = cdf['Epoch'][...]



    my_fmt = mdates.DateFormatter('%H:%M')

    #Let's plot FSPC 1 & 2

    axis1 = plt.subplot2grid((3, 3), (0, 0), colspan=4)
    axis2 = plt.subplot2grid((3, 3), (1, 0), colspan=4)
    axis3 = plt.subplot2grid((3, 3), (2, 0), colspan=4)
    plots = [axis1, axis2, axis3]
    plots[0].xaxis.set_major_formatter(my_fmt)
    plots[1].xaxis.set_major_formatter(my_fmt)
    plots[2].xaxis.set_major_formatter(my_fmt)
    plots[0].set_title(payload +"--" +str(date))

    #limits?
    #plots[0].set_ylim(3, 20)
    axis1.set_ylabel("FSPC1")
    axis2.set_ylabel("FSPC2")
    axis3.set_ylabel("FSPC3")

    if int(date[:4]) < 2016:
        balloon_fspc1a = cdf['FSPC1a'][...]

        balloon_fspc1b = cdf['FSPC1b'][...]

        balloon_fspc1c = cdf['FSPC1c'][...]
        plots[0].plot(time, balloon_fspc1a, "g.")
        plots[0].plot(time, balloon_fspc1b, "g.")
        plots[0].plot(time, balloon_fspc1c, "g.")
    else:
        balloon_fspc1 = cdf['FSPC1'][...]
        plots[0].plot(time, balloon_fspc1, "g.")

    balloon_fspc2 = cdf['FSPC2'][...]
    balloon_fspc3 = cdf['FSPC3'][...]
    plots[1].plot(time, balloon_fspc2, "r.")
    plots[2].plot(time, balloon_fspc3, "y.")
    cdf.close()

    plots[0].legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)
    plt.draw()
    newpath = r'/Users/sosa/research/fspc_plots/'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    plt.savefig(newpath+str(date)+"-"+payload)
    # have it so that it saves the image only and does not show it.
    # plt.show()
    # #(block=False)




def plot_twist(path,payload):
    """Function to plot data from the balloons and Van Allen Probes"""


    cdf = pycdf.CDF(path)

    #then grab the data we want
    time = cdf['Epoch'][...]
    balloon_fspc1 = cdf['FSPC1'][...]

    balloon_fspc2 = cdf['FSPC2'][...]

    balloon_fspc3 = cdf['FSPC3'][...]
    cdf.close()

    my_fmt = mdates.DateFormatter('%H:%M')

    #Let's plot FSPC 1 & 2

    axis1 = plt.subplot2grid((3, 3), (0, 0), colspan=4)
    axis2 = plt.subplot2grid((3, 3), (1, 0), colspan=4)
    axis3 = plt.subplot2grid((3, 3), (2, 0), colspan=4)
    plots = [axis1, axis2, axis3]
    plots[0].xaxis.set_major_formatter(my_fmt)
    plots[1].xaxis.set_major_formatter(my_fmt)


    #limits?
    #plots[0].set_ylim(3, 20)
    axis1.set_ylabel("FSPC1")
    axis2.set_ylabel("FSPC2")
    axis3.set_ylabel("FSPC3")

    plots[0].plot(time, balloon_fspc1, "g.")
    plots[1].plot(time, balloon_fspc2, "r.")
    plots[2].plot(time, balloon_fspc3, "y.")

    map(lambda x: x.set_yscale('log'), plots)

    plots[0].legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)
    plt.draw()
    newpath = r'/Users/sosa/research/fspc_plots/'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    plt.savefig(newpath+str(20130123)+"-"+payload)
    #have it so that it saves the image only and does not show it.

    #(block=False)
# plot_twist("/Users/sosa/research/fspc/bar_1C_l2_fspc_20130123_v05.cdf","1C")
# plot_twist("/Users/sosa/research/fspc/bar_1I_l2_fspc_20130123_v05.cdf","1I")
# plot_twist("/Users/sosa/research/fspc/bar_1G_l2_fspc_20130123_v05.cdf","1G")
# plot_twist("/Users/sosa/research/fspc/bar_1H_l2_fspc_20130123_v05.cdf","1H")
# plot_twist("/Users/sosa/research/fspc/bar_1Q_l2_fspc_20130123_v05.cdf","1Q")
# plot_twist("/Users/sosa/research/fspc/bar_1R_l2_fspc_20130123_v05.cdf","1R")
# plot_twist("/Users/sosa/research/fspc/bar_1S_l2_fspc_20130123_v05.cdf","1S")


