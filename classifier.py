import pandas as pd
import math

def get_count(query):
    return len(data.query(query)[label])


class_probablities = {}
prior_probablities={}

df = pd.read_csv('./data/train.csv')
label = 'Sentiment'
train_len = int(0.8*len(df[label]))
data= df.head(train_len)
total = train_len
test_len = int(0.2*len(df[label]))
test_data = df.tail(test_len)
class_labels=data[label].unique()


print(df.head())
print("\n\n")

#caclculate class probablities
for item in class_labels:
    class_probablities[item]=get_count(f'{label}=="{item}"')/total


print('class probablities', class_probablities,'\n\n')

for feature in data.columns:
    if feature not in ['Tweet','Sentiment']:
        feature_dict={}
        for item in data[feature].unique():
            item_dict={}
            for c in class_labels:
                query1=f'{label}=="{c}"'
                query2=f'({label}=="{c}") and ({feature}=="{item}")'
                item_dict[c]=math.log((1+get_count(query2))/(6+get_count(query1)))
            feature_dict[str(item)]=item_dict
        prior_probablities[feature]=feature_dict

print('prior_probablities',prior_probablities)

predictions=[]
correct=0


for index,row in test_data.iterrows():
    probs=None
    choice=None
    for c in class_labels:
        pci=math.log(class_probablities[c])
        for feature in test_data.columns:
            feature_value=row[feature]
            if feature not in ['Tweet','Sentiment']:
                pci+=prior_probablities[feature][feature_value][c]      
        
        if not probs:
            probs=pci
            choice=c
        else:
            if pci>probs:
                choice=c
                probs=pci
    predictions.append(choice)
    if row[label]==choice:
        correct+=1

print('\nAccuracy ',round(correct*100/test_len,2),'%')
