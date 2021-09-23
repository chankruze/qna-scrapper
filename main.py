import os
import logging
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys

MAX_CLICKS = 10

if __name__ == '__main__':
    date_format = "[%(asctime)s] %(message)s"
    logging.basicConfig(format=date_format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    firefox_options = Options()
    # enable this to run in headless mode
    # firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)
    logging.info("[📣] Driver ready...")

    # read keywords from excel/txt file
    # then store those words in this list below
    # main sections
    word_list = list()

    # I am using pandas but you can use only openpyxl or what ever
    df = pd.read_excel('world_list.xlsx', index_col=None, header=None)
    # grab per answer links per page
    for index, row in df.iterrows():
        logging.info(row[0])
        word_list.append(row[0])

    # create output directory (if not present)
    out_dir = "out"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # main loop
    # for each keyword in word_list loop this
    for key_word in word_list:
        driver.get("https://google.com")
        search_box = driver.find_element_by_xpath("//input[@title='Search']")
        # type the keyword
        search_box.send_keys(key_word)
        # hit enter to search
        search_box.send_keys(Keys.ENTER)
        time.sleep(5)
        # People also ask (div>h3>span)
        # not necessary (can comment out line no 39 - 41)
        people_also_ask = driver.find_element_by_css_selector("div>h3>span")
        if people_also_ask.text.lower() == "People also ask".lower():
            driver.execute_script("document.querySelector('div>h3>span').scrollIntoView();")

        # related question pairs
        # initially there will be 4
        related_q_pairs = driver.find_elements_by_xpath("//div[contains(@class, 'related-question-pair')]")
        # loop counter
        idx = 0

        while idx < len(related_q_pairs):
            related_q_pairs[idx].click()
            time.sleep(1)
            # save to file
            with open(f"{out_dir}/qna-{key_word.replace(' ', '-')}.txt", "a", encoding="utf-8") as qna_file:
                # html content is available in related_q_pairs[idx] variable
                # just for demo, storing the plain text version
                # to save the actual html use related_q_pairs[idx].get_attribute('innerHTML')
                qna_file.write(f"#{idx:04}\n\n") # {int:xy}, y = number of places we want tot pad x
                qna_file.write(related_q_pairs[idx].text)
                qna_file.write("\n------------------------\n")

            # update qna pairs list
            related_q_pairs = driver.find_elements_by_xpath("//div[contains(@class, 'related-question-pair')]")
            # increase the loop counter
            idx += 1

    # when all finished
    logging.info("Shutting down....")
    time.sleep(10)
    #  close the browser
    driver.close()
