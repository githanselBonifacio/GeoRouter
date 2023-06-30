import logging
import os
from mapbox import Directions


access_token = 'sk.eyJ1IjoiaGFuc2Vib24iLCJhIjoiY2xqZGwzOW8yMjFjeDNlbXd5eXIzZmVnOSJ9.KDsGQm9dUhewZBje-I5Lyg'
service = Directions(access_token=access_token)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def calcular_tiempo_desplazamiento(start,end):
    # Define the starting and ending points
    origin = (start[1], start[0])
    destination = (end[1], end[0])
    geo_start = {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [start[1], start[0]]
      },
      "properties": {
        "name": "inicio"
      }
    }
    geo_end = {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [end[1], end[0]]
      },
      "properties": {
        "name": "destino"
      }
    }
    departure_time = '2023-06-27T18:00:00-07:00'
    response = service.directions(
        coordinates=[origin, destination],
        profile='mapbox/driving-traffic',
        annotations=['duration'],
        features=[geo_start, geo_end],
        departure_time=departure_time
    )

    duration = response.json()['routes'][0]['duration']
    return round(duration)+600
