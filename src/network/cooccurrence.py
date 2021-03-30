from collections import deque
from typing import NamedTuple

import pandas as pd
from tqdm.auto import tqdm

from .event import Event

class Cooccurrence(NamedTuple):
  """
  Class mapping two events that were coinciding within deltaTime (optionally, at
  the same loc).
  """
  event:       Event
  other_event: Event
  timedelta:   pd.Timedelta
  time:        pd.Timestamp
  def __str__(self): 
    return (
      f'event      : {self.event}\n'
      f'other_event: {self.otherEvent}\n'
      f'timedelta  : {self.deltaTime}'
    )
  
def get_cooccurrences(
  events: list[Event], *, max_timedelta: pd.Timedelta, verbose: bool = False
  ) -> list[Cooccurrence]:
  """Obtain a list of all co-occurences of two events, being at the same loc 
  (when that information is available) and within at most deltaTimeMax 
  separation."""
  events_per_location = dict()
  for event in events:
    if event.location not in events_per_location: 
      events_per_location[event.location] = list()
    events_per_location[event.location].append(event)
  
  cooccurrences = list()
  queue = deque()
  for location, events in tqdm(events_per_location.items(), position=0, 
                               desc='get cooccurrences',
                               disable=not verbose, leave=False):
    for event in tqdm(events, position=1, desc=location, disable=not verbose, 
                      leave=False):
      for other_event in queue.copy():
        if event.entity != other_event.entity:
          timedelta = event.time - other_event.time
          if timedelta < max_timedelta: 
            cooccurrences.append(
              Cooccurrence(event=event, other_event=other_event, 
                           timedelta=timedelta, time=event.time))
          else: queue.popleft()
      queue.append(event)
  return cooccurrences

def divide_cooccurrences(
  cooccurrences: list[Cooccurrence], *, min_timedelta: pd.Timedelta, 
  verbose:bool=False) -> tuple[list[Cooccurrence], list[Cooccurrence]]:
  """Divide a list of cooccurrencing events in systematic and random cooccurring
  events. An event is considered systematic if multiple events happen between 
  two entities with at minimum mintimedelta time difference.
  
  Usage:
  systematic, random = divideCooccurrences(
    cooccurrences, mintimedelta=pd.Timedelta(2, 'h')
  )"""
  temp = dict()
  for cooccurrence in tqdm(cooccurrences, disable=not verbose, 
                           desc='sort by identities', leave=False):
    identities = tuple(sorted([cooccurrence.event.entity, 
                               cooccurrence.other_event.entity]))
    if identities not in temp: temp[identities] = list()
    temp[identities].append(cooccurrence)
    
  systematic = list()
  random = list()
  desc = 'Determine time gap'
  for _, cooccurrences in tqdm(temp.items(), disable=not verbose, 
                               desc='determine time gap', leave=False):
    cooccurrences.sort()
    if cooccurrences[-1].time - cooccurrences[0].time > min_timedelta:
      systematic.extend(cooccurrences)
    else:
      random.extend(cooccurrences)
  return systematic, random 