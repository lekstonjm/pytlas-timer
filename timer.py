import logging
from threading import Thread, Timer
from uuid import uuid4
from pytlas import on_agent_created, on_agent_destroyed, training, intent, translations
from datetime import datetime
import re

# This entity will be shared among training data since it's not language specific

en_skill = """Timer skill {0} countdown time for you to make a boiled egg a success every time. Simpy ask start a timer for 3 minutes and wait ..."""


@training('en')
def en_data(): return """
%[timer_skill]
  what is timer skill

%[start_timer]
  start a timer for @[timer_duration]

@[timer_duration]
 3 minutes
 4 seconds
 10 hours
 5s
 34mn
 5h
 6 minutes and 12 seconds
 00:03:00
 7m6s
 13m and 4s
"""
# disabled due to duration issues
"""
@[timer_duration](type=duration)
 3 minutes
"""

fr_skill = """
Le minuteur {0} décompte le temps pour vouus pour que vous ne ratiez jamais un oeuf à la coque. Demandez de démarrer le minuteur pour 3 minutes et attendez ... 
"""


@training('fr')
def fr_data(): return """
%[timer_skill]
  qu'est ce que la compétence minuteur

%[start_timer]
  démarre un minuteur pour @[timer_duration]
  commence un minuteur pour @[timer_duration]

@[timer_duration]
 3 minutes
 4 secondes
 10 heures
 5s
 34mn
 5h
 6 minutes et 12 secondes
 00:03:00
 7m6s
 9m et 36s
"""

"""
@[timer_duration](type=duration)
 3 minutes
"""

@translations('fr')
def fr_translations(): return {
  'Times up!!' : 'Le temps est écoulé',
  'What is the duration?' : 'Quelle est la durée',
  'A timer has been started for {0:02d}:{1:02d}:{2:02d} from now ({3})' : 'Un minuteur d\'une durée de {0}:{1}:{2} vient d\'être démarré ({3})' 
}

agents = {}

version = "v1.0"
plaintext_s_re = re.compile('((\\d+) *h[^ ]* +(et|and|,)? *)?((\\d+) *m(i)?n[^ ]* +(et|and|,)? *)?((\\d+) *s[^ ]*)')
plaintext_mn_re = re.compile('((\\d+) *h[^ ]* +(et|and|,)? *)?((\\d+) *m(i)?n[^ ]*)')
plaintext_h_re = re.compile('((\\d+) *h[^ ]*)')
short_re = re.compile('(\\d+):(\\d+):(\\d+)')

def timer_callback(agt_id):
  agents[agt_id].answer('Times up!!')

@on_agent_created()
def when_an_agent_is_created(agt):
  # On conserve une référence à l'agent
  agents[agt.id] = agt

@on_agent_destroyed()
def when_an_agent_is_destroyed(agt):
  # On devrait clear les timers pour l'agent à ce moment là
  pass

@intent('timer_skill')
def on_timer_skill(req):
  req.agent.answer(req._(en_skill).format(version))
  return req.agent.done()


@intent('start_timer')
def on_start_timer(req):
  duration_text = req.intent.slot('timer_duration').first().value 
  if  duration_text == None:
    return req.agent.ask('timer_duration', req._('What is the duration?'))
  hours_text, minutes_text, seconds_text = duration_parse(duration_text)
  
  if hours_text == None and minutes_text == None and seconds_text == None:
    return req.agent.ask('timer_duration', req._('What is the duration?'))
  
  hours = 0  
  try:
    hours = int(hours_text)
  except:
    pass

  minutes = 0
  try:
    minutes = int(minutes_text)
  except:
    pass

  seconds = 0
  try:
    seconds = int(seconds_text)
  except:
    pass

  duration_seconds = int(hours) * 3600  +  int(minutes) * 60 + int(seconds) 
         
  Timer(duration_seconds, timer_callback, args=(req.agent.id,)).start()
  current_time = datetime.now().time()
  req.agent.answer(req._('A timer has been started for {0:02d}:{1:02d}:{2:02d} from now ({3})').format(hours, minutes, seconds, req._d(current_time, time_only=True) ))
  return req.agent.done()

def duration_parse(duration_text):
  match_s_plaintext = plaintext_s_re.match(duration_text) 
  match_mn_plaintext = plaintext_mn_re.match(duration_text) 
  match_h_plaintext = plaintext_h_re.match(duration_text) 
  match_short = short_re.match(duration_text)
  if match_s_plaintext:
    return match_s_plaintext.group(2),  match_s_plaintext.group(5), match_s_plaintext.group(9)
  elif match_mn_plaintext:
    return match_mn_plaintext.group(2),  match_mn_plaintext.group(5), 0
  elif match_h_plaintext:
    return match_s_plaintext.group(2), 0, 0
  elif match_short:
    return match_short.group(1),  match_short.group(2), match_short.group(3)
  return None , None, None
