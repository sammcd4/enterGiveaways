import selenium
from selenium import webdriver
import time
import random


# create giveaway entry class
from selenium.common.exceptions import StaleElementReferenceException


class HumanizedDelay:
    delay = 3.0 # nominal delay value in seconds
    noise = 1.0

    def delay(self):
        time.sleep(self.delay + self.noise * random.random())

    @ delay.setter
    def delay(self, value):
        self.delay = value
        if value == 0:
            self.noise = 0

class GiveawayEntry:
    url = ''
    isEntered = False
    today = ''
    expiration_date = ''
    rating = 10
    expiration_datetime = ''
    entered_date = ''
    human = HumanizedDelay
    isValid = False
    actually_enter = True
    noDelay = False
    _driver = []

    # Constructor
    def __init__(self, url, expiration_date, rating):
        from datetime import date

        if self.noDelay:
            self.human.delay = 0

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
        print(person.first_name + ' ' + self.url)
        if not self.isValid:
            self.print('Giveaway has expired')

        # short circuit entering the giveaway if it is not important enough (based on rating)
        elif self.check_rating():

            # Open web page and begin entry process
            if not self.init_driver():
                return

            self.fill_and_submit(person)

        else:
            self.print('Skipping giveaway because only {}0% chance of entry'.format(self.rating))

    # Check if giveaway rating is satisfied
    def check_rating(self):
        if random.randint(1, 10) > self.rating:
            return False
        else:
            return True

    def init_driver(self):
        try:
            self._driver = selenium.webdriver.Chrome()
            self._driver.get(self.url)
            self.human.delay()
            return True
        except:
            self.print('Unable to initialize webpage! Consider updating the webdriver')
            return False

    def print(self, some_str):
        print('\t' + some_str)

    def fill_textbox(self, text_id, text_str):
        try:
            element = self._driver.find_element_by_id(text_id)
            element.send_keys(text_str)
        except:
            self.print('Unable to fill {} textbox with {}'.format(text_id, text_str))
        self.human.delay()

    def fill_textbox_and_submit(self, text_id, text_str):
        try:
            element = self._driver.find_element_by_id(text_id)
            element.send_keys(text_str)

            if not self.actually_enter:
                self.print('Simulating submission')
            else:
                element.submit()
        except:
            self.print('Unable to fill {} textbox with {}'.format(text_id, text_str))

        self.confirm_submission()

    def submit_from_textbox(self, text_id):
        try:
            element = self._driver.find_element_by_id(text_id)

            if not self.actually_enter:
                self.print('Simulating submission')
            else:
                element.submit()
        except:
            self.print('Unable to submit form from {} textbox'.format(text_id))

    def click_submit_button(self, button):

        if not self.actually_enter:
            self.print('Simulating submission')
        else:
            try:
                button.click()
            except StaleElementReferenceException:
                self.print('StaleElementReferenceException occurred, but likely button still was pressed')
            except:
                self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                button.click()

        self.confirm_submission()

    def submit_with_enter(self, button):
        if not self.actually_enter:
            self.print('Simulating submission')
        else:
            try:
                button.submit()
            except StaleElementReferenceException:
                self.print('StaleElementReferenceException occurred, but likely button still was pressed')
            except:
                self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                button.click()

        self.confirm_submission()

    def confirm_submission(self):
        # pause for short time to manually verify submission, if desired
        if not self.noDelay:
            time.sleep(5)

        try:
            self._driver.close()
        except:
            self.print('Web page could not be closed!')

        try:
            self._driver.quit()
        except:
            self.print('Driver could not be quit!')

        self.isEntered = True
        self.print('Entered Giveaway')


# Generic entry class for First name, Last name, email fields
class FirstLastEmailGiveawayEntry(GiveawayEntry):
    first_name_id = ''
    last_name_id = ''
    email_id = ''
    submit_button_id = ''

    # Fill and submit process specific to SteamyKitchen
    def fill_and_submit(self, person):
        # Fill form
        self.fill_textbox(self.first_name_id, person.first_name)
        self.fill_textbox(self.last_name_id, person.last_name)
        self.fill_textbox(self.email_id, person.email)

        # Submit form
        try:
            button = self._driver.find_element_by_id(self.submit_button_id)
        except:
            self.print('Unable to find submit element {}'.format(self.submit_button_id))
        self.click_submit_button(button)


# Entry class for SteamyKitchen.com giveaways
class SteamyKitchenEntry(FirstLastEmailGiveawayEntry):
    def __init__(self, url, expiration_date, rating):
        # Fill form
        super().__init__(url, expiration_date, rating)
        self.first_name_id = 'skg_first_name'
        self.last_name_id = 'skg_last_name'
        self.email_id = 'skg_email'
        self.submit_button_id = 'skg_submit_button'


# Entry class for GlutenFree.com giveaways
class GlutenFreeEntry(FirstLastEmailGiveawayEntry):
    def __init__(self, url, expiration_date, rating):
        # Fill form
        super().__init__(url, expiration_date, rating)
        self.first_name_id = 'input_1_1'
        self.last_name_id = 'input_1_2'
        self.email_id = 'input_1_3'
        self.submit_button_id = 'gform_submit_button_1'


# Entry class for LeitesCulinaria.com giveaways
class LeitesCulinariaEntry(GiveawayEntry):
    extra_entered = False

    # Fill and submit process specific to SteamyKitchen
    def fill_and_submit(self, person):
        # Fill form
        self.fill_textbox('giveaway_entry_name', person.full_name)
        self.fill_textbox('giveaway_entry_email', person.email)

        self.submit_from_textbox('giveaway_entry_email')

        if not LeitesCulinariaEntry.extra_entered:
            LeitesCulinariaEntry.extra_entered = True
            self.fill_textbox('input_2920_1', person.full_name)
            self.fill_textbox('input_2920_2', person.email)
            self.submit_from_textbox('input_2920_2')

        self.confirm_submission()
