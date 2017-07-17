__author__ = 'Long Phan'

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# import data from excel file (4 time slots 1993, 1995, 2013, 2016)
# Data can be updated manually via Excel-file & update import lines accordingly
try:
    hw = pd.ExcelFile('floodings.xlsx')
    hw1993 = hw.parse('HW1993')
    hw1995 = hw.parse('HW1995')
    hw2013 = hw.parse('HW2013')
    hw2016 = hw.parse('HW2016')

    hwall = hw1993.append(hw1995).append(hw2013).append(hw2016)
    MAX_LENGTH_IDX = 96    # calculated from 0:00 to 24:00, stepsize 15 minutes

except IOError as e:
    print ("Error import data from Excel file")
    import sys
    sys.exit()


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

        self.coeff_gyr = []

        self.subset = hwall[['Zeit', 'W [cm]']]
        self.timeaxis = [t[0] for t in
                         pd.DataFrame(hwall[['Zeit']]).groupby(['Zeit'])]

        self.gyr_list_left = []
        self.gyr_list_right = []

        self.roc = []       # rate of change by days from 0:00 to 24:00
        self.x_roc = []
        self.y_roc = []
        self.list_roc = []

    # TODO: review norm-techniques of z-score & min-max
    # TODO: make normalization as an option for hwall-data and classified-data
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

    """
    Init distance between hw-point and boundary of water level area
    """
    def classifydata(self):
        dist_red = dist_yellow = dist_green = 0

        for elem in hwall.values:
            dist_red = abs(self.wr - elem[3])
            dist_yellow = abs(self.wy - elem[3])
            dist_green = abs(self.wg - elem[3])

            if (dist_red < dist_yellow and dist_red < dist_green):
                self.red_array.append(elem)
            elif (dist_yellow < dist_red and dist_yellow < dist_green):
                self.yellow_array.append(elem)
            elif (dist_green < dist_yellow and dist_green < dist_red):
                self.green_array.append(elem)
            else:
                self.non_distributed.append(elem)

        # convert array into numpy ndarray
        self.red_array = np.asarray(self.red_array)
        self.yellow_array = np.asarray(self.yellow_array)
        self.green_array = np.asarray(self.green_array)

    """
    Calculate Mean Value of water level at every single timepoint
    """
    def calMeanValue(self):
        def groupbyresult(data_array, number_datapoint):
            temp = np.asarray([(elem[1], elem[3]) for elem in data_array])
            temp_result = [(x, temp[np.where(temp[..., 0] == x)][..., 1])
                           for x in sorted(np.unique(temp[..., 0]))]
            result = [(elem[0], elem[1].mean())
                      for elem in temp_result]
            # print ("RESULT calMeanValue ", result)
            return [(result[i][0],
                     result[i][1] * number_datapoint[i][1] / self.total_gyr[i])
                    for i in range(96)]

        self._findWaterlevel()
        self.red_result = np.asarray(groupbyresult(self.red_array,
                                                   self.number_red))
        self.yellow_result = np.asarray(groupbyresult(self.yellow_array,
                                                      self.number_yellow))
        self.green_result = np.asarray(groupbyresult(self.green_array,
                                                     self.number_green))
        # print ("NUMBER GREEN", self.number_green)
        # print ("GREEN RESULT", self.green_result)
        self.max_wy = self.yellow_array[:, 3].max()
        self.min_wy = self.yellow_array[:, 3].min()

        self._processZone()

    def _processZone(self):
        g_list_left, y_list_left, r_list_left, g_list_right, y_list_right, \
            r_list_right = [], [], [], [], [], []

        if (self.time_now - self.time_predict < 0) and \
                (self.time_now + self.time_predict > 24):
            self.start_idx = 0
            self.end_idx = MAX_LENGTH_IDX
        elif (self.time_now + self.time_predict > 23.45):
            self.start_idx = [self._convTimeFloat(elem[0]) for elem in
                              self.green_result].index(self.time_now -
                                                       self.time_predict)
            self.end_idx = MAX_LENGTH_IDX
        elif (self.time_now - self.time_predict < 0):
            self.start_idx = 0
            self.end_idx = [self._convTimeFloat(elem[0]) for elem in
                            self.green_result].index(self.time_now +
                                                     self.time_predict)
        else:
            self.start_idx = [self._convTimeFloat(elem[0]) for elem in
                              self.green_result].index(self.time_now -
                                                       self.time_predict)
            self.end_idx = [self._convTimeFloat(elem[0]) for elem in
                            self.green_result].index(self.time_now +
                                                     self.time_predict)
        self.middle_idx = [self._convTimeFloat(elem)
                           for elem in self.timeaxis].index(self.time_now)

        g_list_left = [elem_g for (idg, elem_g) in
                       enumerate(self.green_result
                                 [self.start_idx:self.middle_idx])]

        y_list_left = [elem_y for (idg, elem_y) in
                       enumerate(self.yellow_result
                                 [self.start_idx:self.middle_idx])]

        r_list_left = [elem_r for (idg, elem_r) in
                       enumerate(self.red_result
                                 [self.start_idx:self.middle_idx])]

        g_list_right = [elem_g for (idg, elem_g) in
                        enumerate(self.green_result
                                  [self.middle_idx:self.end_idx])]

        y_list_right = [elem_y for (idg, elem_y) in
                        enumerate(self.yellow_result
                                  [self.middle_idx:self.end_idx])]

        r_list_right = [elem_r for (idg, elem_r) in
                        enumerate(self.red_result
                                  [self.middle_idx:self.end_idx])]

        self.gyr_list_left = np.dstack((g_list_left, y_list_left, r_list_left))
        self.gyr_list_right = np.dstack((g_list_right, y_list_right,
                                         r_list_right))
        # print (self.timeaxis)
        # print (self.start_idx, self.middle_idx, self.end_idx)
        # print ("g_list_left", g_list_left)
        # print ("y_list_left", y_list_left)
        # print ("r_list_left", r_list_left)
        # print ("gyr_list_left", self.gyr_list_left)
        # print ("gyr_list_right", self.gyr_list_right)

        gyr_list = np.concatenate((self.gyr_list_left, self.gyr_list_right),
                                  axis=0)

        # final result list of value at every single timepoint
        self.x_final_list = [elem[0][0] for elem in gyr_list]

        count = 1
        for elem in self.gyr_list_left:
            value = (elem[1][0] + elem[1][1] + elem[1][2]) \
                * (count) / len(self.gyr_list_left)
            self.y_final_list.append(value)
            self.y_coord.append(value)
            count = count + 1

        for elem in self.gyr_list_right:
            value = (elem[1][0] + elem[1][1] + elem[1][2])
            self.y_final_list.append(value)
            self.y_coord.append(value)
            count = count - 1

    """
    Calculate Mean Value wrt current water level at every single timepoint
    """
    def calMeanValue_prio(self):
        def calculateResult(dataset):
            # lenX/sum* value + lenX-1/sum*value + ...
            # print (dataset[0])
            # print ("LENGTH FIRST DATA ELEMENT: ", len(dataset[0]))
            # temp_sum = sum([i for i in range(1, len(dataset[0])+1)])
            # print ("TEMP SUM: ", temp_sum)
            # print ("First data value: ", dataset[0][0][0])
            result = 0
            final_result = []
            j = 0  # the further the timepoint is, the less affection it is
            # max_timestep = 96
            for i in range(96):
                for elem in dataset[i]:
                    sum_denominator = sum([k for k in
                                           range(1, self.total_gyr[i]+1)])
                    # print ("Nominator: ", self.total_gyr[i]-j)
                    # print ("Sum_denominator: ", sum_denominator)
                    # print ("elem[0]", elem[0])
                    temp_result = (self.total_gyr[i]-j)*elem[0]/sum_denominator
                    # print ("TEMP_RESULT", temp_result)
                    # print ("WATERLEVEL_NOW", self.waterlevel_now)
                    result = result + temp_result
                    j = j + 1
                    # j = j + 1/sum_denominator
                    # j = j + 1/self.total_gyr[i]

                # '''
                # Realizing: Force mean_result go near by current waterlevel
                # at the input-time by increasing the ratio w.r.t
                # 99% waterlevel_now and 1% mean_result -> see:
                # showArtificialResult
                # '''
                # result = (result + self.waterlevel_now)/2
                # result = 2/3*result + 1/3*self.waterlevel_now
                # result = 2/3*self.waterlevel_now + 1/3*result
                # result = 4/5*self.waterlevel_now + 1/5*result
                # result = 9/10*self.waterlevel_now + 1/10*result
                # result = 99/100*self.waterlevel_now + 1/100*result
                # CLOSEST result = 999/1000*self.waterlevel_now + 1/1000*result
                # LIMIT: result= 9999/10000*self.waterlevel_now+1/10000*result
                # BEST OPTION:
                # result = (self.total_gyr[i] - max_timestep)/self.total_gyr[i]
                #     * self.waterlevel_now + (max_timestep/self.total_gyr[i])
                #     * result
                # max_timestep = max_timestep - 1
                # result = (self.total_gyr[i] - 1) / self.total_gyr[i] * \
                #    self.waterlevel_now + (1/self.total_gyr[i]) * result

                final_result.append(result)
                result = 0
                j = 0
            return final_result

        self._findWaterlevel()
        sortedwl = self._findAllPoints()
        waterlevel_result = np.asarray(calculateResult(sortedwl))
        # print ("Waterlevel_result: ", waterlevel_result)
        # print (len(waterlevel_result))
        # print ("Sortedwl: ", sortedwl)
        self._processZone_prio(waterlevel_result)

    def _processZone_prio(self, waterlevel):
        if (self.time_now - self.time_predict < 0) and \
                (self.time_now + self.time_predict > 24):
            self.start_idx = 0
            self.end_idx = MAX_LENGTH_IDX
        elif (self.time_now + self.time_predict > 23.45):
            self.start_idx = [self._convTimeFloat(elem) for elem in
                              self.timeaxis].index(self.time_now -
                                                   self.time_predict)
            self.end_idx = MAX_LENGTH_IDX
        elif (self.time_now - self.time_predict < 0):
            self.start_idx = 0
            self.end_idx = [self._convTimeFloat(elem) for elem in
                            self.timeaxis].index(self.time_now +
                                                 self.time_predict)
        else:
            self.start_idx = [self._convTimeFloat(elem) for elem in
                              self.timeaxis].index(self.time_now -
                                                   self.time_predict)
            self.end_idx = [self._convTimeFloat(elem) for elem in
                            self.timeaxis].index(self.time_now +
                                                 self.time_predict)
        self.middle_idx = [self._convTimeFloat(elem) for elem in
                           self.timeaxis].index(self.time_now)

        list_left = [elem for (idg, elem) in
                     enumerate(waterlevel[self.start_idx:self.middle_idx])]
        list_right = [elem for (idg, elem) in
                      enumerate(waterlevel[self.middle_idx:self.end_idx])]

        # list_lr = np.concatenate((list_left, list_right), axis=0)
        # print ("Concatenated list: ", list_lr)
        # print (len(list_lr))
        # print (type(list_lr))

        self.x_final_list = [t for (idg, t) in
                             enumerate(self.timeaxis
                                       [self.start_idx:self.end_idx])]

        count = 1
        # print ("LIST LEFT ..............", len(list_left))
        for elem in list_left:
            # The further the time, the less affection it is
            # value = (elem * (len(list_left) - count)) / len(list_left)

            # consider all time points are equal
            value = elem
            self.y_final_list.append(value)
            count = count - 1/(len(list_left))

        # print ("LIST RIGHT .............", len(list_right))
        count = 0     # as option
        for elem in list_right:
            # The further the time, the higher is the tendenz of water level
            # value = (elem * (len(list_right) + count)) / len(list_right)

            # consider all time points are equal
            value = elem
            self.y_final_list.append(value)
            count = count + 1/(len(list_right))

    """
    Least square polynomial fit method
    """
    def lspm(self):
        '''
        Calculate mean_value for every time_point (see: function calMeanValue)
        '''
        self._task_lspm([self._convTimeFloat(time)
                         for time in self.x_final_list], self.y_final_list)

    """
    Find coefficient a, b and the corresponding linear equation
    Apply: (Non)Linear Least Square Polynomial Fit
    """
    def _task_lspm(self, data_x, data_y):
        # find result among equations with different degree with smallest error
        def findresult(results):
            mi = results[0]
            te = results[0][0]  # initial first element with error
            for i in results[1:]:
                if (i[0] < te):
                    te = i[0]
                    mi = i      # element with better smaller error
            return mi

        def func(x, a, b):
            return a*x+b

        # print (data_x)
        # print (data_y)
        degree = [1, 2, 3]
        final = []  # contain list of errors measured by every degree
        for dg in degree:
            self.result = np.polyfit(data_x, data_y, dg)
            temp = self.test_waterlevel(self.time_now, self.waterlevel_now)
            final.append((temp, self.result))

        self.error, self.result = findresult(final)

        pred_time = data_x[len(data_x)-1]
        # self.pred_waterlevel = self.result[0]*pred_time + self.result[1]
        self.pred_waterlevel = np.polyval(self.result, pred_time)

        # Optional: ------------ Try curve_fit from scipy ------------------
        # Result by 'curve_fit' is nearly the same with numpy.polyfit degree=1
        popt, pcov = curve_fit(func, data_x, data_y)
        scipy_result = np.polyval(popt, pred_time)

        # print ("........... scipy curve_fit", popt)
        print ("The predicting result with scipy ", scipy_result)
        print ("Result in cm is {} "
               .format(self._convertnormreal(scipy_result)))

    # ------------------------------------------------------------------ #
    #             Improve Method 1 by optimizing coefficients
    # ------------------------------------------------------------------ #
    """
    Find total number of points for every water level at every single timepoint
    """
    def _findWaterlevel(self):
        def groupbyresult(data_array):
            temp = np.asarray([(elem[1], elem[3]) for elem in data_array])
            temp_result = [(x, temp[np.where(temp[..., 0] == x)][..., 1])
                           for x in sorted(np.unique(temp[..., 0]))]
            return [(elem[0], len(elem[1])) for elem in temp_result]

        self.number_red = np.asarray(groupbyresult(self.red_array))
        self.number_yellow = np.asarray(groupbyresult(self.yellow_array))
        self.number_green = np.asarray(groupbyresult(self.green_array))

        self.total_gyr = [self.number_green[i][1] + self.number_yellow[i][1] +
                          self.number_red[i][1] for i in range(96)]

        # print (len(self.total_gyr))
        # Create list of tuple [(green/total, yellow/total, red/total)] for all
        # time point from 0:00 to 23:45
        self.coeff_gyr = [(self.number_green[i][1]/self.total_gyr[i],
                           self.number_yellow[i][1]/self.total_gyr[i],
                           self.number_red[i][1]/self.total_gyr[i])
                          for i in range(96)]
        # print ("\nCoefficients ", self.coeff_gyr)

    """
    Find all points at every time points, sorted wrt. current water level
    """
    def _findAllPoints(self):
        # TODO: apply map & lambda (closure) to this function
        df = pd.DataFrame(hwall[['Zeit', 'W normed']])
        troc = df.groupby(['Zeit'])

        # Sort water level wrt. current water level
        sortedwl = []
        for elem in troc:
            sortedwl.append(sorted([(e[1], abs(e[1]-self.waterlevel_now))
                            for e in elem[1].values], key=lambda te: te[1]))

        # print ("0:00", sortedwl[0])
        # print ("0:15", sortedwl[1])
        # print (len(sortedwl))
        # print (len(troc))
        # print ("Current water level input:", self.waterlevel_now)
        return sortedwl

    # ------------------------------------------------------------------ #
    # Method 2:
    # Sort and visual all water level on days closest to current water level
    # ------------------------------------------------------------------ #
    """
    Classify 'rate of changes' waterlevel by days from 0:00 to 24:00
    """
    def rateofchange(self):
        df = pd.DataFrame(hwall)
        self.roc = df.groupby(['Datum'])
        self.list_roc = np.asarray(self._findcritiquepoint())

    def _findcritiquepoint(self):
        temp = []
        # convert waterlevel_now to float_type in norm between 0 and 1 and
        # then round the waterlevel_now up to 1 decimals
        wln = np.around(self.waterlevel_now, decimals=1)

        # use the same trick to other points, round it up and if the points are
        # close '=' to waterlevel_now at the same current time
        for r in self.roc:
            [temp.append(r) for sub_roc in r[1].values
             if (self._convTimeFloat(sub_roc[1]) == self.time_now and
                 wln == np.around(sub_roc[3], decimals=1))]

        return temp

    """
    Calculate Average Mean Value of water level at every single timepoint
    In combination with rate of change
    """
    def calAvrMeanValues(self):
        def validate(length_day_idx):
            return length_day_idx == MAX_LENGTH_IDX

        t = [lr[1].values[:, 1] for lr in self.list_roc]
        for elem in t:
            if not validate(len(elem)):
                print ("ALARM - Data for current parameters is not sufficient")
                print ("\n Data points from 0:00 to 24:00 need total 96 points")
                print ("\n However, there are only ", len(elem), "data points")
                print (elem)
                print ("\n Please try again with different parameters")
                print ("\n or choose method 1 to run calculation\n")
                self.mean_ax = []    # reset mean_ax to empty list
                import sys
                sys.exit()
            else:
                self.mean_ax = elem  # assign 96 datatime-point

        temp = np.asarray([lr[1].values[:, 3] for lr in self.list_roc])
        transpose = temp.transpose()
        self.mean_ay = [elem.mean() for elem in transpose]

        self._task_lspm([self._convTimeFloat(elem)
                         for elem in self.mean_ax], self.mean_ay)

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

        fig.savefig('figures/Figure3_waterlevelalldays.png', dpi=fig.dpi)

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
        fig.savefig('figures/Figure4_waterlevelroc.png', dpi=fig.dpi)

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

        fig.savefig('figures/Figure1_classifiedwaterlevel.png', dpi=fig.dpi)

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

        fig.savefig('figures/Figure2_predictedwaterlevel.png', dpi=fig.dpi)
        plt.show()

    """
    Call method 1 to calculate water level
    """
    def dotask(self):
        self.init_data()
        self.normalizedata()
        self.classifydata()

        # self.calMeanValue()
        self.calMeanValue_prio()

        self.lspm()

        # TODO: replace _printOut with logging
        # self._printOut()  # used for tracking information (debugging)

        print ("\n **************************************  ")
        self.test_waterlevel(self.time_now, self.waterlevel_now)
        self.showResult()
        self.showArtificialResult()
        print ("\n **************************************\n")

        self._visualize()

    """
    Call method 2 based on rate of changes of water level
    """
    def dotaskroc(self):
        self.init_data()
        self.normalizedata()
        self.rateofchange()
        self.calAvrMeanValues()

        # self._printOut()  # used for tracking information (debugging)

        print (" \n **************************************  ")
        self.test_waterlevel(self.time_now, self.waterlevel_now)
        self.showResult()
        self.showArtificialResult()
        print (" \n **************************************\n")

        self._visualmeanroc()

    """
    Call this task to visual all history data
    """
    def dovisual(self):
        self.init_data()
        self.normalizedata()
        self.rateofchange()
        self._visualroc()

"""
    lspm(waterlevel, hour in float, next predicting hours)
        waterlevel in float type between 0 and 1 (eg. 0.1)
        hour in float with step-time is 0.15    (eg. 10.15)
        next predicting hours   (eg. 8)
"""
if __name__ == '__main__':
    # TODO:
    #   write a loop to start waterlevel_now from Green 300 to Red 700,
    #   with step_size 100
    waterlevel_now = 600.0
    start_time = 10.0       # TODO: WHAT IF start_time in float 2.15, 2.30, 2.45
    predict_hours = 8

    if predict_hours > 12:
        print ("predict_hours can be max at 12")
    else:
        # --------- Call method 1
        fp = FloodPred(waterlevel_now, start_time, predict_hours)
        fp.dotask()

        # --------- Call method 2
        # Step1: Visual all days (Total: 181 days)
        fp2 = FloodPred(waterlevel_now, start_time, predict_hours)
        fp2.dovisual()  # Visual all data
        # Step2: Sort out the needed data
        fp3 = FloodPred(waterlevel_now, start_time, predict_hours)
        fp3.dotaskroc()

    # TODO: improve function test_waterlevel with using pytest, nose (assert)
    # TODO: apply dask module for parallel computing
    # TODO: restructure & refactoring the code into multiple files by applying
    # inheritance
