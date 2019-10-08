import selenium
from selenium import webdriver
import time
import random


# create giveaway entry class
class GiveawayEntry:
    url = ''
    isEntered = False
    today = ''
    expiration_date = ''
    rating = 10
    expiration_datetime = ''
    entered_date = ''
    delay = 4.0  # seconds of delay between field entries
    delay_noise = 1.0  # seconds of delay noise (magnitude of randomization)
    isValid = False
    actually_enter = False
    _driver = []

    # Constructor
    def __init__(self, url, expiration_date, rating):
        from datetime import date

        # get today's date
        today = date.today()
        self.today = today.strftime("%Y-%m-%d")

        self.url = url
        self.expiration_date = expiration_date
        self.rating = int(rating)

        # convert expiration date to datetime format
        [y, m, d] = expiration_date.split('-')
        self.expiration_datetime = date(int(y), int(m), int(d))

        if today <= self.expiration_datetime:
            self.isValid = True

    # Enter Giveaway method
    def enter_giveaway(self, person):
        pass

    # Check if giveaway rating is satisfied
    def check_rating(self):
        if random.randint(1, 10) > self.rating:
            print('Skipping Giveaway {} because only {}0% chance of entry'.format(self.url, self.rating))
            return False
        else:
            return True

    def init_driver(self):
        self._driver = selenium.webdriver.Chrome()
        self._driver.get(self.url)
        time.sleep(self.delay + self.delay_noise * random.random())

    def fill_textbox(self, text_id, text_str):
        last_name = self._driver.find_element_by_id(text_id)
        last_name.send_keys(text_str)
        time.sleep(self.delay + self.delay_noise * random.random())

    def click_submit_button(self, button):
        try:
            if self.actually_enter:
                button.click()
        except:
            self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            if self.actually_enter:
                button.click()

        # pause for short time to manually verify submission, if desired
        time.sleep(5)
        self._driver.close()

        print('Entered Giveaway for {}'.format(self.url))
        self.isEntered = True


# Entry class for SteamyKitchen.com giveaways
class SteamyKitchenEntry(GiveawayEntry):

    # Enter Giveaway method
    def enter_giveaway(self, person):

        # short circuit entering the giveaway if it is not important enough (based on rating)
        if self.check_rating():
            return
        # only enter giveaway if it hasn't reached expiration yet
        elif self.isValid:

            # Open web page and begin entry process
            self.init_driver()

            # Fill form
            self.fill_textbox('skg_first_name', person.first_name)
            self.fill_textbox('skg_last_name', person.last_name)
            self.fill_textbox('skg_email', person.email)

            # Submit form
            button = self._driver.find_element_by_id('skg_submit_button')
            self.click_submit_button(button)
        else:
            print('Giveaway for {} has expired'.format(self.url))


# Entry class for LeitesCulinaria.com giveaways
class LeitesCulinariaEntry(GiveawayEntry):

    # Enter Giveaway method
    def enter_giveaway(self, person):

        # short circuit entering the giveaway if it is not important enough (based on rating)
        if self.check_rating():
            return
        # only enter giveaway if it hasn't reached expiration yet
        elif self.isValid:

            # Open web page and begin entry process
            self.init_driver()

            # Fill form
            self.fill_textbox('giveaway_entry_name', person.full_name)
            self.fill_textbox('giveaway_entry_email', person.email)

            # Submit form
            button = self._driver.find_element_by_class_name('giveaway-field')
            self.click_submit_button(button)
        else:
            print('Giveaway for {} has expired'.format(self.url))
