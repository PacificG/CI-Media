import streamlit as st  
import pandas as pd
import numpy as np
import re
import os
import base64
from openai.embeddings_utils import cosine_similarity
import cohere
import time 
from ast import literal_eval


api_key = st.secrets["api_key"]




st.set_page_config(layout="wide", page_title="SuperMind Design")

@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()




st.sidebar.write("#")

# def remove_stopwords(text):
#     word_tokens = text.split()
#     filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
#     return ' '.join(filtered_text)


# Add your cohere API key from www.cohere.com
co = cohere.ClientV2(api_key)
# stemmer = PorterStemmer()
def get_embedding(text):
      print('Getting embeddings: ', text)
      response = co.embed(texts=[text], model='embed-multilingual-light-v3.0', input_type="search_document", embedding_types=["float"])
      return response.embeddings.float_[0]
# def stem_words(text):
#     word_tokens = text.split()
#     stemmed_text = [stemmer.stem(word) for word in word_tokens]
#     return ' '.join(stemmed_text)

# st.sidebar.image('super.jpg',caption='Supermind Design',use_column_width=True)
@st.cache_data()
def clean_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1JvL9JWgxgR7QdWMqGWoadr6jsvwXKFLEvk9Cz-Ytg0M/edit?usp=sharing"
    url_1 = sheet_url.replace('/edit?usp=sharing', '/export?format=csv&gid=0')
    df = pd.read_csv(url_1, header=[0])
    df.fillna('', inplace=True)  # Replace NaN values with empty string
    df['text_details'] = ''
    if df['Author'] != '':
        df['text_details'] += 'Author: ' + df['Author'] + ','
    if df['Title'] != '':
        df['text_details'] += 'Title: ' + df['Title'] + ','
    if df['Subtitle'] != '':
        df['text_details'] += 'Subtitle: ' + df['Subtitle']
    def lmda(x):
        time.sleep(1)
        return get_embedding(x)
    df['embeddings'] = df['text_details'].apply(lmda)
    return df

def get_data():
    if not os.path.exists('data.csv'):
        db = clean_data()
        db.to_csv('data.csv', index=False)
    db = pd.read_csv('data.csv')
    db.fillna('', inplace=True)
    if len(db) == len(pd.read_csv("https://docs.google.com/spreadsheets/d/1JvL9JWgxgR7QdWMqGWoadr6jsvwXKFLEvk9Cz-Ytg0M/edit?usp=sharing".replace('/edit?usp=sharing', '/export?format=csv&gid=0'), header=[0])):
        print('No change in data')
        pass
    else:
        db = clean_data()
        db.to_csv('data.csv', index=False)
    return db
db = get_data()
st.header('CI Media Database output:')
# st.write(db)




def get_similar_docs(query,df, top_n=5):
    query_embedding = get_embedding(query)
    df["similarity"] = df.embeddings.apply(lambda x: cosine_similarity(literal_eval(str(x)), query_embedding))
    df_res = df.sort_values(by="similarity", ascending=False).head(top_n)
    return df_res 

col1, col2 = st.sidebar.columns(2)
# button = col1.button('Graph (Beta)')
# button2 = col2.button('View Table')
query = st.sidebar.text_input('Search Related Ideas', value='', key=None, type='default')
process = st.sidebar.multiselect('Author',list(set(db['Author'].dropna().to_list())))
module = st.sidebar.multiselect('Topic',['business', 'society', 'science', 'People', 'Process',
       'Technology', 'tags', 'Entities', 'Wave', 'Ivy'])

cols = module

dfhat = db
dfhat['Priority'] = dfhat['Priority'].apply(lambda x: 0 if isinstance(x, str) else x)
if query != '':
    dfhat = get_similar_docs(query, dfhat, top_n=10)
if query != '' or len(cols) != 0 or len(process) != 0:    
    if len(cols) != 0:
        for p in cols:
            dfhat[p] = dfhat[p].apply(lambda x: float(str(x).split('"')[-1]))
            dfhat = dfhat[dfhat[p].isin([1,2])]
    if query == '':

        dfhat.sort_values(by=cols + ['Priority'], ascending=False, inplace=True)
    if len(process) != 0:
        dfhat = dfhat[dfhat['Author'].isin(process)]
    if len(dfhat) == 0:
            st.write('No data found')
    for row in dfhat.iterrows():
        title = row[1]['Title']
        author = row[1]['Author']
        expander_title = title + (' : ' + author if author != '' else '')
        with st.expander(expander_title):
            names = [name for name, value in zip(['business', 'society', 'science', 'People', 'Process', 'Technology', 'tags', 'Entities', 'Wave', 'Ivy'], row[1][cols]) if int(value) == 1]
            st.write(row[1]['Subtitle'])
            st.link_button('Read More', row[1]['Website'])
        # dfhat.drop(columns=['Unnamed: 0'],inplace=True)
    dfhat.to_csv('db_download.csv', index=False)
    with open('db_download.csv', 'rb') as f:
        st.sidebar.download_button('Download filtered Data', f, file_name='db_download.csv', key=None, mime='text/csv')
    st.sidebar.write('Copyright © Supermind.design Creative Commons (share, adapt, credit) license')
        # st.sidebar.download_link(dfhat.to_csv('db_download.csv'))



            