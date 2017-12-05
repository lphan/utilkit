from __future__ import division
import logging
import logging.handlers
import subprocess
import csv
from pandas import read_csv
from pandas.io.parsers import ParserError as ppp
import pandas.io.common
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math
import numpy as np

# ********* This file is used for python code with default-settings? ***********
# NOTICE: security issues
class MultiDownloadYT(object):
    pass

# ----------------- Logging Setting ---------------------------------
class MetaLog(object):
    """ Class implementing log for metadata in format .csv """

    _instance = None

    def foo(self):
        return id(self)

    def __init__(self, func_name, metalog_active=False):
        self.func_name = func_name
        self.metalog_status = metalog_active
        self.count = 0

        # TODO: if log-directory does not exist, create one. Otherwise, pass
        # self.log_dir = './'

        if metalog_active:
            self.logger = self._initBasicLogger()
            self._initMetaLogger()
        else:
            self.logger = self._initBasicLogger()

    def _initBasicLogger(self):
        """ Initialize Basic Logger Settings """

        LOG_FILENAME = self.func_name+'.log'
        self.count = self.count + 1

        # logging.basicConfig(level=logging.DEBUG,
        #                     format='%(asctime)s - %(name)s - \
        #                           %(levelname)-8s %(message)s',
        #                     datefmt='%a, %d %b %Y %H:%M:%S',
        #                     filename=LOG_FILENAME, filemode='w')

        # Console log settings
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))

        # Rotatefile log settings
        rotatefile = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                                          maxBytes=1000000,
                                                          backupCount=5)
        rotateformatter = logging.Formatter('%(asctime)s - %(name)s - \
                                            %(levelname)-8s %(message)s')
        rotatefile.setFormatter(rotateformatter)

        # TODO: inner function
        if self.func_name == 'logging-vid':
            logger = logging.getLogger('downloadVid')
            logger.setLevel(logging.INFO)
            logger.addHandler(console)
            logger.addHandler(rotatefile)
            logger.info('Logger: logging download video(s) activated')

        if self.func_name == 'logging-img':
            logger = logging.getLogger('downloadImg')
            logger.setLevel(logging.INFO)
            logger.addHandler(console)
            logger.addHandler(rotatefile)
            logger.info('Logger: logging download image(s) activated')

        if self.func_name == 'logging-doc':
            logger = logging.getLogger('downloadDoc')
            logger.setLevel(logging.INFO)
            logger.addHandler(console)
            logger.addHandler(rotatefile)
            logger.info('Logger: logging download document(s) activated')

        # else:
            #    logger = logging.getLogger('UNKNOWN')
            #    logger.setLevel(logging.INFO)
            #    logger.addHandler(console)
            #    logger.addHandler(rotatefile)
            #    logger.info('Logger: logging UNKNOWN activated')

        return logger

    def _initMetaLogger(self):
        """ Initialize the Meta Logger Settings """
        META_FILE_NAME = self.func_name+'.csv'
        subprocess.call(["touch", META_FILE_NAME])
        # TODO: Check Level_Debug Modus, default= False

    def getLogger(self):
        """ Get Logger instance """
        return self.logger

    def getMetaLogStatus(self):
        """ get MetaLog status """
        return self.metalog_status

    def getFuncName(self):
        """ get Function Name """
        return self.func_name

    def recordMetaData(self, metalist):
        """ save MetaData from download images to csv-file """
        outputFile = open(self.func_name+'.csv', 'wb')
        try:
            writer = csv.writer(outputFile, dialect='excel')
            for elem in metalist:
                writer.writerow(elem)
        finally:
            outputFile.close()

# -------------------------------------------------------------------


def Singleton(class_name, func_name, metalog_active=False):
    if not class_name._instance:
        # func_name = 'logging-webpage2'
        class_name._instance = class_name(func_name, metalog_active)

    return class_name._instance


class B(MetaLog):
    pass


class VisualData(object):

    def __init__(self, filename, data, visual=False):
        self.filename = filename
        self.visual = visual
        self.data = data
        self.sizelist = []

    def readDataCSV(self):
        """ open csv-file and read (visual) data using pandas"""
        def getDataCSV(self):
            """ query length of data found in file """
            return len(self.data)

        if (getDataCSV(self.data) == 0):
            return
        else:
            for elem in self.data:
                # TODO: get file-name from link
                x = elem[2] / 1000
                self.sizelist.append(math.ceil(x))

    def getDataFormat(self):
        """ query content types of data format in file """
        image_format = ['image/jpeg', 'image/gif', 'image/png']
        count_jpg = 0
        count_png = 0
        count_gif = 0
        for elem in self.data:
            if elem[1] == image_format[0]:
                count_jpg = count_jpg + 1
            elif elem[1] == image_format[1]:
                count_gif = count_gif + 1
            elif elem[1] == image_format[2]:
                count_png = count_png + 1
            else:
                print ("UNKNOWN FORMAT ", elem[1])

        dataformat = {'image/jpeg': count_jpg, 'image/gif': count_gif,
                      'image/png': count_png}

        return dataformat

    def visualDataFormat(self):
        """ visual data by creating diagram using matplotlib """
        y = self.sizelist
        x = np.arange(len(self.sizelist))
        # TODO: error here incompatible size
        # z = (9.0, 8.0, 11.0, 9.0, 10.0, 12.0, 8.0, 10.0, 8.0, 9.0)
        plt.bar(x, y)
        plt.xlabel('Elements')
        plt.ylabel('Value')
        plt.title('Value by size in KB of every element image')
        # plt.show()

        # Save first bar-diagram of size files
        filename = 'diagrambar-size.png'
        with open(filename, 'w') as path:
            plt.savefig(path, dpi=100)


def testVisual(filename):
    try:
        data = read_csv(filename).values
    except (ppp, pandas.io.common.EmptyDataError):
        return

    test = VisualData(filename, data)
    test.readDataCSV()
    test.visualDataFormat()


if __name__ == '__main__':
    # b = Singleton(MetaLog, func_name='logging-webpage')
    # c = Singleton(B, func_name='logging-links')
    # d = Singleton(MetaLog, func_name='logging-url')
    # # print (id(b), b.foo())
    # # print (id(c), c.foo())
    # # print (id(d), d.foo())
    testVisual('../log/logging-webpage.csv')
