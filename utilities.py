from datetime import datetime, timedelta

from flight_data import search_one_way_flight, search_everywhere, get_nearby_airports
from schemas import Stop


def generate_date_range(start, end):
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    return [(s + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((e - s).days + 1)]


def is_valid_weekday(date_str, excluded_days):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A") not in excluded_days


def stay_distributions(min_total, max_total, stop_ranges, num_stops):
    output = []
    if num_stops == 1:
        return [(total,) for total in range(stop_ranges[0][0], stop_ranges[0][1] + 1)]

    for total in range(min_total, max_total + 1):
        for a in range(stop_ranges[0][0], stop_ranges[0][1] + 1):
            for b in range(stop_ranges[1][0], stop_ranges[1][1] + 1):
                if a + b == total:
                    output.append((a, b))
    return output


def fetch_flight_data(combo, container):
    try:
        leg1 = search_one_way_flight(combo["origin"], combo["stop1"], combo["depart1"])
        if not leg1: return False

        leg2 = search_one_way_flight(combo["stop1"], combo["stop2"], combo["depart2"])
        if not leg2: return False

        ret = search_one_way_flight(combo["stop2"], combo["return_to"], combo["return"])
        if not ret: return False

        key = f'{combo["origin"]}_{combo["depart1"]}'
        step1 = f'{combo["origin"]} -> {combo["stop1"]} @ {combo["depart1"]}'
        step2 = f'{combo["stop1"]} -> {combo["stop2"]} @ {combo["depart2"]}'

        container.setdefault(key, {}).setdefault(step1, {})[step2] = {"RETURN": ret}
        return True
    except Exception as e:
        print(f"Error fetching flights for {combo}: {str(e)}")
        return False

def swap_stop_configurations(stops):
    swapped = [
        Stop(
            destination=stops[1].destination,
            stay_range=stops[1].stay_range,
            re_departure_strategy=stops[1].re_departure_strategy
        ),
        Stop(
            destination=stops[0].destination,
            stay_range=stops[0].stay_range,
            re_departure_strategy=stops[0].re_departure_strategy
        )
    ]
    return swapped

def resolve_destinations(stop, origin, date):
    if stop.destination == "everywhere":
        return list(search_everywhere(origin, date).keys())
    elif isinstance(stop.destination, list):
        return stop.destination
    else:
        return [stop.destination]

def resolve_redeparture_options(origin_airport, strategy):
    if strategy.roadtrip_km:
        return get_nearby_airports(origin_airport, *strategy.roadtrip_km)
    if strategy.custom_redeparture_airports:
        return strategy.custom_redeparture_airports
    return [origin_airport]