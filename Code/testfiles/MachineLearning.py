import pandas
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import RegexpTokenizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics


# Count Vectorizer
token = RegexpTokenizer(r'[a-zA-Z0-9]+')
cv = CountVectorizer(lowercase=True, stop_words='english', ngram_range=(1, 1), tokenizer=token.tokenize)

# Preprocessing training data
path = "/Users/DevinThomas/Desktop/School Work/A-Level Work/Computer Science/Coursework/Code/alevelcoursework/backend/infoAPI/infoReturn/training.csv"
train = pandas.read_csv(path, sep=",", low_memory=False)
text_counts = cv.fit_transform(train['reviews.text'].values.astype('U'))

# Preprocessing test data
reviews = ["hi", 'hello']
for i in range(len(reviews)):
    reviews[i] = str(reviews[i]).lower()
reviews = pandas.DataFrame(reviews, columns=["reviews"])
test = cv.transform(reviews['reviews'])

# Train naive-bayes model
X_train, X_test, y_train, y_test = train_test_split(text_counts, train['reviews.rating'].values.astype('U'), test_size=0.1, random_state=1)
clf = MultinomialNB().fit(X_train, y_train)

# Run model on test data
predicted = clf.predict(test)
po = clf.predict(X_test)


# Calculate percentages
scores = [0, 0, 0]  # Index 0 - negative, 1 - neutral, 2 - positive
for p in predicted:
    if float(p) >= 4:
        scores[2] += 1  # Positive
    elif float(p) <= 1:
        scores[0] += 1  # Negative
    else:
        scores[1] += 1  # Neutral

print("MultinomialNB Accuracy:",metrics.accuracy_score(y_test, po))
print(round((scores[2]*100)/len(predicted), 2), round((scores[1]*100)/len(predicted), 2), round((scores[0]*100)/len(predicted), 2))

