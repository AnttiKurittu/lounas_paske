#!/usr/bin/python
# -*- Coding: UTF-8 -*-
import requests
import re
import datetime
import json
from bs4 import BeautifulSoup

def strip_html_tags(data):
  out = re.compile(r'<.*?>')
  out = out.sub('', data)
  out = out.replace('&amp;' , '&')
  return out

def parse_menu_from_html(page_content, weekday):
  soup = BeautifulSoup(page_content, 'html.parser') 
  restaurant = strip_html_tags(str(soup.title))
  print '\n' + '\033[95m' + restaurant.replace(" | Lounasravintola", "") + '\033[0m' + '\n'
  divs = soup.find_all('div')
  for item in divs:
    try:
      if 'menu-day' in item['class']:
        menu = str(item)
        if weekday in menu:
          for line in menu.splitlines():
            if 'menu-name' in line:
              print ' - ', strip_html_tags(line)
    except KeyError:
      continue

today_date = str(datetime.datetime.now().isoformat())[0:10]
weekday_number = datetime.datetime.today().weekday()
if weekday_number == 0:
  weekday = 'Maanantai'
elif weekday_number == 1:
  weekday = 'Tiistai'
elif weekday_number == 2:
  weekday = 'Keskiviikko'
elif weekday_number == 3:
  weekday = 'Torstai'
elif weekday_number == 4:
  weekday = 'Perjantai'
else:
  print 'Nyt on viikonloppu. Lounasta ei tarjoilla.'
  exit()

print "## Lounaslistat %s %s" % (today_date, weekday)

pihka_urls = ['http://ruoholahti.pihka.fi', 'http://meclu.pihka.fi']
amica_urls = ['http://www.amica.fi/modules/json/json/Index?costNumber=3131&language=fi']

for url in pihka_urls:
  try:
    page = requests.get(url)
    parse_menu_from_html(page.text, weekday)
  except requests.exceptions.ConnectionError:
    print "Yhteysvirhe, %s ei vastaa." % url

for url in amica_urls:
  menu_json = requests.get(url)
  menu = json.loads(menu_json.text)
  print '\n' + '\033[95mRavintola ' + menu['RestaurantName'] + '\033[0m'
  for entry in menu['MenusForDays']:
    if today_date in entry['Date']:
      try:
        for option in entry['SetMenus']:
          print "\n",
          for ingredient in option['Components']:
            print " - " + ingredient
      except IndexError:
        continue

print "\n",
