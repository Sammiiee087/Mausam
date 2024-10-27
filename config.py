import json

with open('config.json') as json_file:
    config = json.load(json_file)
    COMPANY_NAME = config["Company_Name"]
    FLASK_KEY = config['Flask_Key']
    WEATHERAPI_KEY = config['Weatherapi_Key']
    GOOGLEMAPSAPI_KEY = config['GoogleMaps_Key']