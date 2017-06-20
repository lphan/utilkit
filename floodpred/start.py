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
    waterlevel = float(input("Input the current waterlevel ex. 300.0: "))
    time = float(input("Input the current time e.g. 10.0 (for 10AM): "))
    hours = float(input("Input the predicting hours e.g. 8.0 (for 8 hours): "))
    method = float(input("Choose '1' to start method 1, '2' for method 2, '3' \
                         for both, '4' to visual history data, others to quit: \
                         "))
    if (type(waterlevel) and type(time) and type(hours) is float):
        kwargs = {"waterlevel": waterlevel, "time_now": time,
                  "time_predict": hours}
        if (method == 1):
            fp1 = FloodPred(**kwargs)
            fp1.dotask()     # Method 1
        elif (method == 2):
            fp2 = FloodPred(**kwargs)
            fp2.dotaskroc()  # Method 2
        elif (method == 3):
            fp1 = FloodPred(**kwargs)
            fp1.dotask()     # Method 1

            fp2 = FloodPred(**kwargs)
            fp2.dotaskroc()  # Method 2
        elif (method == 4):
            fp = FloodPred(**kwargs)
            fp.dovisual()
        else:
            logging.info("Quit...")
    else:
        logging.warning('Wrong type, please input data again')
        # logging.info(type(waterlevel), type(time), type(hours))
