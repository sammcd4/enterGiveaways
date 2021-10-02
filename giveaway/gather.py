import requests
from bs4 import BeautifulSoup
import re
import urllib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime
import time
from datetime import date
from urllib.request import Request, urlopen
import requests
import ssl


def get_iframe_link(giveaway_link):
    driver = webdriver.Chrome()
    driver.get(giveaway_link)
    # p_element = driver.find_element_by_id(id_='vs_widget')
    p_element = driver.find_elements_by_xpath('//*[contains(@id, \'vs_widget\')]')
    src_link = ''
    try:
        src_link = p_element[0].get_attribute('src')
        #print(src_link)
    except:
        print('Unable to get src attribute from iframe link')

    # cleanup webdriver
    driver.close()

    return src_link


class GiveawayGatherer:
    # Class used to automate gathering giveaway sites and populate the GiveawayInfo.txt file

    file = '~/PycharmProjects/enterGiveaways/GiveawayInfo.txt'

    def __init__(self, file_url):
        self.file_url = file_url
        self.debug = True

    def current_giveaway_data(self):
        with open(self.file_url, 'r') as f:
            current_giveaway_data = f.readlines()
        return current_giveaway_data

    def get_giveaway_posts(self, giveaway_page):
        ssl_verify = False
        if 'simplygluten-free' in giveaway_page:
            print('\nGathering all new giveaways from Simply Gluten Free...')
            ssl_verify = True
            element_type = 'div'
            element_class = 'post-s1'
        elif 'steamykitchen' in giveaway_page:
            print('\nGathering all new giveaways from Steamy Kitchen...')
            element_type = 'article'
            element_class = 'category-steamy-kitchen-giveaways'
        elif 'leitesculinaria' in giveaway_page:
            element_type = 'article'
            element_class = 'post recipes'

        soup = self.get_soup(giveaway_page, ssl_verify=ssl_verify)
        return soup.findAll(element_type, {"class": element_class})

    def get_new_giveaway(self, current_giveaway_data, giveaway_link, giveaway_expiration, num_entries=1, matches=None, exclude=None):
        if [i for i in current_giveaway_data if giveaway_link in i]:
            if self.debug:
                print("Old giveaway: {}".format(giveaway_link))
        else:
            # filter out any that don't match
            if matches and not any(x in giveaway_link for x in matches):
                return None

            # filter out any that do match the exclude list
            if exclude and any(x in giveaway_link for x in exclude):
                return None

            print('New giveaway:')

            # Construct and write string to file
            if 'leites' in giveaway_link:
                num_entries = 2
            new_giveaway_line = f'{giveaway_expiration} 7 {num_entries} {giveaway_link}\n'
            print(new_giveaway_line)

            return new_giveaway_line

    def gather_gluten_free(self):
        current_giveaway_data = self.current_giveaway_data()

        main_giveaway_page = 'https://simplygluten-free.com/giveaways/'
        giveaway_posts = self.get_giveaway_posts(main_giveaway_page)

        with open(self.file_url, 'a') as file:
            for gp in giveaway_posts:
                giveaway_link = gp.find('h2').find('a').get('href')
                #print(giveaway_link)

                # extract giveaway expiration from webpage with another soup
                soup_giveaway = self.get_soup(giveaway_link, ssl_verify=True)

                entry_content = soup_giveaway.find('div', {"class": "blog-post-single-content"})
                expiration_date_str = soup_giveaway.body.find(text=re.compile('This giveaway ends on'))
                expiration_date_str = str(expiration_date_str).replace('This giveaway ends on ', '')
                if not expiration_date_str or expiration_date_str == 'None':
                    expiration_date_str = soup_giveaway.body.find(text=re.compile('Contest ends'))
                    expiration_date_str = str(expiration_date_str).replace('Contest ends ', '')
                if expiration_date_str[-1] == '.':
                    expiration_date_str = expiration_date_str[0:-1]

                # replace Sept with Sep
                expiration_date_str = expiration_date_str.replace('Sept', 'Sep')
                if self.debug:
                    print(expiration_date_str)

                # get expiration date string using %b %d, %Y format
                b_flag = False
                expire_datetime = None
                #print(f'expiration_date_str={expiration_date_str}')
                try:
                    expire_datetime = datetime.datetime.strptime(expiration_date_str, '%b %d, %Y')
                except:
                    b_flag = True

                try:
                    expire_datetime = datetime.datetime.strptime(expiration_date_str, '%B %d, %Y')
                except:
                    b_cap_flag = True

                if not expire_datetime:
                    m_flag = False
                    try:
                        expire_datetime = datetime.datetime.strptime(expiration_date_str, '%m %d, %Y')
                    except:
                        m_flag = True

                if not expire_datetime:
                    if b_flag:
                        print(f'Unable to convert {expiration_date_str} to datetime object with %b %d, %Y')
                    if b_cap_flag:
                        print(f'Unable to convert {expiration_date_str} to datetime object with %B %d, %Y')
                    if m_flag:
                        print(f'Unable to convert {expiration_date_str} to datetime object with %m %d, %Y')
                    else:
                        print(f'Unable to convert {expiration_date_str} using any existing methods')

                if expire_datetime < datetime.datetime.today():
                    expected_year = datetime.datetime.today().year + 1
                    if self.debug:
                        print(f'Expiration date is outdated. year is {expire_datetime.year}. Moving up year to {expected_year}.')
                    expire_datetime = expire_datetime.replace(year=expected_year)

                giveaway_expiration = f'{expire_datetime.year}-{expire_datetime.month}-{expire_datetime.day}'
                if self.debug:
                    print(giveaway_expiration)

                # Now that giveaway info is found, write it to GiveawayInfo.txt
                # if giveaway_link in current_giveaway_data:
                new_giveaway_line = self.get_new_giveaway(current_giveaway_data, giveaway_link, giveaway_expiration)
                if new_giveaway_line:
                    file.write(new_giveaway_line)

    def gather_leites(self):
        print('\nGathering all new giveaways from Leites Culinaria...')
        main_giveaway_page = 'https://leitesculinaria.com/category/giveaways'
        soup = self.get_soup(main_giveaway_page)

        # get number of pages
        pages_elements = soup.findAll("div", {"class": "archive-description"})
        # should just be one so get first
        pages = pages_elements[0].find('p').findAll('a')
        giveaway_pages = [page.get('href') for page in pages]
        giveaway_pages.append(main_giveaway_page)
        #print(giveaway_pages)

        # iterate over all pages of giveaways
        for giveaway_page in giveaway_pages:

            with open(self.file_url, 'r') as f:
                current_giveaway_data = f.readlines()

            giveaway_posts = self.get_giveaway_posts(giveaway_page)

            with open(self.file_url, 'a') as file:
                for gp in giveaway_posts:
                    giveaway_link = gp.find('div').find('a').get('href')
                    #print(giveaway_link)

                    # extract giveaway expiration from webpage with another soup
                    try:
                        soup_giveaway = self.get_soup(giveaway_link)
                    except:
                        print(f'There was a problem with get_soup')
                        continue

                    entry_content = soup_giveaway.find('div', {"class": "entry-content"})
                    expiration_date_str = soup_giveaway.body.findAll(text=re.compile('Deadline is'))

                    expiration_date_str = str(expiration_date_str).replace('. Deadline is 11:59PM ET ', '')
                    expiration_date_str = expiration_date_str.replace("['", "")
                    expiration_date_str = expiration_date_str.replace(".']", "")
                    #print(expiration_date_str)
                    digits = expiration_date_str.split('.')
                    #print(digits)

                    # TODO parse number of times can be entered
                    if len(digits) < 3:
                        print(f'Problem with date digits: {digits}')
                        continue
                    giveaway_expiration = '20{}-{}-{}'.format(digits[2], digits[0], digits[1])

                    # Now that giveaway info is found, write it to GiveawayInfo.txt
                    # if giveaway_link in current_giveaway_data:
                    brands = ['oxo', 'hamilton', 'cuisinart', 'all-clad', 'calphalon', 'anolon', 'instant-pot']
                    items = ['ipad', 'waffle', 'air-fryer', 'steak', 'set', 'wood', 'pair', 'skillet', 'knife',
                             'stainless']
                    exclude_list = ['coffee']
                    new_giveaway_line = self.get_new_giveaway(current_giveaway_data, giveaway_link, giveaway_expiration, matches=(brands + items), exclude=exclude_list)
                    if new_giveaway_line:
                        file.write(new_giveaway_line)

    def gather_steamy_kitchen(self):
        current_giveaway_data = self.current_giveaway_data()

        main_giveaway_page = 'https://steamykitchen.com/category/steamy-kitchen-giveaways'
        giveaway_posts = self.get_giveaway_posts(main_giveaway_page)

        with open(self.file_url, 'a') as file:
            count = 0
            for gp in giveaway_posts:
                giveaway_link = gp.find('a').get('href')
                if self.debug:
                    print("Giveaway link: " + giveaway_link)

                # get link to embedded iframe generated html
                src_link = get_iframe_link(giveaway_link)

                # extract expiration date from the embedded html
                try:
                    soup_src = self.get_soup(src_link)
                    date_section_actual = soup_src.find("i", {'class': 'icon-calendar'})
                except:
                    print('Unable to retrieve date element')

                try:
                    giveaway_ends = date_section_actual.next.text
                    if self.debug:
                        print('Giveaway ends:')
                        print(giveaway_ends)
                    ends_idx = giveaway_ends.find(' ')
                    if self.debug:
                        print('ends_idx')
                        print(ends_idx)
                    giveaway_expiration_str = giveaway_ends[ends_idx+1:]
                    if self.debug:
                        print(giveaway_expiration_str)
                    giveaway_datetime = datetime.datetime.strptime(giveaway_expiration_str, '%m-%d-%Y')
                    if self.debug:
                        print(giveaway_datetime)
                    giveaway_expiration = giveaway_datetime.strftime('%Y-%m-%d')
                except:
                    print('Unable to parse expiration date from the embedded html')
                    giveaway_expiration = 'no_expiration_found'

                # Now that giveaway info is found, write it to GiveawayInfo.txt
                exclude_list = ['coffee']
                new_giveaway_line = self.get_new_giveaway(current_giveaway_data, giveaway_link, giveaway_expiration, exclude=exclude_list)
                if new_giveaway_line:
                    count = 0 # reset count
                    file.write(new_giveaway_line)
                else:
                    # short-circuit giveaway lookup because most likely passed all the new ones
                    if count > 10:
                        return
                    count += 1

    @staticmethod
    def get_soup(link, ssl_verify=False):
        if ssl_verify:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

            context = ssl._create_unverified_context()
            req = Request(link, headers=headers)
            webpage = urlopen(req, context=context).read()
        else:
            webpage = requests.get(link).text

        soup = BeautifulSoup(webpage, "html.parser")
        return soup


def gather(exclude_steamy_kitchen=False):
    g = GiveawayGatherer('GiveawayInfo.txt')
    g.gather_gluten_free()
    g.gather_leites()
    if not exclude_steamy_kitchen:
        g.gather_steamy_kitchen()


if __name__ == '__main__':
    gather()
