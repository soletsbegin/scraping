from lxml import html
import requests


URL = 'http://spotguide.kicks-ass.net/'
# URL = 'http://spotguide.kicks-ass.net//default.asp?Area=63&Page=2&WindDir=0&Platt=0&Surf=0&Grunt=0&KiteLaunch=0&SpotID=318'


html_text = requests.get(URL).text
etree = html.fromstring(html_text)

text = etree.xpath('//span[@class="a10"]//@href')

# name = etree.xpath('//h1/text()')
# print(name)

for i in text:
    url = URL+i
    html_text = requests.get(url).text
    etree = html.fromstring(html_text)
    name = etree.xpath('//h1/text()')[0]
    parent = etree.xpath('//td[@style]/table//a[@href]/text()')[1:-5]
    print(name, parent)
    print()
