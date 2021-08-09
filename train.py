import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import RegexpTokenizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
import numpy as np
import matplotlib.pyplot as plt
import json
import seaborn as sns


def preprocess_data(dataset):
    # Remove package name as it's not relevant
    dataset = dataset.drop(['Screen_name', 'Source', 'Link', 'Sentiment', 'New_Sentiment_Score', 'New_Sentiment_State'], axis=1)
    # Convert text to lowercase
    #dataset['review'] = dataset['review'].str.strip().str.lower()
    return dataset

def normalize(maxi,arr):
    normalized_list=[]
    for a in arr:
        normalized_list.append(a/maxi)
    return normalized_list


def bucket_weeks(sdata,pdata):
    buckets = {'sentiment':[],'price':[]}
    for i in range(1,53):
        week_data = sdata[pd.to_datetime(sdata['time']).dt.week == i]
        week_price = pdata[pd.to_datetime(pdata['Date']).dt.week == i]
        buckets['sentiment'].append(week_data['sent_score'].sum())
        buckets['price'].append(week_price['Closing Price (USD)'].sum())
    buckets['normalizedPrice'] = normalize(max(buckets['price']), buckets['price'])
    buckets['normalizedSentiment'] = normalize(max(buckets['sentiment']), buckets['sentiment'])

    out = pd.DataFrame.from_dict(buckets)
    out.index=weeks
    out = out.drop(['sentiment','price'],axis=1)
    out.plot(kind='line',title='weekly price vs social sentiment trend 2020')
    plt.xlabel('month')
    plt.ylabel('trend')
    plt.show()

    return buckets    

def bucket_months(sdata,pdata):
    buckets = {'sentiment':[],'price':[]}
    for i in range(1,13):
        month_data = sdata[pd.to_datetime(sdata['time']).dt.month == i]
        month_price = pdata[pd.to_datetime(pdata['Date']).dt.month == i]
        buckets['sentiment'].append(month_data['sent_score'].sum()/month_data['sent_score'].count())
        buckets['price'].append(month_price['Closing Price (USD)'].sum()/month_price['Closing Price (USD)'].count())
    buckets['normalizedPrice'] = normalize(max(buckets['price']), buckets['price'])
    buckets['normalizedSentiment'] = normalize(max(buckets['sentiment']), buckets['sentiment'])

    out = pd.DataFrame.from_dict(buckets)
    out.index=months
    x,y =out['sentiment'],out['price']
    xy = out[['sentiment','price']]
    print(xy.corr())
    print(x.corr(y))

    reg=sns.lmplot(x='sentiment',y='price',data=xy,fit_reg=True)
    reg.set(ylim=(0,None))

    
    out = out.drop(['sentiment','price'],axis=1)
    out.plot(kind='line',title='monthly price vs social sentiment trend 2020')
    plt.xlabel('month')
    plt.ylabel('trend')
    plt.show()

    return buckets

"""

def correlarte(sdata,pdata,year):
    sentiments=[]
    bdata = pdata[['Date','Closing Price (USD)']]
    for d in pdata['Date']:
        day_sentiment = sdata[pd.to_datetime(sdata['time']).dt.day == pd.to_datetime(pdata['Date']).dt.day]
        print(day_sentiment)
        if day_sentiment['sent_score'].count()>0:
            sentiments.append(day_sentiment['sent_score'].sum()/day_sentiment['sent_score'].count())
        else:
            sentiments.append(None)
    
    print(sentiments)
    
"""

def predict_emotion(file_in,price_file,file_out):
    data = pd.read_json(file_in)
    predict_counts = cv.transform(data['tweet'])
    predictions=MNB.predict(predict_counts)
    data['sentiment'] = predictions
    data['sent_score'] = data['sentiment']*(1000+data['retweets']+data['likes'])
    #print(data.head(20))
    pdata = pd.read_csv(price_file)

    buckets=bucket_months(data,pdata)
    fp = open(file_out,'w')
    json.dump(buckets,fp)
    #correlarte(data, pdata, 2020)
    #bucket_weeks(data, pdata)
    

dataset = pd.read_csv('./data/raw.csv')
dataset = preprocess_data(dataset)
#drop neutral tweets
dataset = dataset.query('(sent_score == 1.0) or (sent_score == -1.0)')

months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
weeks =[w for w in range(1,53)]

#print(dataset)
dataset.replace([np.inf, -np.inf], np.nan, inplace=True)
dataset.fillna(999, inplace=True)
print(dataset['sent_score'].unique())

token = RegexpTokenizer(r'[a-zA-Z0-9]+')
cv = CountVectorizer(stop_words='english',ngram_range = (1,1),tokenizer = token.tokenize)

text_counts = cv.fit_transform(dataset['Tweet'].apply(lambda text_counts: np.str_(text_counts)))
#tdm_q = pd.DataFrame(text_counts.toarray()[0:10], columns=cv.get_feature_names())
#print(cv.get_feature_names())
X_train, X_test, Y_train, Y_test = train_test_split(text_counts, dataset['sent_score'], test_size=0.15, random_state=5)


MNB = MultinomialNB()
MNB.fit(X_train, Y_train)
predicted = MNB.predict(X_test)
accuracy_score = metrics.accuracy_score(predicted, Y_test)

predict_emotion('./data/bitcoin2020.json','./data/bitcoinP2020.csv','app/data/bitcoin/m2020.json')
predict_emotion('./data/ethereum2020.json','./data/ethereumP2020.csv','app/data/ethereum/m2020.json')


print(str('{:04.2f}'.format(accuracy_score*100))+'%')
   

