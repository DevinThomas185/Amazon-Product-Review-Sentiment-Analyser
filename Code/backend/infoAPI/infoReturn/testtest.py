from django.http import HttpResponse, JsonResponse
from bs4 import BeautifulSoup
import re
import requests

# Function to individually search for a detail provided
def searchDetail(soup, element, attributes):
    detail = ""
    for tag in soup.findAll(element, attrs=attributes):
        detail = tag.text.strip()
        break
    return detail


# Separate function to find the large images of the product
def findImage(soup):
    image = soup.find('img', attrs={"id": "landingImage"})
    try:
        return image['data-old-hires']
    except:
        return None

def getReviewsOfPage(reviews, soup):
    for tag in soup.findAll('span', attrs={"data-hook": "review-body"}):
        for span in tag:
            span = str(span)
            t = span.replace("<span>", "")
            t = t.replace("</span>", "")
            t = t.replace("<br>", "")
            t = t.replace("</br>", "")
            t = t.replace("<br/>", "")
            if t != '\n':
                reviews.append(t)
    return reviews


def getAnalysis(asin):
    analysis = dict()
    reviews = getReviews(asin)
    analysis["noreviews"] = len(reviews)
    analysis["reviews"] = reviews

    # Analysis occurs here

    return analysis


def getReviews(asin):
    reviews = []
    i = 0
    proxies = getProxies()
    while True:  # Iterate until the specific message denoting no more reviews is found
        soup = getHTML("https://www.amazon.co.uk/product-reviews/" + asin + "/ref=cm_cr_arp_d_paging_btm_next_2?pageNumber=" + str(i), proxies)
        if "Sorry, no reviews match your current selections." not in str(soup.prettify('utf-8')):
                reviews = getReviewsOfPage(reviews, soup)
                i += 1  # Increment the page fetched each time
        else:
            break
    return reviews


# Search through the soup for each detail required
def searchHTML(asin, soup):
    product_json = dict()
    product_json["name"] = searchDetail(soup, 'span', {"id": "productTitle"})
    product_json["price"] = searchDetail(soup, 'span', {"id": "priceblock_ourprice"})
    product_json["seller"] = searchDetail(soup, 'a', {"id": "bylineInfo"})
    product_json["rating"] = searchDetail(soup, 'span', {"class": "a-icon-alt"})[:3]
    product_json["noratings"] = searchDetail(soup, 'span', {"id": "acrCustomerReviewText"})[:-8]
    product_json["image"] = findImage(soup)
    product_json.update(getAnalysis(asin))
    if product_json["name"] is None:  # Make all fields null if the product is not found
        product_json = dict()
    return product_json


# Get the proxies to use during the extraction of the html
def getProxies():
    proxies = []
    response = requests.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(response.content, 'html.parser')
    tds = []
    for td in soup.findAll('td'):
        tds.append(str(td))
    pattern = '<td>[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*</td>'
    for i in range(len(tds)):
        if re.match(pattern, tds[i]):
            proxy = tds[i].replace("<td>","")
            proxy = proxy.replace("</td>", "")
            port = tds[i+1].replace("<td>", "")
            port = port.replace("</td>", "")
            proxies.append(proxy + ":" + port)
    return proxies


# Get the page from the site
def getPage(url, proxies):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
    fetched = False
    index = 0
    while not fetched:  # Try case in order to try multiple proxies. Free proxies often experience connection issues
        proxy = proxies[index]  # This will retry extraction until it is successful.
        try:
            page = requests.get(url, headers=headers, proxies={"http": proxy})
            return page
        except:
            index += 1
            continue


# Get the HTML file of the URL provided by the user by formatting the page
def getHTML(url, proxies):
    page = getPage(url, proxies)
    soup = BeautifulSoup(page.content, 'html.parser')  # Parse the object obtained
    return soup


# Views are written below here:


# Obtain the html, search for the data and return it
def getInformation(request, asin=None):
    if "dp/" in asin:
        asin = asin.split("dp/", 1)[1]
    if "/" in asin:
       asin = asin.split("/", 1)[0]
    proxies = getProxies()
    soup = getHTML("https://www.amazon.co.uk/dp/" + asin.upper(), proxies)
    product_json = searchHTML(asin, soup)
    return JsonResponse(product_json)


# Function to return an empty json when no URL is given.
def index(request):
    return HttpResponse("This will be called when no URL is given.")
