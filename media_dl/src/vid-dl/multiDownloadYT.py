import sys
import subprocess
import pycurl
import re
import multiprocessing
from multiprocessing import Process, Queue
from threading import Thread, activeCount

PY3 = sys.version_info[0] > 2

if PY3:
    # detect Python version 3
    from queue import Empty
else:
    # detect Python version 2
    from Queue import Empty

MULTI_THREADING_pos = True  # positive as true
MULTI_PROCESSING_pos = True
MULTI_THREADING_neg = False   # negative as false
MULTI_PROCESSING_neg = False


class Test:
    def __init__(self):
        self.contents = ''
        if PY3:
            self.contents = self.contents.encode('ascii')

    def body_callback(self, buf):
        self.contents = self.contents + buf


class MultiDownloadYT(object):

    def __init__(self, url, lines, folder='', mt=False, mp=True):
        self.multithreading = mt
        self.multiprocessing = mp
        self.url = url
        self.lines = lines
        self.folder = folder

    # download by giving input as txt-file from command line
    def dl_from_file(self):
        work_queue = Queue()
        for line in enumerate(self.lines):
            work_queue.put(line[1])
        # print ("Size of queue = ", work_queue.qsize())
        if self.multiprocessing:
            self.taskProcesses(work_queue)
        elif self.multithreading:
            self.taskThreads(work_queue)
        else:
            # print ("Invalid option ...")
            sys.exit()

    # download by giving input web-url from command line
    # test with file yt.txt created by curl below
    #
    # curl https://www.youtube.com/channel/UCvRRdt2Mz7k001w3wvuxShg/videos >>
    # yt.txt
    #
    def dl_from_url(self):
        t = Test()

        # TODO: understand pycurl and its setoption-function
        c = pycurl.Curl()
        c.setopt(c.URL, self.url)
        c.setopt(c.WRITEFUNCTION, t.body_callback)
        c.perform()
        c.close()

        obj = t.contents
        # convert byte-like obj into string-obj
        urls = self.__parseURL(str(obj))

        # print ("URL List")
        # print (urls)

        # add url into work_queue
        work_queue = Queue()
        for url in enumerate(urls):
            work_queue.put(url[1])

        # print ("Size of queue = ", work_queue.qsize())
        if self.multiprocessing:
            self.taskProcesses(work_queue)
        elif self.multithreading:
            self.taskThreads(work_queue)
        else:
            # print ("Invalid option ...")
            sys.exit()

    # TODO: parse webpage downloaded by curl to get list of urls
    # @staticmethod
    def __parseURL(self, content):
        ''' Parse content to get a list of URLs '''
        # vidpattern = "(<a\s[a-zA-Z0-9=:_.-/ \'\"]+>.+<\/a>)"
        # # print (content)
        vidpattern = ".*(<a\s.+>.+<\/a>).*"
        vidobj = re.compile(vidpattern)
        # find all substring where RE matches and return them as a list
        vidlist = vidobj.findall(content)

        # # print (vidlist)
        # # print ("vidlist length: ", len(vidlist))

        vidpattern2 = "<a\s.*\s(title=\".*\")\s.*\s(href=\"\/watch\?v=.*\").*>(.*)<\/a>"
        vidobj2 = re.compile(vidpattern2)
        urls = []
        tempurls = []
        for elem in vidlist:
            # print (elem)
            if 'title' in elem:
                tempurls.append(elem)

        # # print ("temp urls length: ", len(tempurls))

        for elem in tempurls:
            # # print (elem)
            vidlink = vidobj2.findall(elem)

            if len(vidlink) > 0:
                # print ("vidlink =", vidlink)
                link = vidlink[0][1].split("href=")[1]
                # # print (str(link))
                # dllink = "http://www.youtube.com"+str(link)
                # # print (dllink)
                # urls.append(dllink)
                # # print vidlink[0][1]
                urls.append("http://www.youtube.com"+str(link))
            else:
                # # print ("No suitable link has been found")
                pass

        # # print "List of Download vid-link\n", urls
        # print
        # # print (len(urls))
        return urls

    def __validlink(url):
        ''' check whether url is a valid link to download
        After combining with root-url: 'http://www.youtube.com' and
        fixed pattern: '/watch?='
        it must have in format:
            http://www.youtube.com/watch?v=EKeb48qYS3A
        '''
        pass

    def taskProcesses(self, work_queue):
        cpu_cores = multiprocessing.cpu_count()
        # cpu_cores = 2, will run with 2 processes

        processes = [Process(target=MultiDownloadYT._do_work,
                             args=(work_queue,))
                     for i in range(cpu_cores)]
        for p in processes:
            p.start()
        for p in processes:
            p.join()

    def taskThreads(self, work_queue):
        threads = activeCount()

        threads = [Thread(target=MultiDownloadYT._do_work, args=(work_queue,))
                   for i in range(threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    # @staticmethod
    # def __getfoldername(self):
    #     return self.folder

    @staticmethod
    def _do_work(q):
        # options = "--playlist-items 3,4,5 "
        options = "--playlist-start 1 --playlist-end 2 "
        # folder = MultiDownloadYT.__getfoldername()
        # TODO: currently set forder does not work.
        folder = ""
        if len(folder) > 0:
            prog = "youtube-dl -o " + folder + " -f bestvideo+bestaudio "
        else:
            prog = "youtube-dl -f bestvideo+bestaudio --verbose "
        while True:
            try:
                queue_size = q.qsize()
                print ("Length of queue: ", queue_size)
                result = q.get(block=False)
                if (sys.version_info > (3, 0)):
                    # convert byte to string in Python3
                    result = result.decode('UTF-8')
                    # print ('Result: ', str(result))

                if len(options) > 0:
                    command = prog + options + str(result)
                else:
                    command = prog + str(result)
                # print ('Command: ', str(command))

                # obsolete: if os.system(command) == 0:
                if subprocess.call([command], shell=True) == 0:
                    print ("Successful download file ", str(result))
                else:
                    print ("Download FAILED ", result)
            except Empty:
                break

    '''
    # TODO:
    # Get Meta-information from youtube-url
    # Only compatible with python3
    from youtube_dl import YoutubeDL
    ydl = YoutubeDL()
    ydl.add_default_info_extractors()
    info = ydl.extract_info(url, download=False)
    type(info)	# dict
    '''

if __name__ == '__main__':
    # Run test with download from file
    # INPUT: path to file
    path_file = './txt/youtube.txt'
    # INPUT: youtube-url
    src = "https://www.youtube.com/user/ncarucar/videos"
    # TODO:
    # change config-file and create folder accordingly to the link
    # to save files downloaded.
    # foldername = "/media/sf_Desktop/Filme/Video"

    try:
        openfile = open(path_file, 'rb')
        lines = openfile.readlines()
        dl = MultiDownloadYT(src, lines, mt=MULTI_THREADING_neg,
                             mp=MULTI_PROCESSING_pos)

        dl.dl_from_file()
        # dl.dl_from_url()

    except IOError:
        # print ("Error IO")
        sys.exit
