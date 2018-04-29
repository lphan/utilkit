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
Description: Start main_function to download media data (Vid, Img, Doc) 
'''
import configparser
from download import DownloadMedia, DownloadImg, DownloadDoc, DownloadVid
import logging.handlers


def set_logger():
    log_filename = './log/downloadStart.log'
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s-%(name)s-%(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=log_filename, filemode='w')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(' %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    log = logging.getLogger('Download_Start')
    log.addHandler(console)
    return log


if __name__ == '__main__':
    logger = set_logger()

    # Load the configuration file

    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
    except IOError:
        set_logger().info("IO Error, check config.ini file")
        import sys
        sys.exit()

    args_vid = config.getboolean('media', 'vid_dl')
    args_img = config.getboolean('media', 'img_dl')
    args_doc = config.getboolean('media', 'doc_dl')
    log_loc = config['others']['log_loc']

    vid, img, doc = [], [], []

    if args_vid:
        logger.info('Logger: Starting download video(s)')

        vid_url = config['vid_dl']['vid_url']
        vid_txt = config['vid_dl']['vid_txt_file']
        vid_wp = config['vid_dl']['vid_html_link']
        vid_loc = config['others']['save_vid_loc']
        vid = [vid_url, vid_txt, vid_wp, vid_loc]
    else:
        vid = ['', '', '', '']

    if args_img:
        logger.info('Logger: Starting download image(s)')

        img_url = config['img_dl']['img_url']
        img_txt = config['img_dl']['img_txt_file']
        img_wp = config['img_dl']['img_html_link']
        img_loc = config['others']['save_img_loc']
        img = [img_url, img_txt, img_wp, img_loc]
    else:
        img = ['', '', '', '']

    if args_doc:
        logger.info('Logger: Starting download document(s)')

        doc_url = config['doc_dl']['doc_url']
        doc_txt = config['doc_dl']['doc_txt_file']
        doc_wp = config['doc_dl']['doc_html_link']
        doc_loc = config['others']['save_doc_loc']
        doc = [doc_url, doc_txt, doc_wp, doc_loc]
    else:
        doc = ['', '', '', '']

    kwargs = {"args_vid": args_vid, "args_img": args_img, "args_doc": args_doc,
              "vid_url": vid[0], "vid_txt_file": vid[1], "vid_html_link": vid[2], "vid_loc": vid[3],
              "img_url": img[0], "img_txt_file": img[1], "img_html_link": img[2], "img_loc": img[3],
              "doc_url": doc[0], "doc_txt_file": doc[1], "doc_html_link": doc[2], "doc_loc": doc[3],
              }

    logger.info(kwargs["vid_txt_file"])

    dm = DownloadMedia(**kwargs)
    dm.download_task()

    if not args_doc and not args_img and not args_vid:
        logger.info('\nWARNING: NO download decisions are given')
