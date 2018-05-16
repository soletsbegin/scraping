import csv
import re
import threading
from time import sleep

import requests


BASE_URL = 'http://spotguide.kicks-ass.net'
headers = {
    'user-agent':
               'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
}
VECTORS = {
    'Nordväst': 'NW',
    'Nord': 'N',
    'Nordost': 'NE',
    'Ost': 'E',
    'Sydost': 'SE',
    'Syd': 'S',
    'Sydväst': 'SW',
    'Väst': 'W',
}
VECTORS_COND = {
    '0': 'Bad',
    '1': 'Ok',
    '2': 'Good'
}


class Surf:
    def __init__(self, url, *args):
        self._start_url = url
        self.urls_list = []
        self.html_list = []
        self.find_list = args
        self.all_info = dict()

    def make_urls(self):
        html = requests.get(self._start_url, headers=headers).text
        links = re.findall('<a href="/default.+?</a></span><br/>', html)
        for i in links:
            new_link = re.findall(r'/def.+?"', i)
            if new_link[0][:-1].endswith('=0'):
                continue
            else:
                name = re.findall(r'Ingen.+?</a>', i)[0][81:-4].lower()
                self.urls_list.append((new_link[0][:-1], name))

    @classmethod
    def get_coordinates(cls, html):
        return re.findall(r'Lat" .+?/>', html)[0][12:-4], re.findall(r'Lng" .+?/>', html)[0][12:-4]

    @classmethod
    def get_wind(cls, html):
        wind = dict()
        slise = re.findall(r'/d/pil.+?" />', html)
        for s in slise:
            condition = re.findall(r'pil.+?\d', s)[0][-1]
            vector = re.findall(r'alt="\w+', s)[0][5:]
            wind[VECTORS[vector]] = VECTORS_COND[condition]
        return wind

    @classmethod
    def get_parent(cls, html):
        parents = []
        slise = re.findall(r'<a href=.+?&ps=">.+?</a>', html)
        for s in slise[1:]:
            parents.append(re.findall(r'">.+?</', s)[0][2:-2])
        return '/'.join(parents[1:])

    @classmethod
    def get_windguru(cls, html):
        link = re.findall(r'src="http://www.windguru.cz/.+?"', html)
        if len(link) > 0:
            return re.findall(r'src="http://www.windguru.cz/.+?"', html)[0][5:-1]

    @classmethod
    def get_about(cls, html):
        info = re.findall(r'span class="a10b.+?table', html)
        info = re.findall(r'<br/>.+?<table', info[0])
        try:
            info = re.split(r'<.+?>', info[0][:-6])
            return "\n".join(i.strip() for i in info if len(i) > 0)
        except IndexError:
            return ""

    @classmethod
    def get_rating(cls, html):
        price = [i.group(1) for i in re.finditer(r'<em>\((.+?)\)</em>', html)]

        return {
            'Kitelaunch\n vänligt': price[0],
            'Långgrunt':  price[1],
            'Surf':  price[2],
            'Plattvatten':  price[3],
        }

    def parse_url(self, url):
        self.html_list.append(('{}'.format(re.findall(r'ID=\d+', url[0])[0][3:]),
                               url[1].capitalize(),
                               requests.get(self._start_url + url[0], headers=headers).text))

    def parse_all(self):
        step = 100 / len(self.urls_list)
        count = 0
        for url in self.urls_list:
            t = threading.Thread(target=self.parse_url, args=(url, ))
            t.start()
            sleep(0.01)
            # progress bar
            count += step
            print('\n'*100)
            print('Please wait')
            print("[{}]{}%".format('|' * round(count), round(count)))

    def get_info_alt(self):
        self.parse_all()
        for count in range(101):
            sleep(0.1)
            print('\n' * 100)
            print('Please wait')
            print("[{}]{}%".format('|' * round(count), round(count)))

        for html in self.html_list:
            point_id = html[0]
            self.all_info[point_id] = dict()

            # print(point_id, html[1])
            self.all_info[point_id]['NAME'] = html[1]
            self.all_info[point_id]['ID'] = point_id
            self.all_info[point_id]['PARENT DIRECTORY'] = self.get_parent(html[2])
            self.all_info[point_id]['COORDINATES'] = self.get_coordinates(html[2])
            self.all_info[point_id]['WINDGURU'] = self.get_windguru(html[2])
            self.all_info[point_id]['ABOUT'] = self.get_about(html[2])
            self.all_info[point_id].update(self.get_wind(html[2]))
            self.all_info[point_id].update(self.get_rating(html[2]))

    def get_info(self):
        step = 100 / len(self.urls_list[:5])
        count = 0

        for link in self.urls_list[:5]:
            point_id = 'SpotID-{}'.format(re.findall(r'ID=\d+', link[0])[0][3:])
            self.all_info[point_id] = dict()

            html = requests.get(self._start_url + link[0], headers=headers).text
            print(point_id, link[1].capitalize())
            self.all_info[point_id]['NAME'] = link[1].capitalize()
            self.all_info[point_id]['PARENT DIRECTORY'] = self.get_parent(html)
            self.all_info[point_id]['COORDINATES'] = self.get_coordinates(html)
            self.all_info[point_id]['WINDGURU'] = self.get_windguru(html)
            self.all_info[point_id]['ABOUT'] = self.get_about(html)
            self.all_info[point_id].update(self.get_wind(html))
            self.all_info[point_id].update(self.get_rating(html))

            # progress bar
            count += step
            print("[{}]{}%".format('|' * round(count), round(count)))
            print()


def save_csv(dictionary):
    print('Saving...')
    keys = [int(k) for k in dictionary.keys()]
    with open('points.csv', 'w', newline='') as csvfile:
        fieldnames = ['ID', 'NAME', 'PARENT DIRECTORY', 'COORDINATES',
                      'N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE',
                      'Kitelaunch\n vänligt', 'Långgrunt', 'Surf', 'Plattvatten',
                      'WINDGURU', 'ABOUT']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for key in sorted(keys):
            writer.writerow(dictionary[str(key)])
    print('Saved')
    print('Check the file:  .../Kitesurf/points.csv')


if __name__ == '__main__':
    surf = Surf(BASE_URL)
    surf.make_urls()
    # for i in surf.urls_list:
    #     print('"{}",'.format(i[0]))
    surf.get_info_alt()
    save_csv(surf.all_info)
