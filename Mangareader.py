from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import options
from time import sleep
import sys
import os
import pickle

MANGAFREAK_FP = "https://angel.co"
class Mangafreak():
    def __init__(self):
        self.browser = Chrome(executable_path="E:\chromedriver.exe")
        self.browser.get(MANGAFREAK_FP)
        if os.path.exists('angel.pkl'):
            sleep(1)
            cookies = pickle.load(open('angel.pkl', 'rb'))
            for cookie in cookies:
                if cookie.get('expiry', None) is not None:
                    cookie['expires'] = cookie.pop('expiry')
                self.browser.add_cookie(cookie)
            self.browser.get(MANGAFREAK_FP+"/jobs")
            sleep(5)
            self.browser.get(MANGAFREAK_FP+"/jobs")
        else:
            log_in_btn = self.browser.find_element_by_xpath("/html/body/div/div/header/div/div[2]/a[3]")
            log_in_btn.click()
            sleep(1)

            email_box = self.browser.find_element_by_id("user_email").send_keys("vivekkumarshaw9@gmail.com")
            passwd_box = self.browser.find_element_by_id("user_password").send_keys("angelico@job55")
            enter = self.browser.find_element_by_name("commit").click()
            cookies = self.browser.get_cookies()
            pickle.dump(cookies, open('angel.pkl', 'wb'))
            jobs_portal = self.browser.find_element_by_xpath("/html/body/div/header/div/div[1]/nav/ul/li[3]/a")
            jobs_portal.click()

        sleep(5)
        if os.path.exists('templateReq.txt'):
            self.template = open('templateReq.txt', 'r').read()
            # print("Template -- ",self.template)
        self.apply_to_jobs()

    def apply_to_jobs(self):
        sleep(4)
        starting_index = 0
        for _ in range(2):
            job_search_results = self.browser.find_element_by_xpath('//*[@id="main"]/div/div[5]/div[2]/div')
            startup_results = job_search_results.find_elements_by_tag_name('div')
            startup_results = [ element for element in startup_results if element.get_attribute('data-test') == 'StartupResult']
            print("Startup entries", len(startup_results))

            for startup in startup_results[starting_index:]:
                startup.location_once_scrolled_into_view
                company_listings = startup.find_elements_by_class_name('component_07bb9')
                print("GEtting here", len(company_listings))
            # company_listings = [ e for e in company_listings if e.get_attribute('class') == 'listing_4d13a']
                for position in company_listings:
                    sleep(1)
                    self.apply_to_a_single_job_listing(position)

            starting_index = len(startup_results)
            # print(dir(startup_results[0]))
            input("Ready for next round")

    def display_text(self, elementArray, banner):
        if len(elementArray) > 0:
            for entry in elementArray:
                print(banner, entry.text)

    def display_attribute(self, elementArray):
        for entry in elementArray:
            print(entry.get_attribute('class')+"\n")

    def apply_to_a_single_job_listing(self, element):
        #Get the apply button
        company_info_1 = element.find_elements_by_tag_name('a')
        company_info_2 = element.find_elements_by_tag_name('span')
        self.display_text(company_info_1, "Company Info 1 -- ")
        self.display_text(company_info_2[-1:], "Company Info 2 -- ")
        # return
        apply_box = element.find_element_by_class_name('box_1bc08')
        apply_button = apply_box.find_element_by_tag_name('button')
        if apply_button.text != 'Applied':
            apply_button.click()
        sleep(3)
        applicationModal = self.browser.find_element_by_class_name("ReactModalPortal")
        sleep(0.2)
        h4tags = applicationModal.find_elements_by_tag_name('h4')   
        # self.display_text(h4tags, "Contact Person -- ")
        print(h4tags[-1].text.split(" is "))
        contact_person = h4tags[-1].text.split(" is ")[1]
        writeNoteToContact = applicationModal.find_element_by_tag_name('textarea')
        
        writeNoteToContact.send_keys("Hi {}, {}".format(contact_person, self.template))
        bts = applicationModal.find_elements_by_tag_name('button')
        for e in bts:
            if e.text == 'Cancel':
                e.click()
                break
        # _ = [entry.click() for entry in bts if entry.text == 'Cancel']
        


if __name__ == "__main__":
    Mangafreak()