import giveaway.person as gp
import giveaway.entry as ge
import time
import random


class GiveawayManager:
    giveaways = []
    today = ''
    delay = 15  # seconds of delay between giveaway entries
    delay_noise = 5  # seconds of delay noise (magnitude of randomization)

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
            url_str = d.replace("\n", "")
            [expire_date, rating, url] = url_str.split(' ')

            if url in entered_data:
                print('Already entered {} today'.format(url))
            else:
                if 'steamykitchen.com' in url:
                    self.giveaways.append(ge.SteamyKitchenEntry(url, expire_date, rating))
                elif 'leitesculinaria.com' in url:
                    self.giveaways.append(ge.LeitesCulinariaEntry(url, expire_date, rating))

    def run(self):
        # open entered giveaways log file for writing
        entered_filename = 'logs/{}.entered'.format(self.today)
        writefile = open(entered_filename, 'a')

        for g in self.giveaways:
            sam = gp.Person("Sam", "McDonald", "whitehops@gmail.com")
            g.enter_giveaway(sam)
            time.sleep(self.delay + self.delay_noise*random.random())
            if g.isEntered:
                writefile.write('{}\n'.format(g.url))

        writefile.close()
