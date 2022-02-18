"""
A module for creating a map of user twitter's 25 friend's locations
"""
from flask import Flask
import folium as fo
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from requests_oauthlib import OAuth1Session


consumer_key = "ZkCetUl5yQfvwtNglUyQOZxjX"
consumer_secret = "rnrAIp9tRMnQ1ODWCH0GTvEyFimIBFnrR7Sa1WNyQVH1dcxUBD"
access_token = "1493549658597117958-dDksXeTSgbKeZWTXNjNZ9mzwS7j52j"
token_secret = "hC66cal6lNrNbxXCkDJSLG9nvVtz1TQzTHIeuKZKzLfTs"


def get_user_id(username):
    """
    Returns user's id from twitter
    (str) -> str
    """

    url = "https://api.twitter.com/2/users/by/username/" + username

    twitter = OAuth1Session(consumer_key, client_secret=consumer_secret, resource_owner_key=access_token, resource_owner_secret=token_secret)
    response = twitter.get(url)

    return response.json()["data"]["id"]


def get_friends_locations(id):
    """
    Returns user friends locations
    (str) -> list
    """
    url = "https://api.twitter.com/2/users/" + id + "/following?user.fields=location"

    twitter = OAuth1Session(consumer_key, client_secret=consumer_secret, resource_owner_key=access_token, resource_owner_secret=token_secret)
    response = twitter.get(url).json()["data"]

    locations_lst = []
    for friend in response:
        if "location" in friend.keys():
            locations_lst.append([friend["name"], friend["location"]])
    return locations_lst


def get_coords(info_locations):
    """
    Gets coordinations of 25 needed places
    (list) -> list
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
    if len(new_info) < 25:
        num = len(new_info)
        for i in range(num):
            very_new_info.append(new_info[i])
    else:
        for i in range(25):
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
        iframe = fo.IFrame(html=html_1.format(nm, pl), width=200, height=100)
        fg.add_child(fo.Marker(location=[lt, ln], popup=fo.Popup(iframe), icon=fo.Icon(color="darkred")))
    fg_list.append(fg)

    for fg in fg_list:
        map.add_child(fg)
    map.add_child(fo.LayerControl())
    return map._repr_html_()

app = Flask(__name__)


@app.route('/twitter/map/<username>')
def get_map(username):
    """
    main func
    """
    id = get_user_id(username)
    locations_lst = get_friends_locations(id)
    coords_and_locs = get_coords(locations_lst)
    return create_a_map(coords_and_locs)
