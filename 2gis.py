import sys

import requests
import re

import spacy

import json

from urllib.parse import quote

sys.stdout.reconfigure(encoding='utf-8')


def get_platform(link):

    if 'vk.com' in link:

        return 'vk'

    elif 't.me' in link:
        return 'telegram'

    elif 'rutube.ru' in link:

        return 'rutube'

    elif '2gis.com' in link:

        return '2gis'

    else:

        return 'unknown'


# Перевод из широты и долготы в url

def point_to_url(response):

  location = response["result"]["items"][0]["point"]

  loc_str = f"{location['lon']},{location['lat']}"

  return quote(loc_str) 


# -----------------------


# Убираем лишнее
def get_link(link):

    clean_link = re.sub(r'https?://(www\.)?', '', link)

    username = clean_link.split('/')[-1]

    username = re.sub(r'\?.*$', '', username)
    return username


def get_real_2gis_id(short_url):
    try:
        response = requests.get(short_url, allow_redirects=False)
        if 300 <= response.status_code < 400:
            final_url = response.headers['Location']

            firm_id = final_url.split('/firm/')[-1].split('/')[0].split('?')[0]
            return firm_id

        return None

    except Exception as ex:

        print(f"Ошибка: {ex}")

        return None


def get_2gis_id(url):

    if url.startswith(("https://go.2gis.com/", "http://go.2gis.com/")):

        return get_real_2gis_id(url)

    else:
        return get_link(url)

    return None


# ----------------------


def get_2gis_data(api_key, id):

  url = f"https://catalog.api.2gis.com/3.0/items/byid?id={id}&key={api_key}&fields=items.full_address_name,items.rubrics,items.point"

  response = requests.get(url).json()
  return response


def extract_2gis_id(api_key, link):

  url = f"https://catalog.api.2gis.com/3.0/items?q={link}&key={api_key}"

  response = requests.get(url).json()
  return response


def get_2gis_near(location, text):

  url = f"https://catalog.api.2gis.com/3.0/items?q={text}&location={location}&page_size=5&key=49caba50-28ff-41b0-9268-0ff6e43bdc31&fields=items.rubrics,items.external_content&sort=relevance"

  response = requests.get(url).json()

  with open("test.json", "w", encoding="utf-8") as file:

    json.dump(response, file, indent=4, ensure_ascii=False)  
  return response


# --------------------------------


API_KEY = "49caba50-28ff-41b0-9268-0ff6e43bdc31"

url_byid = "https://catalog.api.2gis.com/3.0/items/byid"

url_search = "https://catalog.api.2gis.com/3.0/items"




link = "https://go.2gis.com/ZJip0"

response = get_2gis_data(API_KEY, get_2gis_id(link))
location = point_to_url(response)

text = response["result"]["items"][0]["rubrics"][0]["name"]

response = get_2gis_near(location, text)

for res in response["result"]["items"]:
  print(res)

  print("-"*40)



# url = "https://geocode-maps.yandex.ru/v1/?apikey=b156e65d-f8cb-45a1-8f83-3f613e7710e0&geocode=икариум краснодар&format=json"

# response = requests.get(url).json()

# print(response)



