from typing import NamedTuple
import pandas as pd
from tqdm.auto import tqdm

class Event(NamedTuple):
  """
  Class containing an event. It has the following attributes:
  - Index                :     some unique integer
  - entity             : unique identifier to the entity involved in the event
  - time
  - location   (optional)
  - attributes (optional): Any additional attributes can be stored in this dict.
  """
  Index     : int
  entity    : str
  time      : pd.Timestamp
  location  : str = None
  attributes: dict = dict()

def get_events(data: pd.DataFrame, verbose=False) -> list[Event]:
  """Get a list of events from the data"""
  events_df = data.copy()
  events_df.rename_axis('id', inplace=True)
  return [Event(Index=e.Index, entity=e.entity, time=e.datetime, 
                location=e.location, 
                attributes=dict(velocity=e.velocity, lane=e.lane)) 
          for e in tqdm(events_df.itertuples(), total=len(data), 
                        disable=not verbose)]