import requests
from bs4 import BeautifulSoup

def get_titles(url):

    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    titles = soup.find_all("h2")

    results = []

    for title in titles:
        results.append(title.text.strip())

    return results