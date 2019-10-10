import giveaway.person as gp
import giveaway.entry as ge
import time
import random


class GiveawayEntrant:
    person = []
    giveaways = []
    today = ''
    delay = 15  # seconds of delay between giveaway entries
    delay_noise = 5  # seconds of delay noise (magnitude of randomization)

    def __init__(self, url_file, person):
        self.person = person
        from datetime import date
        import os

        # get today's date
        today = date.today()
        self.today = today.strftime("%Y-%m-%d")

        # read urls of giveaways to enter
        with open(url_file, 'r') as f:
            data = f.readlines()

        # read urls of giveaways entered today
        entered_filename = 'logs/{}.entered'.format(self.today + '-' + self.person.first_name)
        entered_data = []
        if os.path.isfile(entered_filename):
            with open(entered_filename, "r") as f:
                entered_data = f.readlines()

            entered_data = [line.rstrip('\n') for line in entered_data]

        # cleanup url data and create giveaway entries
        for d in data:
            data_str = d.replace("\n", "")
            [expire_date, rating, url_str] = data_str.split(' ')
            print('url_str in giveaway data is {}'.format(url_str))

            if url_str in entered_data:
                print('Already entered {} today'.format(url_str))
            else:
                if 'steamykitchen.com' in url_str:
                    print('Creating new SteamyKitchen giveaway for {}'.format(url_str))
                    self.giveaways.append(ge.SteamyKitchenEntry(url_str, expire_date, rating))
                elif 'leitesculinaria.com' in url_str:
                    self.giveaways.append(ge.LeitesCulinariaEntry(url_str, expire_date, rating))

    def enter_giveaways(self):
        # open entered giveaways log file for writing
        entered_filename = 'logs/{}.entered'.format(self.today + '-' + self.person.first_name)
        writefile = open(entered_filename, 'a')

        for g in self.giveaways:
            g.enter_giveaway(self.person)
            time.sleep(self.delay + self.delay_noise * random.random())
            if g.isEntered:
                print('Writing {} to logs/{}.entered'.format(g.url, self.today + '-' + self.person.first_name))
                writefile.write('{}\n'.format(g.url))

        writefile.close()


class GiveawayManager:
    entrants = []
    delay = 150  # seconds of delay between giveaway entries
    delay_noise = 50  # seconds of delay noise (magnitude of randomization)

    def __init__(self, url_file, people):

        # Create list of entrants
        for p in people:
            self.entrants.append(GiveawayEntrant(url_file, p))

    def run(self):
        for entrant in self.entrants:
            entrant.enter_giveaways()
            time.sleep(self.delay + self.delay_noise * random.random())
