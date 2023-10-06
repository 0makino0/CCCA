import requests
from bs4 import BeautifulSoup
import re
import json
 
url = ["https://anime.eiga.com/program/season/2023/",
       "https://anime.eiga.com/program/season/2022/",
       "https://anime.eiga.com/program/season/2021/",
       "https://anime.eiga.com/program/season/2020/",
       "https://anime.eiga.com/program/season/2019/"
       ]
all_href = []
 #Responseオブジェクト作成
for urls in url:
     
    response = requests.get(urls)
    #文字化け対策
    response.encoding = response.apparent_encoding
    #BeautifulSoupオブジェクト作成
    soup = BeautifulSoup(response.text, "html.parser")
    #<dl>の中に<a>があるので，先に<dl>を解析することにより，関係の無い<a>を除外できるはず．
    #class_は予約語でclassが存在するから，アンダーバーをつけるの忘れる事なかれ
    anime = soup.find_all("dl",class_="seasonAnimeDetail")

    #animeはResultSetオブジェクトなので，その中の要素に対して，find_all('a')を適用
    a = [x.find_all('a') for x in anime]
    #href，つまり，URL情報を取得
    hrefs = [x['href'] for anime_a in a for x in anime_a]

   # 重複を排除してall_hrefに追加
    all_href.extend(set(hrefs)) 

all_href = set(all_href)
all_href = list(all_href)

#dict作成．ここに声優とキャラの対応データを入れる予定
character_dict = {}



#声優出演歴から，キャラを抽出

for syutuen_href in all_href:    
    URL2 ='https://anime.eiga.com' + syutuen_href + 'program/' 
    
    #キャラを格納するリスト
    href_chara = []
    #（）排除した方
    href_chara2 = []
    #アニメタイトルを格納するリスト
    href_title = []
    response = requests.get(URL2)
    #文字化け対策
    response.encoding = response.apparent_encoding
    #BeautifulSoupオブジェクト作成
    soup = BeautifulSoup(response.text, "html.parser")
    #divのなかのclass = tabPersonWrap02の中に出演歴がある
    syutuen = soup.find_all('div',class_ = "tabPersonWrap02")
    
    for each_syutuen in syutuen:
        for each_chara in each_syutuen.find_all("li"):
            #titleにaタグの中身だけを格納
         title = each_chara.find('a').extract()
         #each_charaにはaタグが入っていない
         chara = each_chara
         #それぞれ加えている
         href_chara.append(chara.text)
         href_title.append(title.text)
    
    #キャラの（）を除外
    for chara in href_chara:
            chara_without = re.sub('[（）]','',chara)
            href_chara2.append(chara_without)
    #keyにする名前を取得
    name = soup.find('div',class_ = "path")
    seiyuu_names = name.find_all('a',href=syutuen_href)
    #要素の数をチェックする.タイトルとキャラの数が一致しない場合，強制終了
    if len(href_title) != len(href_chara2):
        print("要素数が一致しません")
        break
    
    for names in seiyuu_names:
        name_text = names.text
        
        character_dict[name_text] = (href_title,href_chara2)
#テストとして，山寺宏一の要素と声優数，アニメとキャラの総数を出す
print(character_dict["山寺 宏一"])
print("声優数：",len(all_href))

with open("C:\CCCA\ccca_python\python\seiyuu.json",mode="wt",encoding="utf-8")as f:
    json.dump(character_dict,f,ensure_ascii=False, indent=2)