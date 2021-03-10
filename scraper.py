from bs4 import BeautifulSoup
import requests as r 
import time 
import re
import pickle

def match_genres(list1, list2):
    match = []
    for x in list1:
        if x.lower() in list2:
            match.append(x)
        else:
            continue 
    return match

def get_releases(articles, user_genres):
    releases = []
    for n in range(len(articles)):
        genres = articles[n].find_all('a', rel='category tag')
        genres = [x.get_text() for x in genres]

        if any(match_genres(genres, user_genres)):
            pass
        else:
            continue

        title = articles[n].find('a', class_= 'title').get_text()
        try:
            if "Various Artists" in title:
                continue
            elif ' – ' not in title and ' / ' in title:
                artist_name = title.split(' / ')[0]
                release_holder = title.split(' / ')[1]
                release_title = release_holder.split(' [')[0]
                release_year = re.sub("\W", "", release_holder.split(' [')[1])
            elif ' – ' in title:
                artist_name = title.split(' – ')[0]
                release_holder = title.split(' – ')[1]
                release_title = release_holder.split(' [')[0]
                release_year = re.sub("\W", "", release_holder.split(' [')[1])
            else:
                continue
        except:
            continue
        release_dict = {
            'artist': artist_name.lower(),
            'title': release_title.lower(),
            'year': release_year.lower(),
            'genres': [x.lower() for x in genres]
        }
        print(release_dict)
        releases.append(release_dict)
    return releases

def scrape(pages, user_genres):
    all_pages = []
    for x in range(1,pages):
        print(f'Scraping page {x}')
        page = r.get(f'https://nodata.tv/blog/page/{x}')
        soup = BeautifulSoup(page.text, 'html.parser')
        columns = soup.find('div', class_ = 'columns')
        articles = columns.find_all('div', class_='column-13')
        page_releases = get_releases(articles, user_genres)
        for release in page_releases:
            all_pages.append(release)
        time.sleep(2)
    return(all_pages)