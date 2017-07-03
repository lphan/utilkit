#!/usr/bin/env python
#
# Copyright (c) 2014-2015 SUSE LLC
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
__author__ = 'Long Phan'

'''
Description: Input basic parameters to predict water level in next hours
'''
from floodpred import FloodPred
import logging
logging.basicConfig(filename='floodpred.log', level=logging.DEBUG)


if __name__ == '__main__':
    waterlevel = float(input("Input the current waterlevel e.g. 450.0: "))
    time = float(input("Input the current time e.g. 10.0 (for 10AM): "))
    hours = float(input("Input the predicting hours e.g. 8.0 (for 8 hours): "))
    method = float(input("Choose '1' to start method 1, \
                         choose '2' for method 2, \
                         choose '3' for both methods, \
                         choose '4' to visual history data, \
                         choose '5' to run all methods, \
                         Others to quit: \
                         "))
    if (type(waterlevel) and type(time) and type(hours) is float):
        kwargs = {"waterlevel": waterlevel, "time_now": time,
                  "time_predict": hours}
        if (method == 1):
            logging.info("Input '1', run first method")
            fp1 = FloodPred(**kwargs)
            fp1.dotask()     # Method 1

        elif (method == 2):
            logging.info("Input '2', run second method")
            fp2 = FloodPred(**kwargs)
            fp2.dotaskroc()  # Method 2

        elif (method == 3):
            logging.info("Input '3', run both methods")
            fp1 = FloodPred(**kwargs)
            fp1.dotask()     # Method 1

            fp2 = FloodPred(**kwargs)
            fp2.dotaskroc()  # Method 2

        elif (method == 4):
            logging.info("Input '4', run visual history data")
            fp = FloodPred(**kwargs)
            fp.dovisual()

        elif (method == 5):
            logging.info("Input '5', run all methods")
            fp1 = FloodPred(**kwargs)
            fp1.dotask()     # Method 1

            fp2 = FloodPred(**kwargs)
            fp2.dotaskroc()  # Method 2

            fp2.dovisual()  # Visual history data

        else:
            logging.info("Quit...")
    else:
        logging.warning('Wrong type, please input data again')
        # logging.info(type(waterlevel), type(time), type(hours))

# TODO: decorator function to record parameters and save it to json-file, call
# function with userlog.json to add more data optionally. If json in
# userlog.json exist, continue. Otherwise, continue without using userlog.json,
# decorator should work as pre-processing to check and import data from
# userlog.json and postprocessing to add current water level and timing
# into userlog.json to update list of data.
