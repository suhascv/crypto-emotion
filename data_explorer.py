import pandas as pd
import matplotlib.pyplot as plt

df=pd.read_json('./data/bitcoin2020.json')
df['time']=pd.to_datetime(df['time'])
df.index=df['time']
df= df.drop(['tweet','id','username'],axis=1)
bitcoin=df.groupby(by=[df.index.month,df.index.year]).agg('sum')


df=pd.read_json('./data/ethereum2020.json')
df['time']=pd.to_datetime(df['time'])
df.index=df['time']
df= df.drop(['tweet','id','username'],axis=1)
ethereum=df.groupby(by=[df.index.month,df.index.year]).agg('sum')

months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

'''
df= pd.DataFrame({'ethereum':list(ethereum['likes']),'bitcoin':list(bitcoin['likes'])},index=months)
df.plot(kind='line',title='Total number of likes/month  of top 40 tweets 2020 (Ethereum vs Bitcoin)')
plt.xlabel('month')
plt.ylabel('number of likes/month')
plt.show()
'''

df=pd.read_csv('./data/bitcoinP2020.csv')
df=df.drop(['Currency'],axis=1)
df['Date']=pd.to_datetime(df['Date'])
df.index=df['Date']
bitcoinP=df.groupby(by=[df.index.month,df.index.year]).mean()
print(bitcoinP)

df=pd.read_csv('./data/ethereumP2020.csv')
df=df.drop(['Currency'],axis=1)
df['Date']=pd.to_datetime(df['Date'])
df.index=df['Date']
ethereumP=df.groupby(by=[df.index.month,df.index.year]).mean()
print(ethereumP)

df= pd.DataFrame({'ethereum':list(ethereumP['Closing Price (USD)'][1:])},index=months)
df.plot(kind='line',title='Avg price/month in USD ethereum')
plt.xlabel('month')
plt.ylabel('avg price in USD')
plt.show()

df= pd.DataFrame({'bitcoin':list(bitcoinP['Closing Price (USD)'][1:])},index=months)
df.plot(kind='line',title='Avg price/month in USD bitcoin')
plt.xlabel('month')
plt.ylabel('avg price in USD')
plt.show()
