import giveaway.person as gp
import giveaway.manager as gm

# Update all giveaways
if False:
    import giveaway.gather as g
    g.gather()

# Choose people to enter giveaways for
people = gp.readpeoplefile('Entrants.txt')

# Choose a list of urls of giveaways to enter
gm = gm.GiveawayManager('GiveawayInfo.txt', people)
gm.run()
