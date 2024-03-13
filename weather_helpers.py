import os
import requests
import urllib.request, json
from datetime import datetime

from flask import redirect, render_template, request, session
from functools import wraps

def coordinates(zipcode):
    """Get latitude and longitude for US zipcode"""

    # Contact API
    api_key = os.environ.get("API_KEY")
    print(api_key)
    url = f"http://api.openweathermap.org/geo/1.0/zip?zip={zipcode},pk&appid={api_key}"
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)

    return (dict)

def getweather(lat, lon, units, date="2024-03-13"):
    # Contact API
    api_key = os.environ.get("API_KEY")
    url = f"https://api.openweathermap.org/data/3.0/onecall/day_summary?lat={lat}&lon={lon}&date={date}&appid={api_key}"
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)

    return (dict)

def getaqi(lat, lon):
    # Contact API
    api_key = os.environ.get("API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={api_key}"
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)

    return (dict)