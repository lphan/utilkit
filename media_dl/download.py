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
Description: Top Class download Media data
'''

import urllib.parse as up
import os
import re
# import pycurl
# import multiprocessing

from src.imgdl.downloadImg import DownloadImg
from src.imgdl.multiDownloadImg import MultiDownload
from src.viddl.multiDownloadYT import MultiDownloadYT
from multiprocessing import Process   #, Queue
from queue import Empty
# from start import logger
# logger = set_logger()


class DownloadMedia(object):
    def __init__(self, **kwargs):
        """
        args_vid : bool type of vid_dl (True = download)
        args_img : bool type of img_dl
        args_doc : bool type of doc_dl
        **kwargs : dictionary type containing configuration information
        save_location: location where document will be saved
        """

        self.dl_vid = kwargs["args_vid"]
        self.dl_img = kwargs["args_img"]
        self.dl_doc = kwargs["args_doc"]

        self.vid_url = kwargs["vid_url"]
        self.vid_txt_file = kwargs["vid_txt_file"]
        self.vid_html_link = kwargs["vid_html_link"]

        self.img_url = kwargs["img_url"]
        self.img_txt_file = kwargs["img_txt_file"]
        self.img_html_link = kwargs["img_html_link"]

        self.doc_url = kwargs["doc_url"]
        self.doc_txt_file = kwargs["doc_txt_file"]
        self.doc_html_link = kwargs["doc_html_link"]

        self.vid_loc = kwargs["vid_loc"]
        self.img_loc = kwargs["img_loc"]
        self.doc_loc = kwargs["doc_loc"]

    def get_metadata(self):
        """ get list all Metadata for URLs """
        return self.metadata

    def parallel_task(self, work_queue, cpu_cores):
        """ run parallel processes """
        def do_work(q):
            while True:
                try:
                    # queue_size = q.qsize()
                    # # # logger.info(queue_size)
                    self.__downloadfile([q.get(block=False)])
                except Empty:
                    break

        processes = [Process(target=do_work, args=(work_queue,))
                     for i in range(cpu_cores)]

        for p in processes:
            p.start()
        for p in processes:
            p.join()

    def download_task(self):
        def pre_processing(txt_path):
            if txt_path is not None:
                try:
                    openfile = open(txt_path, 'rb')
                    lines = openfile.readlines()
                    openfile.close()
                except IOError as e:
                    # # logger.error('I/O Error (Errno %d) : %s', e.errno,
                    #                  e.strerror)
                    pass
                    import sys
                    sys.exit()
                # check empty file (file without any links/ lines)
                if len(lines) == 0:
                    # # logger.error('Empty File. Exit!')
                    pass
                    return
                else:
                    self.__download_from_file(lines)
                    pass

            # else: TODO: again for url and html_link
            #     self.__download_from_url(self.media_url)

        pre_processing(self.vid_txt_file)

        # if self.dl_img:
        #     pre_processing(self.img_url, self.img_txt_file, self.img_html_link)
        #
        # if self.dl_doc:
        #     pre_processing(self.doc_url, self.doc_txt_file, self.doc_html_link)

    def __download_from_url(self, media_url):
        valid, data_type = self.__validate_url_format(media_url)
        if valid:
            # # logger.info('......... Result: Valid link ')
            if data_type == 'img':
                # # logger.info("DOWNLOAD jpg")  # self.__downloadfile([self.doc_url])
                pass
            elif data_type == 'doc':
                # # logger.info("DOWNLOAD pdf")  # self.__downloadfile([self.doc_url])
                pass

        else:
            # # logger.warning('......... Result: NOT valid ')
            return

    """
    Download from file in format csv
    CSV: url (webpage), file format
    e.g.
       www.abc.com, pdf, doc
       www.def.com, jpg, tif
       www.gfh.com, mp4, mp3
    """
    def __download_from_file(self, lines):
        links = []

        if self.dl_vid:
                        
            # remove \r and \n and decode the character 'b' (byte-object) call __validate_mpeg_format 
            print(lines)
            lines = [line.rstrip().decode("utf-8") for line in lines]
            # print(line)
            print(lines)
            vd = DownloadVid(self.vid_url, lines)
            vd.download()

        elif self.dl_img:
            for idx, line in enumerate(lines):
                # logger.info('Validation link: (%d) %s', idx, line)
                if idx == len(lines) - 1:
                    # in case last line is '\n'
                    if line == '\n':
                        pass
                    else:
                        # last line is link, append '\n' to last line
                        if not (line[-1] == '\n'):
                            line = str(line) + '\n'
                valid = self.__validate_url_format(line)
                if valid:
                    # # logger.info('......... Result: Valid link ')
                    links.append(line)

                else:
                    # logger.warning('......... Result: NOT valid ')
                    pass

            print(self.img_url, self.img_txt_file, self.img_html_link, self.save_location)
            img = DownloadImg(self.img_url, self.img_txt_file, self.img_html_link, self.save_location)
            img.download()

        elif self.dl_doc:
            doc = DownloadDoc(links)
            doc.download()

        else:
            # logger.warning('No valid links to download')
            return

    # Validate format of URLs (protocol) inside file
    @staticmethod
    def __validate_image_format(url):
        """
        Validate format of url
        Valid link must be in format http:// or https://.../file.jpg
        """

        scheme, netloc, path, query, fragment = up.urlsplit(url)
        filename = str(os.path.basename(path))

        img = filename.split('.')[-1]

        # filename_pattern = "([\da-zA-Z0-9=:_\.\/-]+.[(jpg)|(jpeg)|(JPG)|(png)|(gif)]+\w)"
        # filename_obj = re.compile(filename_pattern)
        # valid_filename = filename_obj.findall(filename)

        # TODO: use Regular expression to check validity of url-filename in format .jpg
        # in all types images, video and documents
        if (scheme == 'http' or scheme == 'https') and \
                (img[:-1] in ['jpg', 'JPG', 'png', 'PNG', 'gif'] or
                 img in ['jpg', 'JPG', 'png', 'PNG', 'gif']):
            img = 'img'
            return True, img
        else:
            return False
    
    def __validate_doc_format(url):
        """
        Validate format of url
        Valid link must be in format http:// or https://.../file.pdf or .doc
        """

        scheme, netloc, path, query, fragment = up.urlsplit(url)
        filename = str(os.path.basename(path))

        doc = filename.split('.')[-1]

        if (scheme == 'http' or scheme == 'https') and \
                (doc[:-1] in ['pdf', 'PDF', 'doc', 'DOC'] or
                 doc in ['pdf', 'PDF', 'doc', 'DOC']):
            pdf = 'doc'
            return True, pdf
        else:
            return False

    def __validate_mpeg_format(url):
        """
        Validate format of url
        Valid link must be in format http:// or https://.../file.mkv or .mp4
        """

        scheme, netloc, path, query, fragment = up.urlsplit(url)
        filename = str(os.path.basename(path))
        mp = filename.split('.')[-1]
        if (scheme == 'http' or scheme == 'https') and \
                (mp[:-1] in ['mp4', 'webm', 'mkv'] or 
                 mp in ['mp4', 'webm', 'mkv']):
            mp = 'mp4'
            return True, mp
        else:
            return False

    # get Name from link
    @staticmethod
    def __get_name_file(url):
        scheme, netloc, path, query, fragment = up.urlsplit(url)
        filename = os.path.basename(path)
        if "\n" in filename[len(filename)-1]:
            return filename[:-1]
        else:
            return filename

    # get Meta Information from Header
    @staticmethod
    def __get_meta_header(connection):
        meta = connection.info()
        meta_header = meta.getheaders if hasattr(meta, 'getheaders') else \
            meta.get_all
        return meta_header


class DownloadImg(DownloadMedia):
    def __init__(self, img_url, img_links):
        self.img_url = img_url
        self.img_links = img_links

    def download(self):
        dl = MultiDownload(self.img_url, self.img_links)
        dl.download_task()


class DownloadDoc(DownloadMedia):
    def __init__(self, doc_links):
        self.doc_links = doc_links

    def download(self):
        # call module downloaddoc.py
        pass


class DownloadVid(DownloadMedia):
    def __init__(self, vid_url, vid_links):
        self.vid_url = vid_url
        self.vid_links = vid_links

    def download(self):
        dl = MultiDownloadYT(self.vid_url, self.vid_links, mt=False, mp=True)
        dl.dl_from_file()
