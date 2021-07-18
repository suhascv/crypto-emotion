import pandas as pd
import re
from collections import Counter
import string

def clean_tweet(tweets):
    cleaned_tweets=[]
    for tweet in tweets:
        try:
            temp = tweet.replace("#"," ")
            temp = re.sub("@[A-Za-z0-9_]+"," ",temp).strip(" ") #remove @<mentions>
            temp = re.sub("(\w+:\/\/\S+)"," ",temp).strip(" ") #remove url/links
            temp.translate(str.maketrans('', '', string.punctuation))
        except:
            temp=tweet
        cleaned_tweets.append(temp)
    
    return cleaned_tweets


def most_frequent(tweets,frequency):
    counts= Counter()
    for tweet in tweets:
        tokens =re.findall(r"[\w']+",tweet.lower())
        for token in tweet.lower().split(" "):
            if token not in stopwords:
                counts[token]+=1
    return counts.most_common()[:frequency]




with open('./data/stopword.txt','r') as stop_file:
    stopwords = stop_file.read().split('\n')
print(stopwords) 

df = pd.read_csv("./data/train.csv")
df = df.dropna(subset=["Tweet","Sentiment","sent_score"]) 
df['Sentiment']=df['Sentiment'].str.strip("'[]")
df['Tweet']= clean_tweet(df['Tweet'])

positive=df[df['Sentiment']=="positive"]
negative=df[df['Sentiment']=="negative"]
neutral=df[df['Sentiment']=="neutral"]



positive=positive.sort_values(by="New_Sentiment_Score",ascending=False)
negative=negative.sort_values(by="New_Sentiment_Score",ascending=True)

most_frequent_neutral = [item[0] for item in most_frequent(neutral['Tweet'], 20)]

most_frequent_positive = most_frequent(positive['Tweet'], 50)
most_frequent_negative = most_frequent(negative['Tweet'], 50)

most_p = []
most_n = []


for item in most_frequent_positive:
    if item[0] not in most_frequent_neutral:
        most_p.append(item[0])

for item in most_frequent_negative:
    if item[0] not in most_frequent_neutral:
        most_n.append(item[0])



print(" most common words among positive tweets ",most_p)
print(" most common words among negative tweets ",most_n)
