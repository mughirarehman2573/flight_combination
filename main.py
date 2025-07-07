from fastapi import FastAPI
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from flight_data import get_nearby_airports
from schemas import RequestModel
from utilities import (
    generate_date_range,
    is_valid_weekday,
    fetch_flight_data,
    stay_distributions,
    swap_stop_configurations,
    resolve_destinations,
    resolve_redeparture_options
)

app = FastAPI()


@app.post("/generate-itineraries")
def generate_itineraries(request: RequestModel):
    output = {}
    total_combinations = 0
    valid_itineraries = 0
    threads = []

    dep_dates = generate_date_range(*request.general.departure_date_range)
    stay_combos = stay_distributions(
        request.general.total_stay_range[0],
        request.general.total_stay_range[1],
        [s.stay_range for s in request.stops],
        request.number_of_stops
    )

    stop_configs = [request.stops]
    if (request.number_of_stops == 2 and
        request.interchangeable_stops and
        not (request.stops[0].destination == request.stops[1].destination and
             request.stops[0].stay_range == request.stops[1].stay_range and
             request.stops[0].re_departure_strategy == request.stops[1].re_departure_strategy)):
        stop_configs.append(swap_stop_configurations(request.stops))

    with ThreadPoolExecutor(max_workers=10) as executor:
        for origin in request.general.departure_airports:
            for dep_date in dep_dates:
                if not is_valid_weekday(dep_date, request.general.exclude_departure_weekdays):
                    for stops in stop_configs:
                        stop1_list = resolve_destinations(stops[0], origin, dep_date)
                        for stop1 in stop1_list:
                            if request.number_of_stops == 1:
                                for stay1, in stay_combos:
                                    d1 = datetime.strptime(dep_date, "%Y-%m-%d")
                                    d2 = d1 + timedelta(days=stay1)
                                    d2_str = d2.strftime("%Y-%m-%d")

                                    if is_valid_weekday(d2_str, request.general.exclude_return_weekdays):
                                        if request.general.return_to == "same":
                                            return_to_airports = [origin]
                                        elif isinstance(request.general.return_to, dict) and "km_range" in request.general.return_to:
                                            return_to_airports = get_nearby_airports(stop1, *request.general.return_to["km_range"])
                                        else:
                                            return_to_airports = request.general.return_to if isinstance(request.general.return_to, list) else [request.general.return_to]

                                        for return_to in return_to_airports:
                                            total_combinations += 1
                                            combo = {
                                                "origin": origin,
                                                "stop1": stop1,
                                                "stop2": None,
                                                "depart1": dep_date,
                                                "depart2": None,
                                                "return": d2_str,
                                                "return_to": return_to
                                            }
                                            threads.append(executor.submit(fetch_flight_data, combo, output))
                            else:
                                stop2_list = resolve_destinations(stops[1], stop1, dep_date)
                                for stop2 in stop2_list:
                                    for stay1, stay2 in stay_combos:
                                        d1 = datetime.strptime(dep_date, "%Y-%m-%d")
                                        d2 = d1 + timedelta(days=stay1)
                                        d3 = d2 + timedelta(days=stay2)
                                        d2_str, d3_str = d2.strftime("%Y-%m-%d"), d3.strftime("%Y-%m-%d")

                                        if is_valid_weekday(d3_str, request.general.exclude_return_weekdays):
                                            if request.general.return_to == "same":
                                                return_to_airports = [origin]
                                            elif isinstance(request.general.return_to, dict) and "km_range" in request.general.return_to:
                                                return_to_airports = get_nearby_airports(stop2, *request.general.return_to["km_range"])
                                            else:
                                                return_to_airports = request.general.return_to if isinstance(request.general.return_to, list) else [request.general.return_to]

                                            for return_to in return_to_airports:
                                                redep1_list = resolve_redeparture_options(stop1, stops[0].re_departure_strategy)
                                                if stop2 not in redep1_list:
                                                    continue

                                                total_combinations += 1
                                                combo = {
                                                    "origin": origin,
                                                    "stop1": stop1,
                                                    "stop2": stop2,
                                                    "depart1": dep_date,
                                                    "depart2": d2_str,
                                                    "return": d3_str,
                                                    "return_to": return_to
                                                }
                                                threads.append(executor.submit(fetch_flight_data, combo, output))

        for task in as_completed(threads):
            if task.result():
                valid_itineraries += 1

    print(f"Total combinations generated: {total_combinations}")
    print(f"Total valid itineraries found: {valid_itineraries}")

    return {
        "summary": {
            "total_combinations": total_combinations,
            "valid_itineraries": valid_itineraries
        },
        "itineraries": output
    }