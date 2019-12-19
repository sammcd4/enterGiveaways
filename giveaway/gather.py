import requests
from bs4 import BeautifulSoup

class GiveawayGatherer:
    # Class used to automate gathering giveaway sites and populate the GiveawayInfo.txt file

    file = '~/PycharmProjects/enterGiveaways/GiveawayInfo.txt'

    def gather(self):
        print('Gathering all new giveaways from Steamy Kitchen...')
        giveaway_page = 'https://steamykitchen.com/current-giveaways'

        html = requests.get(giveaway_page).text

        soup = BeautifulSoup(html, "lxml")
        giveaway_posts = soup.findAll("article", {"class": "item skg-archive-post"})
        for gp in giveaway_posts:
            print("Giveaway link: " + gp.find('a').text)
            # print("Address: " + r.find("div", {'class': 'address'}).text)
            # print("Website: " + r.find_all("div", {'class': 'pageMeta-item'})[3].text)