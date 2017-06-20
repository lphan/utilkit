__author__ = 'Long Phan'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# import data from excel file
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

        self.x_final_list = []
        self.y_final_list = []
        self.x_coord = []
        self.y_coord = []
        self.idx = []

        self.pred_time = 0
        self.pred_waterlevel = 0

        self.result = 0

    """
    Inititialize values for waterlevel
    """
    def init_data(self):

        self.water_red = hwall.max()    # popular highes flooded status in 1993
        self.water_green = hwall.min()   # Middle water level
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

        self.subset = hwall[['Zeit', 'W [cm]']]

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
        Data before normalizing
        '''
        # print (hwall.values[:, 2])

        '''
        Apply min-max normalizing with pre-defined boundary [0, 1]
        '''
        # hwallmima = (hwall.values[:, 2] - self.wg)/(self.wr-self.wg)
        hwallmima = self._convertrealnorm(hwall.values[:, 2])
        # print (len(hwallmima))
        # print (hwallmima.max())  # pre-defined: 1
        # print (hwallmima.min())  # pre-defined: 0
        # print (hwallmima.mean())
        # print (hwallmima)

        # print (hwall[['W [cm]']])
        # print (type(hwall))
        # print (type(hwall.values[:, 2]))
        # print (type(hwallmima))
        # print (len(hwall.values[:, 2]))
        # print (len(hwallmima))
        # add new normalied data to original data
        hwall['W normed'] = hwallmima

        '''
        Optional: apply z-score normalizing
        '''
        # print ("standard deviation", np.std(hwall.values[:, 2]))
        # print ("mean value ", self.wy)
        # print ("max value ", self.wr)
        # print ("min value ", self.wg)
        # print (abs(hwall.values[:, 2] - self.wy))
        # hwallz = abs(hwall.values[:, 2] - self.wy)/np.std(hwall.values[:, 2])
        # # for hwz in hwallz:
        # #     print (hwz)
        # print (len(hwallz))
        # print ("mean value after normalizing", hwallz.mean())
        # print ("max after normalizing ", hwallz.max())
        # print ("min after normalizing ", hwallz.min())

        # update data manually
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
        def groupbyresult(data_array):
            temp = np.asarray([(elem[1], elem[3]) for elem in data_array])
            temp_result = [(x, temp[np.where(temp[..., 0] == x)][..., 1])
                           for x in sorted(np.unique(temp[..., 0]))]
            return [(elem[0], elem[1].mean()) for elem in temp_result]

        self.red_result = np.asarray(groupbyresult(self.red_array))
        self.yellow_result = np.asarray(groupbyresult(self.yellow_array))
        self.green_result = np.asarray(groupbyresult(self.green_array))

        self.max_wy = self.yellow_array[:, 3].max()
        self.min_wy = self.yellow_array[:, 3].min()

    def _processZone(self, l1, l2, l3, m,  r1, r2, r3):
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
        self.middle_idx = self._convFloatTime(self.time_now)

        g_list_left = [elem_g for (idg, elem_g) in
                       enumerate(self.green_result[self.start_idx:self.middle_idx])]

        y_list_left = [elem_y for (idg, elem_y) in
                       enumerate(self.yellow_result[self.start_idx:self.middle_idx])]

        r_list_left = [elem_r for (idg, elem_r) in
                       enumerate(self.red_result[self.start_idx:self.middle_idx])]

        g_list_right = [elem_g for (idg, elem_g) in
                        enumerate(self.green_result[self.middle_idx:self.end_idx+1])]

        y_list_right = [elem_y for (idg, elem_y) in
                        enumerate(self.yellow_result[self.middle_idx:self.end_idx+1])]

        r_list_right = [elem_r for (idg, elem_r) in
                        enumerate(self.red_result[self.middle_idx:self.end_idx+1])]

        self.gyr_list_left = np.dstack((g_list_left, y_list_left, r_list_left))
        self.gyr_list_right = np.dstack((g_list_right, y_list_right,
                                         r_list_right))

        gyr_list = np.concatenate((self.gyr_list_left, self.gyr_list_right),
                                  axis=0)

        # final result list of value at every single timepoint
        self.x_final_list = [self._convTimeFloat(elem[0][0])
                             for elem in gyr_list]
        count = 1
        for elem in self.gyr_list_left:
            self.x_coord.append(elem[0][0])
            # value = union of (green + yellow + red)* prioritized Position
            value = (l1*elem[1][0] + l2*elem[1][1] + l3*elem[1][2] +
                     m*self.waterlevel_now) * (count) / len(self.gyr_list_left)
            self.y_final_list.append(value)
            self.y_coord.append(value)
            count = count + 1

        for elem in self.gyr_list_right:
            self.x_coord.append(elem[0][0])
            value = (r1*elem[1][0] + r2*elem[1][1] + r3*elem[1][2] +
                     m*self.waterlevel_now)  # *(count)/len(self.gyr_list_right)
            self.y_final_list.append(value)
            self.y_coord.append(value)
            count = count - 1

    """
    Least square polynomial fit method
    """
    def lspm(self):
        '''
        Calculate mean_value for every time_point (see: function calMeanValue)
        '''
        # TODO: pass parameters l1, l2, l3, r1, r2, r3 as type-dict
        if (self.min_wy <= self.waterlevel_now <= self.max_wy):  # yellow zone
            print ("Yellow Zone")
            self._processZone(l1=1/4, l2=1/4, l3=1/4, m=1/4, r1=1/4, r2=1/4,
                              r3=1/4)
            self._task_lspm(self.x_final_list, self.y_final_list)
        elif self.waterlevel_now > self.max_wy:     # red zone
            print ("Red Zone")
            self._processZone(l1=0, l2=1/10, l3=9/10, m=1/10, r1=0, r2=1/10,
                              r3=9/10)
            self._task_lspm(self.x_final_list, self.y_final_list)
        else:   # green zone
            print ("Green zone")
            self._processZone(l1=9/11, l2=1/11, l3=1/11, m=1/11, r1=9/11,
                              r2=1/11, r3=1/11)
            self._task_lspm(self.x_final_list, self.y_final_list)

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

        degree = [1, 2, 3]
        final = []  # contain list of errors measured by every degree
        for dg in degree:
            self.result = np.polyfit(data_x, data_y, dg)
            temp = self.test_waterlevel(self.time_now, self.waterlevel_now)
            final.append((temp, self.result))

        self.result = findresult(final)[1]

        pred_time = data_x[len(data_x)-1]
        # self.pred_waterlevel = self.result[0]*pred_time + self.result[1]
        self.pred_waterlevel = np.polyval(self.result, pred_time)

    """
    Convert the normalized value into real value in cm
    """
    def _convertnormreal(self, data):
        return data*(hwall.values[:, 2].max() - hwall.values[:, 2].min()) \
            + hwall.values[:, 2].min()

    def _convertrealnorm(self, data):
        return (data - self.wg)/(self.wr-self.wg)

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
        '''
        Middle_idx should be idx of start_time (time_now)
        function should return idx
        '''
        if len(self.green_result) == 96:
            self.idx = self.green_result
        elif len(self.yellow_result) == 96:
            self.idx = self.yellow_result
        elif len(self.red_result) == 96:
            self.idx = self.red_result
        else:
            print ("Data is not sufficient to calculate")
            print ("list is empty ", self.idx)
            import sys
            sys.exit
        timeidx = [self._convTimeFloat(elem[0])
                   for elem in self.idx].index(time)
        return timeidx

    """
    Show the final result in normalized format (bet. 0 and 1) and in cm
    """
    def showResult(self):
        print ("\nThe predicting water level is {} "
               .format(self.pred_waterlevel))
        print ("Result in cm is {} "
               .format(self._convertnormreal(self.pred_waterlevel)))

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
        print ("\n --------- Function init_data")
        print ("Data imported from Excel file", hwall.values)
        print ("Highest water level ", hwall.values[:, 2].max())
        print ("Lowest water level ", hwall.values[:, 2].min())

        print ("\n --------- Function classifyData")
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

        print ("\n --------- Function rateofchange")
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
        # boundary between yellow_zone and red_zone
        print ("Max Yellow_Zone (normed): ", self.max_wy)
        print (".... in cm: ", self._convertnormreal(self.max_wy))
        # boundary between green_zone and yellow_zone
        print ("Min Yellow_Zone (normalized): ", self.min_wy)
        print (".... in cm: ", self._convertnormreal(self.min_wy))

        print ("\n --------- Function _process_Zone")
        print ("Indexing: {} {} {}"
               .format(self.start_idx, self.middle_idx, self.end_idx))
        print ("Length left list: ", len(self.gyr_list_left),
               "Length right list: ", len(self.gyr_list_right))
        print ("LEFT ", self.gyr_list_left)
        print ("RIGHT ", self.gyr_list_right)

        print ("\n --------- Function Visualization")
        print ("x_coord :", self.x_coord)
        print ("y_coord :", self.y_coord)

        print ("\n --------- Function _task_lspm")
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
        plt.xlabel('Time from 0:00 to 24:00')
        plt.ylabel('High water level (normalized)')

        # Visual all days (total: 181 days)
        for r in self.roc:
            plt.plot(r[1].values[:, 1], r[1].values[:, 3], color='blue',
                     marker='.')
        plt.show()

    def _visualmeanroc(self):
        plt.xlabel('Time from 0:00 to 24:00')
        plt.ylabel('High water level (normalized)')

        for lr in self.list_roc:
            plt.plot(lr[1].values[:, 1], lr[1].values[:, 3], color='blue',
                     marker='.')

        # Visualize the mean value
        if (len(self.mean_ax) > 0 and len(self.mean_ay) > 0):
            plt.plot(self.mean_ax, self.mean_ay, color='red', marker='.',
                     label='Average Mean Value')

        # TODO: Visualize the predicting water level at predicting time

        # TODO: Visualize the current water level at time_now

        plt.show()

    """
    Visualization
    """
    def _visualize(self):
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

        if (len(self.x_coord) > 0 and len(self.y_coord) > 0):
            plt.plot(self.x_coord, self.y_coord, color='blue',
                     marker='.', label='Average priotized Mean Value')

        # Visualize the predicting water level
        if (self.pred_waterlevel > 0):
            self.pred_time = self.x_coord[len(self.x_coord)-1]
            plt.plot(self.pred_time, self.pred_waterlevel, color='black',
                     marker='X', label='The predicting water level')

        # Visualize the current water level at time_now
        plt.scatter(self.idx[self.middle_idx][0], self.waterlevel_now,
                    color='Orange', marker='X', label='The current water level')

        plt.legend(loc='upper left')
        plt.show()

    # ------------------------------------------------------------------ #
    #                               Method 2
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
        wln = np.around(self.waterlevel_now, decimals=1)

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
                print ("ALARM - Data for current parameters is not sufficient given")
                print ("\n Requirement for method 2 is that all data for all time-points from 0:00 to 24:00 must be given, total length: 96")
                print ("\n However, there are only: ", len(elem), "data points given")
                print (elem)
                print ("\n Please try again with different parameters or choose method 1 to run calculation\n")
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

    """
    Call method 1 to calculate water level
    """
    def dotask(self):
        self.init_data()
        self.normalizedata()
        self.classifydata()
        self.calMeanValue()
        self.lspm()
        self._printOut()  # used for tracking information (debugging)

        print (" \n **************************************  ")
        self.test_waterlevel(self.time_now, self.waterlevel_now)
        self.showResult()
        print (" \n **************************************\n")

        self._visualize()

    """
    Call method 2 based on rate of changes of water level
    """
    def dotaskroc(self):
        self.init_data()
        self.normalizedata()
        self.rateofchange()
        self.calAvrMeanValues()

        print (" \n **************************************  ")
        self.test_waterlevel(self.time_now, self.waterlevel_now)
        self.showResult()
        print (" \n **************************************\n")

        self._visualmeanroc()
        self._printOut()

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
    waterlevel_now = 450.0
    start_time = 10.0       # TODO: WHAT IF start_time in float 2.15, 2.30, 2.45
    predict_hours = 8

    # Input parameters (Yelllow zone, Red zone, Green zone)
    # l1=1/4, l2=1/4, l3=1/4, m=1/4, r1=1/4, r2=1/4, r3=1/4
    # l1=0, l2=1/10, l3=9/10, m=1/10, r1=0, r2=1/10, r3=9/10
    # l1=9/11, l2=1/11, l3=1/11, m=1/11, r1=9/11, r2=1/11, r3=1/11
    # params = {"redzone":[{}], "yellowzone":[{}], "greenzone":[{}]}

    if predict_hours > 12:
        print ("predict_hours can be max at 12")
    else:
        # Call method 1
        fp = FloodPred(waterlevel_now, start_time, predict_hours)
        fp.dotask()

        # Call method 2
        fp2 = FloodPred(waterlevel_now, start_time, predict_hours)
        fp2.dotaskroc()
        fp2.dovisual()

    # TODO: write test to try all combination of all coefficients l1, l2, l3,
    # r1, r2, r3 and find out the best combination so that the testresult
    # should have the best error estimate
    # TODO: improve function test_waterlevel with using pytest, nose (assert)
    # TODO: apply dask module for parallel computing
