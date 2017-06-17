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
Description: Download images from plaintext-file in format jpeg.
Version using pycurl (libcurl)
'''

import urllib2
import urlparse
import os
import sys
import pycurl

# import util
# import downloadlog

# import logging
# import logging.handlers

# ----------------- Logging Setting ---------------------------------
# LOG_FILENAME = 'download.log'
# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s-%(name)s-%(levelname)-8s %(message)s',
#                     datefmt='%a, %d %b %Y %H:%M:%S',
#                     filename=LOG_FILENAME, filemode='w')

# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# formatter = logging.Formatter(' %(levelname)-8s %(message)s')
# console.setFormatter(formatter)
# logger = logging.getLogger('DownloadImg')
# logger.addHandler(console)
# -------------------------------------------------------------------
from util import MetaLog, Singleton
import multiprocessing
from multiprocessing import Process, Queue
from Queue import Empty


class DownloadImg(object):

    def __init__(self, path_file, imageurl, save_location):
        '''
        path_file: path of text file at local
        url: input url directly from CLI
        save_location: location where images will be saved
        '''
        self.save_location = save_location
        self.imageurl = imageurl
        self.path_file = path_file

        # call logging-function from util
        ml = Singleton(MetaLog, func_name='logging-url')
        # self.metaactive = ml.getMetaLogStatus()
        self.metadataimg = []
        self.fn = ml.getFuncName()
        self.logger = ml.getLogger()
        self.logger.info('Init DownloadImg')

    def getMetaDataImg(self):
        """ get list all Metadata for URLs """
        return self.metadataimg

    def taskProcesses(self, work_queue, cpu_cores):
        def do_work(q):
            while True:
                try:
                    # queue_size = q.qsize()
                    # self.logger.info(queue_size)
                    link = q.get(block=False)
                    validlink = []
                    validlink.append(link)
                    self.__downloadfile(validlink)
                except Empty:
                    break

        processes = [Process(target=do_work, args=(work_queue,))
                     for i in range(cpu_cores)]

        for p in processes:
            p.start()
        for p in processes:
            p.join()

    def download_task(self):
        # Open & read file from path_file
        if self.path_file is not None:
            self.__download_from_file()
        else:
            self.__download_from_url()

    def __download_from_url(self):
        valid = self.__validateURLFormat(self.imageurl)
        if valid:
            self.logger.info('......... Result: Valid link ')
            self.__downloadfile([self.imageurl])
        else:
            self.logger.warning('......... Result: NOT valid ')
            return

    def __openfile(self):
        try:
            openfile = open(self.path_file, 'rb')
            lines = openfile.readlines()
            openfile.close()
        except IOError as e:
            self.logger.error('I/O Error (Errno %d) : %s', e.errno, e.strerror)
            import sys
            sys.exit()
        # check empty file (file without any links/ lines)
        if len(lines) == 0:
            self.logger.warn('Empty File. Exit!')
            return
        else:
            return lines

    def __download_from_file(self):
        lines = self.__openfile()

        validlinks = []
        for idx, line in enumerate(lines):
            self.logger.info('Validation link: (%d) %s', idx, line)
            if idx == len(lines) - 1:
                # in case last line is '\n'
                if line == '\n':
                    pass
                else:
                    # last line is link, append '\n' to last line
                    if not (line[-1] == '\n'):
                        line = str(line) + '\n'
            valid = self.__validateURLFormat(line)
            if valid:
                self.logger.info('......... Result: Valid link ')
                validlinks.append(line)
            else:
                self.logger.warning('......... Result: NOT valid ')
                pass

        # Check parallel-condition (at least 2 cores)
        cpu_cores = multiprocessing.cpu_count()
        if cpu_cores > 1:
            work_queue = Queue()
            for l in validlinks:
                work_queue.put(l)

        if len(validlinks) > 0:
            if work_queue.qsize() > 0:
                self.taskProcesses(work_queue, cpu_cores)
            else:
                self.__downloadfile(validlinks)
        else:
            self.logger.warning('No valid links to download')
            return

    # Validate format of URLs (protocol) inside file
    def __validateURLFormat(self, url):
        '''
        Validate format of url
        Valid link must be in format http:// or https://.../file.jpg
        '''
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        filename = os.path.basename(path)
        img = filename.split('.')[-1]

        # url="^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$"
        # check validity of url
        if (scheme == 'http' or scheme == 'https') and \
                (img[:-1] in ['jpg', 'JPG', 'png', 'PNG', 'gif'] or
                 img in ['jpg', 'JPG', 'png', 'PNG', 'gif']):
            return True
        # elif (scheme == 'http' or scheme == 'https') and ..\
        #         # TODO: validate address of webpage, try regular expression
        #     pass
        else:
            return False

    # get Name from link
    def __getNameFile(self, url):
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        filename = os.path.basename(path)
        if "\n" in filename[len(filename)-1]:
            return filename[:-1]
        else:
            return filename

    # get Meta Information from Header
    def __getMetaHeader(self, connection):
        meta = connection.info()
        meta_header = meta.getheaders if hasattr(meta, 'getheaders') else \
            meta.get_all
        return meta_header

    # Execute Download action & check status-code
    def __downloadfile(self, links):
        '''
        Download multiple files input from links
        '''
        self.logger.info("links = %s", links)

        # inner function to download file
        def downloadURL(link):
            name = self.__getNameFile(link)

            try:
                savepath = os.path.join(self.save_location, name)
                with open(savepath, 'wb') as code:
                    self.logger.info(".... Starting download")
                    c = pycurl.Curl()
                    c.setopt(c.URL, link.replace('\n', ''))
                    c.setopt(c.WRITEDATA, code)
                    c.perform()
                    c.close()
            except IOError as e:
                self.logger.error('OS Error- wrong path (Errno %d), Message: \
                                  %s', e.errno, e.strerror)
                sys.exit()

        # inner function to validate HTTP Status code
        def validateHTTP(link):
            req = urllib2.Request(link)
            try:
                connection = urllib2.urlopen(req)
            except urllib2.HTTPError as e:
                # Error codes in range 400, 599
                self.logger.error('error code %d, Message: %s', e.code,
                                  e.strerror)
                sys.exit()
            finally:
                self.logger.info('Status OK')
            return connection

        for link in links:
            # check HTTP Status code
            conn = validateHTTP(link)

            # get Meta Information from header of link
            header_info = self.__getMetaHeader(conn)

            file_lastchanged = header_info("Last-Modified")[0]
            file_format = header_info("Content-Type")[0]
            file_size = header_info("Content-Length")[0]

            # proceed the last check
            if file_format == 'image/jpeg' or 'image/png' or 'image/gif' \
                    and file_size > 0:
                # save Metadata to csv-file
                # TODO: improvement to eliminate the following if-condition
                self.logger.info('File Download: %s', link)
                self.logger.info('File Format: %s', file_format)
                self.logger.info('File Size: %s', file_size)
                self.logger.info('Last-Modified: %s', file_lastchanged)
                self.metadataimg.append([link, file_format, file_size,
                                        file_lastchanged])
                # TODO: check existence of file and continues write to file
                # with open(self.fn+'.csv', 'wb') as mycsv:
                #     csv.writer(mycsv, dialect='excel').writerow(temp[0])
                # mycsv.close()
                # else:
                #     self.logger.info('File Download: %s', link)
                #     self.logger.info('File Format: %s', file_format)
                #     self.logger.info('File Size: %s', file_size)
                #     self.logger.info('Last-Modified: %s', file_lastchanged)
                downloadURL(link)
            else:
                self.logger.ERROR('Error format ')
