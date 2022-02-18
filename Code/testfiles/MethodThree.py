import pandas
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics


def analyseReviews(reviews):
    # Instantiate Scikit-learn CountVectorizer
    token = RegexpTokenizer(r'[a-zA-Z0-9]+')
    cv = CountVectorizer(lowercase=True, stop_words='english', ngram_range=(1, 1), tokenizer=token.tokenize)


    # Training data pre-processing
    train = pandas.read_csv('training.csv', sep=',', low_memory=False)
    text_counts = cv.fit_transform(train['reviews.text'].values.astype('U'))


    # Test data pre-processing
    reviewsTest = []
    for r in reviews:  # Convert unicode characters to string format
        reviewsTest.append(str(r).lower())
    reviewsTest = pandas.DataFrame(reviewsTest, columns=["reviews"])
    test = cv.transform(reviewsTest['reviews'])


    # Split training and test data
    X_train, X_test, y_train, y_test = train_test_split(text_counts, train['reviews.rating'].values.astype('U'), test_size=0.1, random_state=1)


    # Train model
    clf = MultinomialNB().fit(X_train, y_train)


    # Run model on training data
    evaluate = clf.predict(X_test)


    # Run model on real data
    predicted = clf.predict(test)


    # Calculate percentages
    scores = [0, 0, 0]  # Index 0 - negative, 1 - neutral, 2 - positive
    for p in predicted:
        if float(p) >= 4:
            scores[2] += 1  # Positive
        elif float(p) <= 1:
            scores[0] += 1  # Negative
        else:
            scores[1] += 1  # Neutral

    print(round((scores[2]*100)/len(predicted), 2), round((scores[1]*100)/len(predicted), 2), round((scores[0]*100)/len(predicted), 2))



