from selenium import webdriver
from time import sleep
from random import randint
# import csv
# import json

wb = webdriver.Chrome()

START = '''
https://www.google.com/maps/d/viewer?mid=1hALmh8aBkB0z3-641iY41pqK47AWiH9A&ll=44.76479700000003%2C-91.46643499999999&z=8'''

SELECTORS = {
    'open_list':
        '#legendPanel > div > div > div.i4ewOd-PBWx0c-bN97Pc-haAclf > div > div > div.i4ewOd-pbTTYe-haAclf > div > div > div.HzV7m-pbTTYe-bN97Pc.HzV7m-pbTTYe-bN97Pc-qAWA2 > div.HzV7m-pbTTYe-KoToPc-ornU0b-haAclf > div > div',
    'all_parks_xpath':
        '//div[@class="HzV7m-pbTTYe-JNdkSc-PntVL"]/div',
    'back_button_xpath':
        '//span[@style="top: -12px"]/span',
    'back_button_css':
        '#featurecardPanel > div > div > div.qqvbed-tJHJj > div.HzV7m-tJHJj-LgbsSe-haAclf.qqvbed-a4fUwd-LgbsSe-haAclf > div > content > span',
    'park_info_xpath':
        '//div[@class="qqvbed-p83tee"]'
}

data = []


def sleep_rand(a=1, b=1):
    sleep(randint(a, b))


wb.get(START)
open_list = wb.find_element_by_css_selector(SELECTORS['open_list'])
open_list.click()
sleep(1)
parks = wb.find_elements_by_xpath(SELECTORS['all_parks_xpath'])
# print(len(parks))
for i in range(len(parks)):
    parks[i].click()
    title = parks[i].text
    temp = dict()
    print(title)
    info = wb.find_elements_by_xpath(SELECTORS['park_info_xpath'])
    sleep_rand(b=3)
    for line in info:
        text = line.text.split('\n')
        temp[text[0]] = text[1]
    data.append(temp)
    print('='*100)
    sleep_rand()
    back = wb.find_element_by_css_selector(SELECTORS['back_button_css'])
    back.click()
    sleep_rand(b=3)

# with open('parks.json', 'w') as jf:
#     json.dump(data, jf, indent=3)
#
# with open('parks.csv', 'w') as file:
#     headers = ['Park Name', 'Address', 'City', 'State', 'Postal Code', 'Country', 'Phone', 'Website', 'unnamed (1)']
#     writer = csv.DictWriter(file, fieldnames=headers)
#     writer.writeheader()
#     for i in data:
#         writer.writerow(i)
