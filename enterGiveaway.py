import giveaway.person as gp
import giveaway.manager as gm

"""
bulk operation on info file
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
"""

# Update all giveaways
update_giveaways = True

if update_giveaways:
    from giveaway.gather import GiveawayGatherer
    g = GiveawayGatherer('GiveawayInfo.txt')
    g.gather()

# Choose people to enter giveaways for
people = gp.readpeoplefile('Entrants.txt')

# Choose a list of urls of giveaways to enter
gm = gm.GiveawayManager('GiveawayInfo.txt', people)
gm.run()
