__author__ = 'Long Phan'

# import csv
import numpy as np
import matplotlib.pyplot as plt
import predict
import logging
import datetime
from data import pd, hwall
from pathlib import Path

dt = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")

logging.basicConfig(filename='floodpred.log', level=logging.DEBUG)


class FloodPred(object):

    def __init__(self, waterlevel, time_now, time_predict):
        self.waterlevel_now = waterlevel
        self.time_now = time_now
        self.time_predict = time_predict

        self.water_red, self.water_green, self.water_yellow = 0, 0, 0

        self.wr, self.wg, self.wy = 0, 0, 0

        self.red_array, self.green_array, self.yellow_array = [], [], []
        self.non_distributed = []   # stored values undistributed

        self.mean_ax, self.mean_ay = [], []

        self.mean_g, self.mean_y, self.mean_r = [], [], []

        self.start_idx, self.middle_idx, self.end_idx = 0, 0, 0

        self.x_final_list = []      # contain list of time axis from 0:00-24:00
        self.y_final_list = []      # contain mean-value

        self.x_coord, self.y_coord = [], []
        self.idx = []

        self.figname1, self.figname2, self.figname3, self.figname4 = "", "", \
            "", ""

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

        self.max_wy, self.min_wy = 0, 0  # comparing with current water level

        self.red_result, self.yellow_result, self.green_result = [], [], []

        self.number_red, self.number_yellow, self.number_green = [], [], []

        self.total_gyr = 0
        self.pred_waterlevel = 0
        self.result = 0
        self.error = 0
        self.ar_result = 0

        # self.coeff_gyr = []

        self.subset = hwall[['Zeit', 'W [cm]']]
        self.timeaxis = [t[0] for t in
                         pd.DataFrame(hwall[['Zeit']]).groupby(['Zeit'])]

        self.gyr_list_left, self.gyr_list_right = [], []

        # rate of change by days from 0:00 to 24:00
        self.roc, self.x_roc, self.y_roc, self.list_roc = [], [], [], []

        self.datetime = dt.split()[0]+'_'+dt.split()[1]
        self.imagepath = './wui/src/main/webapp/resources/images/'

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
        logging.info(dt)
        logging.info("\n --------- Function normalizedata \n")
        logging.info("All Data before normalizing: %s", str(hwall.values[:, 2]))

        logging.info("\n --------- Function init_data \n")
        logging.info("Data imported from Excel file %s", str(hwall.values))
        logging.info("Highest water level %s", str(hwall.values[:, 2].max()))
        logging.info("Lowest water level %s", str(hwall.values[:, 2].min()))

        logging.info("\n --------- Function classifyData \n")
        logging.info("RED_ARRAY %s", str(self.red_array))
        logging.info("YELLOW_ARRAY %s", str(self.yellow_array))
        logging.info("GREEN_ARRAY %s", str(self.green_array))

        logging.info("-> Waterlevel data in red {%s}", str(self.wr))
        logging.info("-> Waterlevel data in yellow {%s}", str(self.wy))
        logging.info("-> Waterlevel data in green {%s}", str(self.wg))
        logging.info("type of red_array: %s", type(self.red_array))
        if len(self.red_array) > 0:
            logging.info("test first element of red_array: %s",
                         str(self.red_array[0][0]))
            logging.info("test second element of red_array: %s",
                         str(self.red_array[0][1]))
            logging.info("test third element of red_array: %s",
                         str(self.red_array[0][2]))

        logging.info("red array %d", len(self.red_array))               # 1686
        logging.info("yellow array %d", len(self.yellow_array))         # 13254
        logging.info("green array %d", len(self.green_array))           # 2103
        logging.info("non distributed %d", len(self.non_distributed))   # 0
        logging.info(len(hwall))                                      # 17043
        logging.info(type(self.red_array))                      # numpy ndarray

        logging.info("\n --------- Function rateofchange (Method 2)")
        logging.info(self.roc)
        logging.info(type(self.roc))
        logging.info(len(self.roc))       # currently 181 days

        logging.info("Rate of change: ")
        logging.info(self.roc)
        logging.info("Length of list of rate_of_change: %s", str(self.list_roc))

        logging.info("\n --------- Function calAvrMeanValue \n")
        logging.info(self.mean_ax)
        logging.info(self.mean_ay)
        logging.info(len(self.mean_ax))
        logging.info(len(self.mean_ay))

        logging.info("\n --------- Function calMeanValue \n")
        logging.info("Red_Zone (normed): %s", str(self.water_red))
        # boundary between yellow_zone and red_zone
        logging.info("\nMax Yellow_Zone (normed): %s", str(self.max_wy))
        logging.info(".... in cm: %d", self._convertnormreal(self.max_wy))
        # boundary between green_zone and yellow_zone
        logging.info("Min Yellow_Zone (normalized): %s", str(self.min_wy))
        logging.info(".... in cm: %d", self._convertnormreal(self.min_wy))
        logging.info("\nGreen_Zone (normed): %s", str(self.water_green))

        logging.info("\n --------- Function _process_Zone \n")
        logging.info("Indexing: {%d} {%d} {%d}",
                     self.start_idx, self.middle_idx, self.end_idx)
        logging.info("Length left list: %d ", len(self.gyr_list_left))
        logging.info("Length right list: %d ", len(self.gyr_list_right))
        logging.info("LEFT %s", str(self.gyr_list_left))
        logging.info("RIGHT %s", str(self.gyr_list_right))

        logging.info("\n --------- Function _findWaterlevel \n")
        logging.info("RED_RESULT: ")
        logging.info(self.number_red)
        logging.info("----------")
        logging.info("YELLOW_RESULT: ")
        logging.info(self.number_yellow)
        logging.info("----------")
        logging.info("GREEN_RESULT: ")
        logging.info(self.number_green)
        logging.info(self.number_green[0][0])
        logging.info(self.number_green[0][1])
        logging.info("TOTAL GYR: %s ", str(self.total_gyr))

        logging.info("\n --------- Function _process_Zone_prio \n")
        logging.info(str(self.start_idx) + str(" ") + str(self.middle_idx)
                     + str(" ") + str(self.end_idx))

        logging.info("\n --------- Function Visualization \n")
        logging.info("x_coord: %s ", str(self.x_coord))
        logging.info("y_coord: %s ", str(self.y_coord))

        logging.info("\n --------- Function _task_lspm \n")
        logging.info("self.x_final_list: %s", str(self.x_final_list))
        logging.info("self.y_final_list: %s", str(self.y_final_list))
        logging.info("%d %d", len(self.x_final_list), len(self.y_final_list))

        logging.info("\n --------- Method 1: \n")
        logging.info("Length time x-coord %d", len(self.x_final_list))
        logging.info("Length waterlevel y-coord %d", len(self.y_final_list))
        logging.info("Time data x-coord %s", str(self.x_final_list))
        logging.info("Waterlevel data y-coord {%s}", str(self.y_final_list))
        logging.info("Coefficients = {%s}\n", str(self.result))

        logging.info("\n --------- Method 2: \n")
        logging.info("Length time x-coord {%d}", len(self.mean_ax))
        logging.info("Length waterlevel y-coord {%d}", len(self.mean_y))
        logging.info("Time data x-coord {%s}", str(self.mean_ax))
        logging.info("Waterlevel data y-coord {%s}", str(self.mean_y))
        logging.info("Coefficients = {%s}\n", str(self.result))

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
        self.figname3 = 'Figure3_waterlevelalldays_'+self.datetime
        fig.savefig(self.imagepath+self.figname3+'.png', dpi=fig.dpi)

        # plt.show()

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
        self.figname4 = 'Figure4_waterlevelroc_'+self.datetime
        fig.savefig(self.imagepath+self.figname4+'.png', dpi=fig.dpi)

        # plt.show()

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
        self.figname1 = 'Figure1_classifiedwaterlevel_'+self.datetime
        fig.savefig(self.imagepath+self.figname1+'.png', dpi=fig.dpi)

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
        self.figname2 = 'Figure2_predictedwaterlevel_'+self.datetime
        fig.savefig(self.imagepath+self.figname2+'.png', dpi=fig.dpi)
        # plt.show()


"""
Call method 1 to calculate water level
"""


def dotask(waterlevel_now, start_time, predict_hours):
    ap = predict.Predict(waterlevel_now, start_time, predict_hours)

    ap.init_data()
    ap.normalizedata()
    ap.classifydata()

    ap.calMeanValue_prio()
    ap.lspm()

    # TODO: replace _printOut with logging
    ap._printOut()  # used for tracking information (debugging)

    print ("\n **************************************  ")
    ap.showResult()
    ap.showArtificialResult()
    print ("\n **************************************\n")

    ap._visualize()
    updatecsv(waterlevel_now, start_time, predict_hours, ap.figname2+'.png',
              ap._convertnormreal(ap.pred_waterlevel), ap.ar_result)


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
    updatecsv(waterlevel_now, start_time, predict_hours, ap.figname4+'.png',
              ap._convertnormreal(ap.pred_waterlevel), ap.ar_result)


"""
Call this task to visual all history data
"""


def dovisual(waterlevel_now, start_time, predict_hours):
    ap = predict.Predict(waterlevel_now, start_time, predict_hours)

    ap.init_data()
    ap.normalizedata()
    ap.rateofchange()
    ap._visualroc()

    updatecsv(waterlevel_now, start_time, predict_hours, ap.figname3+'.png',
              ap._convertnormreal(ap.pred_waterlevel), ap.ar_result)


# TODO: update result and artificial result either
# TODO: apply decorator to search for result before starting computing
def updatecsv(waterlevel_now, start_time, predict_hours, figname, result,
              ar_result):
    pathcsv = "./wui/src/main/webapp/resources/data.csv"
    mf = Path(pathcsv)

    # Convert data to data_frame and use to_csv, add figure name to df
    # dt = pd.to_datetime('now')    # get wrong time, 2 hour earlier
    # ts = pd.DatetimeIndex([dt])
    # dt = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
    # print (dt)
    # df = pd.DataFrame({'date_time': [dt],
    #                    'waterlevel_now': [waterlevel_now],
    #                    'start_time': [start_time],
    #                    'predict_hours': [predict_hours],
    #                    'figure_name': [figname]
    #                    })

    df = pd.DataFrame([[dt, waterlevel_now, start_time, predict_hours, figname,
                        result, ar_result]],
                      columns=['datetime', 'waterlevel_now', 'start_time',
                               'predict_hours', 'figure_name', 'predict_result',
                               'artificial_result']).set_index('datetime')

    if mf.is_file():
        # update csv-file by adding new parameters
        with open(pathcsv, 'a') as csvfile:
            df.to_csv(csvfile, header=None, encoding='utf-8')

        # with open(pathcsv, 'a') as csvfile:
        #     write = csv.writer(csvfile, delimiter=',', quotechar='|',
        #                        quoting=csv.QUOTE_MINIMAL)
        #     write.writerow([waterlevel_now] + [start_time] + [predict_hours] +
        #                    [figname] + [dt])

    else:
        # create new csv_file
        df.to_csv(pathcsv, header=None, encoding='utf-8')

        # with open(pathcsv, 'w', newline='') as csvfile:
        #     write = csv.writer(csvfile, delimiter=',', quotechar='|',
        #                        quoting=csv.QUOTE_MINIMAL)
        #     write.writerow([waterlevel_now] + [start_time] + [predict_hours] +
        #                    [figname] + [dt])


def updatedb():
    import dbconn
    pathcsv = "./wui/src/main/webapp/resources/data.csv"
    mf = Path(pathcsv)
    if mf.is_file():
        dbconn.updateMongoDB(pathcsv)
        dbconn.read_data()
    else:
        logging.info("File data csv does not exist")


"""
    lspm(waterlevel, hour in float, next predicting hours)
        waterlevel in float type between 0 and 1 (eg. 0.1)
        hour in float with step-time is 0.15    (eg. 10.15)
        next predicting hours   (eg. 8)
Description: Input basic parameters to predict water level in next hours
"""


if __name__ == '__main__':
    try:
        waterlevel_now = int(input("Input the current waterlevel e.g. 450 (for 450cm): "))
        start_time = int(input("Input the current time e.g. 10 (for 10AM): "))
        predict_hours = int(input("Input the predict hours e.g. 8 (for 8 hours): "))
        method = int(input("Choose '1' to start method 1, \
                           '2' to start method 2, \
                           '3' to start both methods, \
                           '4' to visual history data,\
                           '5' to run all methods,\
                           '6' to update database, Others to quit: "))
    except ValueError:
        logging.info("Wrong type, Quit...")
        import sys
        sys.exit()

    if type(waterlevel_now) and type(start_time) and type(predict_hours) is int:
        kwargs = {'start_time': start_time, 'waterlevel_now': waterlevel_now,
                  'predict_hours': predict_hours}

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

        elif (method == 6):
            updatedb()

        else:
            logging.info("Quit...")

    # TODO: improve function test_waterlevel with using pytest, nose (assert)
    # TODO: apply dask module for parallel computing
