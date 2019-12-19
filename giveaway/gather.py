import requests
from bs4 import BeautifulSoup


class GiveawayGatherer:
    # Class used to automate gathering giveaway sites and populate the GiveawayInfo.txt file

    file = '~/PycharmProjects/enterGiveaways/GiveawayInfo.txt'

    def gather(self):
        print('Gathering all new giveaways from Steamy Kitchen...')
        giveaway_page = 'https://steamykitchen.com/current-giveaways'

        soup = self.getSoup(giveaway_page)

        giveaway_posts = soup.findAll("div", {"class": "item skg-archive-post"})
        for gp in giveaway_posts:
            giveaway_link = gp.find('a').get('href')
            print("Giveaway link: " + giveaway_link)

            # extract giveaway expiration from webpage with another soup
            soup_giveaway = self.getSoup(giveaway_link)

            form = soup_giveaway.findAll("div", {'class': 'skg-meta'})

            # form = soup_giveaway.findAll("div", {'class': 'skg-submission-form-container'})

            # expiration_paragraph = form.skg_submission_form
            for f in form:
                giveaway_expiration = f.find("div", {'class': 'skg-meta'})
                print('\tExpires on: ' + giveaway_expiration)
                # print("Address: " + r.find("div", {'class': 'address'}).text)
                # print("Website: " + r.find_all("div", {'class': 'pageMeta-item'})[3].text)

        #for link in soup.find_all('a'):
        #   print(link.get('href'))

    def getSoup(self, link):
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")
        return soup