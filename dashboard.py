import streamlit as st
import requests
import json

st.set_page_config(page_title="Flight Itinerary Generator", layout="wide")
st.title("🛫 Multi-Stop Flight Itinerary Generator")

st.sidebar.header("General Settings")
origin_airports = st.sidebar.text_input("Departure Airports (comma-separated)", "LHR")
dep_date_range = st.sidebar.date_input("Departure Date Range", [])
exclude_dep_days = st.sidebar.multiselect("Exclude Departure Days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
exclude_ret_days = st.sidebar.multiselect("Exclude Return Days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
total_stay = st.sidebar.slider("Total Trip Duration (days)", 2, 30, (5, 10))
return_to = st.sidebar.selectbox("Return Option", ["same", "nearby", "custom"])

st.sidebar.header("Stop 1 Settings")
dest1 = st.sidebar.text_input("Stop 1 Destination (comma or 'everywhere')", "everywhere")
stay1 = st.sidebar.slider("Stay at Stop 1 (days)", 1, 15, (2, 5))
red1 = st.sidebar.text_input("Re-departure Airports Stop 1 (optional)", "")
road1_km = st.sidebar.slider("Roadtrip Range KM (optional)", 0, 500, (0, 0))

st.sidebar.header("Stop 2 Settings")
dest2 = st.sidebar.text_input("Stop 2 Destination (comma-separated)", "FCO, CDG")
stay2 = st.sidebar.slider("Stay at Stop 2 (days)", 1, 15, (2, 5))
red2 = st.sidebar.text_input("Re-departure Airports Stop 2 (optional)", "")
road2_km = st.sidebar.slider("Roadtrip Range KM Stop 2 (optional)", 0, 500, (0, 0))

interchange = st.sidebar.checkbox("Enable Interchangeable Stops", False)
submit = st.sidebar.button("Generate Itineraries")

if submit:
    if len(dep_date_range) != 2:
        st.error("Please select a start and end date for Departure Date Range.")
    else:
        payload = {
            "general": {
                "departure_date_range": [str(dep_date_range[0]), str(dep_date_range[1])],
                "total_stay_range": list(total_stay),
                "departure_airports": [i.strip() for i in origin_airports.split(",")],
                "exclude_departure_weekdays": exclude_dep_days,
                "exclude_return_weekdays": exclude_ret_days,
                "return_to": "same" if return_to == "same" else ([i.strip() for i in origin_airports.split(",")] if return_to == "custom" else {"km_range": [0, 100]})
            },
            "number_of_stops": 2,
            "interchangeable_stops": interchange,
            "stops": [
                {
                    "destination": dest1 if dest1 == "everywhere" else [i.strip() for i in dest1.split(",")],
                    "stay_range": list(stay1),
                    "re_departure_strategy": {
                        "roadtrip_km": list(road1_km) if road1_km != (0, 0) else None,
                        "custom_redeparture_airports": [i.strip() for i in red1.split(",")] if red1 else None
                    }
                },
                {
                    "destination": [i.strip() for i in dest2.split(",")],
                    "stay_range": list(stay2),
                    "re_departure_strategy": {
                        "roadtrip_km": list(road2_km) if road2_km != (0, 0) else None,
                        "custom_redeparture_airports": [i.strip() for i in red2.split(",")] if red2 else None
                    }
                }
            ]
        }

        st.code(json.dumps(payload, indent=2), language="json")
        with st.spinner("Generating all valid combinations and fetching flights..."):
            response = requests.post("http://localhost:8000/generate-itineraries", json=payload)
            if response.status_code == 200:
                data = response.json()
                st.success(f"Generated {data['summary']['total_combinations']} combinations.")
                st.info(f"Valid itineraries found: {data['summary']['valid_itineraries']}")
                st.json(data['itineraries'])
            else:
                st.error("Something went wrong. Check server logs or input.")
