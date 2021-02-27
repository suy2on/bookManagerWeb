import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings; warnings.filterwarnings('ignore')

books = pd.read_csv('final.csv')
books[:1]
books_df = books.drop(['Unnamed: 0'],axis=1) # 필요없는 컬럼 제거


#장르들 string으로 변화
books_df['genre'] = books_df['genre'].apply(lambda x : str(x))
print(books_df.info())

#피처백터화
count_vect = CountVectorizer(min_df=0, ngram_range=(1,2))
genre_mat = count_vect.fit_transform(books_df['genre'])
print(genre_mat.shape)

#코사인유사도 추출
genre_sim = cosine_similarity(genre_mat, genre_mat)
print(genre_sim.shape)

#정렬
genre_sim_sorted_ind = genre_sim.argsort()[:, ::-1]
print(genre_sim_sorted_ind[:2])

#특정책과 유사한 책들 추천 함수
def find_sim_book(df, sorted_ind, title_name, top_n=5):
    title_book = df[df['title'] == title_name]

    title_index = title_book.index.values
    similar_indexes = sorted_ind[title_index, :top_n]

    print(similar_indexes)
    similar_indexes = similar_indexes.reshape(-1)

    return df.iloc[similar_indexes]

similar_books = find_sim_book(books_df, genre_sim_sorted_ind, '코로나 투자 전쟁 =전 세계 금융 역사 이래 최대의 유동성 /Money war ', 5)
print(similar_books[['title', 'genre','age']])

