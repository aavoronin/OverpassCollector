import datetime
import pickle
import time
import json

from data.languages import languages
from objects3D.country_osm_data import country_info
from objects3D.map_box_info import map_box_info
from objects3D.overpass_base import overpass_base
import xml.etree.ElementTree as ET
import requests
import os
import pandas as pd
import geopandas as gpd
#import shapefile
#import partial


#from jsonpath_ng import jsonpath, parse
# https://wiki.openstreetmap.org/wiki/RU:Map_Features

class overpass_countries(overpass_base):
    def __init__(self):
        super().__init__()
        self.country_data = []
        self.country_border_coastline_osm_json = {}
        self.water_osm_json = {}
        self.loaded_country_codes = []
        self.skip_countrues = []
        self.selected_countries = []
        self.force_reload_cache = []
        self.tile_bboxes = []

        self.scan_zoom = 5
        self.scan_n = int(2.0 ** self.scan_zoom)
        self.use_tiles_limit = False
        self.tiles_limit_y = (0, 10)
        self.tiles_limit_x = (0, 32)

    def load(self):
        self.get_list_of_countries()
        self.get_list_of_country_codes()

    def get_list_of_countries(self):
        csv_format = 'csv(name,"ISO3166-1","not:ISO3166-1:alpha2",' + ",".join([f'"name:{lang[0]}"' for lang in languages]) + ')'
        query = 'relation["admin_level" = "2"][boundary = administrative];out;'
        result1 = self.exec_query_csv_format(query, csv_format)
        self.countries_df = pd.DataFrame(result1)

        new_header = self.countries_df.iloc[0]  # grab the first row for the header
        self.countries_df = self.countries_df[1:]  # take the data less the header row
        self.countries_df.columns = new_header  # set the header row as the df header
        self.countries_df.sort_values(by=["ISO3166-1", "name:en"])
        self.countries_df = self.countries_df.drop_duplicates(["ISO3166-1", "name:en"])
        self.countries_df.sort_values(by=["ISO3166-1", "name:en"])

        #print(self.countries_df.columns)

        self.countries_code_name = []
        for index, c_row in self.countries_df[
                    self.countries_df["ISO3166-1"].str.len() > 0][["ISO3166-1", "name:en"]].iterrows():
            country_code = c_row["ISO3166-1"]
            country_name_en = c_row["name:en"]
            self.countries_code_name.append((country_code, country_name_en))

        for index, c_row in self.countries_df[["ISO3166-1", "name:en", "name"]].iterrows():
            country_code = c_row["ISO3166-1"]
            country_name_en = c_row["name:en"]
            print(f'{country_code}, {country_name_en}')
        print("======")

    def extract_bounds(self, xml_string):
        root = ET.fromstring(xml_string)
        bounds_element = root.find('relation/bounds')

        minlat = float(bounds_element.get('minlat'))
        minlon = float(bounds_element.get('minlon'))
        maxlat = float(bounds_element.get('maxlat'))
        maxlon = float(bounds_element.get('maxlon'))

        return map_box_info([minlat, minlon, maxlat, maxlon])
    def get_countries_bounding_boxes(self):
        countries = self.get_current_countries()
        self.countries_bboxes = []
        for d in countries:
            query = f'''
                area["ISO3166-1"={d["ISO3166-1"]}]->.boundaryarea;
                (
                  rel(area.boundaryarea)["boundary"="administrative"]["admin_level"="2"];
                );
                out meta bb;'''
            #print(query)
            result = self.exec_query_json(query, build=False)
            bbox = self.extract_bounds(result)
            self.countries_bboxes.append({"code": d["ISO3166-1"], "name_en": d["name:en"], "bbox": bbox})

    def get_current_countries(self):
        if len(self.selected_countries) == 0:
            countries = [{"ISO3166-1": c_row["ISO3166-1"], "name:en": c_row["name:en"]}
                         for index, c_row in self.countries_df[["ISO3166-1", "name:en", "name"]].iterrows()]
        else:
            countries = [{"ISO3166-1": c_row["ISO3166-1"], "name:en": c_row["name:en"]}
                         for index, c_row in self.countries_df[["ISO3166-1", "name:en", "name"]].iterrows()
                         if c_row["ISO3166-1"] in self.selected_countries]
        countries = sorted(countries, key=lambda d: d["ISO3166-1"])
        return countries

    def get_countries_outer_borders(self):
        countries = self.get_current_countries()
        for d in countries:
            print(f'{d["ISO3166-1"]}, {d["name:en"]}')

        query = f'''[out:json][timeout:900];  
            rel["type"="boundary"]["admin_level" = "2"];  
            out geom;                        
        '''

        result = self.exec_query_json(query, build=False)

        for country_osm_data in result['elements']:
            ci = country_info(country_osm_data)
            ci.parse(self.get_list_of_tiles())
            self.country_data.append(ci)

        for ci in self.country_data:
            if len(countries) > 0 and not ci.country_code in [d["ISO3166-1"] for d in countries]:
                continue
            ci.load_country_borders()

        print(f'{len(countries)} countries')


    def get_list_of_tiles(self):
        self.init_tile_bboxes()
        tiles_xy = []
        for ytile in range(len(self.tile_bboxes)):
            if self.use_tiles_limit and (ytile < self.tiles_limit_y[0] or ytile > self.tiles_limit_y[1]):
                continue
            for xtile in range(len(self.tile_bboxes[0])):
                if self.use_tiles_limit and (xtile < self.tiles_limit_x[0] or xtile > self.tiles_limit_x[1]):
                    continue
                tiles_xy.append((xtile, ytile))
        return tiles_xy

    def get_list_of_admin_level_2_borders(self, log_all_queries= False):
        self.countries_names = {}
        i = 0
        for (xtile, ytile) in self.get_list_of_tiles():
            try:
                start_time = time.time()
                bbox_info = self.tile_bboxes[ytile][xtile]
                bbox_str = bbox_info.bbox_str

                #csv_format = 'csv(name,"ISO3166-1","not:ISO3166-1:alpha2",' + ",".join(
                #    [f'"name:{lang[0]}"' for lang in languages]) + ')'
                csv_format = 'csv(name,"ISO3166-1","not:ISO3166-1:alpha2","name:en")'
                query = f'''
                    rel["type"="boundary"]["admin_level" = "2"]({bbox_str});  
                    out tags;                        
                '''

                print(f'[out:{csv_format}];{query}')
                result = self.exec_query_csv_format(query, csv_format)
                bbox_info.countries_df = pd.DataFrame(result)

                new_header = bbox_info.countries_df.iloc[0]  # grab the first row for the header
                bbox_info.countries_df = bbox_info.countries_df[1:]  # take the data less the header row
                bbox_info.countries_df.columns = new_header  # set the header row as the df header
                bbox_info.countries_df.sort_values(by=["name:en"], ascending=True)

                #if (xtile, ytile) == (8, 5):
                #    print(1)

                countries_here = []
                for index, c_row in bbox_info.countries_df[["name:en", "name", "ISO3166-1"]].iterrows():
                    country_name_en = c_row["name:en"]
                    if len(country_name_en) == 0:
                        continue
                    #print(f'"{country_name}", "{country_name_en}"')
                    if not country_name_en in self.countries_names:
                        self.countries_names[country_name_en] = c_row
                    if not country_name_en in countries_here:
                        countries_here.append(country_name_en)
                        print(f'"{country_name_en}": {c_row["ISO3166-1"]}')
                i += 1

                end_time = time.time()
                time_lapsed = end_time - start_time
                print(f'{i:5} tile: {self.scan_n} {xtile} {ytile} {len(self.countries_names.keys())} {datetime.datetime.now()} ({time_lapsed} secs)')
            except Exception as e:
                print(e)

        for country_name_en in self.countries_names:
            print(f'"{country_name_en}": {self.countries_names[country_name_en]["ISO3166-1"]}')

        self.countries_bboxes = {}

        i = 0
        for (xtile, ytile) in self.get_list_of_tiles():
            try:
                bbox_info = self.tile_bboxes[ytile][xtile]
                bbox_str = f"{bbox_info.bbox[0]},{bbox_info.bbox[1]},{bbox_info.bbox[2]},{bbox_info.bbox[3]}"
                bbox_info.countries_borders = {}
                country_codes_done = []
                for index, c_row in bbox_info.countries_df[["name:en", "name", "ISO3166-1"]].iterrows():
                    i += 1
                    start_time = time.time()
                    country_code = c_row["ISO3166-1"]
                    if country_code in country_codes_done:
                        continue
                    if country_code == "":
                        continue
                    if country_code not in self.selected_countries and len(self.selected_countries) > 0:
                        continue
                    query = f'''
                        [out:json][timeout:900];  
                        area["ISO3166-1"="{country_code}"]({bbox_str})->.country;
                        rel["ISO3166-1"="{country_code}"]["type"="boundary"]["admin_level"="2"]({bbox_str});
                        (
                            way(r)({bbox_str});
                            way(area.country)["natural"="coastline"]({bbox_str});
                        );
                        out geom;                                            
                    '''
                    if log_all_queries:
                        print(f'/*{xtile} {ytile}*/ {query}')
                    if country_code in self.force_reload_cache:
                        self.clear_cache_query_json(query, "", False)
                    result = self.exec_query_json(query, "", False)
                    bbox_info.countries_borders[country_code] = result
                    country_codes_done.append(country_code)

                    if country_code not in self.countries_bboxes:
                        self.countries_bboxes[country_code] = []
                    self.countries_bboxes[country_code].append(bbox_info)

                    end_time = time.time()
                    time_lapsed = end_time - start_time

                    result_pickled = pickle.dumps(result)
                    print(
                        f'{i:5} tile: {self.scan_n} {xtile} {ytile} {country_code}: {len(result_pickled)} {datetime.datetime.now()} ({time_lapsed} secs)')
                    del result_pickled

            except Exception as e:
                print(e)

        print("===========")

        for country_code in self.countries_bboxes:
            print(f'{country_code}: {len(self.countries_bboxes[country_code])}')

        print("===========")


    def load_countries_polygons(self):
        self.countries_osm_json = {}
        i = 0
        for index, c_row in self.countries_df[self.countries_df["ISO3166-1"].str.len() > 0][["ISO3166-1", "name:en"]].iterrows():
            country_code = c_row["ISO3166-1"]
            if country_code in self.countries_osm_json:
                continue
            i += 1
            country_name = c_row["name:en"]
            query = f'''relation["boundary"="administrative"]["admin_level"="2"]["ISO3166-1"="{country_code}"];
                out geom;    
            '''
            result = self.exec_query_json(query, "body geom")
            self.countries_osm_json[country_code] = result
            result_pickled = pickle.dumps(result)
            print(f'{i:5} json for {country_code} loaded -- country "{country_name}" {len(result_pickled)} {datetime.datetime.now()}')
            del result_pickled

    def load_countries_polygons_level4(self):
        self.countries_osm_json = {}
        i = 0
        for index, c_row in self.countries_df[self.countries_df["ISO3166-1"].str.len() > 0][["ISO3166-1", "name:en"]].iterrows():
            country_code = c_row["ISO3166-1"]
            if country_code in self.countries_osm_json:
                continue
            i += 1
            #if country_code != "NO":
            #    continue
            #if country_code == "NO":
            #    print(country_code)
            country_name = c_row["name:en"]
            query = f'''
                rel["ISO3166-2"~"^{country_code}"]
                   [admin_level=4]
                   [type=boundary]
                   [boundary=administrative];
                out geom;
            '''
            result = self.exec_query_json(query, "body geom")
            self.countries_osm_json[country_code] = result
            result_pickled = pickle.dumps(result)
            print(f'{i:5} json for {country_code} loaded -- country "{country_name}" {len(result_pickled)} {datetime.datetime.now()}')
            del result_pickled

    def load_countries_polygons_coastline(self, list_to_load=[]):
        i = 0

        for index, c_row in self.countries_df[self.countries_df["ISO3166-1"].str.len() > 0][
            ["ISO3166-1", "name:en"]].iterrows():
            country_code = c_row["ISO3166-1"]
            if len(list_to_load) > 0 and country_code not in list_to_load:
                continue
            if country_code in self.loaded_country_codes:
                continue
            if country_code in self.skip_countrues:
                continue
            i += 1
            print(f'{i:5} json for {country_code}')
            self.loaded_country_codes.append(country_code)
            country_name = c_row["name:en"]

            self.load_country_polygon_data(country_code, country_name, i)

    def load_country_border_data(self, country_code, country_name, i):
        query = f'''   
                [out:json][timeout:900];             
                area["ISO3166-1"="{country_code}"]->.country;
                rel["ISO3166-1"="{country_code}"]["type"="boundary"]["admin_level"="2"];  
                (
                    way(r)["maritime" != "yes"];
                    way(area.country)["natural"="coastline"];
                );
                out body geom;                
            '''
        result = self.load_and_log_query_for_country(country_code, country_name, i, query)
        self.country_border_coastline_osm_json[country_code] = result

    def load_country_border_data_v2(self, country_code, country_name, i):

        result = []
        if country_code in self.countries_bboxes:
            for bbox_info in self.countries_bboxes[country_code]:
                if country_code in bbox_info.countries_borders:
                    bbox_result = bbox_info.countries_borders[country_code]
                    if "elements" in bbox_result:
                        result.extend(bbox_result["elements"])

        print(f"{country_code} {len(result)}")
        self.country_border_coastline_osm_json[country_code] = result

    def load_country_border_data_v3(self, ci: country_info, i):

        result = []
        if 'elements' in ci.non_maritime_border:
            result.extend([element for element in ci.non_maritime_border['elements']])
        if 'elements' in ci.coastline:
            result.extend([element for element in ci.coastline['elements']])
        ci.country_border_coastline_osm_json = result
        print(f"border data for {ci.country_code} {len(result)}")

    def load_country_lake_data(self, country_code, country_name, i):
        query = f'''   
                [out:json][timeout:900];             
                area["ISO3166-1"="{country_code}"]->.country;
                rel["ISO3166-1"="{country_code}"]["type"="boundary"]["admin_level"="2"];  
                (
                    rel(area.country)["water"="lake"](if: length() > 100000);
                );
                out body geom;                
            '''
        result = self.load_and_log_query_for_country(country_code, country_name, i, query)
        self.water_osm_json[country_code] = result

    def load_and_log_query_for_country(self, country_code, country_name, i, query):
        start_time = time.time()
        result = self.exec_query_json(query, "body geom", build=False)
        end_time = time.time()
        time_lapsed = end_time - start_time
        result_pickled = pickle.dumps(result)
        print(f'{i:5} json for {country_code} loaded -- country "{country_name}" '
              f'{len(result_pickled)} {datetime.datetime.now()} ({time_lapsed} secs)')
        del result_pickled
        return result

    def get_list_of_country_codes(self):
        self.real_countries = self.countries_df[self.countries_df["ISO3166-1"].str.len() > 0][
            ["ISO3166-1", "name", "name:en", "name:ru", "name:ja"]]
        self.real_countries.sort_values(by=["ISO3166-1"], ascending=True)

    def get_countries_water_polygons(self):
        countries = self.get_current_countries()

        for ci in self.country_data:
            if len(countries) > 0 and not ci.country_code in [d["ISO3166-1"] for d in countries]:
                continue
            ci.load_country_lake_data()

        print(f'{len(countries)} countries')


    def get_global_land_polygons(self, zoom):
        folder = "c:/Data/natural_earth/ne_10m_land/"
        url = ''
        file = "ne_10m_land.shp"
        start_time = time.time()

        if not os.path.exists(os.path.join(folder, file)):
            self.download_natural_earth_dataset(folder, file, url)

        gdf = gpd.read_file(os.path.join(folder, file))
        geometry = gdf
        self.global_land_polygons_xy = land_polygons = {}
        self.collect_polygons(geometry, land_polygons, zoom)

        end_time = time.time()
        print(f'continent polygons ({end_time-start_time})')

    def get_global_land_polygons2(self, zoom):
        start_time = time.time()
        folder = "c:/Data/natural_earth/ne_10m_land/"
        f_name1 = "land_polygons10_outer.txt"
        f_name = os.path.join(folder, f_name1)

        with open(f_name, 'r') as file:
            # Read the entire content of the file
            data = file.read()
        self.global_land_outer_polygons = json.loads(data)
        self.global_land_outer_polygons_xy = [[
            [self.deg2xy(lat_lon[1], lat_lon[0], zoom) for lat_lon in poly]
                    for poly in json.loads(data) if len(poly) > 2], []]

        f_name1 = "land_polygons10_inner.txt"
        f_name = os.path.join(folder, f_name1)

        with open(f_name, 'r') as file:
            # Read the entire content of the file
            data2 = file.read()
        self.global_land_inner_polygons_xy = [[
            [self.deg2xy(lat_lon[1], lat_lon[0], zoom) for lat_lon in poly]
                    for poly in json.loads(data2) if len(poly) > 2], []]

        del data
        del data2

        end_time = time.time()
        print(f'land polygons ({end_time-start_time})')

        #print(f'{len(countries)} countries')

    def download_natural_earth_dataset(self, folder, file, url):
        if not os.path.exists(folder):
            os.makedirs(folder)
        response = requests.get(url)
        #z = zipfile.ZipFile(BytesIO(response.content))
        #z.extractall(path=folder)

        with open(os.path.join(folder, file), 'wb') as file:
            file.write(response.content)

    def get_continents_borders(self, zoom):
        folder = "c:/Data/natural_earth/ne-10m/"
        #file = "ne_10m_admin_0_countries.shp"

        start_time = time.time()
        # 'https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip'
        file_name_gdf_countries = "ne_10m_admin_0_countries.shp"
        file_name_gdf_states_province = "ne_10m_admin_1_states_provinces.shp"
        gdf_countries = gpd.read_file(os.path.join(folder, file_name_gdf_countries))
        gdf_provinces = gpd.read_file(os.path.join(folder, file_name_gdf_states_province))

        self.global_continent_polygons_xy = dict()
        for continent in gdf_countries["CONTINENT"].unique():
            if continent == 'Europe':
                continent_geometry = self.get_europe_geom(gdf_countries, gdf_provinces)
            elif continent == 'Asia':
                continent_geometry = self.get_asia_geom(gdf_countries, gdf_provinces)
            else:
                continent_geometry = gdf_countries[gdf_countries['CONTINENT'] == continent]
            print(f"geometry for {continent}")
            continent_polygons = {}
            self.global_continent_polygons_xy[continent] = continent_polygons
            self.collect_polygons(continent_geometry, continent_polygons, zoom)

        end_time = time.time()
        print(f'continent polygons ({end_time-start_time})')

    def get_europe_geom(self, gdf_countries, gdf_provinces):
        # Step 1: Filter all countries which are marked as 'CONTINENT' == 'Europe'
        europe_countries = gdf_countries[gdf_countries['CONTINENT'] == 'Europe']
        # Step 2: Exclude Russia, France, and Turkey
        excluded_countries = ['Russia', 'France',
                              #'Turkey'
                              ]
        europe_countries = europe_countries[~europe_countries['NAME'].isin(excluded_countries)]
        # Fill null values with '-'
        gdf_provinces['name'] = gdf_provinces['name'].fillna('-')
        selected_provinces_Russia = gdf_provinces[
            (gdf_provinces['admin'] == 'Russia') &
            (gdf_provinces['region'].isin(['Northwestern', 'Volga', 'Central']))]

        selected_provinces_France = gdf_provinces[
            (gdf_provinces['admin'] == 'France') &
            ~(gdf_provinces['region'].isin(['Guyane française', 'Martinique', 'Guadeloupe', 'Réunion', 'Mayotte']))]

        europe = pd.concat([europe_countries, selected_provinces_Russia, selected_provinces_France])
        return europe

    def get_asia_geom(self, gdf_countries, gdf_provinces):
        # Step 1: Filter all countries which are marked as 'CONTINENT' == 'Asia'
        europe_countries = gdf_countries[gdf_countries['CONTINENT'] == 'Asia']
        # Step 2: Exclude Russia, France, and Turkey
        excluded_countries = ['Russia'
                #, 'France', 'Turkey'
                              ]
        europe_countries = europe_countries[~europe_countries['NAME'].isin(excluded_countries)]
        # Fill null values with '-'
        gdf_provinces['name'] = gdf_provinces['name'].fillna('-')
        selected_provinces = gdf_provinces[
            (gdf_provinces['admin'] == 'Russia') &
            ~(gdf_provinces['region'].isin(['Northwestern', 'Volga', 'Central']))]

        europe = pd.concat([europe_countries, selected_provinces])
        return europe
