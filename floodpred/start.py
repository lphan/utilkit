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
    waterlevel = input("Input the current waterlevel in format ex. 300.0")
    time = input("Input the current time in format e.g. 10.0 (for 10AM)")
    hours = input("Input the predicting hours in format e.g. 8.0 (for 8 hours)")

    if (type(waterlevel) and type(time) and type(hours) is float):
        kwargs = {"waterlevel": waterlevel, "time_now": time,
                  "time_predict": hours}
        fp = FloodPred(**kwargs)
        fp.dotask()
    else:
        logging.warning('Wrong type, please input data again')
        # logging.info(type(waterlevel), type(time), type(hours))
