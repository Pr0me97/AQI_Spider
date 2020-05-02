# coding=utf-8
import requests
from bs4 import BeautifulSoup
import bs4
import time
import pymysql

def getHTMLText(url):
    try:
        r=requests.get(url,timeout=30)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        return ""

def saveMysql(alist,html,city):
    soup=BeautifulSoup(html,"html.parser")
    alist=soup.find_all('div','value') #爬取网页中标签为<div>且class='value'的存入alist
    db=pymysql.connect("yourDatabaseIp","username","passwd","databaseName")
    cursor=db.cursor()
    date=time.strftime("%Y-%m-%d", time.localtime())
    sql="insert into %s"%city+"AQI(date,\
         aqi,pm25,pm10,so2,no2,co,o3)\
         values('%s',%d,%d,%d,%d,%d,%.2f,%d)" %\
         (date,int(alist[0].string.strip()),int(alist[1].string.strip()),int(alist[2].string.strip()),
          int(alist[7].string.strip()),int(alist[4].string.strip()),float(alist[3].string.strip()),int(alist[5].string.strip()))
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    db.close()
        
def main():
    cityList=['shanghai','nanjing','nantong','hangzhou']
    for i in range(len(cityList)):
        ainfo=[]
        url='http://www.pm25.in/%s'%cityList[i]
        html=getHTMLText(url)
        saveMysql(ainfo,html,cityList[i])

main()
