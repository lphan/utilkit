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
# from floodpred import dotask, dotaskroc, dovisual
import floodpred
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
        kwargs = {"waterlevel_now": waterlevel, "start_time": time,
                  "predict_hours": hours}
        if (method == 1):
            logging.info("Input '1', run first method")
            floodpred.dotask(**kwargs)     # Method 1

        elif (method == 2):
            logging.info("Input '2', run second method")
            floodpred.dotaskroc(**kwargs)  # Method 2

        elif (method == 3):
            logging.info("Input '3', run both methods")
            floodpred.dotask(**kwargs)     # Method 1

            floodpred.dotaskroc(**kwargs)  # Method 2

        elif (method == 4):
            logging.info("Input '4', run visual history data")
            floodpred.dovisual(**kwargs)

        elif (method == 5):
            logging.info("Input '5', run all methods")
            floodpred.dotask(**kwargs)     # Method 1

            floodpred.dotaskroc(**kwargs)  # Method 2

            floodpred.dovisual(**kwargs)   # Visual history data

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
