# ✈️ Multi-Stop Flight Itinerary Generator

This tool generates all possible combinations of multi-stop flight trips based on your input, using AI logic and a backend server built with FastAPI.

---

## 🧰 What You Need to Do (Step by Step)

### 1. Install Python

Make sure you have **Python 3.10** installed on your computer.  
👉 Download it from here: https://www.python.org/downloads/release/python-3100/

---

### 2. Open Your Terminal or Command Prompt

- On **Windows**, search for “cmd” or “Command Prompt”
- On **Mac**, open the “Terminal” app
- On **Linux**, open your terminal as usual

---

### 3. Create a Virtual Environment

- This creates a clean space to manage project dependencies.
- python3 -m venv .venv
- Then activate it:

### Windows:
- venv\Scripts\activate

### Mac/Linux:
- source venv/bin/activate

### 4. Install the Required Packages
- Run this command to install all the necessary libraries:
- pip install -r requirements.txt
- Make sure the requirements.txt file is in the same folder where you are running the command.

### 5. Start the Backend Server
- Once everything is installed, start the FastAPI backend server with:


- uvicorn main:app --reload
- You should see this message:
- INFO:     Uvicorn running on http://127.0.0.1:8000
- That means your API is live at http://localhost:8000

### 📬 How to Use the API
- Once the server is running, you can test it in two ways:

- ✅Use Postman (Recommended)
- Download Postman from: https://www.postman.com/downloads/
- Open Postman and click New → HTTP Request

### Set the request method to POST

- Paste this as the request URL:
- http://localhost:8000/generate-itineraries
- Click the Body tab
- Select raw and choose JSON from the dropdown

- Paste this JSON into the body:


{
  "general": {
    "departure_date_range": ["2025-08-01", "2025-08-03"],
    "total_stay_range": [3, 5],
    "departure_airports": ["LHR"],
    "exclude_departure_weekdays": ["Sunday"],
    "exclude_return_weekdays": ["Wednesday"],
    "return_to": "same"
  },
  "number_of_stops": 2,
  "interchangeable_stops": true,
  "stops": [
    {
      "destination": "everywhere",
      "stay_range": [1, 3],
      "re_departure_strategy": {
        "roadtrip_km": [0, 200]
      }
    },
    {
      "destination": ["FCO"],
      "stay_range": [1, 3],
      "re_departure_strategy": {
        "custom_redeparture_airports": ["FCO"]
      }
    }
  ]
}


### Click Send

### You’ll get a list of all valid itinerary combinations in the response