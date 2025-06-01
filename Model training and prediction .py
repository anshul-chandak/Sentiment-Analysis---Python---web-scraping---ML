#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd 
import re
from nltk.tokenize import word_tokenize
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
stopwords = set(stopwords.words('english'))


# In[3]:


train = pd.read_csv("IMDB Dataset.csv")
train.head()


# In[4]:


train.info


# In[5]:


train.describe()


# In[6]:


no_of_duplicates = train.duplicated().sum()
print("Number of Duplicates : ", no_of_duplicates)
print("Dataframe shape:", train.shape)


# In[7]:


train = train.drop_duplicates()
print("Dataframe shape after duplicates removed:", train.shape)
train.describe()


# In[8]:


for i in range (5):
    print()
    print ("Review:\n",train["review"].iloc[i])
    print ("sentiment:\n",train["sentiment"].iloc[i])


# In[9]:


def word_count(text):
    words = text.split()
    no_of_words = len(words)
    return no_of_words


# In[10]:


train['word_count'] = train['review'].apply(word_count)
train.head()


# In[11]:


def data_processing(text):
    text = text.lower()
    text = re.sub('<br />','',text)
    text = re.sub(r"https\S+|www\S+|http\S+",'',text,flags = re.MULTILINE)
    text = re.sub(r'\@w+|\#','',text)
    text = re.sub(r'[^\w\s]','',text)
    text_tokens = word_tokenize(text)
    filtered_text = [w for w in text_tokens if not w in stopwords]
    return  " ".join(filtered_text)
    
    


# In[12]:


train['processed_review'] = train['review'].apply(data_processing)


# In[13]:


train.head()


# In[14]:


stemmer = PorterStemmer()
def stemming(data):
    text_tokens = word_tokenize(data)
    text = [stemmer.stem(word) for word in text_tokens]
    return " ".join(text)


# In[15]:


train['stemmed_review'] = train['processed_review'].apply(stemming)
train.head()


# In[16]:


train['word_count_post_stemming'] = train['stemmed_review'].apply(word_count)
train.head()


# In[17]:


train["sentiment"].replace('positive', 1, inplace = True)
train["sentiment"].replace('negative', 0, inplace = True)


# In[18]:


train.head()


# In[19]:


train.to_csv("train_processed_data.csv", sep=',', index=True, header=True)
train['sentiment'].value_counts()


# In[20]:


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report


# In[21]:


df = pd.read_csv("train_processed_data.csv")


# In[22]:


X_train, X_test, y_train, y_test = train_test_split(df['stemmed_review'], df['sentiment'], test_size=0.2, random_state=42)


# In[23]:


tfidf = TfidfVectorizer(min_df=15,max_features=50000,ngram_range=(1,3))

X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)


# In[ ]:





# In[24]:


X_train_tfidf


# In[25]:


X_test_tfidf


# In[26]:


tfidf.get_feature_names_out().shape


# In[ ]:





# In[27]:


nb_model = MultinomialNB()

# Train the model
nb_model.fit(X_train_tfidf, y_train)

# Make predictions
y_pred = nb_model.predict(X_test_tfidf)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy * 100:.2f}%')

# Print classification report (precision, recall, F1-score)
print(classification_report(y_test, y_pred))


# # Applying the trained model to scraped reviews
# 

# In[28]:


df_raw_review = pd.read_excel("movie_reviews.xlsx") 


# In[29]:


df_raw_review.head()


# In[30]:


df_raw_review['word_count'] = df_raw_review['review'].apply(word_count)
df_raw_review.head()


# In[31]:


df_raw_review['processed_review'] = df_raw_review['review'].apply(data_processing)
df_raw_review.head()


# In[32]:


df_raw_review['stemmed_review'] = df_raw_review['processed_review'].apply(stemming)
df_raw_review.head()


# In[33]:


df_raw_review['word_count_post_stemming'] = df_raw_review['stemmed_review'].apply(word_count)
df_raw_review.head()


# In[34]:


df_raw_review.to_csv("scraped_review_processed.csv", sep=',', index=True, header=True)


# In[35]:


df2 = pd.read_csv("scraped_review_processed.csv")


# In[36]:


df_raw_review.nunique()


# In[37]:


X = df2["stemmed_review"]
X.shape


# In[38]:


X_tfidf = tfidf.transform(X)


# In[39]:


y_pred = nb_model.predict(X_tfidf)
y_pred.shape


# In[40]:


df_raw_review['Predicted_sentiment'] = y_pred


# In[41]:


df_raw_review.head()


# In[42]:


df_raw_review.to_csv("Raw_review_pred_sentiment.csv")


# In[43]:


df_raw_review["Movie_id"].value_counts()


# In[44]:


sentiment_score = df_raw_review.groupby("Movie_id")["Predicted_sentiment"].sum().reset_index()


# In[45]:


sentiment_score.columns = ["Movie_id","Sentiment_score"]
sentiment_score.head()


# In[46]:


movies_metadata = pd.read_excel("movies_meatadata.xlsx")
movies_metadata.head()


# In[48]:


movies_metadata.merge(sentiment_score,how= 'left', on='Movie_id')

