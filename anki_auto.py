from venv import create
import requests;
from bs4 import BeautifulSoup
requests.packages.urllib3.disable_warnings()
import json
import pandas as pd
import time

username='favar54307@galotv.com'
password='ankitest'
session=requests.Session()

def connection(username,password):
    raw_r=session.get("https://ankiweb.net/account/login")
    r=BeautifulSoup(raw_r.text,'html.parser')
    csrf_token= r.find('input',{'name':'csrf_token'}).get('value')
    login = session.post('https://ankiweb.net/account/login', data={'submitted': 1,'csrf_token':csrf_token,'username':username,'password':password})
    return session.cookies.get_dict()['ankiweb']


def createDeck(nom):
    headers={'X-Requested-With': 'XMLHttpRequest'}
    raw_r=session.get("https://ankiweb.net/decks/create?name="+nom,headers=headers)
    if raw_r.status_code==200:
        print("Deck " + nom + " créé")

def addCard(deck,type,contentList,tags=""):
    raw_r=session.get("https://ankiuser.net/edit/",verify=False)
    if raw_r.status_code==429:
        print("trop de requêtes !!!")
        return
    time.sleep(0.4)
    csrf_token= raw_r.text.split("anki.Editor(")[1].split(",")[0][1:-1]
    raw_r=session.get("https://ankiuser.net/edit/getAddInfo",verify=False)
    if raw_r.status_code==429:
        print("trop de requêtes !!!")
    time.sleep(0.4)
    infos=json.loads(raw_r.text)
    if type=="Basic":
        mid=infos["notetypes"][0]["id"]
        deckid=[d for d in infos['decks'] if d['name']==deck]
        if len(deckid)==0:
            return "Ajout de cartes impossible"
        deckid=deckid[0]['id']
        data=[]
        data.append(contentList)
        data.append(tags)
        data=json.dumps(data)
        datas={"nid":"",'data':data,'csrf_token':csrf_token,'mid':mid,'deck':deckid}
        ajout=session.post("https://ankiuser.net/edit/save",verify=False,data=datas)
        if ajout.status_code==200:
            print( contentList[0] + " : " + contentList[1] + " ajouté dans " + deck)
        elif ajout.status_code==429:
            print("trop de requêtes !!!")
        else:
            print("Erreur d'ajout dans "+ deck)
            print(ajout.text)
        time.sleep(0.4)

def getListDecks():
    raw_r=session.get("https://ankiweb.net/decks/")
    r=BeautifulSoup(raw_r.text,'html.parser')
    return [e.get("data-full") for e in r.find_all('button',{"class":"btn-link","data-full":True})]

def addFromExcel(file):
    decks=getListDecks()
    questions = pd.read_excel(file)
    nbq= questions.shape[0]
    print(questions)
    for i in range(nbq):
        theme= questions._get_value(i,0,takeable=True).strip()
        if theme not in decks:
            createDeck(theme)
            time.sleep(0.4)
        card=[]
        card.append(questions._get_value(i,1,takeable=True))
        card.append(questions._get_value(i,2,takeable=True))
        
        addCard(theme,"Basic",card)

connection(username,password)
addFromExcel('608TRY.xlsx')






