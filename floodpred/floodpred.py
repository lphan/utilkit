__author__ = 'Long Phan'

import csv
import numpy as np
import matplotlib.pyplot as plt
from data import pd, hwall
import predict

# import io
# For Python 2+3 and with unicode (Hint Source: stackoverflow)
try:
    to_unicode = unicode
except:
    to_unicode = str

import datetime
dt = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

from pathlib import Path

# TODO: create json-file to store parameters waterlevel, time_now, time_predict
# and path to figures
# data = {"date_time": dt, "data": {"waterlevel_now": "", "start_time": "",
#                                   "predict_hours": ""}}

# Write JSON file
# import json
# TODO: check if file data.json exist, yes and load and add new data.
# No, create new one.
# with io.open('data.json', 'w', encoding='utf8') as outfile:
#     f = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
#     outfile.write(to_unicode(f))


class FloodPred(object):
    def __init__(self, waterlevel, time_now, time_predict):
        self.waterlevel_now = waterlevel
        self.time_now = time_now
        self.time_predict = time_predict

        self.water_red = 0
        self.water_green = 0
        self.water_yellow = 0

        self.wr = 0
        self.wg = 0
        self.wy = 0

        self.red_array = []
        self.green_array = []
        self.yellow_array = []
        self.non_distributed = []   # stored values undistributed

        self.mean_ax = []
        self.mean_ay = []

        self.mean_g = []
        self.mean_y = []
        self.mean_r = []

        self.start_idx = 0
        self.middle_idx = 0
        self.end_idx = 0

        self.x_final_list = []      # contain list of time axis from 0:00-24:00
        self.y_final_list = []      # contain mean-value

        self.x_coord = []
        self.y_coord = []
        self.idx = []

        self.pred_waterlevel = 0

        self.result = 0
        self.error = 0
        self.ar_result = 0

        self.figname1 = ""
        self.figname2 = ""
        self.figname3 = ""
        self.figname4 = ""

    """
    Inititialize values for waterlevel
    """
    def init_data(self):

        self.water_red = hwall.max()    # popular highes flooded status in 1993
        self.water_green = hwall.min()   # as Middle water level (safe state)
        self.water_yellow = hwall.mean()   # high water level

        self.wr = self.water_red.values[2]
        self.wg = self.water_green.values[2]
        self.wy = self.water_yellow.values[0]

        # normalize waterlevel
        self.waterlevel_now = self._convertrealnorm(self.waterlevel_now)

        self.max_wy = 0     # used for comparing with current water level
        self.min_wy = 0     # ...

        self.red_result = []
        self.yellow_result = []
        self.green_result = []

        self.number_red = []
        self.number_yellow = []
        self.number_green = []
        self.total_gyr = 0

        # self.coeff_gyr = []

        self.subset = hwall[['Zeit', 'W [cm]']]
        self.timeaxis = [t[0] for t in
                         pd.DataFrame(hwall[['Zeit']]).groupby(['Zeit'])]

        self.gyr_list_left = []
        self.gyr_list_right = []

        self.roc = []       # rate of change by days from 0:00 to 24:00
        self.x_roc = []
        self.y_roc = []
        self.list_roc = []

    # TODO:
    # review norm-techniques of z-score & min-max
    # make normalization as an option for hwall-data and classified-data
    """
    Normalizing Data using Min-Max method
    Optional: Z-score method
    """
    def normalizedata(self):
        '''
        Apply min-max normalizing with pre-defined boundary [0, 1]
        '''
        # hwallmima = (hwall.values[:, 2] - self.wg)/(self.wr-self.wg)
        hwallmima = self._convertrealnorm(hwall.values[:, 2])
        hwall['W normed'] = hwallmima

        # update max, min of water level with the normalized data
        self.wr = hwallmima.max()
        self.wg = hwallmima.min()
        self.wy = hwallmima.mean()

    # --------------------------------------------------------------
    #                       HELP FUNCTIONS
    # --------------------------------------------------------------
    """
    Convert the normalized value into real value in cm
    """
    def _convertnormreal(self, data):
        return data*(hwall.values[:, 2].max() - hwall.values[:, 2].min()) \
            + hwall.values[:, 2].min()

    """
    Convert the real value into normed value
    Predefined boundary: [0, 1]
    """
    def _convertrealnorm(self, data):
        wr = self.water_red.values[2]
        wg = self.water_green.values[2]
        return (data - wg)/(wr-wg)

    """
    Convert data in format time-object into float type
    """
    def _convTimeFloat(self, time):
        t = str(time)
        r = t.split(':')
        return float(r[0]+'.'+r[1])

    """
    Return index of 'Time in float' in range from 0:00 to 24:00
    """
    def _convFloatTime(self, time):
        timeidx = [self._convTimeFloat(elem)
                   for elem in self.timeaxis].index(time)
        return self.timeaxis[timeidx]

    # """
    # Return all figure_names
    # """
    # def getFigureNames(self):
    #     return self.figname1, self.figname2, self.figname3, self.figname4

    """
    Show the final result in normalized format (bet. 0 and 1) and in cm
    """
    def showResult(self):
        print ("\nThe predicting water level is {} "
               .format(self.pred_waterlevel))
        print ("Result in cm is {} "
               .format(self._convertnormreal(self.pred_waterlevel)))

    """
    Show (Artificial) result by approximating the predict_result with the
    truncation error between the current water level and
    computed_current water level
    """
    def showArtificialResult(self):
        # print (self.waterlevel_now)
        # print (self.pred_waterlevel)
        if (self.pred_waterlevel < self.waterlevel_now):
            self.ar_result = self._convertnormreal(self.pred_waterlevel) + \
                self.error
        else:
            self.ar_result = self._convertnormreal(self.pred_waterlevel) - \
                self.error
        print ("\n(Artificial) Result in cm: ", self.ar_result)
        print ("(Artificial) Result: ", self._convertrealnorm(self.ar_result))

    """
    Testing by giving the waterlevel_now and current time
    Recalculate the waterlevel_now using above method
    Result will be compared with the input waterlevel_now
    """
    def test_waterlevel(self, time, waterlevel_now):
        print ("\nTesting by input current time to calculate the waterlevel")
        testResult = np.polyval(self.result, time)
        # testResult = self.result[0]*time + self.result[1]
        print (".....The current waterlevel is {}".format(waterlevel_now))
        print (".....-> Result in cm is {}"
               .format(self._convertnormreal(waterlevel_now)))
        print ("\n.....The recalculated water level is {}".format(testResult))
        print (".....-> Result in cm is {}"
               .format(self._convertnormreal(testResult)))
        print ("\n.....Error estimate difference is {}"
               .format(abs(waterlevel_now - testResult)))
        print (".....Error in cm is {}"
               .format(abs(self._convertnormreal(waterlevel_now)
                           - self._convertnormreal(testResult))))
        error = abs(self._convertnormreal(waterlevel_now)
                    - self._convertnormreal(testResult))
        return error

    """
    Print out value of all important variables, functions for purpose debugging
    """
    def _printOut(self):
        print ("\n --------- Function normalizedata")
        print ("All Data before normalizing: ", hwall.values[:, 2])

        print ("\n --------- Function init_data")
        print ("Data imported from Excel file", hwall.values)
        print ("Highest water level ", hwall.values[:, 2].max())
        print ("Lowest water level ", hwall.values[:, 2].min())

        print ("\n --------- Function classifyData")
        print ("RED_ARRAY ", self.red_array)
        print ("YELLOW_ARRAY ", self.yellow_array)
        print ("GREEN_ARRAY ", self.green_array)

        print ("-> Waterlevel data in red {}".format(self.wr))
        print ("-> Waterlevel data in yellow {}".format(self.wy))
        print ("-> Waterlevel data in green {}".format(self.wg))
        print ("type of red_array: ", type(self.red_array))
        if len(self.red_array) > 0:
            print ("test first element of red_array: ", self.red_array[0][0])
            print ("test second element of red_array: ", self.red_array[0][1])
            print ("test third element of red_array: ", self.red_array[0][2])

        print ("red array ", len(self.red_array))               # 1686
        print ("yellow array ", len(self.yellow_array))         # 13254
        print ("green array ", len(self.green_array))           # 2103
        print ("non distributed ", len(self.non_distributed))   # 0
        print (len(hwall))                                      # 17043
        print (type(self.red_array))                            # numpy ndarray

        print ("\n --------- Function rateofchange (Method 2)")
        print (self.roc)
        print (type(self.roc))
        print (len(self.roc))       # currently 181 days

        print ("Rate of change: ", self.roc)
        print ("Length of list of rate_of_change: ", self.list_roc)     # < 181

        print ("\n --------- Function calAvrMeanValue")
        print (self.mean_ax)
        print (self.mean_ay)
        print (len(self.mean_ax))
        print (len(self.mean_ay))

        print ("\n --------- Function calMeanValue")
        print ("Red_Zone (normed): ", self.water_red)
        # boundary between yellow_zone and red_zone
        print ("\nMax Yellow_Zone (normed): ", self.max_wy)
        print (".... in cm: ", self._convertnormreal(self.max_wy))
        # boundary between green_zone and yellow_zone
        print ("Min Yellow_Zone (normalized): ", self.min_wy)
        print (".... in cm: ", self._convertnormreal(self.min_wy))
        print ("\nGreen_Zone (normed): ", self.water_green)

        print ("\n --------- Function _process_Zone")
        print ("Indexing: {} {} {}"
               .format(self.start_idx, self.middle_idx, self.end_idx))
        print ("Length left list: ", len(self.gyr_list_left),
               "Length right list: ", len(self.gyr_list_right))
        print ("LEFT ", self.gyr_list_left)
        print ("RIGHT ", self.gyr_list_right)

        print ("\n --------- Function _findWaterlevel")
        print ("RED_RESULT ", self.number_red)
        print ("YELLOW_RESULT ", self.number_yellow)
        print ("GREEN_RESULT ", self.number_green)
        print (self.number_green[0][0])
        print (self.number_green[0][1])
        print ("TOTAL GYR: ", self.total_gyr)

        print ("\n --------- Function _process_Zone_prio")
        print (self.start_idx, self.middle_idx, self.end_idx)

        print ("\n --------- Function Visualization")
        print ("x_coord :", self.x_coord)
        print ("y_coord :", self.y_coord)

        print ("\n --------- Function _task_lspm")
        print ("self.x_final_list: ", self.x_final_list)
        print ("self.y_final_list: ", self.y_final_list)
        print (len(self.x_final_list), len(self.y_final_list))

        print ("\n --------- Method 1:")
        print ("Length time x-coord {}".format(len(self.x_final_list)))
        print ("Length waterlevel y-coord {}".format(len(self.y_final_list)))
        print ("Time data x-coord {}".format(self.x_final_list))
        print ("Waterlevel data y-coord {}".format(self.y_final_list))
        print ("Coefficients = {}\n".format(self.result))

        print ("\n --------- Method 2:")
        print ("Length time x-coord {}".format(len(self.mean_ax)))
        print ("Length waterlevel y-coord {}".format(len(self.mean_y)))
        print ("Time data x-coord {}".format(self.mean_ax))
        print ("Waterlevel data y-coord {}".format(self.mean_y))
        print ("Coefficients = {}\n".format(self.result))

    """
    Visualization rate of changes
    """
    def _visualroc(self):
        fig = plt.figure()
        plt.xlabel('Time from 0:00 to 24:00')
        plt.ylabel('High water level (normalized)')

        # Visual all days (total: 181 days)
        for r in self.roc:
            plt.plot(r[1].values[:, 1], r[1].values[:, 3], color='blue',
                     marker='.')
        self.figname3 = 'figures/Figure3_waterlevelalldays_'+dt+'.png'
        fig.savefig(self.figname3, dpi=fig.dpi)

        plt.show()

    def _visualmeanroc(self):
        fig = plt.figure()

        plt.xlabel('Time from 0:00 to 24:00')
        plt.ylabel('High water level (normalized)')

        for lr in self.list_roc:
            plt.plot(lr[1].values[:, 1], lr[1].values[:, 3], color='blue',
                     marker='.')

        # Visualize the current water level at time_now
        plt.scatter(self._convFloatTime(self.time_now), self.waterlevel_now,
                    color='Orange', marker='X', label='The current water level')

        pred_time = self._convFloatTime(self.time_now+self.time_predict)

        plt.plot(pred_time, self._convertrealnorm(self.ar_result),
                 color='Black', marker='X',
                 label='The (artificial) predicting water level')

        # Visualize the mean value
        if (len(self.mean_ax) > 0 and len(self.mean_ay) > 0):
            plt.plot(self.mean_ax, self.mean_ay, color='red', marker='.',
                     label='Average Mean Value')
        plt.legend(loc='upper left')
        self.figname4 = 'figures/Figure4_waterlevelroc_'+dt+'.png'
        fig.savefig(self.figname4, dpi=fig.dpi)

        plt.show()

    """
    Visualization
    """
    def _visualize(self):
        fig = plt.figure()

        r_ax = []
        r_ay = []
        for elem in self.red_array:
            r_ax.append(elem[1])
            r_ay.append(elem[3])
        r_ax = np.asarray(r_ax)
        r_ay = np.asarray(r_ay)

        y_ax = []
        y_ay = []
        for elem in self.yellow_array:
            y_ax.append(elem[1])
            y_ay.append(elem[3])
        y_ax = np.asarray(y_ax)
        y_ay = np.asarray(y_ay)

        g_ax = []
        g_ay = []
        for elem in self.green_array:
            g_ax.append(elem[1])
            g_ay.append(elem[3])
        g_ax = np.asarray(g_ax)
        g_ay = np.asarray(g_ay)

        plt.xlabel('Time from 0:00 to 24:00')
        plt.ylabel('High water level (normalized)')

        # Visualize the classified water level
        plt.scatter(r_ax, r_ay, color='Red', marker='.', label='Alarm level')
        plt.scatter(y_ax, y_ay, color='Yellow', marker='.',
                    label='Warning level')
        plt.scatter(g_ax, g_ay, color='Green', marker='.', label='Safe level')
        self.figname1 = 'figures/Figure1_classifiedwaterlevel_'+dt+'.png'
        fig.savefig(self.figname1, dpi=fig.dpi)

        if (len(self.x_final_list) > 0 and len(self.y_final_list) > 0):
            plt.plot(self.x_final_list, self.y_final_list, color='blue',
                     marker='.', label='Average priotized Mean Value')

        # Visualize the predicting water level
        if (self.pred_waterlevel > 0):
            pred_time = self.x_final_list[len(self.x_final_list)-1]
            plt.plot(pred_time, self.pred_waterlevel, color='black',
                     marker='X', label='The predicting water level')

            plt.plot(pred_time, self._convertrealnorm(self.ar_result),
                     color='black', marker='X',
                     label='The (artificial) predicting water level')

        # Visualize the current water level at time_now
        plt.scatter(self._convFloatTime(self.time_now), self.waterlevel_now,
                    color='Orange', marker='X', label='The current water level')

        plt.legend(loc='upper left')
        self.figname2 = 'figures/Figure2_predictedwaterlevel_'+dt+'.png'
        fig.savefig(self.figname2, dpi=fig.dpi)
        plt.show()


"""
Call method 1 to calculate water level
"""


def dotask(waterlevel_now, start_time, predict_hours):
    ap = predict.Predict(waterlevel_now, start_time, predict_hours)

    ap.init_data()
    ap.normalizedata()
    ap.classifydata()

    # or choose calMeanValue()
    ap.calMeanValue_prio()
    ap.lspm()

    # TODO: replace _printOut with logging
    # ap._printOut()  # used for tracking information (debugging)

    print ("\n **************************************  ")
    ap.showResult()
    ap.showArtificialResult()
    print ("\n **************************************\n")

    ap._visualize()
    updatecsv(waterlevel_now, start_time, predict_hours, ap.figname2)


"""
Call method 2 based on rate of changes of water level
"""


def dotaskroc(waterlevel_now, start_time, predict_hours):
    ap = predict.Predict(waterlevel_now, start_time, predict_hours)

    ap.init_data()
    ap.normalizedata()
    ap.rateofchange()
    ap.calAvrMeanValues()

    # ap._printOut()  # used for tracking information (debugging)

    print (" \n **************************************  ")
    ap.showResult()
    ap.showArtificialResult()
    print (" \n **************************************\n")

    ap._visualmeanroc()
    updatecsv(waterlevel_now, start_time, predict_hours, ap.figname4)

"""
Call this task to visual all history data
"""


def dovisual(waterlevel_now, start_time, predict_hours):
    ap = predict.Predict(waterlevel_now, start_time, predict_hours)

    ap.init_data()
    ap.normalizedata()
    ap.rateofchange()
    ap._visualroc()
    updatecsv(waterlevel_now, start_time, predict_hours, ap.figname3)


def updatecsv(waterlevel_now, start_time, predict_hours, figname):

    mf = Path("./data.csv")
    if mf.is_file():
        print ("FILE EXIST")

        # update csv-file by adding new parameters
        with open('data.csv', 'a') as csvfile:
            write = csv.writer(csvfile, delimiter=' ', quotechar='|',
                               quoting=csv.QUOTE_MINIMAL)
            write.writerow([waterlevel_now] + [start_time] + [predict_hours] +
                           [figname] + [dt])

        # IDEA: convert it to a list, then merge with new one
        # add path to all figures, and update csv-file
        # create java-wui to load data from this csv-file and display
        # them on screen
    else:
        print ("FILE DOES NOT EXIST")

        # create csv_file
        with open('data.csv', 'w', newline='') as csvfile:
            write = csv.writer(csvfile, delimiter=' ', quotechar='|',
                               quoting=csv.QUOTE_MINIMAL)
            write.writerow([waterlevel_now] + [start_time] + [predict_hours] +
                           [figname] + [dt])

"""
    lspm(waterlevel, hour in float, next predicting hours)
        waterlevel in float type between 0 and 1 (eg. 0.1)
        hour in float with step-time is 0.15    (eg. 10.15)
        next predicting hours   (eg. 8)
Description: Input basic parameters to predict water level in next hours
"""

import logging
logging.basicConfig(filename='floodpred.log', level=logging.DEBUG)


if __name__ == '__main__':
    try:
        waterlevel = float(input("Input the current waterlevel e.g. 450.0: "))
        time = float(input("Input the current time e.g. 10.0 (for 10AM): "))
        hours = float(input("Input the predict hours e.g. 8.0 (for 8 hours): "))
        method = float(input("Choose '1' to start method 1, \
                             '2' to start method 2, \
                             '3' to start both methods, \
                             '4' to visual history data,\
                             '5' to run all methods, Others to quit: "))
    except ValueError:
        logging.info("Wrong type, Quit...")
        import sys
        sys.exit()

    if (type(waterlevel) and type(time) and type(hours) is float):
        kwargs = {"waterlevel_now": waterlevel, "start_time": time,
                  "predict_hours": hours}

        data = {"date_time": dt, "data": kwargs}

        if (method == 1):
            logging.info("Input '1', run first method")
            dotask(**kwargs)     # Method 1

        elif (method == 2):
            logging.info("Input '2', run second method")
            dotaskroc(**kwargs)  # Method 2

        elif (method == 3):
            logging.info("Input '3', run both methods")
            dotask(**kwargs)     # Method 1

            dotaskroc(**kwargs)  # Method 2

        elif (method == 4):
            logging.info("Input '4', run visual history data")
            dovisual(**kwargs)

        elif (method == 5):
            logging.info("Input '5', run all methods")
            dotask(**kwargs)     # Method 1

            dotaskroc(**kwargs)  # Method 2

            dovisual(**kwargs)   # Visual history data

        else:
            logging.info("Quit...")

    # TODO: improve function test_waterlevel with using pytest, nose (assert)
    # TODO: apply dask module for parallel computing
