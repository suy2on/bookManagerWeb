import pandas as pd



def loan_cnt(df, bookdb):
    df_dict = df.to_dict()
    keys = list(df_dict['title'].keys()) #index값들 리스트

    for index, title in enumerate(list(df_dict['title'].values())):
        books = bookdb[bookdb['title'] == title] # bookdb에서 제목이 같은 df추출
        books.sort_values(by='loan_cnt', ascending= False, inplace= True) # 내림차순정렬
        books = books[:1].values.tolist() # 값으로 추출
        df_dict['loan_cnt'][keys[index]] = books[0][4]# 정렬첫번째 대출량으로 df_dict 대출량 수정

    return pd.DataFrame(df_dict) # 다시 데이터프레임으로 만들어서 반환




def recommand( df, age):
    print(age)
    if age == '영유아(0~5)':
        recommand = df[df['age'] == age]
        recommand.sort_values(by="loan_cnt", axis=0, ascending= False, inplace= True, na_position= 'last')
    elif age == '유아(6~7)':
        recommand = df[ (df['age'] == age)  | (df['age'] == '초등(8~13)')]
        recommand.sort_values(by="loan_cnt", axis=0, ascending=False, inplace=True, na_position='last')
    elif age == '초등(8~13)':
        recommand = df[df['age'] == age]
        recommand.sort_values(by="loan_cnt", axis=0, ascending=False, inplace=True, na_position='last')
    elif age == '청소년(14~19)':
        recommand = df[ (df['age'] == age) | (df['age'] == '20대')]
        recommand.sort_values(by="loan_cnt", axis=0, ascending=False, inplace=True, na_position='last')
    else:
        recommand = df[ ~(df['age'] == '영유아(0~5)') & ~(df['age'] == '유아(6~7)') & ~(df['age'] == '초등(8~13)') & ~(df['age'] == '청소년(14~19)')]
        print(recommand)
        recommand.sort_values(by="loan_cnt", axis=0, ascending=False, inplace=True, na_position='last')

    return recommand