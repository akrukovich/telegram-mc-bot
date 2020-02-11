# -*- coding: utf-8 -*-
"""
This module provides imdb.com parser for telegram bot.
"""

import requests
from bs4 import BeautifulSoup
import concurrent.futures


class ImdbParser:
    """
    Objects of this class consists imdb.com top 250.
    """

    __headers = {'accept': '*/*',
                 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                               'snap Chromium/79.0.3945.130 Chrome/79.0.3945.130 Safari/537.36'
                 }

    @classmethod
    def __create_urls(cls):
        """
        Return urls list.

        This function fill up the list for urls of top 250 movies.
        Returns:
            urls: list of urls.

        """
        urls = []
        for i in range(1, 202, 50):
            urls.append(f'https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start={i}'
                        f'&ref_=adv_nxt')

        return urls

    @classmethod
    def __get_requests(cls):
        """
        Function provide content fo each url from create_urls.

        This function return a list of parsed content for  further retrieving .
        Returns:
            req_contents: a list of requested content

        """

        __session = requests.Session()

        with concurrent.futures.ThreadPoolExecutor() as executor:

            urls = cls.__create_urls()
            headers = cls.__headers
            req_contents = executor.map(lambda a: __session.get(a, headers=headers), urls)

        return req_contents

    @staticmethod
    def read_content(rt):

        soup = BeautifulSoup(rt.content, 'lxml')
        data = soup.find_all('div', class_='lister-item mode-advanced')
        for i in data:
            name = i.h3.a.text
            link = ''.join(('https://www.imdb.com', i.h3.a['href']))
            year = i.find('span', class_='lister-item-year text-muted unbold').text[1:-1]
            rating = i.find('div', class_='inline-block ratings-imdb-rating').text.strip()
            genre = i.find('span', class_='genre').text.strip()
            cast = i.find_all('p', class_='')
            stars = list()
            for actor in cast[0].find_all('a'):
                stars.append(actor.text)
            director, *actors = stars

            d = {'name': name,
                 'link': link,
                 'year': year,
                 'rating': rating,
                 'genre': genre,
                 'director': director,
                 'actors': actors}

            return d

    def get_info(self, select: bool = False, amount: int = 5):

        with concurrent.futures.ProcessPoolExecutor() as executor:
            rts = self.__get_requests()

            results = (executor.submit(read_content, r) for r in rts)

            movies = (movie.result() for movie in concurrent.futures.as_completed(results))
            movies = list(movies)

        if select:

            import random

            movies = random.sample(movies, k=amount)
            return movies

        return movies

    def get_movies_string(self, select=True):

        __reply_str = ''

        for film in self.get_info(select=select):
            tmp_string = f'''Title: {film['name']}\nGenre: {film['genre']}\nRating: {film['rating']}\nYear: {film['year']}
Director: {film['director']}\nActors: {', '.join(film['actors'])}\n{film['link']}\n\n'''

            __reply_str = ''.join([__reply_str, tmp_string])

        return __reply_str
