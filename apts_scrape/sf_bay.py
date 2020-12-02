from time import sleep, time
from random import randint
from warnings import warn
from requests import get 
from tqdm import tqdm
from datetime import datetime 
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

URL = "https://sfbay.craigslist.org/search/sfc/apa?"
FILTERS = [
  "hasPic=1",
  "max_price=2300",
  "max_bedrooms=1",
  "availabilityMode=0"
]
FILTER_STR = "&".join(FILTERS)

#find the total number of posts to find the limit of the pagination
response = get(URL + FILTER_STR)
html_soup = BeautifulSoup(response.text, 'html.parser')
results_num = html_soup.find('div', class_= 'search-legend')
results_total = int(results_num.find('span', class_='totalcount').text)
# pages = np.arange(0, results_total, 120)
pages = range(1)
posts = []

for page in tqdm(pages):
  response = get(URL + "s=" + str(page) + FILTER_STR)
  sleep(randint(1,5)) # gets past checker
     
  if response.status_code != 200:
    warn('Request: {}; Status code: {}'.format(requests, response.status_code))
      
  page_html = BeautifulSoup(response.text, 'html.parser')
  posts_found = html_soup.find_all('li', class_= 'result-row')
      
  for post in posts_found:
    if post.find('span', class_ = 'result-hood') is not None:
      post_datetime = post.find('time', class_= 'result-date')['datetime']
      post_hood = post.find('span', class_= 'result-hood').text
      post_title = post.find('a', class_='result-title hdrlnk')
      post_link = post_title['href']
      post_price = int(post.a.text.strip().replace("$", "").replace(",", ""))
      bedroom_count = np.nan 
      sqft = np.nan 

      if post.find('span', class_ = 'housing') is not None:
        if 'ft2' in post.find('span', class_ = 'housing').text.split()[0]:
          sqft = int(post.find('span', class_ = 'housing').text.split()[0][:-3])

        elif len(post.find('span', class_ = 'housing').text.split()) > 2:
          bedroom_count = post.find('span', class_ = 'housing').text.replace("br", "").split()[0]
          sqft = int(post.find('span', class_ = 'housing').text.split()[2][:-3])

        elif len(post.find('span', class_ = 'housing').text.split()) == 2:
          bedroom_count = post.find('span', class_ = 'housing').text.replace("br", "").split()[0]

      new_post = {}
      new_post["time"] = post_datetime
      new_post["hood"] = post_hood
      new_post["title"] = post_title.text
      new_post["URL"] = post_link
      new_post["price"] = post_price
      new_post["bedroom_count"] = bedroom_count
      new_post["sqft"] = sqft
    posts.append(new_post)
print("Parsed {} posts".format(len(posts)))

apts = pd.DataFrame(posts)
apts = apts.drop_duplicates(subset="URL")
apts['time'] = pd.to_datetime(apts['time'])
apts['hood'] = apts['hood'].str.title()
apts['hood'] = apts['hood'].apply(lambda x: x.split('/')[0])
apts['hood'].replace('Belmont, Ca', 'Belmont', inplace=True)
apts['hood'].replace('Hercules, Pinole, San Pablo, El Sob', 'Hercules', inplace=True)
apts['hood'] = eb_apts['hood'].apply(lambda x: x.strip())
apts.sort_values(by=['time'], inplace=True, ascending=False)

apts.to_csv("check.csv")
