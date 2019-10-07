from selenium import webdriver
import time
import random


class Person:
    first_name = ''
    last_name = ''
    email = ''

    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email


# create giveaway entry class
class GiveawayEntry:
    url = ''
    isEntered = False
    today = ''
    expiration_date = ''
    rating = 10
    expiration_datetime = ''
    entered_date = ''
    delay = 4.0 # seconds of delay between field entries
    delay_noise = 1.0 # seconds of delay noise (magnitude of randomization)
    isValid = False

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

        # short circuit entering the giveaway if it is not important enough (based on rating)
        if random.randint(1, 10) > self.rating:
            print('Skipping Giveaway {} because only {}0% chance of entry'.format(self.url, self.rating))
            return
        # only enter giveaway if it hasn't reached expiration yet
        elif self.isValid:

            driver = webdriver.Chrome()
            driver.get(self.url)
            time.sleep(self.delay + self.delay_noise*random.random())

            self.fill_textbox(driver, 'skg_first_name', person.first_name)
            self.fill_textbox(driver, 'skg_last_name', person.last_name)
            self.fill_textbox(driver, 'skg_email', person.email)

            button = driver.find_element_by_id('skg_submit_button')
            try:
                button.click()
            except:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                button.click()
            # print('Simulated click to submit form')

            # pause for short time to manually verify submission, if desired
            time.sleep(5)
            driver.close()

            print('Entered Giveaway for {}'.format(self.url))
            self.isEntered = True
        else:
            print('Giveaway for {} has expired'.format(self.url))

    def fill_textbox(self, driver, id, str):
        last_name = driver.find_element_by_id(id)
        last_name.send_keys(str)
        time.sleep(self.delay + self.delay_noise * random.random())

class GiveawayManager:
    giveaways = []
    today = ''
    delay = 15 # seconds of delay between giveaway entries
    delay_noise = 5 # seconds of delay noise (magnitude of randomization)

    def __init__(self, urlFile):
        from datetime import date
        import os

        # get today's date
        today = date.today()
        self.today = today.strftime("%Y-%m-%d")

        # read urls of giveaways to enter
        with open(urlFile, 'r') as f:
            data = f.readlines()

        # read urls of giveaways entered today
        entered_filename = 'logs/{}.entered'.format(self.today)
        entered_data = []
        if os.path.isfile(entered_filename):
            with open(entered_filename, "r") as f:
                entered_data = f.readlines()

            entered_data = [line.rstrip('\n') for line in entered_data]

        # cleanup url data and create giveaway entries
        for d in data:
            urlstr = d.replace("\n", "")
            [expire_date, rating, url] = urlstr.split(' ')

            if url in entered_data:
                print('Already entered {} today'.format(url))
            else:
                self.giveaways.append(GiveawayEntry(url, expire_date, rating))


    def run(self):
        # open entered giveaways log file for writing
        entered_filename = 'logs/{}.entered'.format(self.today)
        writefile = open(entered_filename, 'a')

        for g in self.giveaways:
            sam = Person("Sam", "McDonald", "whitehops@gmail.com")
            g.enter_giveaway(sam)
            time.sleep(self.delay + self.delay_noise*random.random())
            if g.isEntered:
                writefile.write('{}\n'.format(g.url))

        writefile.close()

# Choose a list of urls of giveaways to enter
gm = GiveawayManager('SteamyKitchenURL.txt')
gm.run()
