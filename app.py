import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = ""
# you can get API keys for free here - https://www.weatherapi.com/
RSA_API_KEY = ""

app = Flask(__name__)

def generate_forecast(city: str, aqi: str, lang: str):
    url_base_url = "http://api.weatherapi.com"
    url_api = "v1"
    url_endpoint = "current.json"
    url_key = f"?key={RSA_API_KEY}"
    url_city = ""
    url_aqi = ""
    url_lang = ""

    if city:
        url_city = f"&q={city}"

    if aqi:
        url_aqi = f"&aqi={aqi}"

    if lang:
        url_lang = f"&lang={lang}"

    url = f"{url_base_url}/{url_api}/{url_endpoint}{url_key}{url_city}{url_aqi}{url_lang}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)
def weather_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    name = ""
    if json_data.get("requester_name"):
        name = json_data.get("requester_name")   
        
    city = ""
    if json_data.get("q"):
        city = json_data.get("q")

    aqi = ""
    if json_data.get("aqi"):
        aqi = json_data.get("aqi")

    lang = ""
    if json_data.get("lang"):
        lang = json_data.get("lang")

    weather = generate_forecast(city,aqi,lang)
    end_dt = dt.datetime.now()

    result = {
        "event_start_datetime": start_dt.isoformat(),
        "event_finished_datetime": end_dt.isoformat(),
        "event_duration": str(end_dt - start_dt),
        "requester_name": name,
        "weather": weather,
    }

    return result
