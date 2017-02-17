#coding: utf-8

from selenium import webdriver
import time
import re
import sqlite3

conn = sqlite3.connect("giftcon.db")
cursor = conn.cursor()

cursor.execute(
        "Create Table if not exists giftcon(article_num varchar2(12), "
        "article_title varchar2(20), giftcon_id varchar2(20), price number, giftcon_article varchar2(50))")


#########################################################
# 로그인
def login(driver):

    driver.get("http://www.naver.com")

    elem = driver.find_element_by_class_name("bl_btn").click()

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
            address_list.append("http://cafe.naver.com/joonggonara/" + list_url)
        index += 1

    print(address_list)  # 게시글 주소 리스트
    return address_list
########################################################

#######################################################################
# 타겟 게시판 수집
def crawl_target_article(driver, original_article_list):
    index=0
    row = None
    for orginal_link in original_article_list:
        driver.switch_to.default_content()
        if ('http://cafe.naver.com/joonggonara/' in orginal_link):
            file_name = orginal_link[34:]
            article_text = ""

            cursor.execute("Select exists (select * from giftcon where article_num = " + file_name + ");")
            for row in cursor:
                print(row[0])

            if not row[0]:
                driver.get(orginal_link)
                try:
                    driver.switch_to.alert.accept()
                    continue
                except:
                    pass
                try:
                    # 불량글 제목
                    index = 0
                    cursor.execute('''Insert into giftcon(article_num) values("''' + file_name + '''");''')
                    driver.switch_to.frame(driver.find_element_by_id('cafe_main'))

                    title_box = driver.find_element_by_class_name("tit-box")
                    title = title_box.find_elements_by_tag_name("span")
                    while (index < len(title)):
                        if (title[index].get_attribute("class") == "b m-tcol-c"):
                            title_text = title[index].text
                            cursor.execute(
                                '''Update giftcon set article_title = "''' + title_text + '''"where article_num = "''' + file_name + '''"''')

                        index += 1

                    index = 0
                    etc_box = driver.find_element_by_class_name("etc-box")
                    fraud_id = etc_box.find_elements_by_tag_name("a")
                    while (index < len(fraud_id)):
                        if (fraud_id[index].get_attribute("class") == "m-tcol-c b"):
                            id_text = fraud_id[index].text
                            cursor.execute(
                                '''Update giftcon set giftcon_id = "''' + id_text + '''"where article_num = "''' + file_name + '''"''')
                        index += 1

                    # 아이템 가격
                    index = 0
                    item_detail = driver.find_element_by_class_name("details-m")
                    item_price = item_detail.find_elements_by_tag_name("td")
                    while (index < len(item_price)):
                        if (item_price[index].get_attribute("class") == "price border-sub"):
                            price_text = item_price[index].text
                            price_text = re.sub('[^0-9]','',price_text)
                            cursor.execute(
                                '''Update giftcon set price = "''' + price_text + '''"where article_num = "''' + file_name + '''"''')
                        index += 1

                    # 불량글 내용
                    index = 0
                    fraud_article_all = driver.find_element_by_id("tbody")
                    fraud_article = fraud_article_all.find_elements_by_tag_name("p")
                    while (index < len(fraud_article)):
                        class_name = fraud_article[index].get_attribute("class")
                        if (class_name == ''):
                            article_text = article_text+"\n"+fraud_article[index].text
                            cursor.execute(
                                '''Update giftcon set giftcon_article = "''' + article_text + '''"where article_num = "''' + file_name + '''"''')
                        index += 1

                    # cursor.execute('''Update fraud_report set fraud_num = "'''+file_name+'''", fraud_title = "'''+title_text+'''",fraud_id = "'''+id_text+'''",price = "'''+price_text+'''",fraud_article = "'''+article_text+'''" where report_num = "'''+report_num+'''";''')
                    conn.commit()

                except:
                    continue
                finally:
                    print("complete : " + orginal_link)
                    print("")
            else:
                print("이미 읽은 글이다.")

    print("Finish Current Page")
############################################################################



################################################################
# Main
def main():
    driver = webdriver.Firefox()  # 파이어폭스 씁니다

    login(driver)

    # 거래게시판으로 이동
    driver.get("http://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=448&search.boardtype=L")

    index = 1
    while(index<11):
        print("Start "+str(index)+" page")
        driver.switch_to.default_content()
        driver.get("http://cafe.naver.com//ArticleList.nhn?search.clubid=10050146&search.menuid=448&search.boardtype=&search.questionTab=A&search.totalCount=151&search.page="+str(index))
        # 네이버 카페는 게시글 화면이 iframe으로 되어있음. 따라서 iframe으로 이동
        driver.switch_to.frame(driver.find_element_by_id("cafe_main"))

        address_list = get_report_address(driver)

        crawl_target_article(driver, address_list)
        print("Finish "+str(index)+" page")
        index += 1

    print("Complete All Data")

    conn.close()

###################################################################


if __name__ == '__main__': #30분에 한번씩 돌리면 한번에 100개 모을듯
    main()


