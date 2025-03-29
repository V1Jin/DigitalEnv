import sys
import requests
import re
import spacy
import math
import json

from urllib.parse import quote

sys.stdout.reconfigure(encoding='utf-8')

feedbackCount = 5

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',  # Используйте этот заголовок, если отправляете JSON-данные
}

def haversine(lat1, lon1, lat2, lon2):
    # Радиус Земли в метрах
    R = 6371000

    # Преобразование координат в радианы
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Разница координат
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Формула гаверсинусов
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Расстояние в метрах
    distance = R * c
    return distance


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

  url = f"https://catalog.api.2gis.com/3.0/items/byid?id={id}&key={api_key}&fields=items.full_address_name,items.rubrics,items.point,items.org"

  response = requests.get(url).json()
  return response


def extract_2gis_id(api_key, link):

  url = f"https://catalog.api.2gis.com/3.0/items?q={link}&key={api_key}"

  response = requests.get(url).json()
  return response


# --------------------------------


API_KEY = "49caba50-28ff-41b0-9268-0ff6e43bdc31"
second_api_key = "6e7e1929-4ea9-4a5d-8c05-d601860389bd"

url_byid = "https://catalog.api.2gis.com/3.0/items/byid"

url_search = "https://catalog.api.2gis.com/3.0/items"




link = "https://go.2gis.com/gaG3h"
sort = "relevance"

response = get_2gis_data(API_KEY, get_2gis_id(link))
Srubricks = response["result"]["items"][0]["rubrics"]
cords = response["result"]["items"][0]["point"]
location = point_to_url(response)
print(f"cords {cords}")

branches = response["result"]["items"][0]["org"]["branch_count"]
print (branches)

text = response["result"]["items"][0]["rubrics"][0]["name"]

# response = get_2gis_near(location, text,1)

def getResponse(pages, location, text):
   for i in range(pages):
      response = get_2gis_near(location, text, i+1)

# getContacts()

def get_2gis_near(location, text,page):

    url = f"https://catalog.api.2gis.com/3.0/items?q={text}&location={location}&page_size=10&page={page}&key={API_KEY}&fields=items.rubrics,items.external_content&sort={sort}"

    response = requests.get(url).json()

    fullData = []
    for i in response["result"]["items"]:
        rates = getRanks(i["id"])
        dist_lonLat = getSizeDistance(i["id"])
        print(f"new cords {dist_lonLat}m")
        distance = abs(haversine(cords["lat"], cords["lon"], dist_lonLat[1]["lat"], dist_lonLat[1]["lon"])) + 1
        print (f"dist = {distance}m  ")

        rubricks_ratio =  0
        for j in [x["name"] for x in i["rubrics"]]:
            if j in Srubricks: rubricks_ratio += 1
        sizeRatio = abs(branches-dist_lonLat[0]) + 1
        ratio = (rates[1] * rates[0] + (1/distance)*0.5 + rubricks_ratio + 1/sizeRatio)
        data = {
                        "id": i["id"],
                        "name": i["name"],
                        "address": i["address_name"],
                        "rate": rates[1],
                        "rateCount": rates[0],
                        "distance": distance,
                        "rubricks": [x["name"] for x in i["rubrics"]],
                        "size": dist_lonLat[0],
                        "ratio": ratio
                    }
        fullData.append(data)

    with open("test.json", "r", encoding="utf-8") as file:
        try: 
            existing = json.load(file)
            existing += fullData
        except Exception as error:
            existing = fullData
    with open("test.json", "w", encoding="utf-8") as file:
        json.dump(existing, file, indent=4, ensure_ascii=False)
    return fullData

def getRanks(id):
    url = rf"https://public-api.reviews.2gis.com/2.0/objects/{id}/ratings?key={second_api_key}"

    response = requests.get(url).json()["ratings"]
    

    sums = (response["1"] + response["2"] + response["3"] + response["4"] + response["5"])
    avg = (response["1"] + 2 * response["2"] + 3 * response["3"] + 4 * response["4"] + 5 * response["5"] )/ sums
    return [sums, avg]

def getSizeDistance(id):
    url = rf"https://catalog.api.2gis.ru/3.0/items/byid?id={id}&key={API_KEY}&locale=ru_RU&fields=items.org,items.point&stat[sid]=f1cb383d-0824-482b-9ad6-b962778b18fa&stat[user]=d639d964-5d6f-482a-93c5-0c39d988f839&shv=2025-03-21-18&r=1637972868"

    response = requests.get(url).json()

    return [response["result"]["items"][0]["org"]["branch_count"], response["result"]["items"][0]["point"]]

def AllResponse(location, text, pages):
    data = []
    for i in range(pages):
        datan = get_2gis_near(location, text, i+1)
        print (datan)
        data += datan
    return data

print(AllResponse(location, text, 2))
# print(getSizeDistance("70000001084207596"))

[
    {
        "id": "",
        "name": "",
        "address": "",
        "rate": "",
        "rateCount": "",
        "distance": "",
        "rubricks": "",
        "size": "",
        "ratio": ""
    }

]

