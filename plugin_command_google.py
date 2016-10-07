# Magnet2 by Grom PE. Public domain.
import urllib, urllib2, json, re
from magnet_utils import *
from magnet_api import *
from magnet_config import GOOGLE_KEY


def googlesearch(query, num=0, safe="off"):
  url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0%s&safe=%s&q=%s'%(
    GOOGLE_KEY,
    safe,
    urllib.quote_plus(query.encode('utf-8'))
  )
  rec = urllib2.urlopen(url)
  d = rec.read()
  f = open("_google.tmp", "wb")
  f.write(d)
  f.close()
  js = json.loads(d)
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
  url = "https://www.google.com/complete/search?client=opera&q=" + urllib.quote_plus(query.encode('utf-8'))
  rec = urllib2.urlopen(url).read()
  js = json.loads(rec)
  if len(js) > 1 and len(js[1]) > 0:
    if js[1][0].startswith("="):
      return query + ' ' + js[1][0]
    else:
      return js[1][0]
  else:
    return 'No results.'

def googleimagesearch(query, safe="off"):
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
  if 'safesearch' in bot.get_config(room, 'options'):
    safe = "active"
  else:
    safe = "off"
  try:
    res = googlesearch(parameters, 0, safe)
  except:
    import traceback
    res = 'An error occured.'
    bot.log_warn('Error searching google:\n%s' % traceback.format_exc())

  return res

def command_image(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Query expected.'
  if 'safesearch' in bot.get_config(room, 'options'):
    safe = "active"
  else:
    safe = "off"
  try: res = googleimagesearch(parameters, safe)
  except: res = 'An error occured.'
  return res

def command_calc(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Expression or query expected.'
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
  return 'Google plugin v1.0.4'
