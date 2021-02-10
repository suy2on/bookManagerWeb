import urllib.request
import json
import ssl

client_id = "slXTgcZ7T9bocjBAKSFq"
client_secret = "n4tbFhbriV"


def searchbook(url) :
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
        return result
    # 못찾으
    else:
        return 'error'