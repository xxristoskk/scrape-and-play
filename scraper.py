from bs4 import BeautifulSoup
import requests as r 
import time 
import re
import pickle

#function checks to make sure at least one of the genres match
def match_genres(list1, list2):
    match = []
    for x in list1:
        if x.lower() in list2:
            match.append(x)
        else:
            continue 
    return match

#function to scrape and save the data
def get_releases(articles, user_genres, year):
    releases = []
    for n in range(len(articles)):
        genres = articles[n].find_all('a', rel='category tag')
        genres = [x.get_text() for x in genres]
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
        if any(match_genres(genres, user_genres)) and year == release_year:
            pass
        else:
            continue
        release_dict = {
            'artist': artist_name.lower(),
            'title': release_title.lower(),
            'year': release_year.lower(),
            'genres': [x.lower() for x in genres]
        }
        print(release)
        releases.append(release_dict)
    return releases

#function to navigate the blog
def scrape(pages, user_genres, year):
    all_pages = []
    for x in range(1,pages):
        print(f'Scraping page {x}')
        page = r.get(f'https://nodata.tv/blog/page/{x}')
        soup = BeautifulSoup(page.text, 'html.parser')
        columns = soup.find('div', class_ = 'columns')
        articles = columns.find_all('div', class_='column-13')
        page_releases = get_releases(articles, user_genres, year)
        for release in page_releases:
            all_pages.append(release)
        time.sleep(2)
    return(all_pages)