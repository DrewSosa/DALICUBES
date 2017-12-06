#Andrew Sosanya, Dartmouth Balloon Group, BARREL RBSP.
#Last updated October 12, 2017.
from balloonplotter import *
import os
import httplib2
import urllib
from FSPC_Plot import fspc_plot
from globalvariables import POINT_COUNTER

link = 'http://barreldata.ucsc.edu/data_products/'
version = "v05"
level = "l2"
maglevel = "level3"
downloadpayloads = "/Users/sosa/research/payloads/"
downloadmageis = "/Users/sosa/research/mageis/"
downloadto_fspc = "/Users/sosa/research/fspc/"
#mageis data is split into two parts to effectively construct link
#assume that we will be using level three data, if not change mageis base
#mageisbase = "https://rbsp-ect.lanl.gov/data_pub/rbspa/mageis/level3/pitchangle/2016/rbspa_rel03_ect-mageis-L3"
mageisbase = "https://rbsp-ect.lanl.gov/data_pub/rbspa/mageis/level3/pitchangle"
mageisbaseB= "https://rbsp-ect.lanl.gov/data_pub/rbspb/mageis/level3/pitchangle"
mageismid = "rbspa_rel03_ect-mageis-L3"
mageismidB = "rbspb_rel03_ect-mageis-L3"
mageis_aversion = "v7.3.0"
mageis_bversion ="v7.0.0"

#pass in textfile, with columns
def maptime2payload(textfile):
    # -----------------------------------------------
    # Create dictionary of payloads for each date
    #------------------------------------------------
    data = np.genfromtxt(textfile, dtype=['S8', 'S20'], names=True)

    return dict(zip(data['Date'], data['Payloads']))

#takes in a string
def constructURL(date,payload):
    return link+version+"/"+level+"/"+payload+"/"+date[2:]+"/bar_" \
    + payload+ "_"+ level +"_ephm_"+date+"_"+version+".cdf"

def linkexists(link):
    h = httplib2.Http()
    resp = h.request(link, 'HEAD')
    if int(resp[0]['status']) > 400:
        return False
    else: return True

def downloadto(link, location):
    filename = link[58:]
    urllib.urlretrieve(link, location + filename)
    return location + filename



def downloadmageis_to(link, location):
    filename = link[71:]
    urllib.urlretrieve(link, location + filename)
    return location + filename


def constructmageis_aURL(date):
     #splice the date
     year = "/" + date[0:4] + "/"
     if linkexists(mageisbase+ year + mageismid+"_"+date+"_"+mageis_aversion+".cdf"):

         return mageisbase+year+"rbspa_rel03_ect-mageis-L3"+"_"+date+"_"+mageis_aversion+".cdf"

def constructmageis_bURL(date):
    year = "/" + date[0:4] + "/"
    ##====+EXCEPTIIONS=====harcoded====#

    # 20140211 not work??

    if int(date) in (20140211, 20140116, 20140114, 20140122, 20140202,
                    20140211, 20150813, 20150818, 20150821, 20140103):


        return mageisbaseB+year+"rbspb_rel03_ect-mageis-L3"+"_"+date+"_"+"v7.1.0"+".cdf"
    else:
        if linkexists(mageisbase+"_"+date+"_"+mageis_bversion+".cdf"):

            return mageisbaseB+year+"rbspb_rel03_ect-mageis-L3"+"_"+date+"_"+mageis_bversion+".cdf"





#======== FSPC PLOT METHODS =========#
def construct_fspc_link(date, payload):
    """this function creates and returns a link for downloading
    FSPC data"""
    link = ("http://barreldata.ucsc.edu/data_products/v05/l2/"
            + payload + "/" + date[2:] + "/bar_" + payload
            + "_l2_fspc_" + date + "_v05.cdf")
    print link
    return link


def download_fspc(date, payload, link, location):
    """for the purposes of simplicity, we will keep
    fspc plots in a seperate path and just name t
    hem by their payload and date. This function
    downloads the file to a users computer."""
    filename = date + "-" + payload + ".cdf"
    urllib.urlretrieve(link, location + filename)
    return location + filename



def bigmain():
    run = True
    while run:
        #ideally, I would want to have the user input the name of a text file.
        payload_dict = maptime2payload("which_payloads.txt")
        date = raw_input('Starting date (YYYYMMDD), e.g 20130201 for February 1, 2013: ')
        #algorithm s.t we can avoid the pitfalls of the payload
        #dictionary coming in a char array rather than a list.
        for i in range(0, len(payload_dict.get(date)) - 1, 3):
            print "Processing Payloads: "+ payload_dict.get(date)
            print "Currently on: " + payload_dict.get(date)[i: i+2]
            if not linkexists(constructURL(date, payload_dict.get(date)[i: i+2])):
                print "sorry, file does not exist in " + constructURL(date, payload_dict.get(date)[i:i+2])
                if "y" == raw_input("Restart program y/n? "):
                    return
                return main()
            #download CDFs from the internet, store them in a local file, and delete.

            localballoon = downloadto(constructURL(date,payload_dict.get(date)[i:i+2] ),downloadpayloads)
            print "Link for Payload " +payload_dict.get(date)[i: i+2] + " is: " + constructURL(date,payload_dict.get(date)[i:i+2])
            if i == 0:
                localmageis_a = downloadmageis_to(constructmageis_aURL(date), downloadmageis)
                localmageis_b = downloadmageis_to(constructmageis_bURL(date), downloadmageis)
            generalX(localballoon, localmageis_a, localmageis_b, payload_dict.get(date)[i:i+2], date)
            print POINT_COUNTER
            os.remove(localballoon)
            #ideally, i would like the user to decide if they want to
            #delete the file or not.
        if "n" == raw_input("Delete Mageis and Ephemeris files? y/n: "):
            os.remove(localmageis_a) ; os.remove(localmageis_b)
        print "Check output for direct links to ballon Ephermeris files."
        if "y" == raw_input("Stop program? y/n: "):
            run = False



bigmain()


def main():
    global POINT_COUNTER
    """Main function that, given a date, downloads
    the respective payloads and amgeis data to plot the ephemeris data"""
    payload_dict = maptime2payload("which_payloads.txt")
    #date = raw_input('Starting date (YYYYMMDD), e.g 20130201 for February 1, 2013: ')
    #algorithm s.t we can avoid the pitfalls of the payload
    #dictionary coming in a char array rather than a list.
    for key in payload_dict.keys():
        for i in range(0, len(payload_dict.get(key)) - 1, 3):
            print "Processing Payloads on " + key  + " : " + payload_dict.get(key)
            print "Currently on: " + payload_dict.get(key)[i: i+2]
            if not linkexists(constructURL(key, payload_dict.get(key)[i: i+2])):
                print ("sorry, file does not exist in " +
                       constructURL(key, payload_dict.get(key)[i:i+2]))
                if "y" == raw_input("Restart program y/n? "):
                    return
                return main()
            #download CDFs from the internet, store them in a local file, and delete.

            localballoon = downloadto(constructURL(key, payload_dict.get(key)[i:i+2]), downloadpayloads)

            print ("Link for Payload " + payload_dict.get(key)[i: i+2] +
                   " is: " + constructURL(key, payload_dict.get(key)[i:i+2]))
            if i == 0:
                localmageis_a = downloadmageis_to(constructmageis_aURL(key), downloadmageis)
                localmageis_b = downloadmageis_to(constructmageis_bURL(key), downloadmageis)
            generalX(localballoon, localmageis_a, localmageis_b, payload_dict.get(key)[i:i+2], key)
            print POINT_COUNTER, "SOSA"
            os.remove(localballoon)
            #ideally, i would like the user to decide if they want to
            #delete the file or not.

        os.remove(localmageis_a)
        os.remove(localmageis_b)
        #print "Check output for direct links to ballon Ephermeris files."


#main()



def plot_fspc_data():
    payload_dict = maptime2payload("which_payloads.txt")
    #date = raw_input('Starting date (YYYYMMDD), e.g 20130201 for February 1, 2013: ')
    #algorithm s.t we can avoid the pitfalls of the payload
    #dictionary coming in a char array rather than a list.
    print "FSPC PLOT DATA PROCESSING"
    for key in payload_dict.keys():
        for i in range(0, len(payload_dict.get(key)) - 1, 3):
            print "Processing Payloads on " + key  + " : " + payload_dict.get(key)
            print "Currently on: " + payload_dict.get(key)[i: i+2]
            if not linkexists(construct_fspc_link(key, payload_dict.get(key)[i: i+2])):
                print ("sorry, file does not exist in " +
                       construct_fspc_link(key, payload_dict.get(key)[i:i+2]))
                if raw_input("Restart program y/n? ") == "y":
                    return
                return main()

            localballoon = download_fspc(key, payload_dict.get(key)[i:i+2],
                                         construct_fspc_link(key, payload_dict.get(key)[i:i+2]),
                                         downloadto_fspc)
            fspc_plot(localballoon, payload_dict.get(key)[i:i+2], key)
            os.remove(localballoon)






