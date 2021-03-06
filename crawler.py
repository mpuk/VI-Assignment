from urllib2 import urlopen
from urlparse import urljoin
from time import sleep
from bs4 import BeautifulSoup
from re import compile
from sys import argv
from parser import Parser
from elasticsearch import Elasticsearch


class Crawler(object):
    def __init__(self, start_url):
        self.visited_urls = set()
        self.unvisited_urls = []
        self.base_url = 'http://www.imdb.com/'
        self.base_url_regexp = compile(self.base_url + '*')
        self.movie_url_regexp = compile(self.base_url + 'title/tt[0-9]*')
        self.movie_urls = set()

        self.unvisited_urls.append(start_url)

    def crawl(self, limit):
        for url in self.unvisited_urls:
            print "Crawling {}...".format(url)
            self.visited_urls.add(url)
            try:
                response = urlopen(url)
            except:
                continue

            soup = BeautifulSoup(response.read(), 'lxml')
            links_soup = soup('a')

            for link in links_soup:
                if 'href' in link.attrs:
                    url_joined = urljoin(self.base_url, link['href'])
                    if self.base_url_regexp.match(url_joined) is not None:
                        if (url_joined not in self.visited_urls and
                                url_joined not in self.unvisited_urls):

                            self.unvisited_urls.append(url_joined)

                            if self.movie_url_regexp.match(url_joined) is not None:
                                movie_url = self.movie_url_regexp.search(url_joined)

                                if movie_url is not None:
                                    self.movie_urls.add(movie_url.group(0))

                                if len(self.movie_urls) == limit:
                                    return

            print "{} movies found...".format(len(self.movie_urls))
            print "Sleeping..."
            sleep(1)


if __name__ == '__main__':
    print "Started crawling..."
    c = Crawler('http://www.imdb.com/genre/')
    c.crawl(int(argv[1]))
    es = Elasticsearch()

    print "Started parsing..."
    p = Parser(c.movie_urls, es)
    p.parse()