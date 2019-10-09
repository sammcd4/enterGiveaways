import giveaway.person as gp
import giveaway.manager as gm

# Choose people to enter giveaways for
people = [gp.Person('Sam', 'McDonald', 'whitehops@gmail.com')]
# people.append(gp.Person('Melissa', 'McDonald', 'melis.lott@gmail.com'))
people.append(gp.Person('Julia', 'McDonald', 'juliamcdonald88@gmail.com'))

# Choose a list of urls of giveaways to enter
gm = gm.GiveawayManager('GiveawayInfo.txt', people)
gm.run()
