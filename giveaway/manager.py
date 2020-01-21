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
    noDelay = False

    def __init__(self, url_file, person):
        self.person = person
        from datetime import date
        import os

        if self.noDelay:
            self.delay = 0
            self.delay_noise = 0

        # get today's date
        today = date.today()
        self.today = today.strftime("%Y-%m-%d")

        # read urls of giveaways to enter
        with open(url_file, 'r') as f:
            data = f.readlines()

            # TODO: Use for line in f instead of f.readlines()
            # Can potentially consolidate logic in for d in data loop

        # read urls of giveaways entered today
        entered_filename = 'logs/{}.entered'.format(self.today + '-' + self.person.first_name)
        entered_data = []
        if os.path.isfile(entered_filename):
            with open(entered_filename, "r") as f:
                entered_data = f.readlines()

            entered_data = [line.rstrip('\n') for line in entered_data]

        # cleanup url data and create giveaway entries
        self.giveaways = []
        setOfURLs = set()
        for d in data:
            data_str = d.replace("\n", "")
            [expire_date, rating, num_entries, url_str] = data_str.split(' ')
            num_entries = int(num_entries)
            # print('url_str in giveaway data is {}'.format(url_str))

            if url_str in setOfURLs:
                print('Duplicate giveaway ', url_str)
            elif url_str in entered_data:
                print('Already entered {} today'.format(url_str))
            else:
                if 'steamykitchen.com' in url_str:
                    print('{} Creating new SteamyKitchen giveaway for {}'.format(person.first_name, url_str))
                    self.giveaways.append(ge.SteamyKitchenEntry(url_str, expire_date, rating, num_entries))
                elif 'leitesculinaria.com' in url_str:
                    self.giveaways.append(ge.LeitesCulinariaEntry(url_str, expire_date, rating, num_entries))
                elif 'simplygluten-free.com' in url_str:
                    self.giveaways.append(ge.GlutenFreeEntry(url_str, expire_date, rating, num_entries))

    def enter_giveaways(self):

        for g in self.giveaways:
            # open entered giveaways log file for writing
            if g.actually_enter:
                entered_filename = 'logs/{}.entered'.format(self.today + '-' + self.person.first_name)
            else:
                entered_filename = 'logs/{}.entered'.format(self.today + '-' + self.person.first_name + '-test')

            writefile = open(entered_filename, 'a')

            g.enter_giveaway(self.person)
            if not g.noDelay:
                time.sleep(self.delay + self.delay_noise * random.random())
            if g.isEntered:
                print('\tWriting to {}'.format(entered_filename))
                writefile.write('{}\n'.format(g.url))

            writefile.close()


class GiveawayManager:
    entrants = []
    delay = 150  # seconds of delay between giveaway entries
    delay_noise = 50  # seconds of delay noise (magnitude of randomization)

    def __init__(self, url_file, people):

        # Create list of entrants
        for p in people:
            entrant = GiveawayEntrant(url_file, p)
            self.entrants.append(entrant)

    def run(self):
        for entrant in self.entrants:
            entrant.enter_giveaways()
            time.sleep(self.delay + self.delay_noise * random.random())

        # TODO: Print out all expired giveaways here at the end so they can easily be removed?
        #  Or just automate it because manager has access to the GiveawaysInfo.txt file


def bulk_operation():
    with open('GiveawayInfo.txt', 'r') as f:
        data = f.readlines()

    for f in data:
        print(f)

    # rewrite info
    with open('GiveawayInfo.txt', 'w') as f:
        for line in data:
            link_idx = line.find('https')
            new_line = line[:link_idx] + '1 ' + line[link_idx:] + '\n'
            f.write(new_line)
