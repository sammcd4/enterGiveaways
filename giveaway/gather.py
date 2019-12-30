import requests
from bs4 import BeautifulSoup


class GiveawayGatherer:
    # Class used to automate gathering giveaway sites and populate the GiveawayInfo.txt file

    file = '~/PycharmProjects/enterGiveaways/GiveawayInfo.txt'

    def __init__(self, file_url):
        self.file_url = file_url

    def gather(self):
        print('Gathering all new giveaways from Steamy Kitchen...')
        giveaway_page = 'https://steamykitchen.com/current-giveaways'

        with open(self.file_url, 'r') as f:
            current_giveaway_data = f.readlines()
        # print(current_giveaway_data)

        soup = self.getSoup(giveaway_page)
        giveaway_posts = soup.findAll("div", {"class": "item skg-archive-post"})

        with open(self.file_url, 'a') as file:

            for gp in giveaway_posts:
                giveaway_link = gp.find('a').get('href')
                # print("Giveaway link: " + giveaway_link)

                # extract giveaway expiration from webpage with another soup
                soup_giveaway = self.getSoup(giveaway_link)

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

    def getSoup(self, link):
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")
        return soup