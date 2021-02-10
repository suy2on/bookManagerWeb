from flask import Flask, render_template, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import urllib.request
from urllib.parse import urlencode, quote
import json
import ssl
import datetime
import requests

# 네이버 api사용을 위한 정보
client_id = "slXTgcZ7T9bocjBAKSFq"
client_secret = "n4tbFhbriV"

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookManager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
    title={1:' ', 2:' ', 3:' ', 4:' ', 5:' ', 6:' ', 7:' ', 8:' ', 9:' ', 10:' '}
    author={1:' ', 2:' ', 3:' ', 4:' ', 5:' ', 6:' ', 7:' ', 8:' ', 9:' ', 10:' '}
    img_url={1:' ', 2:' ', 3:' ', 4:' ', 5:' ', 6:' ', 7:' ', 8:' ', 9:' ', 10:' '}
    link={1:' ', 2:' ', 3:' ', 4:' ', 5:' ', 6:' ', 7:' ', 8:' ', 9:' ', 10:' '}
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
            title[i]=book['title']
            author[i]=book['authorList'][0]['name']

            title2 = urllib.parse.quote(title[i])
            author2 = urllib.parse.quote(author[i])
            url = "https://openapi.naver.com/v1/search/book_adv.json?d_titl=" + title2 + "&d_auth=" + author2  # json 결과
            request2 = urllib.request.Request(url)
            request2.add_header("X-Naver-Client-Id", client_id)
            request2.add_header("X-Naver-Client-Secret", client_secret)
            context = ssl._create_unverified_context()
            response = urllib.request.urlopen(request2, context=context)
            rescode = response.getcode()
            # 찾으면
            if (rescode == 200):
                response_body = response.read().decode('utf-8')
                result = json.loads(response_body)
                book = result['items'][0]
                imgurl = book['image']
                urllink = book['link']
                img_url[i]=imgurl
                link[i]=urllink
            # 못찾으면
            else:
                img_url[i]=' '
                link[i]=' '


            i = i+1
    return title, author, img_url, link


### 모델시작 ####
class User(db.Model):
    __table_name__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(20), nullable=False)
    userpw = db.Column(db.String(30), nullable=False)
    records = db.relationship('Record', backref='author')
    calendar = db.relationship('Calendar', backref='calendar')


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
    pw_receive = generate_password_hash(pw_receive)
    user = User(userid=id_receive, userpw=pw_receive)
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
    request2 = urllib.request.Request(url)
    request2.add_header("X-Naver-Client-Id", client_id)
    request2.add_header("X-Naver-Client-Secret", client_secret)
    context = ssl._create_unverified_context()
    response = urllib.request.urlopen(request2, context=context)
    rescode = response.getcode()
    # 찾으면
    if (rescode == 200):
        response_body = response.read().decode('utf-8')
        result = json.loads(response_body)
        addBook(result['items'][0])  ##addBook함수실행
        return jsonify({'result': 'success', 'msg': '책추가완료'})
    # 못찾으면
    else:
        print("Error Code:" + rescode)
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
    print('user id: ', userid, 'user: ', user)
    return render_template('looking.html', user=user)

# 베스트셀러 _ 클릭하면 장르별 책 나열하기
@app.route("/genre", methods=["POST"])
def bestseller_genre():
    genre_receive = request.form.get("genre")

    global novel; global essay; global business; global self; global children;
    global kids; global humanities; global life; global language; global history;

    genre_dict = {'novel': novel, 'essay': essay, 'business': business, 'self': self, 'children': children,
                  'kids': kids, 'humanities': humanities, 'life': life, 'language': language, 'history': history}

    url = genre_dict[request.form.get("genre")]
    title, author, img_url, link = weekBest(url) # 책제목 딕셔너리 반환
    return jsonify({'result': 'success', 'title': title, 'author': author, 'img_url': img_url, 'link': link})



if __name__ == "__main__":
    app.run(port=5000, debug=True)
