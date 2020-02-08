# Simple responder bot for /r/JoeRogan

Responds with (mostly legit probably) quotes from Joe Rogan. Can be triggered on /r/cringe and /r/JoeRogan either by saying a specific keyword in the list below or simply by
commenting `!joe`. 

You can opt out of the bot sending you a message by clicking on the link in the footer
or by sending it a message containing `fuck off` either in the subject or body. This will place your account on a permanent blacklist stored in Postgres. You can undo it by sending it a message saying `im sorry` (written as-is, without apostrophes).

The current cooldown period for one user to be replied to is 6 minutes.

## List of phrases it can respond with
```
I get out of breath playing quake.
Have you ever heard the theory that moses and the burning bush was actually him tripping balls from inhaling DMT?
According to my friend Rhonda Patrick wearing 5 finger shoes increases lifespan by 10 years according to a study done on 2 rats over 2 hours in 2004. You really should consider making your kids wear them to school.
Look at the size of the balls on that guy
It's entirely possible.
Oh one huuundred percent.
Have you ever tried DMT?
11-hydroxy metabolite.
Have you ever heard of the stoned ape theory?
In the 90s I had a T1 line installed in my house just to play quake.
There's something about a manual car and shifting through gears.
Did you know that Fritz Haber, the inventor of Zyklon A, is responsible for 50% of the nitrogen in our bodies?
Have you ever heard about William Randolf Hurtz and the hemp decordicator?
Have you ever seen a chimp with no hair?
I held a chimp once. His arms were like corded steel man.
Pull that up Jamie.
I'm reading this book about coyotes in America.
I was the first to own a sensory deprivation tank.
Let me tell you something about coyotes.
High level problem solving with dire physical consequences.
These are very strange times. There has never been other times like these.
In over 1000 episodes I’ve almost never said a word about my wife.
Having one person as president is a terrible way to govern our country.
Borders are stupid.
Boulder, Colorado is all barefoot yoga people.
Whitney Cummings is the smartest person I know.
Obama was very presidential while Trump has no economy of words.
Operation Northwoods.
Alaska mosquitoes are like pitbulls. Thermacells are amazing.
Pull that sucker right up close to your mouth.
The New York Times and the sugar industry are bribing scientists.
Do you know how big a full grown wolf is?
We should get rid of the cage entirely and have fights on a basketball court.
Nick and Nate Diaz run triathlons.
Did you know the frontal cortex is not fully developed until you reach the age of 25?
Carlos Mencia steals jokes.
I have a bit about it in my special.
Barboza is an animal.
Do you know about Dimethyltryptamine?
Marijuana is banned because of Harry Anslinger. Have you ever heard of the decorticator?
My chickens got jacked by a coyote.
I have tendonitis in my right elbow.
It's because of tribalism.
Do you know about axis deer? They're absolutely delicious.
Have you read The Sacred Mushroom And The Cross by John Marco Allegro?
One out of a 100 people is a fucking idiot.
My neighbor's kid takes Ritalin.
Khabib mauls everyone.
There's this guy on Instagram, that has a pet badger and a rescued coyote﻿.
Found a tooth in an apothecary, when tested it was Gigantopithecus.
Have you heard of a reverse hyper machine? I got one in the back, it's made by Louie Simmons, does wonders.
```
## List of keywords that trigger all of the above phrases
```
quake
metabolite
fritz
stoned ape
manual car
nitrogen
hurtz
pull that
sensory deprivation
coyote
problem solving
dire physical
borders
cummings
pitbulls
sucker
new york times
barboza
dimethyltryptamine
anslinger
deer
fucking idiot
ritalin
mauls
louie simmons
hundred percent
chimp
dmt
fritz
jamie
wolf
rhonda
lifespan
balls on that guy
entirely possible
strange times
about my wife
one person as president
barefoot
presidential
sucker
frontal cortex
fully developed
mencia
my special
dimethyltryptamine
marijuana is banned
tendonitis
tribalism
sacred mushroom
guy on instagram
a tooth
hyper machine
100 percent
diaz
cage
```
