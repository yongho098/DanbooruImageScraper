#! python3
#downloads images from booru, final

import requests, os, bs4, webbrowser, pyinputplus as pyip, re, time, random, sys
from urllib.parse import unquote
from pathlib import Path

lookup = pyip.inputStr('What to search on Danbooru? ')

# #finds google results first
res = requests.get(f'https://google.com/search?q=danbooru {lookup.lower()}')
res.raise_for_status()
soup = bs4.BeautifulSoup(res.text, 'html.parser')
linkPreview = soup.find_all('h3') #google search links
numOpen = min(5, len(linkPreview)) #show top 5 links
for i in range(numOpen):
    print(f'Result {str(i + 1)}: {linkPreview[i].getText()}')

select = pyip.inputNum('Choose result: ', max=5)

x = linkPreview[select - 1].find_parent('a')
x2 = x.get('href')
url = (unquote(x2)[7:])
webbrowser.open(url)
p = 1
absolute_path = os.path.dirname(__file__)
relative_path = "Danbooru download"
homeFolder = os.path.join(absolute_path, relative_path)


# make a function to download the image
def downloadImage(url2):
    res3 = requests.get(url2)
    res3.raise_for_status()
    soup3 = bs4.BeautifulSoup(res3.text, 'html.parser')
    imageElem = soup3.find_all('a', class_="image-view-original-link")
    if imageElem == []:
        try:
            imageElem = soup3.find_all('source')
            if "," in imageElem[-1].get('srcset'):
                # for videos with multiple versions
                imageElem = soup3.find_all('image')
                x = imageElem[-1].get('src')
            else:
                print(imageElem[-1].get('srcset'))
                x = imageElem[-1].get('srcset')
        except IndexError:
            imageElem = soup3.find_all('video')
            x = imageElem[-1].get('src')

    else:
        x = imageElem[-1].get('href')

    res4 = requests.get(x)
    res4.raise_for_status()

    imageFile = open(os.path.join(f'{homeFolder}\{lookup.lower()}', os.path.basename(x)), 'wb')
    for chunk in res4.iter_content(100000):
        imageFile.write(chunk)
    imageFile.close()
    print('downloaded file')

yesno = pyip.inputYesNo('Download images? ')
if yesno == 'no':
    sys.exit()

os.makedirs(f'{homeFolder}\{lookup.lower()}', exist_ok=True)

#scrape and download
res = requests.get(url)
res.raise_for_status()
soup = bs4.BeautifulSoup(res.text, 'html.parser')
nextElem = soup.find_all('a', {'class': 'paginator-next'})
while nextElem != []:
    res2 = requests.get(url)
    res2.raise_for_status()
    soup2 = bs4.BeautifulSoup(res2.text, 'html.parser')
    imagePreview = soup2.find_all('a', {'href': re.compile(r'/posts/\d+')})
    for link in imagePreview:
        y = "https://danbooru.donmai.us" + link.get('href')
        print(f'downloading file {p}: {y}')
        downloadImage(y)
        time.sleep(random.randint(2, 5))
        p += 1
    nextElem = soup2.find_all('a', {'class': 'paginator-next'})
    if nextElem != []:
        url = f'https://danbooru.donmai.us{nextElem[-1].get("href")}'
    else:
        break
    print('next page')
    time.sleep(10)

print('done')
