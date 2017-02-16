
from selenium import webdriver
import time
import sqlite3
import re


conn = sqlite3.connect("theCheat.db")
cursor = conn.cursor()

sql = "Create Table if not exists theCheat(article_num varchar2(10), date date, fraud_email varchar2(30), item_category varchar(20), fraud_item varchar2(20), item_price number(10), fraud_bank varchar2(10), fraud_account varchar2(20), article_body varchar2(50))"

cursor.execute(sql)

#########################################################
# 로그인
def login(driver):

    driver.get("http://thecheat.co.kr/rb/?mod=_home")

    elem = driver.find_element_by_id("hm_u_id")
    elem.send_keys("USERID")
    elem = driver.find_element_by_id("hm_u_pw")
    elem.send_keys("USERPW")
    elem = driver.find_element_by_class_name("btnLogin").click()

    time.sleep(5)
#########################################################

def get_report_address(driver):
    #driver.get("http://thecheat.co.kr/rb/?m=bbs&bid=cheat")

    goods = driver.find_element_by_tag_name("tbody")
    #index = 0
    address_list = []
    #goods_a = []
    goods_a = goods.find_elements_by_tag_name("a")

    for href in goods_a:
        address_list.append(href.get_attribute("href"))

    address_list = list(set(address_list))
    index = 0
    while (index < len(address_list)):
        print(address_list[index])
        index += 1

    return address_list

def crawl_report(driver, address_list):

    read_article = 0
    exist = 0

    for address in address_list:
        try:
            driver.get(address)
            article_num = address[-7:]
            cursor.execute('''Select * from theCheat where article_num="'''+article_num+'''"''')
            for row in cursor:
                exist = row[0]
            if not exist:
                cursor.execute('''Insert into theCheat(article_num) values("''' + article_num + '''");''')
                damage_info_area = driver.find_element_by_class_name("damageInfoArea")
                date = damage_info_area.find_element_by_xpath("./div[2]/table/tbody/tr[1]/td")
                cursor.execute(
                    '''Update theCheat set date = "''' + date.text + '''" where article_num = "''' + article_num + '''"''')
                fraud_email = damage_info_area.find_element_by_xpath("./div[2]/table/tbody/tr[2]/td[2]")
                cursor.execute(
                    '''Update theCheat set fraud_email = "''' + fraud_email.text + '''" where article_num = "''' + article_num + '''"''')
                item_category = damage_info_area.find_element_by_xpath("./div[2]/table/tbody/tr[3]/td[1]/li/img")
                item_category = item_category.get_attribute("alt")
                cursor.execute(
                    '''Update theCheat set item_category = "''' + item_category + '''" where article_num = "''' + article_num + '''"''')
                fraud_item = damage_info_area.find_element_by_xpath("./div[2]/table/tbody/tr[3]/td[1]")
                cursor.execute(
                    '''Update theCheat set fraud_item = "''' + fraud_item.text + '''" where article_num = "''' + article_num + '''"''')
                fraud_price = damage_info_area.find_element_by_xpath("./div[2]/table/tbody/tr[3]/td[2]")
                fraud_price = re.sub('[^0-9]', '', fraud_price.text)
                cursor.execute(
                    '''Update theCheat set item_price = "''' + fraud_price + '''" where article_num = "''' + article_num + '''"''')
                account = damage_info_area.find_element_by_xpath("./div[3]/table/tbody/tr[2]/td/b")
                bank = account.text
                bank = bank.split(" ")[0]
                cursor.execute(
                    '''Update theCheat set fraud_bank = "''' + bank + '''" where article_num = "''' + article_num + '''"''')
                cursor.execute(
                    '''Update theCheat set fraud_account = "''' + account.text + '''" where article_num = "''' + article_num + '''"''')
                article_body = damage_info_area.find_element_by_xpath("./div[4]/table/tbody/tr[1]/td")
                cursor.execute(
                    '''Update theCheat set article_body = ' ''' + article_body.text + ''' ' where article_num = "''' + article_num + '''"''')

                conn.commit()

            else:
                read_article +=1
                if(read_article > 3):
                    break



        except Exception as e:
            print(e)
            continue
        finally:
            print("OK")

    if(read_article > 3):
        return 0
    else:
        return 1




def main():
    driver = webdriver.Firefox()
    login(driver)

    driver.get("http://thecheat.co.kr/rb/?m=bbs&bid=cheat")

    index = 1
    next_page = 0
    while (1):
        print("Start " + str(index) + " page")

        driver.get(
            "http://thecheat.co.kr/rb/?m=bbs&bid=cheat&page_num=&search_term=&se=&p=" + str(index))

        address_list = get_report_address(driver)
        next_page = crawl_report(driver, address_list)
        if(next_page == 0):
            break

        print("Finish " + str(index) + " page")
        index += 1

    print("Complete All Data")




if __name__ == '__main__':
    # while(1):
    #     main()
    #     time.sleep(3600)
    main()
