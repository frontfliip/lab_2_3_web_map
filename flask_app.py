from flask import Flask
from flask import Response
import requests
import json
import folium as fo
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


def get_user_id(username):

    url = "https://api.twitter.com/2/users/by/username/" + username

    payload={}
    headers = {
    'Authorization': 'OAuth oauth_consumer_key="ZkCetUl5yQfvwtNglUyQOZxjX",oauth_token="1493549658597117958-dDksXeTSgbKeZWTXNjNZ9mzwS7j52j",oauth_signature_method="HMAC-SHA1",oauth_timestamp="1645042984",oauth_nonce="tHUOaER28oC",oauth_version="1.0",oauth_signature="qB2r98AB7%2F9ynGYh%2BHz09YdUHw0%3D"'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()["data"]["id"]

def get_friends_locations(id):

    url = "https://api.twitter.com/2/users/" + id + "/following?user.fields=location"

    payload={}
    headers = {
    'Authorization': 'OAuth oauth_consumer_key="ZkCetUl5yQfvwtNglUyQOZxjX",oauth_token="1493549658597117958-dDksXeTSgbKeZWTXNjNZ9mzwS7j52j",oauth_signature_method="HMAC-SHA1",oauth_timestamp="1645043546",oauth_nonce="4TnymrxnrGC",oauth_version="1.0",oauth_signature="uMXbEn47Tm4RbyzPBi8U7fJSJk0%3D"'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    response = response["data"]
    
    locations_lst = []
    for friend in response:
        if "location" in friend.keys():
            locations_lst.append([friend["name"], friend["location"]])
    return locations_lst

def get_coords(info_locations):
    """
    Gets coordinations of needed places and finds distance
    (float, float, list) -> list
    """
    geolocator = Nominatim(user_agent="main.py")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.001)
    for loc in info_locations:
        try:
            location = geolocator.geocode(loc[1])
            loc.append(location.latitude)
            loc.append(location.longitude)
        except:
            info_locations.remove(loc)
            continue
    new_info = []
    for i in range(len(info_locations)):
        if len(info_locations[i]) >= 4:
            new_info.append(info_locations[i])
    very_new_info = []
    for i in range(10):
        very_new_info.append(new_info[i])
    return very_new_info

def create_a_map(locs):
    """
    Creats a map and saves it
    """

    html_1 = """ Name: {} <br>
    Place: {} <br>
    """

    map = fo.Map(location=[locs[0][2], locs[0][3]], zoom_start=6)

    latitude = []
    longitude = []
    places = []
    name = []
    fg_list = []
    for item in locs:
        latitude.append(item[2])
        longitude.append(item[3])
        places.append(item[1])
        name.append(item[0])

    fg = fo.FeatureGroup(name="Friend's locations")
    for lt, ln, pl, nm in zip(latitude, longitude, places, name):
        iframe = fo.IFrame(html=html_1.format(nm, pl), width=400, height=150)
        fg.add_child(fo.Marker(location=[lt, ln], popup=fo.Popup(iframe), icon=fo.Icon(color="darkred")))
    fg_list.append(fg)

    for fg in fg_list:
        map.add_child(fg)
    map.add_child(fo.LayerControl())
    return map._repr_html_()

app = Flask(__name__)

@app.route('/twitter/map/<username>')
def get_map(username):    
    id = get_user_id(username)
    locations_lst = get_friends_locations(id)
    coords_and_locs= get_coords(locations_lst)
    return create_a_map(coords_and_locs)
