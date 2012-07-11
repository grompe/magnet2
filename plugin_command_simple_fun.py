#
#  This file is part of Magnet2.
#  Copyright (c) 2011  Grom PE
#
#  Magnet2 is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or     
#  (at your option) any later version.                                   
#
#  Magnet2 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Magnet2.  If not, see <http://www.gnu.org/licenses/>.
#
import time, random, md5
from magnet_api import *

rndobjects = [
  "a USB cable", "a small boulder", "a pointed stick", "a shotgun", "dust",
  "AOL CDs", "peanut butter", "a golf club", "air", "water", "a stapler",
  "a pair of scissors", "a size 13 bowling shoe", "a dead mouse", "a toilet",
  "a shampoo bottle", "instant soup", "the State of Maryland", "a piano",
  "Sparkling Cider", "a box of Kleenexes", "a Fig Newton", "an Apple ][",
  "a gallon of milk", "a Cuban cigar", "a 1968 Corvette", "a chess set",
  "a ZIP disk", "a can of Pig Brains with Gravy", "a trumpet", "a $2 bill",
  "the 2006 US Federal Tax Code", "Charles Manson's hair clippings", "yes",
  "CSI Season 1 DVD Set", "nothing in particular", "a tail", "a shrug",
  "99 bottles of beer on the wall", "a beanstalk", "a long pole", "lint",
  "a Patriot Missile", "an Oak 2x4", "a ROKR cellphone", "a light bulb",
  "a smoothbore depleted uranium sniper shell", "lots and lots of penguins",
  "a bottle of Welch's Sparkling White Grape Juice Cocktail (non-alcoholic)",
  "a trumpet mouthpiece", "a pair of headphones", "three sporks", "stuff",
  "a spiral fluorescent light bulb", "Sony's DRM Software", "Deep Space 9",
  "a slice of pizza", "a nosehair plucker", "three grains of sand", "earwax",
  "'One Fish Two Fish Red Fish Blue Fish'", "a coconut monkey", "a bathtub",
  "a Lego head, one of those cool ones with the sunglasses and stubble",
  "bellybutton lint", "the 1932 World's Fair", "a Sharpie, Ultra Fine Point",
  "15 golf ball tees", "a roll of pennies", "a Chinese Crested Hairless dog",
  "dental floss", "a toothpick", "a cow pie", "a toilet seat cover", "Jewel",
  "a toilet seat", "12 pounds of bacon", "a shrimp, a starfish, and a pigmy",
  "a fur coat", "a dot matrix printer", "a leg lamp", "RITZ bits", "a sock",
  "a mechanical pencil (0.5mm lead)", "fuzzy dice", "a watch", "a keyboard",
  "toenail clippings", "the letter 'L'", "8 dill pickles", "carpet remnants",
  "one of those squishy rubbery things that spring keyboard keys back up",
  "an EIDE cable", "a tube of m&m's minis", "a gerbil dressed as Domo-kun",
  "two suction cups, a peanut, and a can of cooking spray", "an ice skate",
  "a slinkey", "3 hard boiled eggs", "french vanilla icecream", "a salad",
  "5 poker decks", "a stapler", "ants", "a glass of water", "5 pounds of asphalt",
  "pickled pigs feet", "a trap door spider", "a stained glass window",
  "a bell tower", "string, wax, a bowling ball, and a tape measurer", "Twix",
  "a shoebox", "an ABIT motherboard", "a large yacht", "an LCD screen",
  "plains, trains, and automobiles", "a campfire", "peanut butter and syrup",
  "melted chocolate", "a crowbar", "a satellite dish", "a sheet of drywall",
  "a ceiling fan blade", "a broken tennis racquet", "2 pair of water skis",
  "a 38 inch tire", "a smoke alarm", "a plastic fly", "a Pepsi cap",
  "a gopher", "a gopher trap", "a random kitchen utensil", "a plutonium rod",
  "peach fuzz", "oyster crackers", "electrolytes", "kosher salt", "termites",
  "dihydrogen monoxide", "a partial solar eclipse", "crayons", "an anteater",
  "a plastic hanger, tube kind, not the ones that come with items from a store",
  "the kitchen sink", "a refrigerator", "a broken shot glass", "curly fries",
  "73 cranberries", "a meteorite", "a can of tomato sauce", "a pimple",
  "bamboo stilts", "a Tickle Me Elmo", "a Mickey Mouse Clock", "soy milk",
  "a Capri Sun pouch", "a rusty shot put ball", "a breakfast",
  "a random sea slug", "Gigli (Special Edition DVD)", "tofu casserole",
  "a spider, 4 toenail clippings, and a toupee", "24 pancakes", "an iphone",
  "chicken parmesan, an innertube, and dental floss", "used chewing gum",
  "termites, packing peanuts, and 14 gummy bears", "used corn husks",
  "a hockey stick", "nine hockey pucks", "a bag of dogfood", "738 buttons",
  "a timebomb", "18 cans of Alpo", "random emoticons", "a newspaper from 1947",
  "a random tv show, but not a 'random' show as in 'OMG that was random' but a random show as in, well, random throw of the dice",
  "a random tv show", "a picknick table", "a ping pong table", "a techno DJ",
  "a lobster, three onions, seven pencils, and a chewed up roll of 'Fruit by the Foot'",
  "chicken legs", "two pitchforks", "Nebraska", "a .torrent of Darkwing Duck",
  "America's Next Top Model", "a 52 inch plasma monitor", "sugar", "an oven mitt",
  "a fax machine", "four tennis racquets tied together to form a pyramid",
  "3 coupons and 2 AAA batteries", "a clown shoe", "a POS graphics card",
  "random prescription medicine", "three muffins and two slices of toast",
  "dental floss", "42 Pringles cans", "flakes of dead skin", "a shoe",
  "2 plastic coat hangers and a roll of nickles", "38 IDE cables", "an ant",
  "a box of t-shirts, 3 yards of dental floss, and a broken plastic fork",
  "the remains of Humpty Dumpty after all the King's Men couldn't put him back together",
  "7 egg whites and a cup of flour", "38 pigs and their farmer Willifred",
  "a first aid kit", "Salad Shooter(tm)", "a 17 car pile up on the freeway",
  "200 yards of barbed wire", "a PEZ dispenser filled with Tic-Tacs", "lice",
  "a Universal Power Supply backup battery", "a 4U racmount server",
  "314 empty envelops with prepaid postage from Credit Card companies",
  "mizspeld werds", "13 pounds of dust", "a spider's web", "a table leg",
  "42 Oreo Cookies, 2 Watermelons, 4 machine guns, and twisty ties",
  "a NERF bow and arrow", "an empty can of wasp spray", "the summer sky",
  "bubble wrap that has been painted blue", "99 red balloons", "bubbles",
  "the interwebs", "solid arguments", "21,357 DVDs", "the letter W",
  "a broken watch that has been dipped in gasoline", "7 potted plants",
  "shoes, a rock, toilet paper, 3 inch plastic dice, and a Swiss Army knife with the main blade removed",
  "32 freshly beheaded chickens", "a New Kids on the Block tape", "a Furby",
  "fiiiiiiiiiiiive goooolden riiiiiiiiings", "a freshly formatted floppy disk",
  "a hug", "a pat on the back", "a surprised face", "a door", "a belt",
  "a <3", "the passenger mirror of a 1972 Mercedes-Benz 280SEL",
  "3 rose bushes", "a box of 248 crayons that are half used", "a cold",
  "2 bottles of 'all small & mighty' with stainlifter and 3x concentrated laundry detergent",
  "a bicycle helmet", "a horn", "a spider plant", "mayonnaise",
  "a brown paper bag filled with Cheetos", "a Swingline 790 stapler",
  "a Linksys 16-Port Workgroup Switch", "200 yards of Cat 4 cable", "Nemo",
  "a smoke detector", "moldy cheese that a mouse didn't eat", "33 broken CDs",
  "Swiss Miss powdered Hot Chocolate with little marshmallows", "a spatula",
  "a Five Star binder", "a spider's egg sack", "3 dozen no bake cookies"
]

rnddesc = [
  'hairy', 'awesome', 'addicted to trying this command', 'evil', 'hungry',
  'bored', 'happy with something', 'sleepy', 'painted blue', 'skinny', 'cool',
  'mysterious', 'alive', 'famous', 'odd', 'shy', 'wrong', 'obedient', 'fancy',
  'noisy', 'slow', 'old-fashioned', 'delicious', 'juicy', 'erratic', 'salty',
  'sweet', 'fluffy', 'amusing', 'confused', 'adorable', 'crazy', 'nutritious',
  'impossible', 'lazy', 'venomous', 'unknown', 'unruly', 'huggable', 'cute',
  'silly', 'spiky', 'jealous of someone', 'chosen', 'slowly mutating',
  'thinking about the future', 'a phenomenon', 'a recognized person',
  'breathing', 'able to teleport', 'forgiving', 'awesomesauce', 'selfish',
  'in love with person above', 'important', 'evolving', 'very bored',
  'clueless', 'ignorant', 'wandering', 'uninspired', 'unbelieveable',
  'close to getting banned'
]

def command_hug(bot, room, nick, access_level, parameters, message):
  if parameters: target = parameters
  else: target = nick
  return '/me hugs %s'%(target)

def command_glomp(bot, room, nick, access_level, parameters, message):
  if parameters: target = parameters
  else: target = nick
  if random.getrandbits(1):
    newtarget = random.choice(bot.roster[room].keys())
    if newtarget != target and newtarget != bot.self_nick[room]:
      return '/me was going to glomp %s, but misses and crashes into %s instead.'%(target, newtarget)
    else:
      if newtarget != nick:
        return '/me decides to glomp %s'%(nick)
  return '/me glomps %s'%(target)

def command_slap(bot, room, nick, access_level, parameters, message):
  if parameters: target = parameters
  else: target = nick
  if bot.self_nick[room].lower() in target.lower():
    if random.getrandbits(1):
      return random.choice(["No.", "Never.", "Don't even think about it.", "I refuse."])
    else:
      target = nick
  if random.getrandbits(1):
    return '/me slaps %s with %s'%(target, random.choice(rndobjects))
  else:
    return '/me repeatedly slaps %s with %s and then %s '%(target, random.choice(rndobjects), random.choice(rndobjects))

def command_gift(bot, room, nick, access_level, parameters, message):
  if parameters: target = parameters
  else: target = nick
  if bot.self_nick[room].lower() in target.lower():
    target = nick
  if random.getrandbits(1):
    return '/me opens a box and gives '+random.choice(rndobjects)+' to '+target
  else:
    return '/me hands '+random.choice(rndobjects)+' to '+target

def command_stab(bot, room, nick, access_level, parameters, message):
  if parameters: target = parameters
  else: target = nick
  if bot.self_nick[room].lower() in target.lower():
    if random.getrandbits(1):
      return random.choice(["No.", "Never.", "Don't even think about it.", "I refuse."])
    else:
      target = nick
  return '/me stabs %s with %s'%(target, random.choice(rndobjects))

def command_poke(bot, room, nick, access_level, parameters, message):
  if parameters: target = parameters
  else: target = nick
  if bot.self_nick[room].lower() in target.lower():
    target = nick
  return '/me pokes %s with %s'%(target, random.choice(rndobjects))

def command_transform(bot, room, nick, access_level, parameters, message):
  if parameters: target = parameters
  else: target = random.choice(rndobjects)
  if bot.self_nick[room].lower() in target.lower():
    target = nick
  return '/me picks %s up and transforms into %s'%(target, random.choice(rndobjects))

def command_status(bot, room, nick, access_level, parameters, message):
  if parameters:
    target = parameters
    if not target in bot.roster[room]:
      return 'Who is %s, anyway?'%(target)
  else: target = nick
  pos = bot.roster[room][target][ROSTER_AFFILIATION]
  role = bot.roster[room][target][ROSTER_ROLE]
  jid = bot.roster[room][target][ROSTER_JID]
  if pos=='none': pos='a guest'
  if pos=='member': pos=('a member','a moderator')[role=='moderator']
  if pos=='member': pos='a member'
  if pos=='admin': pos='an admin'
  if pos=='owner': pos='an owner'
  if role=='visitor': pos='speechless'

  # use per hour randomization to prevent overuse
  initstring = jid or target
  hashname = md5.new('%s%d'%(initstring.encode('utf-8'), time.time()//3600)).hexdigest()
  hashnum = 0
  for c in hashname: hashnum += ord(c)
  desc = rnddesc[hashnum % len(rnddesc)]

  if target == nick:
    response = 'You are %s. You are %s. You are also %s.'%(target, pos, desc)
  else:
    response = '%s is %s and also %s.'%(target, pos, desc)
  return response

def command_roll(bot, room, nick, access_level, parameters, message):
  p = parameters.find('d')
  x = parameters.find('+')
  s = parameters.find(' ')
  if s != -1: parameters = parameters[:s]
  number = 0
  sides = 0
  add = 0
  if p == -1: p = len(parameters)
  try:
    if x == -1:
      sides = int(parameters[p+1:])
    else:
      sides = int(parameters[p+1:x])
      add = int(parameters[x+1:])
    number = int(parameters[:p])
  except:
    pass
  if number < 1: number = 1
  if number > 10: number = 10
  if sides < 2: sides = 6
  if sides > 100: sides = 100
  if add < -1000: add = -1000
  if add > 1000: add = 1000
  rolls = []
  for i in range(number): rolls.append(random.randint(1, sides))
  if add: rolls.append(add)
  output = '%s, %dd%d+%d roll: %s'%(nick, number, sides, add, '+'.join([str(i) for i in rolls]))
  if len(rolls) > 1: output += '=' + str(sum(rolls))
  return output

def command_tellfruit(bot, room, nick, access_level, parameters, message):
  if parameters:
    target = parameters
    if not target in bot.roster[room]:
      return 'Who is %s, anyway?'%(target)
  else: target = nick
  jid = bot.roster[room][target][ROSTER_JID]
  he = jid or target
  hashname = md5.new('Is %s a fruit or a vegetable'%(he.encode('utf-8'))).digest()
  hashnum = 0
  for c in hashname: hashnum += ord(c)
  veg = ("fruit", "vegetable")[hashnum % 2]
  return '%s is a %s.'%(target, veg)

def command_flip(bot, room, nick, access_level, parameters, message):
  return nick+', '+random.choice(['Heads!', 'Tails!'])

def command_say(bot, room, nick, access_level, parameters, message):
  bot.send_room_message(room, parameters)
  return ''

def command_act(bot, room, nick, access_level, parameters, message):
  bot.send_room_message(room, '/me %s'%(parameters))
  return ''

def load(bot):
  bot.add_command('hug', command_hug, LEVEL_GUEST, 'simple_fun')
  bot.add_command('glomp', command_glomp, LEVEL_GUEST, 'simple_fun')
  bot.add_command('slap', command_slap, LEVEL_GUEST, 'simple_fun')
  bot.add_command('gift', command_gift, LEVEL_GUEST, 'simple_fun')
  bot.add_command('stab', command_stab, LEVEL_GUEST, 'simple_fun')
  bot.add_command('poke', command_poke, LEVEL_GUEST, 'simple_fun')
  bot.add_command('transform', command_transform, LEVEL_GUEST, 'simple_fun')
  bot.add_command('status', command_status, LEVEL_GUEST, 'status')
  bot.add_command('tellfruit', command_tellfruit, LEVEL_GUEST, 'status')
  bot.add_command('roll', command_roll, LEVEL_GUEST, 'rpg')
  bot.add_command('flip', command_flip, LEVEL_GUEST, 'rpg')
  bot.add_command('say', command_say, LEVEL_ADMIN, 'say')
  bot.add_command('act', command_act, LEVEL_ADMIN, 'say')

def unload(bot):
  pass

def info(bot):
  return 'Simple fun plugin v1.0.2'
