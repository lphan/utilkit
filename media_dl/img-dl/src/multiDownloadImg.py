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
Description: Download images parsed from URL (libcurl)
'''

# import urllib2
# import urlparse
# import os
import re
import sys
# import logging
# import logging.handlers
import pycurl
from downloadImg import DownloadImg

# Console settings
# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# formatter = logging.Formatter(' %(levelname)-8s %(message)s')
# console.setFormatter(formatter)
# logger = logging.getLogger('multiDownloadImg')
# logger.addHandler(console)
# ---------------------------------------------------------------
from util import MetaLog, Singleton

# -*- coding: utf-8 -*-
# vi:ts=4:et
PY3 = sys.version_info[0] > 2


class Test:
    def __init__(self):
        self.contents = ''
        if PY3:
            self.contents = self.contents.encode('ascii')

    def body_callback(self, buf):
        self.contents = self.contents + buf

sys.stderr.write("Testing %s\n" % pycurl.version)


class MultiDownload(object):

    def __init__(self, url, save_location, metalog_active=False):
        self.save_location = save_location
        self.url = url

        self.ml = Singleton(MetaLog, func_name='logging-webpage')
        self.logger = self.ml.getLogger()
        self.logger.info('Init MultiDownload')
        self.mla = metalog_active
        self.metalist = []

    # Function to download HTML-page
    def download_task(self):
        t = Test()
        c = pycurl.Curl()
        c.setopt(c.URL, self.url)
        c.setopt(c.WRITEFUNCTION, t.body_callback)
        c.perform()
        c.close()

        obj = t.contents
        self.__parseImg(obj)

        # pass metalist to util-recordMetaData to create csv
        if self.mla:
            print "PRINT: ", self.metalist
            self.ml.recordMetaData(self.metalist)

    # Function to parse the downloaded HTML-content and download
    def __parseImg(self, content):
        self.logger.debug(content)
        self.logger.debug("Type content: %s", type(content))

        # FIRST: Parse HTML-tag using regular expression
        imgpattern = "(<img[a-zA-Z0-9=:_.\"'-/ >]+)"
        imgobj = re.compile(imgpattern)
        imglist = imgobj.findall(content)
        self.logger.debug("FIRST FILTER")
        self.logger.debug("Imagelist: %s", imglist)
        self.logger.debug("Imageslist length: %d", len(imglist))

        # SECOND: Parse link from img-tag
        imgpattern2 = "(src=['|\"][https?:]*\/\/[\da-zA-Z0-9=:_\.\/-]+\w)"
        imgobj2 = re.compile(imgpattern2)

        # THIRD: Filter link inside img-tag in src='', (gif) goes wrong.
        imgpattern3 = "([\da-zA-Z0-9=:_\.\/-]+.[(jpg)|(jpeg)|(JPG)|(png)|(gif)]+\w)"
        imgobj3 = re.compile(imgpattern3)

        # FOURTH: Check link in src=''
        imgpattern4 = "(https?://)"
        imgobj4 = re.compile(imgpattern4)

        # FIFTH: Special Check link in src=''
        imgpattern5 = "(src=['|\"][\da-zA-Z0-9=:_\.\/-]+\w)"
        imgobj5 = re.compile(imgpattern5)

        self.logger.info("IMAGE LIST = %s", imglist)

        for elem in imglist:
            self.logger.debug("SECOND FILTER")
            self.logger.debug("IMG link= %s", elem)
            urllink2 = imgobj2.findall(elem)
            self.logger.info("URL link= %s", urllink2)
            self.logger.info("Type link= %s", type(urllink2))
            if len(urllink2) == 0:
                # add root-webpage
                self.logger.info("url link is empty")
                urllink5 = imgobj5.findall(elem)
                # self.logger.info("length urllink2 = %s", urllink2)
                for src in urllink5:
                    self.logger.debug(" ********** %s", src)
                    # hack to cut the first 5 characters src="
                    newlink = self.url+'/'+src.split('"')[1]
                    self.logger.info("\n Newlink = %s", newlink)
                    kwargs = {"path_file": None,
                              "save_location": self.save_location,
                              "imageurl": newlink}
                    dl = DownloadImg(**kwargs)
                    dl.download_task()

                    # append new metadata for metalist
                    self.metalist.append(dl.getMetaDataImg()[0])
            else:
                self.logger.debug("url link is not empty")
                for elem in urllink2:
                    self.logger.debug("ELEM = %s", elem)
                    urllink3 = imgobj3.findall(elem)
                    self.logger.debug("------ THIRD FILTER ------")
                    self.logger.debug("------ IMG link= %s", elem)
                    self.logger.debug("------ URL link= %s", urllink3)
                    self.logger.info("Valid link... start to download")
                    if len(urllink3) > 0 and \
                        bool(imgobj4.search(urllink3[0])) is False and \
                            '//' in urllink3[0]:
                        self.logger.debug("------ ERROR URL, need to fix")
                        self.logger.debug("------ new url: %s",
                                          'http:'+urllink3[0])
                        kwargs = {"path_file": None,
                                  "save_location": self.save_location,
                                  "imageurl": 'http:'+urllink3[0]}
                        dl = DownloadImg(**kwargs)
                        dl.download_task()
                    elif len(urllink3) > 0 and \
                        bool(imgobj4.search(urllink3[0])) is False and \
                            '//' not in urllink3[0]:
                        self.logger.debug("------ ERROR URL, need to fix")
                        self.logger.debug("------ new url: %s",
                                          'http://'+urllink3[0])
                        kwargs = {"path_file": None,
                                  "save_location": self.save_location,
                                  "imageurl": 'http://'+urllink3[0]}
                        dl = DownloadImg(**kwargs)
                        dl.download_task()
                    elif len(urllink3) == 0:
                        self.logger.debug("------ ERROR URL, can NOT FIX")
                    else:
                        self.logger.info("------ URL VALID TRUE")
                        self.logger.info(urllink3[0])
                        kwargs = {"path_file": None,
                                  "save_location": self.save_location,
                                  "imageurl": urllink3[0]}
                        dl = DownloadImg(**kwargs)
                        dl.download_task()


if __name__ == '__main__':
    # url = 'https://curl.haxx.se/dev/'
    # url = 'http://www.schlafsack-fabrik.de'
    # http://i1382.photobucket.com/albums/ah245/PhotobucketMKTG/whitespace-divider.png
    # url = 'http://s5.photobucket.com/'
    url = 'http://www.youtube.com'
    save_location = '../sourceimage'
    test = MultiDownload(url, save_location)
    test.download_task()
