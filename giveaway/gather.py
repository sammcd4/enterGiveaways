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
        print(src_link)
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
        self.debug = False

    def has_icon_calendar_class(self, tag):
        return tag.has_attr('class') and not tag.has_attr('id')

    def execute_js(self, script):
        return js2py.eval_js(script)

    def gather_gluten_free(self):
        print('Gathering all new giveaways from Simply Gluten Free...')
        main_giveaway_page = 'https://simplygluten-free.com/giveaways/'
        soup = self.get_soup(main_giveaway_page, ssl_verify=True)

        with open(self.file_url, 'r') as f:
            current_giveaway_data = f.readlines()

        # only one page right now
        giveaway_posts = soup.findAll("div", {"class": "post-s1"})

        with open(self.file_url, 'a') as file:
            for gp in giveaway_posts:
                giveaway_link = gp.find('h2').find('a').get('href')
                print(giveaway_link)

                # extract giveaway expiration from webpage with another soup
                soup_giveaway = self.get_soup(giveaway_link, ssl_verify=True)

                entry_content = soup_giveaway.find('div', {"class": "blog-post-single-content"})
                expiration_date_str = soup_giveaway.body.find(text=re.compile('This giveaway ends on'))
                expiration_date_str = str(expiration_date_str).replace('This giveaway ends on ', '')
                if not expiration_date_str:
                    expiration_date_str = soup_giveaway.body.find(text=re.compile('Contest ends'))
                    expiration_date_str = str(expiration_date_str).replace('Contest ends ', '')
                if self.debug:
                    print(expiration_date_str)

                # get expiration date string using %b %d, %Y format
                b_flag = False
                try:
                    expire_datetime_object = datetime.datetime.strptime(expiration_date_str, '%b %d, %Y')
                    #print(expire_datetime_object)
                except:
                    b_flag = True

                if not expire_datetime_object:
                    m_flag = False
                    try:
                        expire_datetime_object = datetime.datetime.strptime(expiration_date_str, '%m %d, %Y')
                        #print(expire_datetime_object)
                    except:
                        m_flag = True

                    if not expire_datetime_object:
                        if b_flag:
                            print(f'Unable to convert {expiration_date_str} to datetime object with %b %d %Y')
                        elif m_flag:
                            print(f'Unable to convert {expiration_date_str} to datetime object with %m %d %Y')
                        else:
                            print(f'Unable to convert {expiration_date_str} using any existing methods')

                if expire_datetime_object < datetime.datetime.today():
                    expected_year = datetime.datetime.today().year + 1
                    print(f'Expiration date is outdated. year is {expire_datetime_object.year}. Moving up year to {expected_year}.')
                    expire_datetime_object = expire_datetime_object.replace(year=expected_year)

                giveaway_expiration = '{}-{}-{}'.format(expire_datetime_object.year, expire_datetime_object.month, expire_datetime_object.day)
                if self.debug:
                    print(giveaway_expiration)

                # Now that giveaway info is found, write it to GiveawayInfo.txt
                # if giveaway_link in current_giveaway_data:
                if [i for i in current_giveaway_data if giveaway_link in i]:
                    print("Old giveaway: {}".format(giveaway_link))
                else:
                    print("New giveaway: {}".format(giveaway_link))

                    # Construct and write string to file
                    new_giveaway_line = giveaway_expiration + ' 7 1 ' + giveaway_link + '\n'
                    print(new_giveaway_line)

                    file.write(new_giveaway_line)

    def gather_leites(self):
        print('Gathering all new giveaways from Leites Culinaria...')
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

            giveaway_posts = soup.findAll("article", {"class": "post recipes"})

            with open(self.file_url, 'a') as file:
                for gp in giveaway_posts:
                    giveaway_link = gp.find('div').find('a').get('href')
                    #print(giveaway_link)

                    # extract giveaway expiration from webpage with another soup
                    soup_giveaway = self.get_soup(giveaway_link)

                    entry_content = soup_giveaway.find('div', {"class": "entry-content"})
                    expiration_date_str = soup_giveaway.body.findAll(text=re.compile('Deadline is'))

                    expiration_date_str = str(expiration_date_str).replace('. Deadline is 11:59PM ET ', '')
                    expiration_date_str = expiration_date_str.replace("['", "")
                    expiration_date_str = expiration_date_str.replace(".']", "")
                    #print(expiration_date_str)
                    digits = expiration_date_str.split('.')
                    #print(digits)

                    giveaway_expiration = '20{}-{}-{}'.format(digits[2], digits[0], digits[1])

                    # Now that giveaway info is found, write it to GiveawayInfo.txt
                    # if giveaway_link in current_giveaway_data:
                    if [i for i in current_giveaway_data if giveaway_link in i]:
                        print("Old giveaway: {}".format(giveaway_link))
                    else:
                        # need to filter some of these before writing everything
                        brands = ['oxo', 'hamilton', 'cuisinart', 'all-clad', 'calphalon', 'anolon', 'instant-pot']
                        items = ['ipad', 'waffle', 'air-fryer', 'steak', 'set', 'wood', 'pair', 'skillet', 'knife', 'stainless']
                        matches = brands + items
                        if any(x in giveaway_link for x in matches):
                            print("New giveaway: {}".format(giveaway_link))

                            # Construct and write string to file
                            new_giveaway_line = giveaway_expiration + ' 7 1 ' + giveaway_link + '\n'
                            print(new_giveaway_line)

                            file.write(new_giveaway_line)

    def gather(self):
        print('Gathering all new giveaways from Steamy Kitchen...')
        giveaway_page = 'https://steamykitchen.com/category/steamy-kitchen-giveaways'

        with open(self.file_url, 'r') as f:
            current_giveaway_data = f.readlines()
        # print(current_giveaway_data)

        soup = self.get_soup(giveaway_page)
        #giveaway_posts = soup.findAll("div", {"class": "item archive-post"})
        giveaway_posts = soup.findAll("article", {"class": "category-steamy-kitchen-giveaways"})
        if self.debug:
            print(f'DEBUG - All giveaway posts: \n{giveaway_posts}')

        with open(self.file_url, 'a') as file:

            for gp in giveaway_posts:
                giveaway_link = gp.find('a').get('href')
                if self.debug:
                    print("Giveaway link: " + giveaway_link)

                # extract giveaway expiration from webpage with another soup
                soup_giveaway = self.get_soup(giveaway_link)
                giveaway_html = self.get_html(giveaway_link)

                vsscript_soup = soup_giveaway.findAll('div', id=lambda x: x and x.startswith('vsscript'))
                vs_widget_soup = soup_giveaway.findAll('div', id=lambda x: x and x.startswith('vs_widget'))

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
                    ends_idx = giveaway_ends.find(' ')
                    giveaway_expiration_str = giveaway_ends[ends_idx+1:]
                    if self.debug:
                        print(giveaway_expiration_str)
                    giveaway_datetime = datetime.datetime.strptime(giveaway_expiration_str, '%m-%d-%Y')
                    if self.debug:
                        print(giveaway_datetime)
                    giveaway_expiration = giveaway_datetime.strftime('%Y-%m-%d')
                except:
                    print('Unable to extract expiration date from the embedded html')
                    giveaway_expiration = 'no_expiration_found'

                # Now that giveaway info is found, write it to GiveawayInfo.txt
                # if giveaway_link in current_giveaway_data:
                if [i for i in current_giveaway_data if giveaway_link in i]:

                    print("Old giveaway: {}".format(giveaway_link))
                else:
                    print("New giveaway: {}".format(giveaway_link))

                    # Construct and write string to file
                    new_giveaway_line = giveaway_expiration + ' 7 1 ' + giveaway_link + '\n'
                    print(new_giveaway_line)
                    file.write(new_giveaway_line)

    @staticmethod
    def get_html(link):
        text = ''
        try:
            text = requests.get(link).text
        except:
            print("Unable to get link text")
        return text

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


def gather():
    g = GiveawayGatherer('GiveawayInfo.txt')
    g.gather_gluten_free()
    g.gather_leites()
    g.gather()


if __name__ == '__main__':
    gather()
