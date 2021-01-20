import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random
import sys
import requests
from bs4 import BeautifulSoup

# create giveaway entry class
from selenium.common.exceptions import StaleElementReferenceException


class HumanizedDelay:

    def __init__(self):
        self._delay = 2.0  # nominal delay value in seconds
        self.noise = 2.0

    def apply(self):
        time.sleep(self.delay + self.noise * random.random())

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, value):
        self._delay = value
        if value == 0:
            self.noise = 0


class GiveawayEntry:
    url = ''
    is_entered = False
    today = ''
    expiration_date = ''
    rating = 10
    expiration_datetime = ''
    entered_date = ''
    human_delay = HumanizedDelay()
    is_valid = False
    actually_enter = True
    no_delay = False
    _driver = None
    use_headless = True
    ads_removed = [False, False]
    use_chrome = True
    automate_entry = True
    # TODO: Read from a config file for all these hardcoded settings

    # TODO: log all successful or unsuccessful attempts

    # Constructor
    def __init__(self, url, expiration_date, rating, num_entries=1):
        from datetime import date

        if self.no_delay:
            self.human_delay.apply = 0

        # get today's date
        today = date.today()
        self.today = today.strftime("%Y-%m-%d")

        self.url = url
        self.expiration_date = expiration_date
        self.rating = int(rating)
        self.num_entries = num_entries

        self.ads_removed = [False, False]

        # convert expiration date to datetime format
        [y, m, d] = expiration_date.split('-')
        self.expiration_datetime = date(int(y), int(m), int(d))

        if today <= self.expiration_datetime:
            self.is_valid = True

    # Enter Giveaway method
    def enter_giveaway(self, person):
        print(person.first_name + ' has opened ' + self.url)
        if not self.is_valid:
            self.print('Giveaway has expired')

        # short circuit entering the giveaway if it is not important enough (based on rating)
        elif self.check_rating():
            for i in range(self.num_entries):
                if self.num_entries > 1:
                    self.print('Entry #{}'.format(i+1))

                # Open web page and begin entry process (try twice) TODO poll and timeout
                if not self.init_driver():
                    self.print('Unable to init driver')
                    continue

                if not self.prefill(person):
                    self.print('Prefill process was unsuccessful')
                    continue

                if not self.fill_and_submit(person):
                    self.print('Unable to fill and submit')
                    continue
        else:
            self.print('Skipping giveaway because only {}0% chance of entry'.format(self.rating))

    #Prefill process
    def prefill(self, person):
        #Unimplemented method
        return True

    # Check if giveaway rating is satisfied
    def check_rating(self):
        random_int = random.randint(1, 10)
        #self.print(f'Random int: {random_int} < Rating: {self.rating}')
        return random_int < self.rating

    def get_soup(self, link):
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def init_driver(self):

        init_status = True
        try:
            if self.use_chrome:
                chrome_options = Options()
                #chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
                #chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument("--incognito")
                #chrome_options.add_argument("—disable-infobars")
                if self.use_headless:
                    # chrome_options.add_argument("--disable-extensions")
                    if 'win' in sys.platform:
                        chrome_options.add_argument("--disable-gpu")

                    if 'linux' in sys.platform:
                        chrome_options.add_argument("--no-sandbox")

                    chrome_options.add_argument("--headless")
                    self._driver = webdriver.Chrome(options=chrome_options)
                else:
                    chrome_options.headless = False
                    self._driver = selenium.webdriver.Chrome(options=chrome_options)
            else:
                options = Options()
                options.headless = self.use_headless
                self._driver = webdriver.Firefox()

        except:
            self.print('Unable to initialize webpage! Consider updating the webdriver')
            self.close_driver()
            return False

        get_status = False
        try:
            self._driver.get(self.url)
            get_status = True
        except:
            self.print('Unable to call driver.get({})! Investigate any changes to webpage'.format(self.url))

        # Attempt 2 for driver.get
        if not get_status:
            try:
                self._driver.get(self.url)
                get_status = True
                self.print('Successfully called driver.get({})'.format(self.url))
            except:
                self.print('Unable to call driver.get({})! Investigate any changes to webpage'.format(self.url))
                self.close_driver()

        if not get_status:
            return False
        
        #  TODO: span.mv_close_button.mv_unbutton

        # removing certain ads may be required
        #self.remove_iframe_ads()

        # TODO: internalize error handling for human delay
        try:
            self.human_delay.apply()
            return True
        except:
            self.print('Unable to apply delay. Consider updating the HumanizedDelay class ')
        
    def print(self, *args, **kwargs):
        print('\t', end="")
        print(*args, **kwargs)

    def remove_iframe_ads(self):

        # exit early if ads are already removed
        if self.ads_removed[0]:
            return

        try:
            all_iframes = self._driver.find_elements_by_tag_name("iframe")
            if len(all_iframes) > 0:
                self._driver.execute_script("""
                    var elems = document.getElementsByTagName("iframe"); 
                    for(var i = 0, max = elems.length; i < max; i++)
                         {
                             elems[i].hidden=true;
                         }
                                      """)
            self.ads_removed[0] = True
        except:
            self.print('Unable to find any iframe ads')

    def fill_textbox(self, text_id, text_str):

        filled = False
        try:
            element = self._driver.find_element_by_id(text_id)
            element.send_keys(text_str)
            filled = True
        except:
            self.print('Unable to fill {} textbox with {}'.format(text_id, text_str))
        self.human_delay.apply()
        return filled

    def uncheck_box(self, box_id):
        unchecked = False
        try:
            element = self._driver.find_element_by_id(box_id)
            if element.is_selected():
                element.click()

            element = self._driver.find_element_by_id(box_id)
            if not element.is_selected():
                unchecked = True
                #print(f'element {box_id} has been unchecked')
            #else:
                #print(f'element {box_id} remained checked')
        except:
            self.print(f'Unable to uncheck {box_id}')
            raise
        return unchecked

    def fill_textbox_and_submit(self, text_id, text_str):
        submitted = False
        try:
            element = self._driver.find_element_by_id(text_id)
            element.send_keys(text_str)

            if not self.actually_enter:
                self.print('Simulating submission')
            else:
                element.submit()
                self.confirm_submission()
        except:
            self.print('Unable to fill {} textbox with {}'.format(text_id, text_str))

        self.close_driver()

    def submit_from_textbox(self, text_id):
        submitted = False
        try:
            element = self._driver.find_element_by_id(text_id)

            if not self.actually_enter:
                self.print('Simulating submission')
            else:
                element.submit()
                submitted = True
        except:
            self.print('Unable to submit form from {} textbox'.format(text_id))

        return submitted

    def click_submit_button(self, button):
        if self.actually_enter:
            if self.click_button(button):
                self.confirm_submission()
        else:
            self.print('Simulating submission')

        self.close_driver()

    def click_button_impl(self, button, method=1):
        status = False
        if method == 1:
            try:
                button.click()
                status = True
            except StaleElementReferenceException:
                self.print('StaleElementReferenceException occurred, but likely button still was pressed')
            except:
                self.print('Unable to click submit button. Attempting another click...')

        elif method == 2:
            try:
                #self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self._driver.execute_script("arguments[0].click();", button)
                status = True
            except:
                self.print('Unable to perform secondary click method! Could not enter giveaway')

        return status

    def click_button(self, button):
        status = self.click_button_impl(button, 2)
        if not status:
            status = self.click_button_impl(button, 1)

        return status

    def confirm_submission(self):
        # pause for short time to manually verify submission, if desired
        if not self.no_delay:
            time.sleep(5)

        self.is_entered = self.confirm_submission_page()
        if self.is_entered:
            self.print('Entered Giveaway')

    # real implementation is in child classes
    def confirm_submission_page(self):
        return True

    def close_driver(self):

        try:
            if self._driver is not None:
                self._driver.close()
        except:
            self.print('Web page could not be closed!')

        try:
            if self._driver is not None:
                self._driver.quit()
        except:
            self.print('Driver could not be quit!')


# Generic entry class for First name, Last name, email fields
class FirstLastEmailGiveawayEntry(GiveawayEntry):
    first_name_id = ''
    last_name_id = ''
    email_id = ''
    submit_button_id = ''

    # Fill and submit process
    def fill_and_submit(self, person):
        # Fill form
        filled_first_name = self.fill_textbox(self.first_name_id, person.first_name)
        filled_last_name = self.fill_textbox(self.last_name_id, person.last_name)
        filled_email = self.fill_textbox(self.email_id, person.email)

        if not filled_first_name or not filled_last_name or not filled_email:
            return False

        # Submit form
        found_submit = False
        try:
            button = self._driver.find_element_by_id(self.submit_button_id)
            found_submit = True
        except:
            self.print('Unable to find submit element {}'.format(self.submit_button_id))

        # TODO: improve quick fix of trying a second time. Look into polling
        if not found_submit:
            try:
                button = self._driver.find_element_by_id(self.submit_button_id)
                self.print('Eventually found submit element {}'.format(self.submit_button_id))
                found_submit = True
            except:
                self.print('Unable to find submit element {}'.format(self.submit_button_id))

        if found_submit:
            self.click_submit_button(button)

        return found_submit


# Entry class for SteamyKitchen.com giveaways
class SteamyKitchenEntry(FirstLastEmailGiveawayEntry):
    def __init__(self, url, expiration_date, rating, num_entries=1):

        # Fill form
        super().__init__(url, expiration_date, rating, num_entries)

        # define ids
        self.first_name_id = 'first_name'
        self.last_name_id = 'last_name'
        self.email_id = 'email'
        self.submit_button_id = 'skg_submit_button'

    def init_driver(self):
        status = super().init_driver()

        #driver = webdriver.Chrome()
        #driver.get(self.url)
        p_element = self._driver.find_elements_by_xpath('//*[contains(@id, \'vs_widget\')]')
        src_link = p_element[0].get_attribute('src')
        # print(src_link)

        # init new webdriver for javascript generated page
        # TODO: create a helper to generate chrome options to use here as well as the main page
        chrome_options = Options()
        chrome_options.headless = self.use_headless
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(src_link)

        # swap webdrivers
        self._orig_driver = self._driver
        self._driver = driver

        if False:
            # swap urls
            self.orig_url = self.url
            self.url = src_link

        #self.remove_sk_ads(3)

        return status

    # fill and submit specific to Steamy Kitchen giveaways
    def fill_and_submit(self, person):

        # TODO: generalize this process with a submit by textbox flag rather than an entirely different process
        # Fill form
        self.fill_textbox(self.first_name_id, person.first_name)
        self.fill_textbox(self.last_name_id, person.last_name)
        self.fill_textbox(self.email_id, person.email)

        submitted = self.submit_from_textbox(self.email_id)

        if submitted:
            self.confirm_submission()
        self.close_driver()

        # additionally, close original pages webdriver
        self.close_orig_driver()

        return submitted

    def close_orig_driver(self):

        try:
            if self._orig_driver is not None:
                self._orig_driver.close()
        except:
            self.print('Orig Web page could not be closed!')

        try:
            if self._orig_driver is not None:
                self._orig_driver.quit()
        except:
            self.print('Orig Driver could not be quit!')

    def deselect_subscribe_checkbox(self):
        # should have the correct driver already before calling this method
        # first determine whether the checkbox is selected/deselected
        # Either toggle if selected or explicitly deselect checkbox
        pass

    def enter_giveaway_with_enter(self):
        # need to specialize how the giveaway is entered, just like leites does
        pass

    def remove_sk_ads(self, sleep_time=0):

        if sleep_time > 0:
            self.print("Sleeping for {} seconds...setup to remove ads".format(sleep_time))
        time.sleep(sleep_time)

        if not self.ads_removed[1]:
            # Attempt to close any ads on the page that might prevent fields to fill
            try:
                popmake_close_element = self._driver.find_element_by_class_name('pum-close')
                popmake_close_element.click()
                self.ads_removed[1] = True
            except:
                self.print('Unable to find any popmake popups')

    def confirm_submission_page(self):
        # https://steamykitchen.com/giveaway-confirmation
        # TODO: at least verify that new webpage is correct
        self.print('Confirm submission page')
        return True

    def close_driver(self):
        # close the driver under use
        super().close_driver()

        # close the original driver as well
        self._orig_driver.close()


# Entry class for GlutenFree.com giveaways
class GlutenFreeEntry(FirstLastEmailGiveawayEntry):
    def __init__(self, url, expiration_date, rating, num_entries=1):
        # Fill form
        super().__init__(url, expiration_date, rating, num_entries)
        self.first_name_id = 'input_1_1'
        self.last_name_id = 'input_1_2'
        self.email_id = 'input_1_3'
        self.submit_button_id = 'gform_submit_button_1'

    # Prefill process
    def prefill(self, person):
        # uncheck all newsletter and subscription boxes
        unchecked_newsletter = self.uncheck_box('choice_1_5_1')
        if unchecked_newsletter:
            self.print('Chose not to subscribe to newsletter')
        unchecked_other = self.uncheck_box('choice_1_5_2')
        if unchecked_other:
            self.print('Chose not to subscribe to other communication')
        return unchecked_newsletter and unchecked_other

    def confirm_submission_page(self):
        return True


# Entry class for LeitesCulinaria.com giveaways
class LeitesCulinariaEntry(GiveawayEntry):
    extra_entered = False
    num_extra_entries = 0

    # Fill and submit process specific to Leites Culinaria
    def fill_and_submit(self, person):

        # Fill form
        self.fill_textbox('giveaway_entry_name', person.full_name)
        self.fill_textbox('giveaway_entry_email', person.email)

        submitted = self.submit_from_textbox('giveaway_entry_email')

        # TODO: check for number of entries so far and don't skip if less than max entries
        if not LeitesCulinariaEntry.extra_entered and (LeitesCulinariaEntry.num_extra_entries < 2):
            LeitesCulinariaEntry.extra_entered = True
            self.fill_textbox('input_2932_1', person.full_name)
            self.fill_textbox('input_2932_2', person.email)
            self.submit_from_textbox('input_2932_2')
            LeitesCulinariaEntry.num_extra_entries += 1

        if submitted:
            self.confirm_submission()
        self.close_driver()

        return submitted

    def confirm_submission_page(self):
        return True
