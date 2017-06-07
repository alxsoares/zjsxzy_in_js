from selenium import webdriver
import time

import const
import utils

driver = webdriver.Chrome('D:/bin/chromedriver.exe')

def shanghai():
    print("=====================================================================================")
    driver.get('http://sns.sseinfo.com/qa.do')
    elems = driver.find_elements_by_class_name('m_feed_item')
    for ele in elems:
        [que, ans] = ele.find_elements_by_class_name('m_feed_txt')
        author = ele.find_elements_by_class_name('m_feed_face')
        t = ele.find_elements_by_class_name('m_feed_from')
        if utils.containKeyWord(ans.text):
            print('%s %s: %s'%(t[1].text.split(' ')[0], author[1].text, ans.text))

if __name__ == '__main__':
    while True:
        shanghai()
        time.sleep(10)
    driver.close()
