import numpy as np
from floodpred import FloodPred
# import floodpred
from scipy.optimize import curve_fit
from data import pd, hwall, MAX_LENGTH_IDX


class Predict(FloodPred):

    def __init__(self, waterlevel, time_now, time_predict):
        FloodPred.__init__(self, waterlevel, time_now, time_predict)

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
        degree = [1, 2]
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
        # self.coeff_gyr = [(self.number_green[i][1]/self.total_gyr[i],
        #                    self.number_yellow[i][1]/self.total_gyr[i],
        #                    self.number_red[i][1]/self.total_gyr[i])
        #                   for i in range(96)]
        # print ("\nCoefficients ", self.coeff_gyr)

    """
    Find all points at every time points, sorted wrt. current water level
    """
    def _findAllPoints(self):
        df = pd.DataFrame(hwall[['Zeit', 'W normed']])
        troc = df.groupby(['Zeit'])

        # Sort water level wrt. current water level
        sortedwl = []
        for elem in troc:
            sortedwl.append(sorted([(e[1], abs(e[1]-self.waterlevel_now))
                            for e in elem[1].values], key=lambda te: te[1]))

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
