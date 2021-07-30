import pandas as pd

data = pd.read_csv('./data/raw.csv')

data = data.drop(['Screen_name', 'Source', 'Link', 'Sentiment', 'New_Sentiment_Score', 'New_Sentiment_State'], axis=1)
data=data.query('sent_score != 0.0')
print(data['Date'])


