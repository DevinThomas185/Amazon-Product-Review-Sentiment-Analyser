import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def convert(pos):
    if pos == "CC":
        return ""
    if pos == "CJ":
        return ""
    if pos == "DT":
        return "#n"
    if pos == "EX":
        return ""
    if pos == "FW":
        return ""
    if pos == "IN":
        return ""
    if pos == "JJ" or pos == "JJR" or pos == "JJS":
        return "#a"
    if pos == "LS":
        return ""
    if pos == "MD":
        return ""
    if pos == "NN" or pos == "NNS" or pos == "NNP" or pos == "NNPS":
        return "#n"
    if pos == "PDT":
        return ""
    if pos == "POS":
        return ""
    if pos == "PRP":
        return ""
    if pos == "PRP$":
        return ""
    if pos == "RB" or pos == "RBR" or pos == "RBS":
        return "#r"
    if pos == "RP":
        return ""
    if pos == "TO":
        return ""
    if pos == "UH":
        return ""
    if pos == "VB" or pos == "VBD" or pos == "VBG" or pos == "VBN" or pos == "VBP" or pos == "VBZ":
        return "#v"
    if pos == "WDT":
        return ""
    if pos == "WP":
        return ""
    if pos == "WP$":
        return ""
    if pos == "WRB":
        return ""


review = "This product is really disappointing"a
tokens = nltk.word_tokenize(review.lower())
tagged = nltk.pos_tag(tokens)
score = 0
words = {}
with open("SentiWords_1.1.txt", "r") as f:
    for line in f:
        a = line.strip()
        a = a.split("\t")
        words[a[0]] = float(a[1])
    f.close()
for token in tagged:
    word = token[0] + convert(token[1])
    if word in words:
        score += words[word]
print(score)


analyser = SentimentIntensityAnalyzer()
vs = analyser.polarity_scores(review)
print(vs)

