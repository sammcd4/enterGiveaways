import giveaway.gather as g
import datetime
import time
from datetime import date


def remove_expired():
    giveaway_info_file = 'GiveawayInfo.txt'
    a_file = open(giveaway_info_file, "r")
    lines = a_file.readlines()
    a_file.close()

    new_file = open(giveaway_info_file, "w")
    found_expired = False
    for line in lines:
        # get today's date
        today = date.today()

        # get expiration date
        [expiration_date, rating, num_entries, url_str] = line.split(' ')
        [y, m, d] = expiration_date.split('-')
        expiration_datetime = date(int(y), int(m), int(d))

        # only write the ones that have not yet expired
        if today <= expiration_datetime:
            is_valid = True
            new_file.write(line)
        else:
            if not found_expired:
                print('Checking for expired giveaways...')
                found_expired = True
            print(line)

    if not found_expired:
        print('No giveaways have expired')
    new_file.close()


if __name__ == "__main__":
    # first, remove all expired giveaways
    remove_expired()
    g.gather()