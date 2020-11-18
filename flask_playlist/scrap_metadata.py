from bs4 import BeautifulSoup
import requests
import youtube_dl
import youtube_dl.utils


def scrap_lxml():
    url = "https://www.youtube.com/watch?v=HwSfURSe18Q"
    html = requests.get(url)
    soup = BeautifulSoup(html.text, "lxml")
    for div in soup.find_all("div", class_="style-scope ytd-watch-flexy"):
        print(div.text.replace("\n", ""))


def get_meta():
    # url = "https://www.youtube.com/watch?v=_g02ECRXCtE"
    url = "https://www.youtube.com/watch?v=jJLzjXVUysk"
    video = youtube_dl.YoutubeDL({}).extract_info(url, download=False)
    print(video['artist'], video['track'])


def scrap_html():
    url = "https://www.youtube.com/watch?v=ng2o98k983k"
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find_all('div')
    title = divs[1].find('span', class_='watch-title').text.strip()
    print(title)


if __name__ == '__main__':
    # get_meta()
    scrap_html()

