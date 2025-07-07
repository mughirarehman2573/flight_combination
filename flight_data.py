import random


def search_one_way_flight(origin, destination, date):
    return {"origin": origin, "destination": destination, "date": date, "price": random.randint(80, 400)}

def search_everywhere(origin, date):
    return {"BCN": 120, "FCO": 160, "CDG": 200}

def get_nearby_airports(airport, min_km, max_km):
    return {"LHR": ["LGW", "STN", "LCY"], "BCN": ["REU", "GRO"], "FCO": ["CIA"]}.get(airport, [])