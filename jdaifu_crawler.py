from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoSuchElementException
import time
import json

driver = webdriver.Chrome("C:\\DESK\\chromedriver.exe")
url = 'http://www.jdaifu.com/sdk_ssl/rest/ssl?from=oyNtkdONsM2v5fZc'

# main_crawler 爬取的記錄，因為每次點擊都會使頁面發生變化
step_1_save = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13']
step_2_save = ['14-0','14-1','14-2','14-3']

# qa_crawler 變數
qa_save = []
qas = []
qa = {}
block = 0

def class_check(class_name):
    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )
    except TimeoutException:
        pass

def id_check(id_name):
    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, id_name))
        )
    except TimeoutException:
        pass

def main_crawler():
    global step_1_save, step_2_save
    global qa_save, qas, qa, block
    try:
        # 第一層
        class_check('sy')
        sy = driver.find_element_by_css_selector('.sy')
        sy_li = sy.find_elements_by_css_selector('li')
        for sli_index, sli in enumerate(sy_li):
            if str(sli_index) not in step_1_save:
                time.sleep(1)
                sli.click()
                step1_text = sli.text
                # 第二層
                # 第二層其實是獨立的，只是第一層的點擊會影響標籤的顯示/隱藏，所以要寫在下一階段
                class_check('by')
                content_by = driver.find_elements_by_css_selector('.F_wd_top_con2_r .content .by')
                for by_index, by in enumerate(content_by):
                    # 第二層的 index 要對應到第一層的 index
                    if by_index == sli_index:
                        by_li = by.find_elements_by_css_selector('li')
                        for bli_index, bli in enumerate(by_li):
                            # 目前爬取位置 <第一層> - <第二層>
                            step2_text = bli.text
                            step_2 = str(by_index) + "-" + str(bli_index)
                            if step_2 not in step_2_save:
                                time.sleep(1)
                                bli.click()
                                while True:
                                    result  = qa_crawler('s')
                                    if result == 0:
                                        # 有異常
                                        time.sleep(10)
                                        print('有異常')
                                        return 0
                                    elif result == 1:
                                        # 存檔
                                        to_json(step1_text+"-"+step2_text)
                                        # 變數歸零
                                        qa_save = []
                                        qas = []
                                        qa = {}
                                        block = 0
                                        print('存檔與歸零')
                                        break
                                    else:
                                        return 0
                                step_2_save.append(step_2)
                                print(step1_text + "-" + step2_text)

                                # 爬完第二層時，將第一層的 index 加入 save 陣列
                                if bli_index == len(by_li) - 1:
                                    step_1_save.append(str(sli_index))

                                # 確認是否已經爬到最後
                                final_check = str(len(sy_li) - 1) + "-" + str(len(by_li) - 1)
                                if final_check == step_2:
                                    return 1

                                return 0
    except NoSuchElementException:
        return 0

def qa_crawler(step):
    global qa_save, qas, qa, block
    time.sleep(2)
    block += 1
    if 's' in qa_save:
        return 1
    elif block > 30:
        block = 0
        return 0
    else:
        pass

    check = [step + '0', step + '1']
    class_check('decoration')

    try:
        goback = driver.find_element_by_css_selector('#re_dgn')
        end = driver.find_element_by_css_selector('.notification-page-item em').text
        qa_save.append(step)

        qa['answer'] = end
        qas.append(qa)
        qa = {}

        driver.execute_script("arguments[0].click();", goback)
        block = 0
        qa_crawler('s')

    except NoSuchElementException:
        try:
            id_check('qst_content')
            q = driver.find_element_by_css_selector('#qst_content').text
            if check[1] not in qa_save:
                class_check('footer-google')
                yes = driver.find_element_by_css_selector('.footer-google')

                qa[q] = 'yes'

                driver.execute_script("arguments[0].click();", yes)
                qa_crawler(step + '1')
            elif check[0] not in qa_save:
                class_check('footer-share')
                no = driver.find_element_by_css_selector('.footer-share')

                qa[q] = 'no'

                driver.execute_script("arguments[0].click();", no)
                qa_crawler(step + '0')
            else:
                qa_save.append(step)
                return 2
        except NoSuchElementException:
            print('qst_content not found')
            return 0

def to_json(filename):
    newlist = sorted(qas, key=lambda k: k['answer'])
    with open(filename + '.json', 'w', encoding='utf-8') as f:
        data = json.dumps(newlist, ensure_ascii=False)
        f.write(data)
    print('save : {}'.format(filename))

# 每次爬取要重新進到首頁
while True:
    try:
        driver.get(url)
        check = main_crawler()
        if check == 1:
            break
        else:
            pass
    except TimeoutException:
        time.sleep(60)