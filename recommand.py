import pandas as pd



def loan_cnt(df, bookdb):
    df_dict = df.to_dict()
    print(df_dict['title'].values())

    for index, title in enumerate(list(df_dict['title'].values())):
        books = bookdb[bookdb['title'] == title] # bookdb에서 제목이 같은 df추출
        books.sort_values(by='loan_cnt', ascending= False, inplace= True) # 내림차순정렬
        print(books[['loan_cnt']])
        df_dict['loan_cnt'][index] = books[:1]['loan_cnt'] # 정렬첫번째 대출량으로 df_dict 대출량 수정


    return pd.DataFrame(df_dict) # 다시 데이터프레임으로 만들어서 반환




def recommand( df, age):
    if age == '영유아(0~5)':
        recommand_df = df[df['age'] == age]
        recommand_df.sort_values(by="loan_cnt", axis=0, ascending= False, inplace= True, na_position= 'last')
    elif age == '유아(6~7)':
        recommand_df = df[df['age'] == age or df['age'] == '초등(8~13)']
        recommand_df.sort_values(by="loan_cnt", axis=0, ascending=False, inplace=True, na_position='last')
    elif age == '초등(8~13)':
        recommand_df = df[df['age'] == age]
        recommand_df.sort_values(by="loan_cnt", axis=0, ascending=False, inplace=True, na_position='last')
    elif age == '청소년(14~19)':
        recommand_df = df[df['age'] == age or df['age'] == '20대']
        recommand_df.sort_values(by="loan_cnt", axis=0, ascending=False, inplace=True, na_position='last')
    elif age == '20대' or age == '30대':
        recommand_df = df[df['age'] == '20대' or df['age'] == '30대' or df['age'] == '40대']
        recommand_df.sort_values(by="loan_cnt", axis=0, ascending=False, inplace=True, na_position='last')
    else:
        recommand_df = df[df['age'] == '50대' or df['age'] == '30대' or df['age'] == '40대' or df['age'] == '60대 이상']
        recommand_df.sort_values(by="loan_cnt", axis=0, ascending=False, inplace=True, na_position='last')

    return recommand_df