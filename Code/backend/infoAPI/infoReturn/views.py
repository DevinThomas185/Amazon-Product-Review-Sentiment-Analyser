from bs4 import BeautifulSoup
from django.http import HttpResponse, JsonResponse
from math import sqrt
from nltk.tokenize import RegexpTokenizer
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from statistics import mean
from sqlite3 import Error
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import ast
import datetime
import os
import pandas
import re
import requests
import sqlite3


# Obtain reviews from a single review page
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


# Obtain reviews from Amazon by scraping them
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


# Simple function to calculate the percentage of reviews
def calc(num, total):
    return round((num*100)/total, 2)


# Multiply the transformation matrix to form 2D plot
def matrixMultiplication(pos, neu, neg):
    x = (-sqrt(2) / 2) * pos + (sqrt(2) / 2) * neu
    y = (sqrt(6) / 2) * neg
    return round(x, 3), round(y, 3)


# Determination function to determine the overall outcome for a product
def determinationFunction(pos, neu, neg):
    # Convert 3D Coordinates to 2D Shapely coordinate
    coords = Point(matrixMultiplication(pos, neu, neg))

    # Define the important points
    centre = (-0.44, 0.45)
    bottomwall = (-0.3, -0.01)
    leftwall = (-0.45, 0.45)
    rightwall = (0.65, 0.11)

    # Constant points
    leftcorner = (-0.72, -0.01)
    rightcorner = (0.72, -0.01)
    topcorner = (0, 1.23)

    # Defining regions/polygons
    buy = Polygon([centre, bottomwall, leftcorner, leftwall])
    neutral = Polygon([centre, bottomwall, rightcorner, rightwall])
    nobuy = Polygon([centre, rightwall, topcorner, leftwall])

    # Determine which region the point lies in and return outcome
    if buy.contains(coords):
        return "buy"
    elif neutral.contains(coords):
        return "neutral"
    elif nobuy.contains(coords):
        return "nobuy"
    else:
        return "error"


# Function to analyse just one review - FOR RULE BASED
def analyseOne(review):
    analyser = SentimentIntensityAnalyzer()
    score = analyser.polarity_scores(review)['compound']
    # The number of each type will be saved in a list. 0 - negative, 1 - neutral, 2 - positive
    if score >= 0.05:
        return 2, score  # Denotes an index of 2 - Positive Review
    elif score <= -0.05:
        return 0, score  # Denotes an index of 0 - Negative Review
    else:
        return 1, score  # Denotes an index of 1 - Neutral Review


# Function to analyse all the reviews of a product - RULE BASED
def analyseReviewsRuleBased(reviews):
    analysis = dict()
    analysis["most_positive"] = ""
    analysis["most_critical"] = ""
    mostposnum = -1
    mostcritnum = 1
    counts = [0, 0, 0]  # 0 - negative, 1 - neutral, 2 - positive
    for review in reviews:  # Iterate through all reviews
        index = analyseOne(review)  # Identify which sentiment needs to be incremented
        counts[index[0]] += 1  # Increment number
        if index[1] > mostposnum:  # Change data for the most positive reviews
            mostposnum = index[1]
            analysis["most_positive"] = review
        if index[0] < mostcritnum:  # Change the data for the most critical reviews
            mostcritnum = index[1]
            analysis["most_critical"] = review
    analysis["neg_percent"] = calc(counts[0], sum(counts))  # Calculate percentages of each type
    analysis["neu_percent"] = calc(counts[1], sum(counts))
    analysis["pos_percent"] = calc(counts[2], sum(counts))
    analysis["avg"] = "Not applicable for Rule-Based Analysis"
    analysis['outcome'] = determinationFunction(analysis["pos_percent"]/100, analysis["neu_percent"]/100, analysis["neg_percent"]/100)
    return analysis


# Function to analyse all the reviews of a product - AUTOMATIC APPROACH
def analyseReviewsAutomatic(reviews):
    analysis = dict()
    counts = [0, 0, 0]  # Index: 0 - negative, 1 - neutral, 2 - positive

    # Instantiate Scikit-learn CountVectorizer
    token = RegexpTokenizer(r'[a-zA-Z0-9]+')
    cv = CountVectorizer(lowercase=True, stop_words='english', ngram_range=(1, 1), tokenizer=token.tokenize)

    # Training data pre-processing
    path = "/Users/DevinThomas/Desktop/School Work/A-Level Work/Computer Science/Coursework/Code/alevelcoursework/backend/infoAPI/infoReturn/training.csv"
    train = pandas.read_csv(path, sep=',', low_memory=False)
    text_counts = cv.fit_transform(train['reviews.text'].values.astype('U'))

    # Test data pre-processing
    for i in range(len(reviews)):  # Convert unicode characters to string format
        reviews[i] = str(reviews[i]).lower()
    reviews = pandas.DataFrame(reviews, columns=["reviews"])
    test = cv.transform(reviews['reviews'])

    # Split training and test data
    X_train, X_test, y_train, y_test = train_test_split(text_counts, train['reviews.rating'].values.astype('U'), test_size=0.1, random_state=1)

    # Train model
    clf = MultinomialNB().fit(X_train, y_train)

    # Run model on real data
    predicted = clf.predict(test)

    # Calculate percentages
    for p in predicted:
        if float(p) >= 4:
            counts[2] += 1  # Positive
        elif float(p) <= 1:
            counts[0] += 1  # Negative
        else:
            counts[1] += 1  # Neutral
    analysis["neg_percent"] = calc(counts[0], sum(counts))  # Calculate percentages of each type
    analysis["neu_percent"] = calc(counts[1], sum(counts))
    analysis["pos_percent"] = calc(counts[2], sum(counts))

    predicted = [float(i) for i in predicted]
    analysis["avg"] = round(mean(predicted), 2)
    
    analysis["most_positive"] = "Not applicable for Automatic analysis"
    analysis["most_critical"] = "Not applicable for Automatic analysis"

    analysis['outcome'] = determinationFunction(analysis["pos_percent"]/100, analysis["neu_percent"]/100, analysis["neg_percent"]/100)
    return analysis


# Get analysis of reviews
def getAnalysis(asin, analysis_type):
    analysis = dict()
    reviews = getReviews(asin)
    analysis["noreviews"] = len(reviews)
    if analysis_type == "0":
        analysis.update(analyseReviewsRuleBased(reviews))
    elif analysis_type == "1":
        analysis.update(analyseReviewsAutomatic(reviews))
    return analysis


# Function to individually search for a detail provide
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


# Search through the soup for each detail required
def searchHTML(asin, soup, analysis_type):
    product_json = dict()
    product_json["name"] = searchDetail(soup, 'span', {"id": "productTitle"})
    if product_json["name"] is None:  # Make all fields null if the product is not found
        return dict()
    product_json["asin"] = asin
    product_json["price"] = searchDetail(soup, 'span', {"id": "priceblock_ourprice"})
    product_json["seller"] = searchDetail(soup, 'a', {"id": "bylineInfo"})
    product_json["rating"] = searchDetail(soup, 'span', {"class": "a-icon-alt"})[:3]
    product_json["noratings"] = searchDetail(soup, 'span', {"id": "acrCustomerReviewText"})[:-8]
    product_json["image"] = findImage(soup)
    product_json["date_last_analysed"] = str(datetime.date.today())
    product_json["date_full"] = datetime.datetime.strptime(product_json["date_last_analysed"], '%Y-%m-%d').strftime('%d %B %Y')
    product_json.update(getAnalysis(asin, analysis_type))
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
        if index == len(proxies)-1:
            index = 0
        proxy = proxies[index]  # This will retry extraction until it is successful.
        try:
            page = requests.get(url, headers=headers, proxies={"http": proxy})
            if "To discuss automated access" in str(BeautifulSoup(page.content, 'html.parser').prettify('utf-8')):
                index += 1
                continue
            else:
                return page
        except:
            index += 1
            continue


# Get the HTML file of the URL provided by the user by formatting the page
def getHTML(url, proxies):
    page = getPage(url, proxies)
    soup = BeautifulSoup(page.content, 'html.parser')  # Parse the object obtained   page.content
    return soup


# Set the base directory to this path. Any extra directories will branch from here.
os.chdir("/Users/DevinThomas/Desktop/School Work/A-Level Work/Computer Science/Coursework/Code/alevelcoursework/backend/db")


# Create connection to database.
def createConnection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        print("Connected to " + db_file)
        return conn
    except Error as e:
        print(e)
    return None


# Create product_info to save data in.
def createTable(conn):
    sql = """CREATE TABLE IF NOT EXISTS products(
                                    id INTEGER PRIMARY KEY,
                                    asin TEXT NOT NULL,
                                    product_json json NOT NULL,
                                    date_last_analysed TEXT NOT NULL);"""
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    except Error as e:
        print(e)
    print("Table access successful")


def asinInDB(conn, asin):
    sql = """SELECT product_json FROM products WHERE asin = (?);"""
    cur = conn.cursor()
    cur.execute(sql, (asin,))
    res = cur.fetchall()
    if res == list():
        return False, None
    else:
        return True, ast.literal_eval(res[0][0])


def saveToDB(conn, asin, product_json, date):
    sql = """SELECT * FROM products WHERE asin = (?)"""
    cur = conn.cursor()
    cur.execute(sql, (asin,))
    if cur.fetchall() == list():
        sql = """INSERT INTO products(asin, product_json, date_last_analysed) VALUES (?,?,?);"""
        cur.execute(sql, (asin, product_json, date))
    else:
        sql = """UPDATE products SET product_json=(?), date_last_analysed=(?) WHERE asin=(?)"""
        cur.execute(sql, (product_json, date, asin))
    conn.commit()
    print("Save Successful for " + asin)


def analysed(asin, analysis_type, conn):
    proxies = getProxies()
    soup = getHTML("https://www.amazon.co.uk/dp/" + asin, proxies)
    product_json = searchHTML(asin, soup, analysis_type)
    saveToDB(conn, asin, str(product_json), product_json['date_last_analysed'])
    return product_json


def urlFormat(url):
    ext = url.split("/")
    analysis_type = ext[0]
    force_analysis = ext[1]
    if 'dp/' in url:
        asin = (url.split("dp/", 1)[1]).split('/')[0]
    else:
        asin = ext[2]
    return [asin.upper(), analysis_type, force_analysis]


# Views are written below here:


# Obtain the html, search for the data and return it
def getInformation(request, url=None):
    url = urlFormat(url)
    asin, analysis_type, force_analyse = url[0], url[1], url[2]

    conn = createConnection('products.db')  # Connect to database
    if conn is not None:
        # Create product_info table
        createTable(conn)
    else:
        print("Error! cannot create the database connection.")
        exit()

    if not asinInDB(conn, asin)[0] or force_analyse == "true":
        if force_analyse == "true":
            print("Analysis for " + asin + " forced to update")
        else:
            print(asin + " does not exist in DB; Analysing and Saving to DB")
        return JsonResponse(analysed(asin, analysis_type, conn))
    else:
        print(asin + " exists in DB")
        result = asinInDB(conn, asin)[1]
        if (datetime.datetime.now() - datetime.datetime.strptime(result["date_last_analysed"], "%Y-%m-%d")).days >= 30:
            print("Analysis out of date; re-analysing and updating DB")
            return JsonResponse(analysed(asin, analysis_type, conn))
        else:
            return JsonResponse(result)


# Function to return an empty json when no URL is given.
def index(request):
    return HttpResponse("This will be called when no URL is given.")
