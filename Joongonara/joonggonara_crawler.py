# -*- coding: UTF-8 -*-

from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import sqlite3
import re

conn = sqlite3.connect("fraud_report.db")
cursor = conn.cursor()

cursor.execute(
    "Create Table if not exists fraud_report(report_num varchar2(12), report_title varchar2(20), report_article varchar2(50),"
    " fraud_num varchar2(12), fraud_title varchar2(20), fraud_id varchar2(20), price number, fraud_article varchar2(50))")



#########################################################
# 로그인
def login(driver):

    driver.get("http://www.naver.com")

    driver.find_element_by_class_name("bl_btn").click()

    time.sleep(5)

    elem = driver.find_element_by_id("id")
    elem.send_keys("USERID")
    elem = driver.find_element_by_id("pw")
    elem.send_keys("USERPW")
    elem.submit()

    time.sleep(5)
#########################################################


########################################################
# #각 신고게시글 주소를 가져오는 과정
def get_report_address(driver):

    aaa = driver.find_elements_by_class_name("m-tcol-c")
    index = 0
    address_list = []

    while (index < len(aaa)):
        hre = driver.find_elements_by_class_name("m-tcol-c")[index]
        if (hre.get_attribute("class") == "m-tcol-c list-count"):  # m-tcol-c list-count : article number
            list_url = hre.text
            if not hre == "":
                address_list.append("http://cafe.naver.com/joonggonara/" + list_url)
        index += 1

    print(address_list)  # 게시글 주소 리스트
    return address_list
########################################################


########################################################################
# 각 신고게시글로 들어가서 그 게시글이 신고한 불량글 링크를 가져옴
def get_fraud_address(driver, address_list):

    # source_page = []
    # original_article_list = []

    for address in address_list:
        driver.switch_to.default_content()
        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
        driver.get(address)
        driver.switch_to.frame(driver.find_element_by_id('cafe_main'))
        # craw_report(driver.page_source)
        report_address = report_article_crawl(driver, address)

        count = 0
        if(report_address != 0):
            try:
                article = driver.find_element_by_id("tbody")
                article_link = article.find_elements_by_tag_name("a")
                while (count < len(article_link)):
                    if ('http://cafe.naver.com/joonggonara/' in article_link[count].text
                        and article_link[count].text != 'http://cafe.naver.com/joonggonara/282825392'):
                        fraud_address = article_link[count].text
                        crawl_fraud_article(driver, fraud_address, report_address)
                    count += 1
            except:
                print("양식을 지키지 않은 글이다.")
                pass
            print("OK")
            driver.find_element_by_tag_name("body").send_keys(Keys.CONTROL + 'w')

    cursor.execute('''Delete from fraud_report where fraud_num is null''')
    conn.commit()

    print("Finish All Data")
##########################################################################


#########################################################################
#신고글도 가져옴
def report_article_crawl(driver, address):
    try:
        index=0
        row=None
        file_name = address[34:]
        cursor.execute('''Select exists (select * from fraud_report where report_num = "'''+file_name+'''");''')
        for row in cursor:
            print(row)

        if not row[0]:

            article_text=""

            cursor.execute('''Insert into fraud_report(report_num) values("''' + file_name + '''");''')
            title_box = driver.find_element_by_class_name("tit-box")
            title = title_box.find_elements_by_tag_name("span")
            while (index < len(title)):
                if (title[index].get_attribute("class") == "b m-tcol-c"):
                    title_text = title[index].text
                    cursor.execute('''Update fraud_report set report_title = "'''+title_text+'''" where report_num = "'''+file_name+'''"''')
                index += 1
            index = 0

            article_body = driver.find_element_by_id("tbody")

            article_div = article_body.find_elements_by_tag_name("div")
            if article_div == []:
                article_div = article_body.find_elements_by_tag_name("p")

            while (index < len(article_div)):
                article_text = article_text + article_div[index].text

                cursor.execute(
                    '''Update fraud_report set report_article = "''' + article_text + '''" where report_num = "''' + file_name + '''"''')
                index += 1

            #cursor.execute('''Insert into fraud_report(report_num, report_title, report_article) values("''' + file_name + '''"," '''+ title_text + '''","''' + article_text + '''");''')
            conn.commit()
            return file_name
        else:
            print("이미 읽은 게시글이다.")
            return 0

    except Exception as e:
        print(e)
        return 0
#######################################################################


#######################################################################
# 불량글 수집
def crawl_fraud_article(driver, fraud_address, report_num):

    index = 0

    #for orginal_link in fraud_address:
    driver.switch_to.default_content()
    if ('http://cafe.naver.com/joonggonara/' in fraud_address):
        file_name = fraud_address[34:]

        driver.get(fraud_address)
        try:
            driver.switch_to.alert.accept()
            exit(0)
        except:
            pass
        try:
            # 불량글 제목
            cursor.execute(
                '''Update fraud_report set fraud_num = "''' + file_name + '''"where report_num = "''' + report_num + '''"''')
            driver.switch_to.frame(driver.find_element_by_id('cafe_main'))
            title_box = driver.find_element_by_class_name("tit-box")
            title = title_box.find_elements_by_tag_name("span")
            while (index < len(title)):
                if (title[index].get_attribute("class") == "b m-tcol-c"):
                    title_text = title[index].text
                    cursor.execute(
                        '''Update fraud_report set fraud_title = "''' + title_text + '''"where report_num = "''' + report_num + '''"''')
                index += 1

            # 불량글 작성자
            index = 0
            etc_box = driver.find_element_by_class_name("etc-box")
            fraud_id = etc_box.find_elements_by_tag_name("a")
            while (index < len(fraud_id)):
                if (fraud_id[index].get_attribute("class") == "m-tcol-c b"):
                    id_text = fraud_id[index].text
                    cursor.execute(
                        '''Update fraud_report set fraud_id = "''' + id_text + '''"where report_num = "''' + report_num + '''"''')
                index += 1

            # 불량글 아이템 가격
            index = 0
            item_detail = driver.find_element_by_class_name("details-m")
            item_price = item_detail.find_elements_by_tag_name("td")
            while (index < len(item_price)):
                if (item_price[index].get_attribute("class") == "price border-sub"):
                    price_text = item_price[index].text
                    price_text = re.sub('[^0-9]','',price_text)
                    cursor.execute(
                        '''Update fraud_report set price = "''' + price_text + '''"where report_num = "''' + report_num + '''"''')
                index += 1

            # 불량글 내용
            index = 0
            fraud_article_all = driver.find_element_by_id("tbody")
            fraud_article = fraud_article_all.find_elements_by_tag_name("p")
            while (index < len(fraud_article)):
                class_name = fraud_article[index].get_attribute("class")
                if (class_name == ''):
                    article_text = fraud_article[index].text
                    cursor.execute(
                        '''Update fraud_report set fraud_article = "''' + article_text + '''"where report_num = "''' + report_num + '''"''')
                index += 1

            conn.commit()


        except Exception as e:
            print(e)
            print("양식을 지키지 않은 글이다.")
            exit(0)
        finally:
            print("complete : " + fraud_address)
            print("")
    else:
        print("이미 읽은 불량글이다.")

############################################################################


################################################################
# Main
def main():
    driver = webdriver.Firefox()
    # 파이어폭스 씁니다

    login(driver)

    # 불량글 신고게시판으로 이동
    driver.get(
        "http://cafe.naver.com/joonggonara.cafe?iframe_url=/ArticleList.nhn%3Fsearch.clubid=10050146%26search.menuid=168%26search.boardtype=L")

    index = 1
    while (index < 5):
        print("Start " + str(index) + " page")
        driver.switch_to.default_content()
        driver.get("http://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=168&search.boardtype=&search.questionTab=A&search.totalCount=151&search.page="+str(index))
        driver.switch_to.frame(driver.find_element_by_id("cafe_main"))

        address_list = get_report_address(driver)

        get_fraud_address(driver, address_list)

        print("Finish " + str(index) + " page")
        index += 1

    print("Complete All Data")



    conn.close()
###################################################################


if __name__ == '__main__':
    main()


