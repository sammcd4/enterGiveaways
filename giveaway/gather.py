import requests
from bs4 import BeautifulSoup
import re
import urllib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime


def get_iframe_link(giveaway_link):
    driver = webdriver.Chrome()
    driver.get(giveaway_link)
    # p_element = driver.find_element_by_id(id_='vs_widget')
    p_element = driver.find_elements_by_xpath('//*[contains(@id, \'vs_widget\')]')
    src_link = p_element[0].get_attribute('src')
    print(src_link)

    # cleanup webdriver
    driver.close()

    return src_link


class GiveawayGatherer:
    # Class used to automate gathering giveaway sites and populate the GiveawayInfo.txt file

    file = '~/PycharmProjects/enterGiveaways/GiveawayInfo.txt'

    def __init__(self, file_url):
        self.file_url = file_url

    def has_icon_calendar_class(self, tag):
        return tag.has_attr('class') and not tag.has_attr('id')

    def execute_js(self, script):
        return js2py.eval_js(script)

    def gather(self):
        print('Gathering all new giveaways from Steamy Kitchen...')
        giveaway_page = 'https://steamykitchen.com/current-giveaways'

        with open(self.file_url, 'r') as f:
            current_giveaway_data = f.readlines()
        # print(current_giveaway_data)

        soup = self.getSoup(giveaway_page)
        giveaway_posts = soup.findAll("div", {"class": "item archive-post"})

        with open(self.file_url, 'a') as file:

            for gp in giveaway_posts:
                giveaway_link = gp.find('a').get('href')
                # print("Giveaway link: " + giveaway_link)

                # extract giveaway expiration from webpage with another soup
                soup_giveaway = self.getSoup(giveaway_link)
                giveaway_html = self.getHTML(giveaway_link)

                vsscript_soup = soup_giveaway.findAll('div', id=lambda x: x and x.startswith('vsscript'))
                vs_widget_soup = soup_giveaway.findAll('div', id=lambda x: x and x.startswith('vs_widget'))

                if False:
                    # dead-end code for parsing js code that generates the embedded document
                    src_idx = giveaway_html.find('src="https://app.viralsweep.com')
                    src_re = re.compile('https://app.viralsweep.com\S*"')
                    src_result = src_re.findall(giveaway_html)
                    js_code_url = src_result[0][:-1]
                    js_script = self.getHTML(js_code_url)

                #js_result = self.execute_js(js_script)

                # get link to embedded iframe generated html
                src_link = get_iframe_link(giveaway_link)

                # extract expiration date from the embedded html
                soup_src = self.getSoup(src_link)
                date_section_actual = soup_src.find("i", {'class': 'icon-calendar'})
                giveaway_ends = date_section_actual.next.text
                ends_idx = giveaway_ends.find(' ')
                giveaway_expiration_str = giveaway_ends[ends_idx+1:]
                giveaway_expiration = datetime.datetime.strptime(giveaway_expiration_str, '%m-%d-%Y').strftime('%Y-%m-%d')


                #options = Options()
                #options.headless = True
                #driver = webdriver.Chrome(options=options)
                #driver.get(giveaway_link)


                if False:
                    # This will get the initial html - before javascript
                    html1 = driver.page_source

                    with open('giveaway.html', 'w') as f:
                        f.write(html1)

                    #giveaway_html = giveaway_html.split('\n')

                    #req = urllib.request.Request(giveaway_link)
                    #resp = urllib.request.urlopen(req)
                    #respData = resp.read()
                    #paragraphs = re.findall(r'icon-calendar', str(respData))

                    if 'icon-calendar' in giveaway_html:
                        print('found it')

                    footer_sections = soup_giveaway.findAll("div", {'class': "footer"})
                    for footer in footer_sections:
                        date_section4 = footer.find_all("i", {'class': 'icon-calendar'})

                    date_section5 = soup_giveaway.find_all(re.compile('icon-calendar'))
                    date_section = soup_giveaway.findAll(attrs={'class': "icon-calendar"})
                    date_section3 = soup_giveaway.find_all("i", {'class': "icon-calendar"})
                    date_section2 = soup_giveaway.find_all("div", class_="icon-calendar")

                    form = soup_giveaway.findAll("div", {'id': 'skg-meta'})
                    # form = soup_giveaway.find_all("div", {'class': 'skg-submission-form'})
                    # form = soup_giveaway.findAll("div", {'class': 'skg-submission-form-container'})
                    # print(form)
                    # expiration_paragraph = form.skg_submission_form
                    for f in form:
                        if f is not None:
                            p_text = f.find('p').text
                            # print(p_text)
                            before_str = 'Giveaway Ends: '
                            sidx = p_text.find('Giveaway Ends: ')
                            # print('start idx: {}, end idx: {}'.format(sidx, sidx + len(before_str) + 10))
                            sidx = sidx + len(before_str)
                            giveaway_expiration = p_text[sidx:sidx + 10]
                            # giveaway_expiration = f.find("div", {'class': 'skg-meta'})

                            # print('\tExpires on: ' + giveaway_expiration)
                            # print("Address: " + r.find("div", {'class': 'address'}).text)
                            # print("Website: " + r.find_all("div", {'class': 'pageMeta-item'})[3].text)

                # Now that giveaway info is found, write it to GiveawayInfo.txt
                # if giveaway_link in current_giveaway_data:
                if [i for i in current_giveaway_data if giveaway_link in i]:

                    print("Old giveaway: {}".format(giveaway_link))
                else:
                    print("New giveaway: {}".format(giveaway_link))

                    # Construct and write string to file
                    new_giveaway_line = giveaway_expiration + ' 5 1 ' + giveaway_link + '\n'
                    print(new_giveaway_line)
                    file.write(new_giveaway_line)

        #for link in soup.find_all('a'):
        #   print(link.get('href'))

    def getHTML(self, link):
        return requests.get(link).text

    def getSoup(self, link):
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")
        return soup


def gather():
    g = GiveawayGatherer('GiveawayInfo.txt')
    g.gather()


if __name__ == '__main__':
    gather()
