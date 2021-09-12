import os
import sys
import json
import pickle
import argparse
import traceback
from time import sleep
from random import randint
from datetime import datetime
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class Cupid():
    def __init__(self, browser):
        """
            Intialization of Cupid Class which takes care of 
            automating various okcupid operations

            :browser: Instance of webdriver.Chrome
        """
        self.browser = browser
        self.data_dict = dict()
        self.main_page = "https://okcupid.com"
        self.cookies_path = "cupid.pkl"
        self.phone_no = open('mob_no.txt').read()
        print(self.phone_no)
        self.arrows = None
        if os.path.isfile("cupid_arrows"):
            self.arrows = open("cupid_arrows", 'r').readlines()

    def util_click(self, ele, sleep_time=1):
        sleep(sleep_time)
        # try:
        #     ele.click()
        # except Exception as ex:
        #     print(ex)
        self.browser.execute_script("arguments[0].click();", ele)

    def util_input(self, ele, keys):
        for i in range(len(keys)):
            sleep(0.23)
            ele.send_keys(keys[i])
    
    def use_css_selector(self, key, total_time=20, interval=5,     
                        click_element=False, input_text=None, siblings=False,
                        extract_attribute=None):
        """
        Returns Element only when click_element and input_text are default values
        """
        if siblings:
            eles = WebDriverWait(self.browser, total_time, interval) \
                    .until(lambda browser: browser.find_elements_by_css_selector(key))
            if extract_attribute == "text":
                details = ""
                if isinstance(eles, list):
                    for e in eles:
                        details += " " + e.text
                return eles, details
            return eles
        else:
            ele = WebDriverWait(self.browser, total_time, interval) \
                .until(lambda browser: browser.find_element_by_css_selector(key))
                # .until(EC.visibility_of_element_located((By.CSS_SELECTOR, key)))
            if click_element:
                return self.util_click(ele, 2)
            if input_text:
                return self.util_input(ele, input_text)
        return ele

    def login(self):
        self.browser.get(self.main_page)
        if os.path.exists(self.cookies_path):
            sleep(1)
            cookies = pickle.load(open(self.cookies_path, 'rb'))
            for cookie in cookies:
                if cookie.get('expiry', None) is not None:
                    cookie['expires'] = cookie.pop('expiry')
                self.browser.add_cookie(cookie)
            self.browser.get(self.main_page)
        else:
            self.browser.get(self.main_page)
            self.use_css_selector('a[class="splash-signin"]', click_element=True)
            self.use_css_selector('button[class="login-actions-button login-actions-button-sms"]',
                                click_element=True)
            self.use_css_selector('input[name="phone-number"]', input_text=self.phone_no)
            self.use_css_selector('input[class="login-actions-button"]', click_element=True)
            otp = input("Enter the OTP\n >>")
            otp_input_eles = [ \
                self.use_css_selector(f'div[class="code-inputs-digits"] > input[data-index="{e}"]') for e in range(6)
            ]
            for idx, ele in enumerate(otp_input_eles):
                self.util_input(ele, otp[idx])
            self.use_css_selector('button[class="login-actions-button"]', click_element=True)
            sleep(10)
            cookies = self.browser.get_cookies()
            pickle.dump(cookies, open(self.cookies_path, 'wb'))
            print("Saved Cookies!!")

    def get_started(self):
        self.browser.implicitly_wait(3)
        try:
            self.use_css_selector('button[class*="keep-mobile"]', total_time=6, click_element=True)
        except:
            print("NO DIALOG - I PREFER THE MOBILE SITE")
        try:
            self.use_css_selector('button[id*="onetrust-accept-btn-handler"]', total_time=6, click_element=True)
        except:
            print("NO DIALOG - AGREEING TO BE TRACKED, YIKES!!")

    def match_preferences(self, details, n_images):
        #Return True/False which will end up as Like/Pass
        if n_images == 1:
            return False
        return True

    def send_intro(self, already_liked):
        print("LIKE..")
        if already_liked:
            self.use_css_selector('button[aria-label="Message"]', click_element=True)
        else:
            self.use_css_selector('button[aria-label="Like"]', click_element=True)
            self.use_css_selector(
                'button[class="profile-buttons-modal-buttons-cta blue-new flatbutton"]',
                click_element=True)
        try:
            self.use_css_selector('div[class="messenger-composer-wrapper"] > textarea[placeholder="Say something..."]',
                                    input_text=self.arrows[randint(0, len(self.arrows)-1)])
            self.use_css_selector('button[class="messenger-toolbar-send"]', click_element=True)
        except Exception as ex:
            print(ex)
            pass


    def get_profile(self):
        try:
            sleep(1)
            # self.use_css_selector('div[class*="card-content-header__name"]', 30, click_element=True)
            #'use tappy_tap_container ele for screenshot'
            n_images = len(self.use_css_selector('div[class*="tappy-thumb-indicator"]', siblings=True))
            print("IMAGES", n_images)
            # _, details = self.use_css_selector('div[class="matchprofile-details-text"]', siblings=True, extract_attribute="text")
            # print("==========================\n" + details + "\n============================")
            if self.match_preferences([], n_images):
                # self.send_intro()
                self.use_css_selector('button[aria-label="Like"]', click_element=True)
                # self.browser.get(self.main_page + "/doubletake")
            else:
                print("PASSING..")
                self.use_css_selector('button[aria-label="Pass"]', click_element=True)
        except StaleElementReferenceException as ex:
            print("STALE ELEMENT, GO TO DOUBLETAKE!!")
            self.use_css_selector('button[aria-label="Pass"]', click_element=True)
            # self.browser.get(self.main_page+"/doubletake")

    def send_intro_to_likes_who_are_online(self):
        try:
            self.browser.get(self.main_page + "/who-you-like?cf=likesIncoming")
            sleep(5)
            for i in range(2):
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(5)
            online_now = self.use_css_selector(
                'span[class="onlinedot userInfo-username-online"]',
                siblings=True)
            profile_links = [WebDriverWait(entry.find_element_by_xpath("../../.."),10,1)
                        .until(lambda ele: ele.find_element_by_css_selector(
                        'div[class="usersresponsivecard-thumb"] > a').get_attribute("href")) 
                        for entry in online_now]
            print(profile_links)
            for entry in profile_links:
                try:
                    self.browser.get(entry)
                    self.send_intro(True)
                    os.system(f"echo {entry} >> sent_intro.txt")
                except:
                    print("Profile doesn't exist anymore!!")
                    pass
        except Exception as ex:
            print("SEND INTRO TO LIKES EXCEPTION", ex)
if __name__ == "__main__":
    options = ChromeOptions()
    mobile_emulation = {
    "deviceMetrics": { "width": 375, "height": 612},
    "userAgent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36"
    }
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--ignore-ssl-errors')
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome = Chrome(executable_path="E:\chromedriver.exe", chrome_options=options)
    cupid_auto_obj = Cupid(chrome)
    cupid_auto_obj.login()
    cupid_auto_obj.get_started()
    # for u in range(20):
    #     cupid_auto_obj.get_profile()
    # cupid_auto_obj.send_intro_to_likes_who_are_online()
