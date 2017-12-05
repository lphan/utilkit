#!/usr/bin/env python3
#
# Copyright (c) 2014-2015
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

__author__ = 'Long Phan'

'''
Description: others download media-data
'''
import configparser
import json
import io
from src.others.util import Singleton, MetaLog
from download import DownloadMedia, DownloadImg, DownloadDoc, DownloadVid


if __name__ == '__main__':

    # Load the configuration file
    # TODO: exeception
    config = configparser.ConfigParser()
    config.read('config.ini')

    args_vid = config.getboolean('media', 'viddl')
    args_img = config.getboolean('media', 'imgdl')
    args_doc = config.getboolean('media', 'docdl')

    vid, img, doc = [], [], []

    if args_vid:
        mf = Singleton(MetaLog, func_name='logging-vid')
        logger = mf.getLogger()
        logger.info('Logger: Starting download video(s)')

        # dl = DownloadImg(**kwargs)
        # dl.download_task()
        vid_url = config['viddl']['vid_url']
        vid_txt = config['viddl']['vid_txt_file']
        vid_wp = config['viddl']['vid_html_link']
        vid = [vid_url, vid_txt, vid_wp]
    else:
        vid = ['', '', '']

    if args_img:
        mf = Singleton(MetaLog, func_name='logging-img')
        logger = mf.getLogger()
        logger.info('Logger: Starting download image(s)')

        # dl = DownloadImg(**kwargs)
        # dl.download_task()
        img_url = config['imgdl']['img_url']
        img_txt = config['imgdl']['img_txt_file']
        img_wp = config['imgdl']['img_html_link']
        img = [img_url, img_txt, img_wp]
    else:
        img = ['', '', '']

    if args_doc:
        # TODO: input-argument to set METALOG_active value TRUE| FALSE
        mf = Singleton(MetaLog, func_name='logging-doc', metalog_active=True)
        logger = mf.getLogger()
        logger.info('Logger: Starting download document(s)')

        # dl = MultiDownload(metalog_active=True, **kwargs)
        # dl.download_task()
        doc_url = config['docdl']['doc_url']
        doc_txt = config['docdl']['doc_txt_file']
        doc_wp = config['docdl']['doc_html_link']
        doc = [doc_url, doc_txt, doc_wp]
    else:
        doc = ['', '', '']

    sl = config['others']['save_location']

    kwargs = {"vid_url": vid[0], "vid_txt_file": vid[1], "vid_html_link": vid[2],
              "img_url": img[0], "img_txt_file": img[1], "img_html_link": img[2],
              "doc_url": doc[0], "doc_txt_file": doc[1], "doc_html_link": doc[2],
              "save_location": sl}

    # print(kwargs["vid_txt_file"])
    d = DownloadMedia(args_vid, args_img, args_doc, **kwargs)
    d.download_task()

    # elif (args.links and args.save):
    #     # TODO: check format whether file is csv
    #     print "PRINT: analyse CSV_DATA"
    #     mf = Singleton(MetaLog, func_name='analyse', metalog_active=False)
    #     mf.readDataCSV(args.links, ops='read_data')

    if not args_doc and not args_img and not args_vid:
        print ('\nWARNING: NO download decisions are given')