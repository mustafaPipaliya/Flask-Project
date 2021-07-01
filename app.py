import json
import math
import urllib.parse
from datetime import date

import requests
from flask import Flask, render_template

app = Flask(__name__)


# Displays form to select state and district
@app.route("/")
def hello_world():
    return render_template('input.html')


# Get States from cowin API
@app.route("/getstates")
def get_states():
    url = "https://cdn-api.co-vin.in/api/v2/admin/location/states"

    payload = {}
    headers = {
        'accept': 'application/json',
        'Accept-Language': 'hi_IN',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.text


# Get districts from cowin API
@app.route("/getdistricts/<state_ID>")
def get_districts(state_ID):
    url = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/" + state_ID

    payload = {}
    headers = {
        'accept': 'application/json',
        'Accept-Language': 'hi_IN',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.text


# Does Following:
# 1. Get vaccination centre data from cowin
# 2. Get all vaccination centre data - lat, lng, distance and time taken via car
@app.route("/processform/<district_id>/<user_lat_long>")
def processform(district_id, user_lat_long):
    result = [];

    centers = get_centres(district_id)
    centers_dict = json.loads(centers)
    district = centers_dict['sessions'][0]['district_name']
    state = centers_dict['sessions'][0]['state_name']
    for i in centers_dict['sessions']:

        address = i['name'] + " , " + i["address"] + " , " + i["district_name"]
        latlong = getLatLng(address)

        # Here pi does not have data fro all centres, skip whatever is not available
        if latlong != "":
            center_data = {}
            latlong_str = str(latlong['lat']) + "," + str(latlong['lng'])

            distance = get_distance(latlong_str, user_lat_long)

            center_data['name'] = i['name']
            center_data['lat'] = latlong['lat']
            center_data['lng'] = latlong['lng']
            center_data['distance'] = distance['distance']
            center_data['duration'] = distance['duration']

            result.append(center_data)

    return render_template('app.html', data=json.dumps(result), userlat=user_lat_long.split(",")[0],
                           userlng=user_lat_long.split(",")[1], district=district, state=state)


# Get latlng data, if not available return ""
def getLatLng(address):
    url = "https://geocode.search.hereapi.com/v1/geocode?apikey=bAip29b6wUMRDUMznVpeLaQuM9Q783ZH_cFM4e45eXw&q=" + urllib.parse.quote(
        address)
    response = requests.request("GET", url).json()
    if len(response['items']) != 0:
        return response['items'][0]['position']
    else:
        return ""


def get_centres(district_id):
    today = date.today()
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id=" + district_id + "&date=" + str(
        today.strftime("%d-%m-%y"))

    payload = {}
    headers = {
        'accept': 'application/json',
        'Accept-Language': 'hi_IN',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text


def get_distance(center_lat_long, user_lat_long):
    result = {}
    url = "https://router.hereapi.com/v8/routes?transportMode=car&origin=" + user_lat_long + "&destination=" + center_lat_long + "&return=summary"
    myparams = {'apiKey': "bAip29b6wUMRDUMznVpeLaQuM9Q783ZH_cFM4e45eXw"}
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload, params=myparams).json()
    routes = response['routes'][0]['sections'][0]['summary']

    # api_response = "Distance between points is " + str(routes['length']/1000) + " kilometers and time taken is " +
    # str(routes['duration'])
    result['distance'] = routes['length'] / 1000
    result['duration'] = math.trunc(routes['duration'] / 60)
    return result