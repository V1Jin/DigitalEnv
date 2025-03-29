import sys

import requests
import re

import spacy

import json

from urllib.parse import urlparse, parse_qs, quote

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

  url = f"https://catalog.api.2gis.com/3.0/items/byid?id={id}&key={api_key}&fields=items.full_address_name,items.rubrics,items.point,items.statistic"

  response = requests.get(url).json()
  return response


def extract_2gis_id(api_key, link):

  url = f"https://catalog.api.2gis.com/3.0/items?q={link}&key={api_key}"

  response = requests.get(url).json()
  return response

def extract_2gis_rubric(location, text):
	url = f"https://catalog.api.2gis.com/3.0/items?q={text}&location={location}&page_size=5&key=49caba50-28ff-41b0-9268-0ff6e43bdc31&fields=items.rubrics"

	response = requests.get(url).json()
	return response["result"]["items"][0]["rubrics"][0]["name"]

def get_2gis_near(location, text):

  url = f"https://catalog.api.2gis.com/3.0/items?q={text}&location={location}&page_size=5&key=49caba50-28ff-41b0-9268-0ff6e43bdc31&fields=items.external_content,items.reviews&sort=relevance"

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

# for res in response["result"]["items"]:
#   print(res)

#   print("-"*40)



# Реализация перехода из яндекса --> 2гис --------------------------

def parse_yandex_maps_url(yandex_url):
    try:
        org_name = urlparse(yandex_url).path.split('/org/')[1].split('/')[0]
        
        parsed = urlparse(yandex_url)
        params = parse_qs(parsed.query)
        ll = params.get('ll', [None])[0]    
        return {
            "name": org_name.replace('_', ' '),
            "geo": quote(ll)
        }
    
    except Exception as ex:
        print(f"Ошибка парсинга URL Яндекс.Карт: {ex}")
        return None


parsed_yandex = parse_yandex_maps_url("https://yandex.ru/maps/org/akvarium/173408900265/?ll=38.995723%2C45.037458")
if parsed_yandex:
    print(get_2gis_near(parsed_yandex["geo"], extract_2gis_rubric(parsed_yandex["geo"], parsed_yandex["name"])))




