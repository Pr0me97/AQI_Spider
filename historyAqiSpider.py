import requests
from bs4 import BeautifulSoup
import bs4
import xlrd
import xlwt
from xlutils.copy import copy
import os
import pymysql

def getHTMLText(url):
    try:
        r=requests.get(url,timeout=30)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        return ""

def fillAQIList(alist,html):
    soup=BeautifulSoup(html,"html.parser")
    for tr in soup.find('table').children:
        if isinstance(tr,bs4.element.Tag):
            tds=tr('td')
            alist.append([tds[0].string,tds[2].string,tds[4].string,
                          tds[5].string,tds[6].string,tds[7].string,
                          tds[8].string,tds[9].string])

def saveMysql(alist,city):
    db=pymysql.connect("databaseIp","username","passwd","databaseName")
    cursor=db.cursor()
    for i in range(len(alist)):
        if i==0:
            continue
        sql="insert into %s"%city+"AQI(date,\
             aqi,pm25,pm10,so2,no2,co,o3)\
             values('%s',%d,%d,%d,%d,%d,%.2f,%d)" %\
             (alist[i][0].strip(),int(alist[i][1]),int(alist[i][2]),int(alist[i][3]),
             int(alist[i][4]),int(alist[i][5]),float(alist[i][6]),int(alist[i][7]))
        print(sql)
        try:
            cursor.execute(sql)
            #提到数据库执行
            db.commit()
        except:
            #如果发生错误则回滚
            db.rollback()
    db.close()

    
def saveExcel(alist):
    file='.\AQI.xls'
    if os.path.exists(file):
        rb=xlrd.open_workbook(file)
        book=copy(rb)
        sheet_rows=rb.sheet_by_name('AQI汇总').nrows
        sheet1=book.get_sheet(0)
        for i in range(len(alist)):
            if i==0:
                continue
            for j in range(len(alist[i])):
                sheet1.write(i+sheet_rows-1,j,alist[i][j].strip())
        os.remove(file)
        book.save(file)
    else:
        book = xlwt.Workbook()
        sheet1=book.add_sheet("AQI汇总")
        sheet1=book.get_sheet(0)
        for i in range(len(alist)):
            if i==0:
                continue
            for j in range(len(alist[i])):
                sheet1.write(i-1,j,alist[i][j].strip())
        book.save(file)
        
def main():
    city="nantong"
    year=2014
    while year<=2020:
        month=1
        while month<=12:
            if year==2020 and month==4:
                break
            if month<10:
                month="0"+str(month)
            else:
                month=str(month)
            ainfo=[]
            url='http://www.tianqihoubao.com/aqi/%s'%city+'-%s'%year+month+'.html'
            print(url)
            html=getHTMLText(url)
            fillAQIList(ainfo, html)
            saveMysql(ainfo,city)
            month=int(month)+1
        year=year+1
    print("爬取数据完毕!!!")

main()
