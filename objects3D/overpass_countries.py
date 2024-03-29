import datetime
import hashlib
import pickle
import time
import json

from shapely import Polygon, Point

from data.languages import languages
from objects3D.country_osm_data import country_info
from objects3D.map_box_info import map_box_info
from objects3D.overpass_base import overpass_base
import xml.etree.ElementTree as ET
import requests
import os
import pandas as pd
import geopandas as gpd
from scipy.spatial import distance

from objects3D.polygon_fill_info import polygon_fill_info


#import shapefile
#import partial


#from jsonpath_ng import jsonpath, parse
# https://wiki.openstreetmap.org/wiki/RU:Map_Features

class overpass_countries(overpass_base):
    def __init__(self, lang="en"):
        super().__init__()
        self.lang = lang
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
        self.continent_info = []
        self.ocean_info = []
        self.countries_info = []
        self.global_continent_polygons_xy = None

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


    def get_global_land_polygons(self):
        folder = "c:/Data/natural_earth/ne_10m_land/"
        url = ''
        file = "ne_10m_land.shp"
        start_time = time.time()

        cache_name = f"lang ne-10m"
        md5 = hashlib.md5(cache_name.encode('utf-8')).hexdigest()
        fname = f"{self.cache_path}\\{str(md5)}.zlib"
        self.global_land_polygons_xy = self.try_load_from_cache(fname)
        if self.global_land_polygons_xy is None:
            gdf = gpd.read_file(os.path.join(folder, file))
            geometry = gdf
            self.global_land_polygons_xy = land_polygons = {}
            self.collect_polygons(geometry, land_polygons)
            #[self.deg2xy(point[1], point[0], zoom) for point in polygon.exterior.coords]
            self.save_to_cache(fname, self.global_land_polygons_xy)

        end_time = time.time()
        print(f'land polygons ({end_time-start_time})')

    def download_natural_earth_dataset(self, folder, file, url):
        if not os.path.exists(folder):
            os.makedirs(folder)
        response = requests.get(url)
        with open(os.path.join(folder, file), 'wb') as file:
            file.write(response.content)

    def get_country_borders(self):
        start_time = time.time()
        cache_name = f"country_borders ne-10m"
        md5 = hashlib.md5(cache_name.encode('utf-8')).hexdigest()
        fname = f"{self.cache_path}\\{str(md5)}.zlib"
        self.global_country_land_borders = self.try_load_from_cache(fname)
        if self.global_country_land_borders is None:
            folder = "c:/Data/natural_earth/ne-10m/"
            # 'https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip'
            file_name_gdf_countries = "ne_10m_admin_0_countries.shp"
            gdf_countries = gpd.read_file(os.path.join(folder, file_name_gdf_countries))

            geometry = gdf_countries
            country_polygons = {}
            self.global_country_land_borders = country_polygons
            self.collect_polygons(geometry, country_polygons)
            self.save_to_cache(fname, self.global_continent_polygons_xy)

        end_time = time.time()
        print(f'country polygons ({end_time-start_time})')

    def get_continents_borders(self):
        start_time = time.time()
        cache_name = f"continents_borders ne-10m"
        fname = self.get_cache_file_name(cache_name)
        self.global_continent_polygons_xy = self.try_load_from_cache(fname)
        if self.global_continent_polygons_xy is None:
            folder = "c:/Data/natural_earth/ne-10m/"
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
                elif continent == 'Africa':
                    continent_geometry = self.get_africa_geom(gdf_countries, gdf_provinces)
                elif continent == 'South America':
                    continent_geometry = self.get_south_america_geom(gdf_countries, gdf_provinces)
                else:
                    continent_geometry = gdf_countries[gdf_countries['CONTINENT'] == continent]
                print(f"geometry for {continent}")
                continent_polygons = {}
                self.global_continent_polygons_xy[continent] = continent_polygons
                self.collect_polygons(continent_geometry, continent_polygons)

            self.save_to_cache(fname, self.global_continent_polygons_xy)

        cache_name2 = f"continents_bboxes ne-10m"
        fname2 = self.get_cache_file_name(cache_name2)
        self.global_continent_bboxes = self.try_load_from_cache(fname2)
        if self.global_continent_bboxes is None:
            self.global_continent_bboxes = dict()
            for continent, continent_geometry in self.global_continent_polygons_xy.items():
                self.global_continent_bboxes[continent] = self.get_lat_lon_bbox(continent_geometry["outer"])
                #print(continent, self.global_continent_bboxes[continent])
            for continent, continent_geometry in self.global_continent_polygons_xy.items():
                print(f'"{continent}",')
            #self.save_to_cache(fname2, self.global_continent_bboxes)
        end_time = time.time()
        print(f'continent polygons ({end_time-start_time})')

    def get_europe_geom(self, gdf_countries, gdf_provinces):
        # Step 1: Filter all countries which are marked as 'CONTINENT' == 'Europe'
        europe_countries = gdf_countries[gdf_countries['CONTINENT'] == 'Europe']
        # Step 2: Exclude Russia, France, and Turkey
        excluded_countries = ['Russia', 'France',  'Turkey' ]
        europe_countries = europe_countries[~europe_countries['NAME'].isin(excluded_countries)]
        # Fill null values with '-'
        gdf_provinces['name'] = gdf_provinces['name'].fillna('-')
        selected_provinces_Russia = gdf_provinces[
            (gdf_provinces['admin'] == 'Russia') &
            (gdf_provinces['region'].isin(['Northwestern', 'Volga', 'Central']))]

        selected_provinces_France = gdf_provinces[
            (gdf_provinces['admin'] == 'France') &
            ~(gdf_provinces['region'].isin(['Guyane française', 'Martinique', 'Guadeloupe', 'Réunion', 'Mayotte']))]

        turkey_in_europe = ['Edirne', 'Tekirdag', 'Kirklareli']
        selected_provinces_Turkey = gdf_provinces[
            (gdf_provinces['admin'] == 'Turkey') &
            (gdf_provinces['name'].isin(['Edirne', 'Tekirdag', 'Kirklareli']))]

        europe = pd.concat([europe_countries, selected_provinces_Russia, selected_provinces_France, selected_provinces_Turkey])
        return europe

    def get_asia_geom(self, gdf_countries, gdf_provinces):
        # Step 1: Filter all countries which are marked as 'CONTINENT' == 'Asia'
        asia_countries = gdf_countries[gdf_countries['CONTINENT'] == 'Asia']
        # Step 2: Exclude Russia, France, and Turkey
        excluded_countries = ['Russia', 'Turkey']
        asia_countries = asia_countries[~asia_countries['NAME'].isin(excluded_countries)]
        # Fill null values with '-'
        gdf_provinces['name'] = gdf_provinces['name'].fillna('-')
        selected_provinces_Russia = gdf_provinces[
            (gdf_provinces['admin'] == 'Russia') &
            ~(gdf_provinces['region'].isin(['Northwestern', 'Volga', 'Central']))]

        turkey_in_europe = ['Edirne', 'Tekirdag', 'Kirklareli']
        selected_provinces_Turkey = gdf_provinces[
            (gdf_provinces['admin'] == 'Turkey') &
            ~(gdf_provinces['name'].isin(['Edirne', 'Tekirdag', 'Kirklareli']))]

        selected_provinces_Egypt = gdf_provinces[
            (gdf_provinces['admin'] == 'Egypt') &
            (gdf_provinces['name_en'].isin(['South Sinai', 'North Sinai']))]

        asia = pd.concat([asia_countries, selected_provinces_Russia, selected_provinces_Turkey, selected_provinces_Egypt])
        return asia

    def get_south_america_geom(self, gdf_countries, gdf_provinces):
        # Step 1: Filter all countries which are marked as 'CONTINENT' == 'Asia'
        europe_countries = gdf_countries[gdf_countries['CONTINENT'] == 'South America']
        # Step 2: Exclude Russia, France, and Turkey
        excluded_countries = []
        europe_countries = europe_countries[~europe_countries['NAME'].isin(excluded_countries)]
        # Fill null values with '-'
        gdf_provinces['name'] = gdf_provinces['name'].fillna('-')
        selected_provinces_France = gdf_provinces[
            (gdf_provinces['admin'] == 'France') &
            (gdf_provinces['region'].isin(['Guyane française']))]

        europe = pd.concat([europe_countries, selected_provinces_France])
        return europe

    def get_africa_geom(self, gdf_countries, gdf_provinces):
        africa_countries = gdf_countries[gdf_countries['CONTINENT'] == 'Africa']
        excluded_countries = ['Egypt']
        africa_countries = africa_countries[~africa_countries['NAME'].isin(excluded_countries)]
        # Fill null values with '-'
        gdf_provinces['name'] = gdf_provinces['name'].fillna('-')
        
        selected_provinces_Egypt = gdf_provinces[
            (gdf_provinces['admin'] == 'Egypt') &
            ~(gdf_provinces['name_en'].isin(['South Sinai', 'North Sinai']))]

        africa = pd.concat([africa_countries, selected_provinces_Egypt])
        return africa

    def get_continent_labels(self, label_size):
        query = '''[out:json];node["place"="continent"];out;'''
        data = self.exec_query_json(query, "out", build=False)
        self.get_labels_info(data, self.continent_info, self.lang)
        self.continent_info = [{**info, "size": label_size} for info in self.continent_info]
        europe = next(filter(lambda o: o["name_en"].startswith("Europe"), self.continent_info), None)
        europe['lon'] += 20.0
        europe['size'] *= 2
        asia = next(filter(lambda o: o["name_en"].startswith("Asia"), self.continent_info), None)
        asia['lat'] -= 20.0
        asia['size'] *= 2.5
        n_america = next(filter(lambda o: o["name_en"].startswith("North"), self.continent_info), None)
        n_america['lon'] += 15.0
        n_america['lat'] -= 10.0
        s_america = next(filter(lambda o: o["name_en"].startswith("South"), self.continent_info), None)
        s_america['lat'] += 15.0
        s_america['lon'] += 5.0
        antarctica = next(filter(lambda o: o["name_en"].startswith("Antarctica"), self.continent_info), None)
        antarctica['lon'] = 0.0
        for info in self.continent_info:
            if abs(info["lat"]) < 60 and len(info["name"]) > 10:
                info["name"] = self.make_multiline(info)
            info["lines"] = 2 if '\n' in info["name"] else 1


    def make_multiline(self, info):
        return self.split_string(info["name"])

    def split_string(self, s):
        # Find the median point of the string
        mid = len(s) // 2

        # Find all occurrences of whitespace in the string
        whitespaces = [i for i, char in enumerate(s) if char == ' ']

        # If no whitespace exists, return the string as is
        if not whitespaces:
            return s

        # Determine the whitespace which is closest to the median point
        closest_whitespace = min(whitespaces, key=lambda ws: abs(ws - mid))

        # Split the string at that whitespace
        return f'{s[:closest_whitespace]}\n{s[closest_whitespace + 1:]}'

    def get_ocean_labels(self, label_size):
        query = '''[out:json];node["place"="ocean"];out;'''
        data = self.exec_query_json(query, "out", build=False)
        self.get_labels_info(data, self.ocean_info, self.lang)
        self.ocean_info = [{**info, "size": label_size} for info in self.ocean_info]
        for o in self.ocean_info:
            print(f'"{o["name_en"]}",')
        arctic = next(filter(lambda o: o["name_en"].startswith("Arctic"), self.ocean_info), None)
        arctic['lat'] = 75.0
        pacific = next(filter(lambda o: o["name_en"].startswith("Pacific"), self.ocean_info), None)
        pacific['size'] *= 2.5
        for info in self.ocean_info:
            if abs(info["lat"]) < 60 and len(info["name"]) > 10:
                info["name"] = self.make_multiline(info)
            info["lines"] = 2 if '\n' in info["name"] else 1

    def get_labels_info(self, data, info, lang):
        name_tag_lang = f'name:{lang}'
        name_tag_en = f'name:en'
        for element in data['elements']:
            try:
                lat = element['lat']
                lon = element['lon']
                tags = element['tags']
                name = tags[name_tag_lang] if name_tag_lang in tags else tags[name_tag_en] \
                    if name_tag_en in tags else tags["name"] if "name" in tags else '-'
                name_en = tags[name_tag_en] if name_tag_en in tags else tags["name"] if "name" in tags else '-'
                info.append({"lat": lat, "lon": lon, "name": name, "name_en": name_en})
            except KeyError:
                continue

    def get_lat_lon_bbox(self, lat_lon_geom):
        d = 0.0001

        portion_to_reduce = 0.2
        # Assume polygons is a list of polygons, where each polygon is a list of tuples (x, y)
        total_area = 0
        total_mass = 0
        total_x = 0
        total_y = 0

        polygons2 = lat_lon_geom.copy()
        polygons = []
        for polygon in polygons2:
            # Create a Polygon object
            poly = Polygon(polygon)

            # Calculate area
            area = poly.area
            total_area += area
            total_mass += area

            # Calculate center of mass (centroid)
            centroid = poly.centroid
            total_x += area * centroid.x
            total_y += area * centroid.y
            polygons.append(poly)

        # Calculate final center of mass
        final_x = total_x / total_mass
        final_y = total_y / total_mass
        final_centroid = (final_x, final_y)

        polygons1 = [poly for poly in polygons if poly.area > 0.01 * total_area]

        # Sort polygons by distance from final centroid
        sorted_polygons = sorted(polygons1, key=lambda polygon: distance.euclidean(
            final_centroid, (polygon.centroid.x, polygon.centroid.y)))

        # Exclude most distant polygons until total area is reduced not less than 20%
        while len(sorted_polygons) > 1 and total_area * (1.0 - portion_to_reduce) < sum(poly.area for poly in sorted_polygons):
            sorted_polygons.pop()
        #lat_lon_geom
        poly = sorted_polygons[0]
        min_maxes = [
            #(min([p[0] for p in poly]), min([p[1] for p in poly]), max([p[0] for p in poly]), max([p[1] for p in poly]))
            poly.bounds for poly in sorted_polygons
        ]
        min_maxes0 = [min([m[0] for m in min_maxes]), min([m[1] for m in min_maxes]),
                      max([m[2] for m in min_maxes]), max([m[3] for m in min_maxes])]

        #if min_maxes0[3] - min_maxes0[1] > 350:
        #    bbox = {
        #        "bbox": [min_maxes0[0], -180, min_maxes0[2], 180.0],
        #        "width": 360.0,
        #        "height": (min_maxes0[2] - min_maxes0[0]),
        #        "center_lat": (min_maxes0[0] + min_maxes0[2]) / 2.0,
        #        "center_lon": 0.0,
        #    }
        #el
        if min_maxes0[3] - min_maxes0[1] > 180:
            min_maxes1 = [min([m[1] for m in min_maxes if m[1] < 0] + [0]), max([m[3] for m in min_maxes if m[3] < 0] + [0])]
            min_maxes2 = [min([m[1] for m in min_maxes if m[1] > 0] + [0]), max([m[3] for m in min_maxes if m[3] > 0] + [0])]
            width = (360.0 + min_maxes1[1] - min_maxes2[0])
            center_lon = (360.0 + min_maxes1[1] + min_maxes2[0]) / 2.0
            min_maxes3 = [min_maxes0[0], min_maxes2[0], min_maxes0[2], min_maxes1[1]]
            if center_lon > 180.0:
                center_lon -= 360.0
            bbox = {
                "bbox": min_maxes3,
                "width": width,
                "height": (min_maxes0[2] - min_maxes0[0]),
                "center_lat": (min_maxes0[0] + min_maxes0[2]) / 2.0,
                "center_lon": center_lon,
            }
        else:
            bbox = {
                "bbox": min_maxes0,
                "width": (min_maxes0[3] - min_maxes0[1]),
                "height": (min_maxes0[2] - min_maxes0[0]),
                "center_lat": (min_maxes0[0] + min_maxes0[2]) / 2.0,
                "center_lon": (min_maxes0[1] + min_maxes0[3]) / 2.0,
            }

        bbox["n"] = len(lat_lon_geom)

        return bbox
