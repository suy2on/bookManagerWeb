import requests
import urllib.request
from urllib.parse import urlencode
from searchBook import *



## 베스트셀러 장르별 url
novel = "https://book.naver.com/bestsell/home_bestseller_json.nhn?cp_cate=001001044&cp_name=yes24"
essay = "https://book.naver.com/bestsell/home_bestseller_json.nhn?cp_cate=001001045&cp_name=yes24"
business = "https://book.naver.com/bestsell/home_bestseller_json.nhn?cp_cate=001001025&cp_name=yes24"
self = "https://book.naver.com/bestsell/home_bestseller_json.nhn?cp_cate=001001026&cp_name=yes24"
children = "https://book.naver.com/bestsell/home_bestseller_json.nhn?cp_cate=001001016&cp_name=yes24"
kids = "https://book.naver.com/bestsell/home_bestseller_json.nhn?cp_cate=001001027&cp_name=yes24"
humanities = "https://book.naver.com/bestsell/home_bestseller_json.nhn?cp_cate=001001019&cp_name=yes24"
life = "https://book.naver.com/bestsell/home_bestseller_json.nhn?cp_cate=001001001&cp_name=yes24"
language = "https://book.naver.com/bestsell/home_bestseller_json.nhn?cp_cate=001001049&cp_name=yes24"
history = "https://book.naver.com/bestsell/home_bestseller_json.nhn?cp_cate=001001010&cp_name=yes24"

## 베스트셀러 크롤링 함수
def weekBest(url):
    title={}
    author={}
    img_url={}
    link={}
    isbns={}

    i=1
    custom_header = {
        'referer' : "https://book.naver.com/",
        'user-agent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36"
    }

    req = requests.get(url, headers = custom_header)

    if req.status_code == requests.codes.ok:
        print("접속 성공")
        book_data = json.loads(req.text)
        for book in book_data['result']:
            book['title']= book['title'].replace('&#40', "(")
            book['title'] = book['title'].replace('&#41', ")")
            book['title'] = book['title'].replace('&amp;amp;', "&")
            title[i]=book['title']
            author[i]=book['authorList'][0]['name']

            title2 = urllib.parse.quote(title[i])
            author2 = urllib.parse.quote(author[i])
            url = "https://openapi.naver.com/v1/search/book_adv.json?d_titl=" + title2 + "&d_auth=" + author2  # json 결과
            result = searchbook(url)

            if (result != 'error'):
                book = result['items'][0]
                imgurl = book['image']
                urllink = book['link']
                isbn = book['isbn'][-13:]
                img_url[i] = imgurl
                link[i] = urllink
                isbns[i] = isbn
            else:
                img_url[i]=' '
                link[i]=' '


            i = i+1
    return title, author, img_url, link, isbns