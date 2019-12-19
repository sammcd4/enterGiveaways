import giveaway.person as gp
import giveaway.manager as gm

# Update all giveaways
if False:
    from giveaway.gather import GiveawayGatherer
    g = GiveawayGatherer()
    g.gather()

else:

    # Choose people to enter giveaways for
    people = [gp.Person('Sam', 'McDonald', 'whitehops@gmail.com')]
    # people.append(gp.Person('Melissa', 'McDonald', 'melis.lott@gmail.com'))
    # people = []
    people.append(gp.Person('Julia', 'Larson', 'juliamcdonald88@gmail.com'))

    # Choose a list of urls of giveaways to enter
    gm = gm.GiveawayManager('GiveawayInfo.txt', people)
    gm.run()
