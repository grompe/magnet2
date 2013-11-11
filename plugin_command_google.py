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
import urllib, urllib2, json, re
from magnet_utils import *
from magnet_api import *
from magnet_config import GOOGLE_KEY


def googlesearch(query, num=0):
  if 'safesearch' in bot.get_config(room, 'options'):
    safe = "active"
  else:
    safe = "off"
  url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0%s&safe=%s&q=%s'%(
    GOOGLE_KEY,
    safe,
    urllib.quote_plus(query.encode('utf-8'))
  )
  rec = urllib2.urlopen(url)
  js = json.loads(rec.read())
  results = js['responseData']['results']
  if len(results)>num:
    r = results[num]
    #reg = re.compile('<b>([^<]+)</b>', re.IGNORECASE)
    #content = reg.sub('\\1', r['content'])
    content = r['content']
    content = content.replace('<b>', '')
    content = content.replace('</b>', '')
    content = unhtml(content)
    title = unhtml(r['titleNoFormatting'])
    return '%s\n%s\n%s'%(title, content, r['unescapedUrl'])
  else:
    return 'Nothing found.'

def googlecalc(query):
  url = 'http://www.google.com/ig/calculator?hl=en&q=%s'%urllib.quote_plus(query.encode('utf-8'))
  rec = urllib2.urlopen(url).read()
  
  r = re.match('{lhs: "(.*)",rhs: "(.*)",error: "(.*)"', rec)
  if r:
    if r.group(3):
      res = 'error: '+r.group(3)
    else:
      res = r.group(1)+' = '+r.group(2)
    res = res.decode('unicode-escape')
    res = res.replace('&#215;', unichr(215))
    res = res.replace('<sup>', '^(')
    res = res.replace('</sup>', ')')
    return res
  return 'Something bad happened.'

def googleimagesearch(query):
  if 'safesearch' in bot.get_config(room, 'options'):
    safe = "active"
  else:
    safe = "off"
  url = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0%s&safe=%s&q=%s'%(
    GOOGLE_KEY,
    safe,
    urllib.quote_plus(query.encode('utf-8'))
  )
  rec = urllib2.urlopen(url)
  js = json.loads(rec.read())
  results = js['responseData']['results']
  if len(results)>0:
    return results[0]['unescapedUrl']
  else:
    return 'Nothing found.'

def command_google(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Query expected.'
  try: res = googlesearch(parameters)
  except: res = 'An error occured.'
  return res

def command_image(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Query expected.'
  try: res = googleimagesearch(parameters)
  except: res = 'An error occured.'
  return res

def command_calc(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Expression expected.'
  try: res = googlecalc(parameters)
  except: res = 'An error occured.'
  return res

LANGCODES = [
  'af','sq','ar','hy','az','eu','be','bn','bg','ca','hr','cs','da',
  'nl','en','et','tl','fi','fr','gl','ka','de','el','gu','ht','iw',
  'hi','hu','is','id','ga','it','ja','kn','ko','la','lv','lt','mk',
  'ms','mt','no','fa','pl','pt','ro','ru','sr','sk','sl','es','sw',
  'sv','ta','te','th','tr','uk','ur','vi','cy','yi','zh-CN','zh-TW'
]

def command_translate(bot, room, nick, access_level, parameters, message):
  global langreg
  if not parameters: return 'Expected parameters: [langfrom [langto]] <text>'
  m = langreg.match(parameters)
  if not m: return 'An error occured.'
  (langfrom, langto, text) = m.groups()
  # Set first parameter to langto if only two are given
  if langfrom and not langto: langto, langfrom = langfrom, 'auto'
  if not langfrom: langfrom = 'auto'
  if not langto: langto = 'en'
  qtext = urllib.quote_plus(text.encode('utf-8'))
  if message.getType() == 'groupchat' and len(qtext) > 400 or len(qtext) > 4000:
    return 'For long texts go to http://translate.google.com/?sl=%s&tl=%s'%(
      langfrom, langto)
  return 'http://translate.google.com/?sl=%s&tl=%s&q=%s'%(
    langfrom, langto, qtext)

def load(bot):
  global langreg
  bot.add_command('google', command_google, LEVEL_GUEST, 'google')
  bot.add_command('g', command_google, LEVEL_GUEST, 'google')
  bot.add_command('image', command_image, LEVEL_GUEST, 'google')
  bot.add_command('calc', command_calc, LEVEL_GUEST, 'google')
  bot.add_command('translate', command_translate, LEVEL_GUEST, 'google')
  bot.add_command('tr', command_translate, LEVEL_GUEST, 'google')
  l = '|'.join(LANGCODES)
  langreg = re.compile('(?:(%s) )?(?:(%s) )?(.+)'%(l, l), re.IGNORECASE | re.DOTALL)

def unload(bot):
  pass

def info(bot):
  return 'Google plugin v1.0.2'
