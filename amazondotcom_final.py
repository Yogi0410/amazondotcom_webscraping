import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_title(soup):
    # Function to extract Product Title
    try:
        title = soup.find("span", attrs={'id': 'productTitle'})
        title_string = title.text.strip()
    except AttributeError:
        title_string = ""

    return title_string


def get_price(soup):
    try:
        price = soup.find("span", attrs={'class': 'a-offscreen'}).get_text().strip()
    except AttributeError:
        try:
            price = soup.find("span", attrs={'class': 'a-size-medium a-color-price priceBlockBuyingPriceString'}).get_text().strip()
        except:
            price = ""

    return price



def get_rating(soup):
    # Function to extract product ratings
    try:
        rating = soup.find("i", attrs={'class': 'a-icon a-icon-star a-star-4-5'}).string.strip()
    except AttributeError:
        try:
            rating = soup.find("span", attrs={'class': 'a-icon-alt'}).string.strip()
        except:
            rating = ""

    return rating


def get_availability(soup):
    # Function to extract availability status
    try:
        available = soup.find("div", attrs={'id': 'availability'})
        available = available.find("span").string.strip()
    except AttributeError:
        available = "Not Available"

    return available


if __name__ == '__main__':
    # Headers for request
    HEADERS = ({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    })

    # Base URL for the search
    base_url = 'https://www.amazon.com/s?k=mobile+phones&page='

    d = {"title": [], "price": [], "rating": [], "availability": []}
    record_count = 0
    page = 1

    while record_count < 100:
        url = base_url + str(page)
        webpage = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(webpage.content, "html.parser")
        links = soup.find_all("a", attrs={
            'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})

        for link in links:
            if record_count >= 100:
                break

            link_url = "https://amazon.com" + link.get('href')
            link_webpage = requests.get(link_url, headers=HEADERS)
           # link_webpage = requests.get(urljoin("https://www.amazon.com", link), headers=HEADERS)

            link_soup = BeautifulSoup(link_webpage.content, "html.parser")

            d['title'].append(get_title(link_soup))
            d['price'].append(get_price(link_soup))
            d['rating'].append(get_rating(link_soup))
            d['availability'].append(get_availability(link_soup))

            record_count += 1

        page += 1

    amazon_df = pd.DataFrame.from_dict(d)
    amazon_df['title'].replace('', np.nan, inplace=True)
    amazon_df = amazon_df.dropna(subset=['title'])
    amazon_df.to_csv("amazon_data.csv", header=True, index=False)
