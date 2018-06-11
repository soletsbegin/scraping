from bs4 import BeautifulSoup
import requests

BASE_URL = 'https://habr.com/'


class HabrNews:
    def __init__(self, url):
        self.start_link = url
        self.url_all = url+'all/'
        self.url_top = url+'top/'
        self._current_page = url+'top/'
        self.current_post = None
        self.current_titles = None

    @property
    def current_page(self):
        return self._current_page

    @current_page.setter
    def current_page(self, url):
        self._current_page = url

    @classmethod
    def _get_html(cls, url):
        resp = requests.get(url)
        html = resp.text
        return html

    def get_step_links(self):
        html = self._get_html(self._current_page)
        soup = BeautifulSoup(html, 'lxml')
        buttons = soup.find('ul', class_='arrows-pagination')
        previous_but = buttons.find('a', class_="arrows-pagination__item-link arrows-pagination__item-link_prev")
        next_but = buttons.find('a', class_="arrows-pagination__item-link arrows-pagination__item-link_next")
        try:
            prev_link = self.start_link + previous_but.get('href').lstrip('/')
        except AttributeError:
            prev_link = None
        try:
            next_link = self.start_link + next_but.get('href').lstrip('/')
        except AttributeError:
            next_link = None
        print(prev_link, next_link)
        return prev_link, next_link

    def get_posts(self, url):
        html = self._get_html(url)
        posts_list = []
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('ul', class_='content-list content-list_posts shortcuts_items')
        posts = table.find_all('li', class_='content-list__item content-list__item_post shortcuts_item')
        for post in posts:
            time = post.find('span', class_='post__time')
            title = post.find('a', class_='post__title_link')
            # prev = post.find('div', class_='post__text post__text-html js-mediator-article')
            if time is not None:
                posts_list.append(
                    {'time': time.text,
                     'title': title.text,
                     # 'preview': prev.text.strip(),
                     'link': title.get('href'),
                     # 'post_id': post.get('id')[5:]
                     })
        self.current_titles = posts_list

    def get_post(self, url):
        html = self._get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('div', class_='post__text post__text-html js-mediator-article')
        return table.text


if __name__ == '__main__':
    habr = HabrNews(BASE_URL)
    print(habr.current_page)
    habr.get_posts(habr.current_page)
    for p in habr.current_titles:
        print(p['title'])
    print(habr.current_titles[1]['link'])
    print(habr.get_post(habr.current_titles[2]['link']))
    habr.get_posts(habr.current_page)
    # for p in habr.current_titles:
    #     print(p['title'])
    # print(habr.current_titles[1]['link'])
