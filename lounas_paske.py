#!/usr/bin/python
# -*- Coding: UTF-8 -*-
import requests
import re
import datetime
import json
import os.path
import hashlib
from os.path import expanduser
from bs4 import BeautifulSoup

home = expanduser("~")
if not os.path.exists(home + "/.lounas"):
  os.mkdir(home + "/.lounas")

def get_page(url):
  hash = hashlib.md5()
  hash.update(url)
  hash = hash.hexdigest()
  cachefile = home + "/.lounas/" + week_number + "-" + hash
  if os.path.isfile(cachefile):
      page = open(cachefile, "r")
      page = page.read()
      return page
  else:   
    try:
      page = requests.get(url)
      page = page.text
      page = page.encode('utf8')
      file = open(cachefile, "w")
      file.write(page)
      file.close()
      return page
    except requests.exceptions.ConnectionError:
      print "Yhteysvirhe, %s ei vastaa." % url
      return False

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
week_number = datetime.datetime.now().strftime("%W")
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

print "## Lounaslistat %s %s, viikko numer %s" % (today_date, weekday, week_number)

pihka_urls = ['http://ruoholahti.pihka.fi', 'http://meclu.pihka.fi']
amica_urls = ['http://www.amica.fi/modules/json/json/Index?costNumber=3131&language=fi']

for url in pihka_urls:
  page = get_page(url)
  parse_menu_from_html(page, weekday)

for url in amica_urls:
  menu_json = get_page(url)
  menu = json.loads(menu_json)
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
