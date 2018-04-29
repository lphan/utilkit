import sys
import subprocess
import pycurl
import re
import multiprocessing
from multiprocessing import Process, Queue
from threading import Thread, activeCount
from queue import Empty
# from start import set_logger as logger
# import start


MULTI_THREADING_pos = True  # positive as true
MULTI_PROCESSING_pos = True
MULTI_THREADING_neg = False   # negative as false
MULTI_PROCESSING_neg = False


class Test:
    def __init__(self):
        self.contents = ''

    def body_callback(self, buf):
        self.contents = self.contents + buf


class MultiDownloadYT(object):

    def __init__(self, url, lines, mt=False, mp=True):
        self.mt_threading = mt
        self.mt_processing = mp
        self.url = url
        self.lines = lines

    # download by giving input as txt-file from command line
    def dl_from_file(self):
        work_queue = Queue()
        # for line in enumerate(self.lines):
        #     print(line[1])
        work_queue.put(self.lines)

        # logger.info ("Size of queue = ", work_queue.qsize())
        if self.mt_processing:
            self.run_multi_processes(work_queue)
        elif self.mt_threading:
            self.run_multi_threads(work_queue)
        else:
            # logger.info ("Invalid option ...")
            sys.exit()

    # download by giving input web-url from command line
    # test with file yt.txt created by curl below
    #
    # curl https://www.youtube.com/channel/UCvRRdt2Mz7k001w3wvuxShg/videos >>
    # yt.txt
    #
    def dl_from_url(self):
        t = Test()

        c = pycurl.Curl()
        c.setopt(c.URL, self.url)
        c.setopt(c.WRITEFUNCTION, t.body_callback)
        c.perform()
        c.close()

        obj = t.contents
        # convert byte-like obj into string-obj
        urls = self.__parse_url(str(obj))

        # add url into work_queue
        work_queue = Queue()
        for url in enumerate(urls):
            work_queue.put(url[1])

        if self.mt_processing:
            self.run_multi_processes(work_queue)
        elif self.mt_threading:
            self.run_multi_threads(work_queue)
        else:
            # logger.info ("Invalid option ...")
            sys.exit()

    # TODO: parse webpage downloaded by curl to get list of urls
    @staticmethod
    def __parse_url(content):
        """ Parse content to get a list of URLs """
        # url_pattern1 = "(<a\s[a-zA-Z0-9=:_.-/ \'\"]+>.+<\/a>)"
        # logger.info (content)
        url_pattern1 = ".*(<a\s.+>.+<\/a>).*"
        url_obj = re.compile(url_pattern1)
        # find all substring where RE matches and return them as a list
        url_list = url_obj.findall(content)

        # # logger.info (url_list)
        # # logger.info ("url_list length: ", len(url_list))

        url_pattern2 = "<a\s.*\s(title=\".*\")\s.*\s(href=\"\/watch\?v=.*\").*>(.*)<\/a>"
        url_obj2 = re.compile(url_pattern2)
        urls = []
        temp_urls = []
        for elem in url_list:
            # logger.info (elem)
            if 'title' in elem:
                temp_urls.append(elem)

        # # logger.info ("temp urls length: ", len(temp_urls))

        for elem in temp_urls:
            # # logger.info (elem)
            url_link = url_obj2.findall(elem)

            if len(url_link) > 0:
                # logger.info ("url_link =", url_link)
                link = url_link[0][1].split("href=")[1]
                # # logger.info (str(link))
                # dllink = "http://www.youtube.com"+str(link)
                # # logger.info (dllink)
                # urls.append(dllink)
                # # logger.info url_link[0][1]
                urls.append("http://www.youtube.com"+str(link))
            else:
                # # logger.info ("No suitable link has been found")
                pass

        # # logger.info "List of Download vid-link\n", urls
        # logger.info
        # # logger.info (len(urls))
        return urls

    def __valid_link(self, url):
        """ check whether url is a valid link to download
        After combining with root-url: 'http://www.youtube.com' and
        fixed pattern: '/watch?='
        it must have in format:
            http://www.youtube.com/watch?v=EKeb48qYS3A
        """
        pass

    @staticmethod
    def run_multi_processes(work_queue):
        cpu_cores = multiprocessing.cpu_count()
        # cpu_cores = 2, will run with 2 processes

        processes = [Process(target=MultiDownloadYT._do_work,
                             args=(work_queue,))
                     for _ in range(cpu_cores)]
        for p in processes:
            p.start()
        for p in processes:
            p.join()

    @staticmethod
    def run_multi_threads(work_queue):
        # no need self-param, can be chosen as staticmethod
        threads = activeCount()

        threads = [Thread(target=MultiDownloadYT._do_work, args=(work_queue,))
                   for i in range(threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    @staticmethod
    def _do_work(q):
        # customize file youtube-dl.conf to configure further options
        # command = "youtube-dl -f bestvideo+bestaudio --config-location youtube-dl.conf --verbose "
        # options = " --playlist-start 1 --playlist-end 5 "

        command = "youtube-dl -f bestvideo+bestaudio --config-location youtube-dl.conf --verbose "

        while True:
            try:
                queue_size = q.qsize()
                # start.logger.info("Length of queue: ", queue_size)
                result = q.get(block=False)
                
                # start.logger.info('Result: ', str(result))

                command = command + str(result)
                # logger.info ('Command: ', str(command))

                # obsolete: if os.system(command) == 0:
                if subprocess.call([command], shell=True) == 0:
                    # start.logger.info("Successful download file ", str(result))
                    pass
                else:
                    # start.logger.info("Download FAILED ", result)
                    pass
            except Empty:
                break

    # TODO:
    # Get Meta-information from youtube-url
    # Only compatible with python3
    # from youtube_dl import YoutubeDL
    # ydl = YoutubeDL()
    # ydl.add_default_info_extractors()
    # info = ydl.extract_info(url, download=False)
    # type(info)	# dict

