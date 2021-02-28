from flask import Flask, render_template, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import urllib.request
from urllib.parse import urlencode
import datetime
from bestSeller import *
from contentsFilter import *
import pandas as pd
import numpy as np

# 네이버 api사용을 위한 정보
client_id = "slXTgcZ7T9bocjBAKSFq"
client_secret = "n4tbFhbriV"

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



### 모델시작 ####
class User(db.Model):
    __table_name__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.String(15), nullable=False)
    userid = db.Column(db.String(20), nullable=False)
    userpw = db.Column(db.String(30), nullable=False)
    records = db.relationship('Record', backref='author')
    calendar = db.relationship('Calendar', backref='calendar')
    wishlist = db.relationship('Wishlist', backref='wishlist')


class Record(db.Model):
    __table_name__ = 'record'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    ISBN = db.Column(db.String(30), nullable=False)
    sub = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String, nullable=False)
    writer = db.Column(db.String, nullable=False)
    author_id = db.Column(db.String(20), db.ForeignKey('user.id'))
    summary = db.Column(db.String(2000), nullable=True)
    comments = db.relationship('Comment', backref='book')


class Comment(db.Model):
    __table_name__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(140), nullable=False)
    book_id = db.Column(db.String(10), db.ForeignKey('record.id'))


class Calendar(db.Model):
    __table_name__ = 'calendar'

    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.String(20), db.ForeignKey('user.id'))

class Wishlist(db.Model):
    __table_name__ = 'wishlist'

    id = db.Column(db.Integer, primary_key=True)
    ISBN = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    img_url = db.Column(db.String, nullable=False)
    writer = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String(20), db.ForeignKey('user.id'))

db.create_all()

### 모델끝 ###


## 책추함수
def addBook(book):
    print(book)
    userid = session.get('userid', None)
    author = User.query.filter_by(userid=userid).first()
    title = book['title']
    img = book['image']
    writer = book['author']
    ISBN = book['isbn']

    # <b> </b> 삭제
    title = title.replace('<b>', '')
    title = title.replace('</b>', '')
    writer = writer.replace('<b>', '')
    writer = writer.replace('</b>', '')

    record = Record(title=title, img_url=img, sub='', writer=writer, ISBN=ISBN, author=author)
    db.session.add(record)
    db.session.commit()

#해당사용자의 isbn리스트
def isbnlist():
    userid = session.get('userid', None)
    user = User.query.filter(User.userid == userid).first()
    likelists = user.wishlist  # user의 wish객체들의 리스트 반
    isbns = []
    for likelist in likelists:
        isbns.append(likelist.ISBN)
    return isbns


## 로그인
@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    else:
        id = request.form['id_give']
        pw = request.form['pw_give']
        user = User.query.filter_by(userid=id).first()
        if user == None:  # 아이디 존재여부
            return jsonify({'result': 'fail', 'msg': '없은 아이디입니다.'})
        realpw = user.userpw
        if check_password_hash(realpw, pw):  # 비밀번호 일치여부
            session['userid'] = user.userid  # session에 저장
            return jsonify({'result': 'success', 'msg': '로그인 성공'})
        else:
            return jsonify({'result': 'fail', 'msg': '아이디와 비밀번호가 일치하지않습니다'})


## 회원가입
@app.route("/join", methods=['GET', 'POST'])
def join():
    if request.method == 'GET':
        return render_template('join.html')
    else:
        id = request.form['id']
        pw = request.form['pw']
        pw = generate_password_hash(pw)
        user = User(userid=id, userpw=pw)
        db.session.add(user)
        db.session.commit()
        return jsonify({'msg': '회원가입 성공'})



# 홈화면
@app.route("/home")
def home():
    user = session.get('userid', None)
    events = Calendar.query.filter(Calendar.user_id == user).all()
    # 이거 문자열로 보내는데 받을 때 숫자로 받아 03/02 로 보내면 저거 나눠서 1.5로 표시되더라 이거 좀 형변환을 만져주거나 저렇게 나처럼 3.4이렇게 날짜 표시해야할듯
    times = ['35', '55', '44', '22', '0', '22', '30']
    dates = ['3.10', '3.2', '3.0', '3.4', '3.5', '3.6', '3.7']

    today = datetime.date.today()
    for i in range(7):
        today += datetime.timedelta(-1)
        today.strftime('%Y-%m-%d')
        date = str(today)  ## date 의 type 은 str
        dates[6 - i] = date[5:7] + '.' + date[8:]
        dates[6-i] = float(dates[6-i])
        dates[6-i] = format(dates[6-i], ".2f") #이거 30일 처럼 끝이 0인게 그래프에서 0이 출력이 안되어서
        # 내가 format으로 소수점 형식 지정했는데 서버에선 제대로 출력되도 저 망할 그래프가 인식을 안해줌
        # 저 그래프 자체가 뒤에있는 0을 없애버림ㅋㅋㅋㅋ흐앙

        #DB에서 date에 해당하는 time 가져오기 >> userid 와 date 의 값 두개가 모두 필요
        _times = Calendar.query.filter(Calendar.user_id == user).filter(Calendar.date == date).all()
        len_time = len(_times)
        if len_time==0: #시간 기록이 없으면 > 0분 기록
            times[6-i]=0
        elif len_time==1:
            times[6-i]=_times[0].time
        else: # 읽은 책의 개수가 여러권일때 > 시간 모두 더하기
            n=0
            for k in range(len_time):
                n = n + int(_times[k].time)
            times[6-i]=n
    print('dates: ', dates)
    print('times: ', times) # dates랑 times 모두 잘 가져오는거 확인완료
    return render_template('home.html', user=user, events = events, dates = dates, times = times)


# 아이디 중복확인
@app.route('/check1', methods=["post"])
def check1():
    _id = request.form['give_id']
    same_users = User.query.filter(User.userid == _id).first()
    print(same_users)

    if same_users == None:
        return jsonify({'result': 'success', 'msg': '사용가능한 아이디입니다.'})
    else:
        return jsonify({'result': 'failure', 'msg': '이미 사용중인 아이디입니다.'})


# 회원가입 완료시
@app.route('/form_submit', methods=["post"])
def form_submit():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    age_receive = request.form['age_give']
    pw_receive = generate_password_hash(pw_receive) #암호화
    user = User(userid=id_receive, userpw=pw_receive, age= age_receive)
    db.session.add(user)
    db.session.commit()
    return jsonify({'result': 'success', 'msg': '회원가입 성공'})


# 나의 서재 페이지
@app.route("/mylibrary", methods={'GET', 'POST'})
def mylibrary():
    if request.method == 'GET':
        user = session.get('userid', None)
        _user = User.query.filter(User.userid == user).first()
        print(_user)
        user_idnum = _user.id
        records = Record.query.filter(Record.author_id == user_idnum).all()
        return render_template('mylibrary.html', user=user, records=records)


## 읽은 책추가
@app.route("/search", methods=['POST'])
def searchBook():
    title = request.form['title_give']
    publ = request.form['pub_give']
    title = urllib.parse.quote(title)
    publ = urllib.parse.quote(publ)
    url = "https://openapi.naver.com/v1/search/book_adv.json?d_titl=" + title + "&d_publ=" + publ  # json 결과
    result = searchbook(url)
    # 찾으면
    if (result != 'error'):
        addBook(result['items'][0])  ##addBook함수실행
        return jsonify({'result': 'success', 'msg': '책추가완료'})
    # 못찾으면
    else:
        print('검색중오류')
        return jsonify({'result': 'fail', 'msg': '검색중에 오류가 났습니다'})


## viewbook
@app.route("/update", methods=["POST", "GET"])
def update():
    if request.method == 'POST':
        record_id = request.form.get(("record_id"))
        record = Record.query.filter_by(id=record_id).first()
        session['record_id'] = record.id  ## 여기서 record_id를 session에 저
        # print(type(record))
        comments = record.comments
        return render_template('viewbook.html', record=record, comments=comments)
    else:
        record_id = session.get('record_id', None)
        record = Record.query.filter_by(id=record_id).first()
        comments = record.comments
        return render_template('viewbook.html', record=record, comments=comments)


## 책 삭제하기
@app.route("/deletebook", methods=["POST"])
def deletebook():
    record_id = request.form.get(("record_id"))
    record = Record.query.filter_by(id=record_id).first()
    comments = record.comments  # 해당 record의 comments들 다 가져오기
    for comment in comments:
        print(comment)
        db.session.delete(comment)
        db.session.commit()  # 그 책에 해당하는 comment 다 삭제

    db.session.delete(record)
    db.session.commit()  # 책 카드 삭제

    return redirect('/mylibrary')


## comment 작성하기
@app.route("/makeComment", methods={"POST"})
def makeComment():
    page_receive = request.form.get("page_give")
    comment_receive = request.form.get("comment_give")
    record_id = session.get('record_id', None)
    comment = Comment(page=page_receive, content=comment_receive, book_id=record_id)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'result': 'success'})


## comment_page수정
@app.route("/update_page", methods=["POST"])
def update_page():
    newpage = request.form.get("newpage")
    commentid = request.form.get("commentid")
    comment = Comment.query.filter(Comment.id == commentid).first()
    comment.page = newpage
    db.session.commit()
    return redirect('/update')


## comment_content 수정
@app.route("/update_content", methods=["POST"])
def update_content():
    newcontent = request.form.get("newcontent")
    commentid = request.form.get("commentid")
    comment = Comment.query.filter(Comment.id == commentid).first()
    comment.content = newcontent
    db.session.commit()
    return redirect('/update')


## comment delete 하기
@app.route("/delete_comment", methods=["POST"])
def delete_comment():
    comment_id = request.form.get("commentid")
    comment = Comment.query.filter(Comment.id == comment_id).first()
    db.session.delete(comment)
    db.session.commit()
    return redirect('/update')


## summary 독후감
@app.route("/update_summary", methods=["POST"])
def update_summary():
    newsummary = request.form.get("newsummary")
    record_id = session.get('record_id', None)
    record = Record.query.filter_by(id=record_id).first()
    record.summary = newsummary
    db.session.commit()
    return redirect('/update')

## calendar
@app.route("/calendar", methods=["POST"])
def calendar():
    user = session.get('userid', None)
    book_receive = request.form.get("book_give")
    date_receive = request.form.get("date_give")
    time_receive = request.form.get("time_give")
    calendar = Calendar(book=book_receive, date=date_receive, time=time_receive, user_id=user)
    db.session.add(calendar)
    db.session.commit()
    return jsonify({'result': 'success' , 'msg': '추가완료'})

# 둘러보기 페이지
@app.route("/looking", methods=["GET"])
def looking():
    userid = session.get('userid', None)
    user = User.query.filter(User.userid == userid).first()
    isbns = isbnlist();
    print(isbns) # isbns 는 사용user가 좋아요 누른 모든 책들의 isbn 목록들
    return render_template('looking.html', user=user, isbnlist=isbns)

# 책 추천
@app.route("/looking2", methods=["GET"])
def looking2():
    userid = session.get('userid', None)
    user = User.query.filter(User.userid == userid).first()
    isbns = isbnlist();
    print(isbns)
    print(type(isbns))
    if isbns == []: # 위시북이 한권도 없는 경우
        return jsonify({'result': 'nobook'})
    else: # 위시북이 하나라도 있는 경우
        ## 책이 있나 없나 확인 > final.csv에서 확인
        ### 있다 > 책 title이 한개인지 중복인지 확인 > bookdb.csv에서 확인
        #### 책 title이 한개임 > ok
        #### 책 title이 중복임 > bookdb.csv에서 중복책들의 대출권수 합해서 final.csv의 대출권수를 대신하기
        ### 없다 > 구글api 로 final.csv에 책 추가하기 > ok
        for isbn in isbns:
            final_df = pd.read_csv('final.csv')
            finalbook = final_df[final_df['isbn13'] == int(isbn)]
            bookdb_df = pd.read_csv('bookdb.csv')
            bookdb_df = bookdb_df.drop_duplicates(['title'], keep = 'first')
            bookdbbook = bookdb_df[bookdb_df['isbn13'] == int(isbn)]
            if finalbook is not None: # 책(한권)이 북db에 있는 경우
                book_title = (finalbook['title'].values)[0]
                book_index = (finalbook['title'].index.values)[0]
                booklist = []
                similar_books = find_sim_book(final_df, genre_sim_sorted_ind, book_title, 5)
                print(similar_books[['title', 'genre','age']])
                #booklist.append(similar_books)
            else: # 책(한권)이  북db에 없는 경우 > 구글 api로 final.csv에 책 추가하기
                print("!")
        return jsonify({'result': 'yesbook'})


# 베스트셀러 _ 클릭하면 장르별 책 나열하기
@app.route("/genre", methods=["POST"])
def bestseller_genre():
    genre_receive = request.form.get("genre")
    genre_dict = {'novel': novel, 'essay': essay, 'business': business, 'self': self, 'children': children,
                  'kids': kids, 'humanities': humanities, 'life': life, 'language': language, 'history': history}

    url = genre_dict[genre_receive]
    title, author, img_url, link, isbn = weekBest(url) # 책제목 딕셔너리 반환
    return jsonify({'result': 'success', 'title': title, 'author': author, 'img_url': img_url, 'link': link, 'isbn': isbn})

# 좋아요 누르기 기능 구현
@app.route("/heart1", methods=["POST"])
def clicklike():
    userid = session.get('userid', None)
    user = User.query.filter(User.userid == userid).first()
    userid =user.id
    title = request.form.get("title")
    author = request.form.get("author")
    img_url = request.form.get("img_url")
    isbn = request.form.get("isbn")
    print(userid, isbn)

    like = Wishlist(ISBN=isbn, title=title, img_url=img_url, writer=author, user_id=userid)
    db.session.add(like)
    db.session.commit()
    return jsonify({'result': 'success'})

# 좋아요 취소 기능 구현
@app.route("/heart2", methods=["POST"])
def heart2():
    userid = session.get('userid', None)
    user = User.query.filter(User.userid == userid).first()
    userid = user.id
    isbn = request.form.get("isbn")
    print(userid, isbn)

    record = Wishlist.query.filter(Wishlist.user_id == userid).filter(Wishlist.ISBN == isbn).first()
    db.session.delete(record)
    db.session.commit()
    return jsonify({'result': 'success'})

@app.route('/search_page1', methods=['POST'])
def search_page1():
    query1= request.form.get('query')
    session['query']= query1 # session에 검색어 저장
    query = urllib.parse.quote(query1)
    url = "https://openapi.naver.com/v1/search/book.json?query=" + query + "&display=10&start=1" # json 결과
    result = searchbook(url)
    pages = int(result['total']/10) + 1 #페이지수
    pagelist = []

    for i in range(pages):
        pagelist.append(i+1)
    session['pagelist']=pagelist
    items = result['items']
    print(items)
    isbns = isbnlist(); #사용자의 isbn list

    return render_template("search.html", items = items, pagelist = pagelist, query=query1, isbnlist = isbns)

@app.route('/search_page2', methods=['POST'])
def search_page2():
    page = int(request.form.get('pagenum')) #현재페이지
    start = str((page - 1) * 10 + 1)
    query1 = session.get('query', None)
    query = urllib.parse.quote(query1)
    url = "https://openapi.naver.com/v1/search/book.json?query=" + query + "&display=10&start=" + start  # json 결과
    result = searchbook(url)
    items = result['items']
    items = items[:10]
    pagelist = session.get('pagelist', None)
    return render_template("search.html", items=items, pagelist=pagelist, query = query1)


#나의 서재 > 나의 위시북페이지로 이동
@app.route("/wishbook", methods={'GET', 'POST'})
def wishbook():
    if request.method == 'GET':
        user = session.get('userid', None)
        _user = User.query.filter(User.userid == user).first()
        print(_user)
        user_idnum = _user.id
        wishbooks = Wishlist.query.filter(Wishlist.user_id == user_idnum).all()
        print(wishbooks)

        isbns = isbnlist();
        print(isbns)
        return render_template('wishbook.html', user=user, items=wishbooks, isbns=isbns)


##########책 추천##########
#위시북 리스트에 위시북이 있는지 확인




if __name__ == "__main__":
    app.run(port=5000, debug=True)
