# https://automating-gis-processes.github.io/CSC18/lessons/L3/retrieve-osm-data.html
# https://api.openstreetmap.org/api/0.6/map?bbox=11.54,48.14,11.543,48.145
# https://api.openstreetmap.org/api/0.6/map?bbox=27.95,86.90,28.02,86.95
# https://stackoverflow.com/questions/65748099/open-elevation-api-for-python
import folium
import pandas as pd


def test_follium():

    m = folium.Map(location=[45.5236, -122.6750])
    m.save('index_map.html')

    my_map2 = folium.Map(location=[28.5011226, 77.4099794],
                         zoom_start=12)

    # CircleMarker with radius
    folium.CircleMarker(location=[28.5011226, 77.4099794],
                        radius=50, popup=' FRI ').add_to(my_map2)

    # save as html
    my_map2.save(" my_map2.html ")
