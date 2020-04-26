import webbrowser
import time

giveaway_info = 'GiveawayInfo.txt'
with open(giveaway_info, 'r') as f:
    for line in f:
        url = line[line.find('http'):]
        print('Opening {}'.format(url))
        webbrowser.open_new_tab(url)
        time.sleep(20)