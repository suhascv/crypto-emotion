import pandas as pd
import re
from collections import Counter
import string
from emosent import get_emoji_sentiment_rank
import json
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from better_profanity import profanity

  
ps = PorterStemmer()



def get_stemmed(tokens):
    stemmed_words=set()
    for token in tokens:
        stemmed_words.add(ps.stem(token))
    return stemmed_words


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

def emoji_score(line):
    emoticons=re.findall(r'[^\w\s,]',line)
    score=0
    errors=0
    if len(emoticons)==0:
        return "no_emoji"
    for emoji in emoticons:
        try:
            score += get_emoji_sentiment_rank(emoji)['sentiment_score']
        except:
            pass
    if score!=0 and len(emoticons)>0:
        score=score/len(emoticons)
    
    if score>0.5:
        score="highly_positive"
    elif score<=0.5 and score>0:
        score="positive"
    elif score==0:
        score="neutral"
    elif score <0 and score >-0.5:
        score="negative"
    elif score <=-0.5:
        score="highly_negative"
    
    
    return score

def has_feature(tokens,words):
    flag='no'
    for token in tokens:
        if token in words:
            flag='yes'
            break
    return flag
        
def check_profanity(tweet):
    if profanity.contains_profanity(tweet):
        return 'yes'
    else:
        return 'no'


def get_features(tweets):
    has_positives=[]
    has_negatives=[]
    has_frequent_positives=[]
    has_frequent_negatives=[]
    emoji_sentiments=[]
    has_profanity=[]

    for tweet in tweets:
        tokens =re.findall(r"[\w']+",tweet.lower())
        emoji_sentiments.append(emoji_score(tweet))
        has_positives.append(has_feature(tokens, positive_words))
        has_negatives.append(has_feature(tokens, negative_words))
        has_frequent_positives.append(has_feature(tokens, frequent_positives))
        has_frequent_negatives.append(has_feature(tokens, frequent_negatives))
        #has_profanity.append(check_profanity(tweet))
            
    return {'has_negatives':has_negatives,
            'has_positives':has_positives,
            'has_frequent_positives':has_frequent_positives,
            'has_frequent_negatives':has_frequent_negatives,
            'emoji_sentiments':emoji_sentiments,
            'has_profanity':has_profanity
            }
            


with open('./data/stopword.txt','r') as stop_file:
    stopwords = set(stop_file.read().split('\n'))


with open('./data/positive.txt','r') as positive_file:
    positive_words = set(positive_file.read().split('\n'))

with open('./data/positive.txt','r') as negative_file:
    negative_words = set(negative_file.read().split('\n'))

with open('./data/frequent_positive.txt','r') as frequent_pos_file:
    frequent_positives = set(frequent_pos_file.read().split('\n'))

with open('./data/frequent_negative.txt','r') as frequent_neg_file:
    frequent_negatives = set(frequent_neg_file.read().split('\n'))


df = pd.read_csv("./data/raw.csv")
df = df.dropna(subset=["Tweet","Sentiment","sent_score"]) 
del df['Unnamed: 0']
del df['Date']
del df['Screen_name']
del df['Source']
del df['Link']
del df['sent_score']
del df['New_Sentiment_State']
del df['New_Sentiment_Score']
df['Sentiment']=df['Sentiment'].str.strip("'[]")
df['Sentiment']=df['Sentiment'].str.replace('0.0','neutral')
df['Tweet']= clean_tweet(df['Tweet'])



print(df.columns)
features=get_features(df['Tweet'])

df['has_negatives']=features['has_negatives']
df['has_positives']=features['has_positives']
df['has_frequent_positives']=features['has_frequent_positives']
df['has_frequent_negatives']=features['has_frequent_negatives']
df['emoji_sentiments']=features['emoji_sentiments']
#df['has_profanity']=features['has_profanity']

positive=df[df['Sentiment']=="positive"]
negative=df[df['Sentiment']=="negative"]
neutral=df[df['Sentiment']=="neutral"]



#positive=positive.sort_values(by="New_Sentiment_Score",ascending=False)
#negative=negative.sort_values(by="New_Sentiment_Score",ascending=True)

#most_frequent_neutral = [item[0] for item in most_frequent(neutral['Tweet'], 20)]

#most_frequent_positive = most_frequent(positive['Tweet'], 50)
#most_frequent_negative = most_frequent(negative['Tweet'], 50)



print(df.head(15))
print('unique emoji states',df['emoji_sentiments'].unique())


with open('./data/train.csv','w') as out_file:
    out_file.write(df.to_csv(index=False))
df.to_json('./data/train.json',orient='index')

"""

neutral_counter=set()
negative_counter={}
positive_counter={}

for tweet in neutral['Tweet']:
    tokens =re.findall(r"[\w']+",tweet.lower())
    for token in tokens:
        if token not in stopwords:
            neutral_counter.add(token)

for tweet in negative['Tweet']:
    tokens =re.findall(r"[\w']+",tweet.lower())
    for token in tokens:
        if token not in stopwords:
            try:
                negative_counter[token]+=1
            except:
                negative_counter[token]=1

for tweet in positive['Tweet']:
    tokens =re.findall(r"[\w']+",tweet.lower())
    for token in tokens:
        if token not in stopwords:
            try:
                positive_counter[token]+=1
            except:
                positive_counter[token]=1

for item in neutral:
    try:
        del negative_counter[item]
    except:
        pass
    try:
        del positive_counter[item]
    except:
        pass

for item in sorted(negative_counter,key=negative_counter.get,reverse=True):
    if negative_counter[item] >=50 and item not in stopwords and item not in negative_words:
        print(item," : ",negative_counter[item])

for item in sorted(positive_counter,key=positive_counter.get,reverse=True):
    if positive_counter[item] >=50 and item not in stopwords and item not in positive_words:
        print(item," : ",positive_counter[item])
    
"""         
            

            
