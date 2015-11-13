from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import requests
import collections
import os
import threading
import time
import gui_build
import people_info
import url2img


class CrawlIMDB:
    def __init__(self):
        self.host_name_ = 'http://www.imdb.com'  # the base address of the website
        self.seed_url_ = []
        self.seed_url_.append('http://www.imdb.com/name/nm0914612/')  # Emma Watson
        self.seed_url_.append('http://www.imdb.com/name/nm0000129/')  # Tom Cruise
        self.seed_url_.append('http://www.imdb.com/name/nm0000138/')  # Leonardo DiCaprio

        self.image_count_ = 0
        self.actor_queue_ = collections.deque()  # store the temporaty list
        self.actor_visited_set_ = set()  # store the history
        self.movie_visited_set_ = set()  # store the history
        self.LoadPreIteration()  # load the previous history

        # self.max_actor_queue_length_ = 10000

        self.actor_queue_lock_ = threading.Lock()
        self.actor_visited_set_lock_ = threading.Lock()
        self.movie_visited_set_lock_ = threading.Lock()
        self.cast_list_strainer_ = SoupStrainer('table', {'class': 'cast_list'})  # for beautiful soup purpose
        self.file_lock_ = threading.Lock()
        self.close_thread_call_ = False
        self.json_file_ = open('../data/people.json', 'a')
        self.time_lock_ = threading.Lock()
        self.save_temp_file_lock_ = threading.Lock()

        self.sleep_commend_ = False
        self.sleep_event = threading.Event()
        self.sleep_event.set()

    def LoadPreIteration(self):
        if os.path.isfile('./__crawlercache/actor_visited_list.txt'):
            with open('./__crawlercache/actor_visited_list.txt', 'r') as avl_f:
                self.actor_visited_set_ = set(avl_f.read().split('\n'))

        if os.path.isfile('./__crawlercache/movie_visited_list.txt'):
            with open('./__crawlercache/movie_visited_list.txt', 'r') as mvl_f:
                self.movie_visited_set_ = set(mvl_f.read().split('\n'))

        if os.path.isfile('./__crawlercache/actor_visited_list.txt'):
            with open('./__crawlercache/actor_queue.txt', 'r') as avq_f:
                self.actor_queue_ = collections.deque(avq_f.read().split('\n'))

    def RunThread(self, num_of_threading=-1):
        if num_of_threading > len(self.seed_url_) or num_of_threading == -1:
            num_of_threading = len(self.seed_url_)
        self.start_time = time.time()
        for i in range(num_of_threading):
            threading.Thread(target=self.CrawActor, args=(self.seed_url_[i],)).start()

        gui_build.GUI_Window(self.ExitFunction, self.PauseFunction)  # manully exit
        self.ExitFunction()

    def CrawActor(self, actor_url):
        '''
        :param img_url: the url contain the image of the actor or the actress
        :return:
        '''
        with self.actor_visited_set_lock_, self.actor_queue_lock_:
            if actor_url not in self.actor_visited_set_:
                self.actor_visited_set_.add(actor_url)

        self.actor_queue_.appendleft(
            actor_url)  # because it is the seed, so it will be push here anyway in order to check if the seed is crawl over or not

        while len(self.actor_queue_) > 0:
            if self.close_thread_call_:
                return

            self.sleep_event.wait()

            with self.time_lock_:
                curr_epsilon = time.time() - self.start_time
                if curr_epsilon > 60 * 60 * 2:
                    self.SaveTempData()
                    self.start_time = time.time()

            with self.actor_queue_lock_:
                curr_actor_url = self.actor_queue_.popleft()

            try:
                source_code = requests.get(curr_actor_url)
                plain_text = source_code.text
                soup = BeautifulSoup(plain_text, "html.parser")

                link = soup.find('img', {'id': 'name-poster'})
                if link:
                    # make sure the link is valid, which means this celebrity has a picture
                    img_url = link.get('src')
                    actor_name = link.get('alt').replace(' Picture', '')
                    born_info = soup.find('div', {'id': 'name-born-info'})
                    curr_actor_info = people_info.PeopleInfo()

                    curr_actor_info.SetName(actor_name)
                    curr_actor_info.SetLink(curr_actor_url)
                    birth_day = ""
                    birth_year = ""
                    location = ""

                    if born_info is not None:
                        born_info_list = born_info.findAll('a')
                        for link in born_info_list:
                            curr_href = link.get("href")
                            if curr_href.find("birth_monthday") != -1:
                                birth_day = link.text
                            elif curr_href.find("birth_year") != -1:
                                birth_year = link.text
                            elif curr_href.find("birth_place") != -1:
                                location = link.text

                    curr_actor_info.SetBirthYear(birth_year)
                    curr_actor_info.SetBirthDay(birth_day)
                    curr_actor_info.SetLocation(location)

                    with self.file_lock_:
                        curr_actor_info.JsonDump(self.json_file_)

                    url2img.url2img('../data/IMDB', actor_name, img_url)

                # if len(self.actor_queue_) < self.max_actor_queue_length_:
                # if the current queue is larger than the defined maximum length,
                # the program would not adding new link ustil it reduce to the maximum length
                node = soup.find_all('div', {'class': 'filmo-category-section'})
                for item in node:
                    films_class = item.find_all('b')
                    for single_movie in films_class:
                        if self.close_thread_call_:
                            return
                        self.sleep_event.wait()

                        # in case the name of the movie is unprintable
                        try:
                            print(single_movie.text)
                        finally:
                            pass

                        movie_url = self.host_name_ + (single_movie.contents[0].get('href'))
                        movie_url = self.RemoveQuestionMark(movie_url)
                        self.CrawMovie(movie_url)
            except:
                print("some error encountered")

    def CrawMovie(self, movie_url):
        '''
        :param movie_url: the url contains the list of actors or actresses
        :return:
        '''
        with self.movie_visited_set_lock_:
            if movie_url in self.movie_visited_set_:
                return
            else:
                self.movie_visited_set_.add(movie_url)

        self.sleep_event.wait()

        source_code = requests.get(movie_url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, "html.parser", parse_only=self.cast_list_strainer_)
        # cast_list = soup.find_all('table',{'class':'cast_list'})
        cast_list_urls = soup.find_all('a', {'itemprop': 'url'})
        for item in cast_list_urls:
            if self.close_thread_call_:
                return
            self.sleep_event.wait()

            # if the seeds are changed, the lines below should be commended out
            actor_name = item.text

            if actor_name[0] == ' ':
                actor_name = actor_name[1:]

            if actor_name[-1] == '\n':
                actor_name = actor_name[:-1]

            actor_url = self.host_name_ + item.get('href')
            actor_url = self.RemoveQuestionMark(actor_url)

            self.actor_visited_set_lock_.acquire()
            self.actor_queue_lock_.acquire()
            try:
                if actor_url not in self.actor_visited_set_:
                    self.actor_queue_.append(actor_url)
                    self.actor_visited_set_.add(actor_url)
            finally:
                self.actor_visited_set_lock_.release()
                self.actor_queue_lock_.release()

    def SaveTempData(self):
        with self.save_temp_file_lock_:
            f_actor = open('./__crawlercache/actor_visited_list.txt', 'w')
            f_movie = open('./__crawlercache/movie_visited_list.txt', 'w')
            f_actor_q = open('./__crawlercache/actor_queue.txt', 'w')
            f_actor.write('\n'.join(self.actor_visited_set_))
            f_movie.write('\n'.join(self.movie_visited_set_))
            f_actor_q.write('\n'.join(self.actor_queue_))
            f_actor.close()
            f_movie.close()
            f_actor_q.close()

    def RemoveQuestionMark(self, url):
        return url[:url.find('?')]

    def ExitFunction(self):
        self.close_thread_call_ = True
        self.sleep_event.set()
        while threading.active_count() > 1:
            time.sleep(0.1)
        self.json_file_.close()
        self.SaveTempData()
        exit()

    def PauseFunction(self):
        if self.sleep_event.is_set() is True:
            self.sleep_event.clear()
            print("sleep")
        elif self.sleep_event.is_set() is False:
            self.sleep_event.set()
            print("wake")
        self.SaveTempData()


if __name__ == '__main__':
    spider = CrawlIMDB()
    spider.RunThread()
