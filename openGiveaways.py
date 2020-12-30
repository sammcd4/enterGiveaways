import webbrowser
import time
import os
import random


def open_incognito_tab(url):
    system_command = "open -na \"Google Chrome\" --args -incognito {}".format(url)
    #print(system_command)
    os.system(system_command)


if __name__ == "__main__":
    use_incognito = True
    giveaway_info = 'GiveawayInfo.txt'
    with open(giveaway_info, 'r') as f:
        for line in f:
            [expire_date, rating, num_entries, url] = line.split(' ')

            # skip any leitesculinaria giveaways, because they can be automated
            if 'leites' in url:
                continue

            # skip any simply gluten free giveaways, because they can be automated
            if 'simplygluten-free' in url:
                continue

            if random.randint(1, 10) > int(rating):
                print('Due to rating of {}/10 skipping {}'.format(int(rating), url))
                continue

            for i in range(int(num_entries)):
                url = line[line.find('http'):]
                print('Opening {}'.format(url))
                if use_incognito:
                    #chrome_path = 'open -na /Applications/Google\ Chrome.app %s --args -incognito'
                    #webbrowser.get(chrome_path).open_new_tab(url)

                    open_incognito_tab(url)
                else:
                    webbrowser.open_new_tab(url)
                time.sleep(15)
