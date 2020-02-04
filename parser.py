# -*- coding: utf-8 -*-
"""
This module provides imdb.com parser for telegram bot.
"""

import requests
from bs4 import BeautifulSoup


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
        req_contents = []
        __session = requests.Session()

        for url in cls.__create_urls():
            req_contents.append(__session.get(url, headers=cls.__headers))

        return req_contents

    def get_info(self, select: bool = False, amount: int = 5):
        """
        Function for parsed data handling from imdb.com.

        Function parse name link, year, rating, genre and cast of movie.
        Args:
            select: Boolean value indicates random movies selection
            amount: Amount of choices for random.

        Returns:
            info: A list of parsed info.
        """

        info = []

        for request in self.__get_requests():

            soup = BeautifulSoup(request.content, 'lxml')

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

                #
                # cast = (actor.find_all('a')[0].text for actor in cast)

                # print(next(cast))

                # for actor in actors:
                #     [print(i.text) for i in actor.find_all('a')]

                info.append(
                    {'name': name,
                     'link': link,
                     'year': year,
                     'rating': rating,
                     'genre': genre,
                     'director': director,
                     'actors': actors}
                )

        if select:
            import random
            info = random.choices(info, k=amount)

            return info

        return info
