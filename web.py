import requests
from bs4 import BeautifulSoup


def queryLinks(name):
    url = rf"https://yandex.ru/search/?text={name}&clid=2270455&win=675&lr=35"
    print(f"Входящий name --- {name}")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"
    }

    

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')

    elements = soup.find_all(class_="Link Link_theme_normal OrganicTitle-Link organic__url link")
    hrefs = [a.get('href') for a in elements if a.get('href') is not None and ("vk.com" in a.get('href') or "t.me" in a.get('href') )]
    print (hrefs)

    

    print (response.status_code)
    # print(response.text)
    return hrefs

# text = "Глория джинс"

# queryLinks(f"{text} вконтакте")
# https://yandex.ru/search/?text=site%3Avk.com+вкусно+и+точка&lr=35&clid=2270455&win=675
# https://yandex.ru/search/?text=site%3Avk.com+вкусно+и+точка&lr=35&clid=2270455&win=675