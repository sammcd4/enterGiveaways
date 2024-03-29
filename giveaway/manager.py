import giveaway.person as gp
import giveaway.entry as ge
import time
import random
import threading


class GiveawayEntrant:
    person = []
    giveaways = []
    today = ''
    delay = 8  # seconds of delay between giveaway entries
    delay_noise = 4  # seconds of delay noise (magnitude of randomization)
    no_delay = False
    able_to_automate_SK = False

    def __init__(self, url_file, person):
        self.person = person
        from datetime import date
        import os

        if self.no_delay:
            self.delay = 0
            self.delay_noise = 0

        # get today's date
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")

        # read urls of giveaways to enter
        with open(url_file, 'r') as f:
            data = f.readlines()

            # TODO: Use for line in f instead of f.readlines()
            # Can potentially consolidate logic in for d in data loop

        # read urls of giveaways entered today
        entered_filename = self.get_entered_filename()
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
                print('{} already entered {} today'.format(person.first_name, url_str))
            else:
                # TODO Create a GiveawayLauncher class that will always determine whether to automate or launch the giveaway
                # TODO Support focusing particular site
                # TODO Support focusing particular person
                # if self.person.first_name != 'Sam':
                #     print('Skipping giveaway because I am not Sam')
                #     continue
                if self.able_to_automate_SK and 'steamykitchen.com' in url_str:
                    print('{} Creating new SteamyKitchen giveaway for {}'.format(person.first_name, url_str))
                    self.giveaways.append(ge.SteamyKitchenEntry(url_str, expire_date, rating, num_entries))
                elif 'leitesculinaria.com' in url_str:
                    self.giveaways.append(ge.LeitesCulinariaEntry(url_str, expire_date, rating, num_entries))
                elif 'simplygluten-free.com' in url_str:
                    self.giveaways.append(ge.GlutenFreeEntry(url_str, expire_date, rating, num_entries))

    # get entered filename matching the current date and person
    def get_entered_filename(self):
        from datetime import date
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")
        return 'logs/{}.entered'.format(today_str + '-' + self.person.first_name)

    def enter_giveaways(self):

        for g in self.giveaways:
            # open entered giveaways log file for writing

            # TODO Test log multiple days in single run
            if g.actually_enter:
                entered_filename = self.get_entered_filename()
            else:
                entered_filename = self.get_entered_filename() + '-test'

            with open(entered_filename, 'a') as f:
                g.enter_giveaway(self.person)
                if not g.no_delay:
                    time.sleep(self.delay + self.delay_noise * random.random())
                if g.is_entered:
                    print('\tWriting to {}'.format(entered_filename))
                    f.write('{}\n'.format(g.url))


class GiveawayManager:
    entrants = []
    delay = 50  # seconds of delay between giveaway entries
    delay_noise = 30  # seconds of delay noise (magnitude of randomization)
    multithreaded = True

    def __init__(self, url_file, people):

        # Create list of entrants
        for p in people:
            entrant = GiveawayEntrant(url_file, p)
            self.entrants.append(entrant)

    def run(self):
        # TODO here where we'd create multiple threads
        for entrant in self.entrants:
            if self.multithreaded:
                x = threading.Thread(target=entrant.enter_giveaways)
                x.start()
            else:
                entrant.enter_giveaways()
                time.sleep(self.delay + self.delay_noise * random.random())


def bulk_operation():
    with open('GiveawayInfo.txt', 'r') as f:
        data = f.readlines()

    # TODO: limit amount of time .entered file is open
    for f in data:
        print(f)

    # rewrite info
    with open('GiveawayInfo.txt', 'w') as f:
        for line in data:
            link_idx = line.find('https')
            new_line = line[:link_idx] + '1 ' + line[link_idx:] + '\n'
            f.write(new_line)
