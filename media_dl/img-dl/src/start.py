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
Description: Download images from plaintext-file in format jpeg
'''

import argparse
# from downloadImg import DownloadImg
from downloadImg import DownloadImg
from multiDownloadImg import MultiDownload
from util import MetaLog, Singleton


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download Images & Save at \
                                     local disc')
    parser.add_argument("-l", "--links", help="input path of text file contains\
                        links")
    parser.add_argument("-u", "--url", help="input url to download")
    parser.add_argument("-w", "--webpage", help="input webpage to download")
    parser.add_argument("-s", "--save", required=True,
                        default='./',
                        help="input location where will save images at local \
                        disc")
    # TODO: set options to activate variable metalog_active
    args = parser.parse_args()

    if (args.links and args.save):
        mf = Singleton(MetaLog, func_name='logging-links')
        logger = mf.getLogger()
        logger.info('Logger: Starting download images')

        kwargs = {"path_file": args.links, "save_location": args.save,
                  "imageurl": None}
        dl = DownloadImg(**kwargs)
        dl.download_task()

    elif (args.url and args.save):
        mf = Singleton(MetaLog, func_name='logging-url')
        logger = mf.getLogger()
        logger.info('Logger: Starting download image')

        kwargs = {"path_file": None, "save_location": args.save,
                  "imageurl": args.url}
        dl = DownloadImg(**kwargs)
        dl.download_task()

    elif (args.webpage and args.save):
        # TODO: input-argument to set METALOG_active value TRUE| FALSE
        mf = Singleton(MetaLog, func_name='logging-webpage',
                       metalog_active=True)
        logger = mf.getLogger()
        logger.info('Logger: Starting download images')

        kwargs = {"url": args.webpage, "save_location": args.save}
        dl = MultiDownload(metalog_active=True, **kwargs)
        dl.download_task()

    # elif (args.links and args.save):
    #     # TODO: check format whether file is csv
    #     print "PRINT: analyse CSV_DATA"
    #     mf = Singleton(MetaLog, func_name='analyse', metalog_active=False)
    #     mf.readDataCSV(args.links, ops='read_data')

    else:
        print 'PRINT: WARNING: Error Input Parameters'
