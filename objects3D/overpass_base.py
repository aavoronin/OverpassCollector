import hashlib
import json
import math
import os
import pickle
import time
import zlib

#import time
import overpy
import overpass
from shapely import MultiPolygon, Polygon

#https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL
#http://overpass-turbo.eu/
#tiles math https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
#warter borders https://gis.stackexchange.com/questions/157842/how-to-get-landmass-polygons-for-bounding-box-in-overpass-api
#https://www.mathworks.com/help/matlab/ref/geoplot.html
from objects3D.map_box_info import map_box_info
from objects3D.relation_info import relation_info


class overpass_base:
    def __init__(self):
        self.api = overpass.API(timeout=900)
        self.api2 = overpy.Overpass()
        self.cache_path = "c:\\Cache\\cache_overpass"
        self.max_retries = 10
        self.retry_delay = 20

    def try_load_from_cache(self, fname):
        if os.path.isfile(fname) and os.path.getsize(fname) > 0:
            with open(fname, "rb") as f:
                result_compressed = f.read()
                result_pickled = zlib.decompress(result_compressed)
                result = pickle.loads(result_pickled)
                del result_compressed
                del result_pickled
                return result
        return None

    def save_to_cache(self, fname, result):
        result_pickled = pickle.dumps(result)
        result_compressed = zlib.compress(result_pickled, 9)
        with open(fname, "wb") as f:
            f.write(result_compressed)
            f.close()
        del result_compressed
        del result_pickled

    def exists_in_cache_query_json(self, query, verbosity = "", build=True):
        try:
            md5 = hashlib.md5((query + verbosity).encode('utf-8')).hexdigest()
            fname = f"{self.cache_path}\\{str(md5)}.zlib"
            result = self.try_load_from_cache(fname)
            if result is not None:
                return True
        except:
            pass

        return False

    def clear_cache_query_json(self, query, verbosity, build=True):
        try:
            md5 = hashlib.md5((query + verbosity).encode('utf-8')).hexdigest()
            fname = f"{self.cache_path}\\{str(md5)}.zlib"
            os.remove(fname)
        except Exception as err:
            print(f"error: {err} {query}")

    def exec_query_json(self, query, verbosity="", build=True):
        try:
            md5 = hashlib.md5((query + verbosity).encode('utf-8')).hexdigest()
            fname = f"{self.cache_path}\\{str(md5)}.zlib"
            result = self.try_load_from_cache(fname)
            if result is not None:
                return result
        except Exception as err:
            print(f"error: {err} {query}")
        retry = self.max_retries
        while retry > 0:
            try:
                result = self.api.get(query, responseformat="json", verbosity=verbosity, build=build)
                self.save_to_cache(fname, result)
                return result
            except Exception as err:
                print(f"error: {err} {query}")
                time.sleep(self.retry_delay)
                retry -= 1

    def exec_query_xml(self, query):
        md5 = hashlib.md5(("xml " + query).encode('utf-8')).hexdigest()
        fname = f"{self.cache_path}\\{str(md5)}.zlib"
        result = self.try_load_from_cache(fname)
        if result is not None:
            return result
        retry = self.max_retries
        while retry > 0:
            try:
                result = self.api.get(query, responseformat="xml")
                self.save_to_cache(fname, result)
                return result
            except Exception as err:
                print(f"error: {err}")
                time.sleep(self.retry_delay)
                retry -= 1

    def exec_query_geojson(self, query):
        md5 = hashlib.md5(("geojson " + query).encode('utf-8')).hexdigest()
        fname = f"{self.cache_path}\\{str(md5)}.zlib"
        result = self.try_load_from_cache(fname)
        if result is not None:
            return result
        retry = self.max_retries
        while retry > 0:
            try:
                result = self.api.get(query, responseformat="geojson")
                self.save_to_cache(fname, result)
                return result
            except Exception as err:
                print(f"error: {err}")
                time.sleep(self.retry_delay)
                retry -= 1

    def exec_query_csv_format(self, query, csv_format):
        try:
            md5 = hashlib.md5((csv_format + " " + query).encode('utf-8')).hexdigest()
            fname = f"{self.cache_path}\\{str(md5)}.zlib"
            result = self.try_load_from_cache(fname)
            if result is not None:
                return result
        except Exception as err:
            print(f"error: {err} {query}")

        retry = self.max_retries
        while retry > 0:
            try:
                result = self.api.get(query, responseformat=csv_format)
                self.save_to_cache(fname, result)
                return result
            except Exception as err:
                print(f"error: {err}")
                time.sleep(self.retry_delay)
                retry -= 1

    def exec_query_overpass(self, query):
        md5 = hashlib.md5(("overpass " + query).encode('utf-8')).hexdigest()
        fname = f"{self.cache_path}\\{str(md5)}.zlib"
        result = self.try_load_from_cache(fname)
        if result is not None:
            return result
        retry = self.max_retries
        while retry > 0:
            try:
                result = self.api2.query(query)
                self.save_to_cache(fname, result)
                return result
            except Exception as err:
                print(f"error: {err}")
                time.sleep(self.retry_delay)
                retry -= 1

    def dump_query_result(self, result):
        for way in result.ways:
            print("Name: %s" % way.tags.get("name", "n/a"))
            print(" Highway: %s" % way.tags.get("highway", "n/a"))
            print(" Nodes:")
        for node in way.nodes:
            print(" Lat: %f, Lon: %f" % (node.lat, node.lon))

    def scan_for_polygons(self, json_osm, zoom, data_name):
        #jsonpath_expression = parse('$.[@.type="node"]')
        try:
            #outer_lat_lon = [(match.value['lat'], match.value['lat']) for match in
            #    parse("$.elements[*].members[?(@.role == 'outer')].geometry[*]").find(json_osm)]
            #inner_lat_lon = [(match.value['lat'], match.value['lat']) for match in
            #    parse("$.elements[*].members[?(@.role == 'inner')].geometry[*]").find(json_osm)]
            #outer_lat_lon = [self.deg2xy(match.value['lat'], match.value['lat'], zoom) for match in
            #    parse("$.elements[*].members[?(@.role == 'outer')].geometry[*]").find(json_osm)]
            #inner_lat_lon = [self.deg2xy(match.value['lat'], match.value['lat'], zoom) for match in
            #    parse("$.elements[*].members[?(@.role == 'inner')].geometry[*]").find(json_osm)]

            converted_list = self.load_polygon_from_cache(data_name, zoom)
            if converted_list is not None:
                return converted_list

            p_list = []
            self.polygons_recursive(json_osm, p_list)
            #print(p_list)
            p_list2 = self.merge_polygons(p_list)
            fname = self.get_cache_file_name(data_name)
            self.save_to_cache(fname, p_list2)
            return ([[self.deg2xy(lat_lon['lat'], lat_lon['lon'], zoom) for lat_lon in poly] for poly in p_list2], [])

            return ([
                self.deg2xy(49.674, -14.015517, zoom),
                self.deg2xy(61.061, -14.015517, zoom),
                self.deg2xy(61.061, 2.0919117, zoom),
                self.deg2xy(49.674, 2.0919117, zoom)
            ], [])

            return (outer_lat_lon, inner_lat_lon)
            #for match in parse("$.elements[*].members[?(@.role == 'outer')].geometry[*]").find(json_osm):
                #lats_lons = [ for in match]
                #print(match)
                # parse("$.elements[*].members[?(@.type=='node')]").find(json_osm)[0]
            pass
        except Exception as err :
            print (err)

        return ([], [])

    def scan_for_polygons_v2(self, json_osm, zoom, data_name):
        try:
            #converted_list = self.load_polygon_from_cache_v2(data_name, zoom)
            #if converted_list is not None:
            #    return converted_list
            p_list2 = self.merge_polygons_v2(json_osm)
            fname = self.get_cache_file_name(data_name)
            self.save_to_cache(fname, p_list2)
            return [[self.deg2xy(lat_lon['lat'], lat_lon['lon'], zoom) for lat_lon in poly["geometry"]] for poly in p_list2], []
        except Exception as err:
            print(err)
        return [], []

    def scan_for_polygons_v3(self, json_osm, data_name):
        try:
            p_list2 = self.merge_polygons_v2(json_osm)
            fname = self.get_cache_file_name(data_name)
            self.save_to_cache(fname, p_list2)
            return p_list2
        except Exception as err:
            print(err)
        return []

    def load_polygon_from_cache(self, data_name, zoom):
        fname = self.get_cache_file_name(data_name)
        p_list2 = self.try_load_from_cache(fname)
        if p_list2 is not None:
            converted_list = ([[self.deg2xy(lat_lon['lat'], lat_lon['lon'], zoom) for lat_lon in poly] for poly in p_list2], [])
            return converted_list
        return None

    def load_polygon_from_cache_v2(self, data_name, zoom):
        fname = self.get_cache_file_name(data_name)
        p_list2 = self.try_load_from_cache(fname)
        if p_list2 is not None:
            converted_list = ([[self.deg2xy(lat_lon['lat'], lat_lon['lon'], zoom) for lat_lon in poly["geometry"]]
                               for poly in p_list2], [])
            return converted_list
        return None

    def load_polygon_from_cache_v3(self, data_name, zoom):
        fname = self.get_cache_file_name(data_name)
        p_list2 = self.try_load_from_cache(fname)
        return p_list2

    def get_cache_file_name(self, data_name):
        md5 = hashlib.md5(data_name.encode('utf-8')).hexdigest()
        fname = f"{self.cache_path}\\{str(md5)}.zlib"
        return fname

    def polygons_recursive(self, root, p_list, l=0, upper_nodes=[]):
        upper_nodes_next = []
        upper_nodes_next.extend(upper_nodes)
        upper_nodes_next.append(root)
        debug = False
        if isinstance(root, list):
            for i, el in enumerate(root):
                self.polygons_recursive(el, p_list, l + 1, upper_nodes_next)
                if i % 1000 == 1:
                    print(f'scanning polygons {i}')
        elif isinstance(root, dict):
            if 'elements' in root:
                if debug:
                    print(f'{"--"* l}elements')
                self.polygons_recursive(root['elements'], p_list, l + 1, upper_nodes_next)
            if 'bounds' in root:
                if debug:
                    print(f'{"--"* l}bounds')
            if 'members' in root:
                if debug:
                    print(f'{"--"* l}members')
                self.polygons_recursive(root['members'], p_list, l + 1, upper_nodes_next)
            if 'type' in root:
                if 'role' in root:
                    if not root['type'] == 'way':
                        if debug:
                            print(f'{"--" * l}type={root["type"]} role={root["role"]}')
                if root['type'] == 'relation':
                    pass #print(f'.')
                elif root['type'] == 'node':
                    pass #print(f'.')
                elif root['type'] == 'way':
                    if 'geometry' in root:
                        p_list.append(root['geometry'])
                        if debug:
                            s = ""
                            for el_up in upper_nodes:
                                if 'tags' in el_up and "name:en" in el_up["tags"]:
                                    s = s + el_up["tags"]["name:en"] + '-'
                            print(f'{s}-geometry')
                        #print(f'{"--"* l}geometry')
                else:
                    pass
            pass
        elif isinstance(root, tuple):
            pass
        else:
            pass

    def merge_polygons_v2(self, p_lists):
        debug = False
        print(f"dedupping {len(p_lists)}")
        p_lists1 = []
        hashes = {}
        for p_list in p_lists:
            if "geometry" not in p_list or "id" not in p_list or "type" not in p_list or p_list["type"] != "way":
                continue
            if len(p_list["geometry"]) == 0:
                continue
            hash1 = p_list["id"]
            if hash1 in hashes:
                continue
            hashes[hash1] = None
            p1 = p_list["geometry"][0]
            p2 = p_list["geometry"][-1]
            if not ((p1['lat'] < p2['lat']) or (p1['lat'] == p2['lat'] and p1['lon'] < p2['lon'])):
                p_list["geometry"] = p_list["geometry"][::-1]
                p_list["nodes"] = p_list["nodes"][::-1]
            p_lists1.append(p_list)

        print(f"dedupped {len(p_lists1)}")

        new_p_lists = self.merge_polygons_core_v2(p_lists1)

        return new_p_lists

    def merge_polygons(self, p_lists):
        debug = False
        if debug:
            for p_list in p_lists:
                print(f"{p_list[0]}-{p_list[-1]}-{len(p_list)}")

        new_p_lists = []
        last = None
        p_lists1 = []
        hashes = {}
        for p_list in p_lists:
            if len(p_list) == 0:
                continue
            if len(p_lists1) % 1000 == 1 and len(p_lists1) > 3000:
                print(f'dedup {len(p_lists1)}')
            hash1 = self.create_hash(p_list)
            hash2 = self.create_hash(p_list[::-1])
            if hash1 in hashes or hash2 in hashes:
                continue
            #if self.start_less_end(p_list[0], p_list[-1]): ## t o d o expand method
            p1 = p_list[0]
            p2 = p_list[-1]
            if (p1['lat'] < p2['lat']) or (p1['lat'] == p2['lat'] and p1['lon'] < p2['lon']):
                p_lists1.append(p_list)
            else:
                p_lists1.append(p_list[::-1])
            hashes[hash1] = None
            hashes[hash2] = None
        print(f"dedupped {len(p_lists)}")

        new_p_lists = self.merge_polygons_core(new_p_lists, p_lists1)

        if debug:
            for p_list in new_p_lists:
                print(f"{p_list[0]}-{p_list[-1]}-{len(p_list)}")
        return new_p_lists

    def merge_polygons_core(self, new_p_lists, p_lists1):
        new_p_lists = p_lists1

        debug = False
        merged = True
        n_merges = 0
        new_p_lists_finally_done = []
        while merged:
            merged = False
            n_merges += 1
            print(f'{n_merges} merge ({len(new_p_lists)})')
            merge_dict = {}
            for i, p_list1 in enumerate(new_p_lists):
                p1 = (p_list1[0]['lat'], p_list1[0]['lon'])
                p2 = (p_list1[-1]['lat'], p_list1[-1]['lon'])
                p1_s = f'{p1[0]}|{p1[1]}'
                p2_s = f'{p2[0]}|{p2[1]}'
                if p1_s == p2_s:
                    continue
                if p1_s not in merge_dict:
                    merge_dict[p1_s] = [i]
                else:
                    merge_dict[p1_s].append(i)
                if p2_s not in merge_dict:
                    merge_dict[p2_s] = [i]
                else:
                    merge_dict[p2_s].append(i)

            indexes_taken = []
            new_p_lists2 = []
            for k in merge_dict:
                pair = merge_dict[k]
                if len(pair) == 1:
                    continue
                elif len(pair) >= 2:
                    if pair[0] in indexes_taken or pair[1] in indexes_taken:
                        continue
                    if pair[0] == pair[1]:
                        continue
                    indexes_taken.append(pair[0])
                    indexes_taken.append(pair[1])
                    p_list1 = new_p_lists[pair[0]]
                    p_list2 = new_p_lists[pair[1]]
                    p11 = p_list1[0]
                    p12 = p_list1[-1]
                    p21 = p_list2[0]
                    p22 = p_list2[-1]
                    if p22['lat'] == p11['lat'] and p22['lon'] == p11['lon']:
                        if debug:
                            print(self.get_first_last(p_list1))
                            print(self.get_first_last(p_list2))
                        p_list2.extend(p_list1[1:])
                        new_p_lists2.append(p_list2)
                        merged = True
                        if debug:
                            print(self.get_first_last(p_list2))
                    elif p21['lat'] == p11['lat'] and p21['lon'] == p11['lon']:
                        if debug:
                            print(self.get_first_last(p_list1))
                            print(self.get_first_last(p_list2))
                        p_list1 = p_list1[::-1]
                        p_list1.extend(p_list2[1:])
                        new_p_lists2.append(p_list1)
                        merged = True
                        if debug:
                            print(self.get_first_last(p_list1))
                    elif p21['lat'] == p12['lat'] and p21['lon'] == p12['lon']:
                        if debug:
                            print(self.get_first_last(p_list1))
                            print(self.get_first_last(p_list2))
                        p_list1.extend(p_list2[1:])
                        new_p_lists2.append(p_list1)
                        merged = True
                        if debug:
                            print(self.get_first_last(p_list1))
                    elif p22['lat'] == p12['lat'] and p22['lon'] == p12['lon']:
                        if debug:
                            print(self.get_first_last(p_list1))
                            print(self.get_first_last(p_list2))
                        p_list1 = p_list1[::-1]
                        p_list2.extend(p_list1[1:])
                        new_p_lists2.append(p_list2)
                        merged = True
                        if debug:
                            print(self.get_first_last(p_list2))


            for i in range(len(new_p_lists)):
                if i not in indexes_taken:
                    new_p_lists2.append(new_p_lists[i])

            new_p_lists3 = []
            for i, p_list in enumerate(new_p_lists2):
                p1 = p_list[0]
                p2 = p_list[-1]
                if p2['lat'] == p1['lat'] and p2['lon'] == p1['lon']:
                    new_p_lists_finally_done.append(p_list)
                else:
                    new_p_lists3.append(p_list)

            del new_p_lists
            del new_p_lists2
            new_p_lists = new_p_lists3

        if len(new_p_lists) > 0:
            new_p_lists_finally_done.extend(new_p_lists)

        print(f'{n_merges} done')
        return new_p_lists_finally_done

    def merge_polygons_core_v2(self, p_lists1):
        print(f'{len(p_lists1)} ways')
        new_p_lists_finally_done = []
        new_p_lists = []
        for p_list in p_lists1:
            p_list["is_maritime"] = 'tags' in p_list and "maritime" in p_list['tags'] and p_list['tags']["maritime"] == "yes"

        # detect enclosed polygons (start == end)
        for p_list in p_lists1:
            try:
                if p_list["nodes"][0] == p_list["nodes"][-1]:
                    if not p_list["is_maritime"]:
                        new_p_lists_finally_done.append(p_list)
                else:
                    if not p_list["is_maritime"]:
                        new_p_lists.append(p_list)
            except Exception as err:
                print(err)


        print(f'{len(new_p_lists)} ways for merge')
        print(f'{len(new_p_lists_finally_done)} ways completed')

        debug = False
        merged = True
        n_merges = 0
        while merged:
            merged = False
            n_merges += 1
            print(f'{n_merges} merge ({len(new_p_lists)})')
            merge_dict = {}
            for i, p_list1 in enumerate(new_p_lists):
                nodes = p_list1["nodes"]
                p1 = nodes[0]
                p2 = nodes[-1]
                if p1 == p2:
                    continue
                if p1 not in merge_dict:
                    merge_dict[p1] = [i]
                else:
                    merge_dict[p1].append(i)
                if p2 not in merge_dict:
                    merge_dict[p2] = [i]
                else:
                    merge_dict[p2].append(i)

            indexes_taken = {}
            new_p_lists2 = []
            for k in merge_dict:
                try:
                    pair = merge_dict[k]
                    if len(pair) == 1:
                        continue
                    elif len(pair) >= 2:
                        if pair[0] in indexes_taken or pair[1] in indexes_taken:
                            continue
                        if pair[0] == pair[1]:
                            continue
                        if len(pair) == 2:
                            p_list1 = new_p_lists[pair[0]]
                            p_list2 = new_p_lists[pair[1]]
                            if p_list1["is_maritime"] and p_list1["is_maritime"]:
                                continue
                        else:
                            continue
                            pair = self.fix_pair(pair, new_p_lists)
                            if len(pair) != 2:
                                continue
                            p_list1 = new_p_lists[pair[0]]
                            p_list2 = new_p_lists[pair[1]]

                        indexes_taken[pair[0]] = None
                        indexes_taken[pair[1]] = None
                        merged = self.connect_two_ways(merged, new_p_lists2, p_list1, p_list2)

                except Exception as err:
                    print(err)

            for i in range(len(new_p_lists)):
                if i not in indexes_taken:
                    new_p_lists2.append(new_p_lists[i])

            new_p_lists3 = []
            for i, p_list in enumerate(new_p_lists2):
                if p_list["nodes"][0] == p_list["nodes"][-1]:
                    if not p_list["is_maritime"]:
                        new_p_lists_finally_done.append(p_list)
                else:
                    new_p_lists3.append(p_list)

            del new_p_lists
            del new_p_lists2
            new_p_lists = new_p_lists3

        new_p_lists = self.connect_disconnected_polygons(new_p_lists)

        if len(new_p_lists) > 0:
            new_p_lists_finally_done.extend(new_p_lists)

        print(f'{n_merges} done')
        return new_p_lists_finally_done

    def connect_two_ways(self, merged, new_p_lists2, p_list1, p_list2):
        nodes1 = p_list1["nodes"]
        nodes2 = p_list2["nodes"]
        p11 = nodes1[0]
        p12 = nodes1[-1]
        p21 = nodes2[0]
        p22 = nodes2[-1]
        if p22 == p11:
            p_list2["nodes"].extend(p_list1["nodes"][1:])
            p_list2["geometry"].extend(p_list1["geometry"][1:])
            new_p_lists2.append(p_list2)
            self.adjust_polygon_type(p_list2, p_list1)
            merged = True
        elif p21 == p11:
            p_list1["nodes"] = p_list1["nodes"][::-1]
            p_list1["geometry"] = p_list1["geometry"][::-1]
            p_list1["nodes"].extend(p_list2["nodes"][1:])
            p_list1["geometry"].extend(p_list2["geometry"][1:])
            new_p_lists2.append(p_list1)
            self.adjust_polygon_type(p_list1, p_list2)
            merged = True
        elif p21 == p12:
            p_list1["nodes"].extend(p_list2["nodes"][1:])
            p_list1["geometry"].extend(p_list2["geometry"][1:])
            new_p_lists2.append(p_list1)
            self.adjust_polygon_type(p_list1, p_list2)
            merged = True
        elif p22 == p12:
            p_list1["nodes"] = p_list1["nodes"][::-1]
            p_list2["nodes"].extend(p_list1["nodes"][1:])
            p_list1["geometry"] = p_list1["geometry"][::-1]
            p_list2["geometry"].extend(p_list1["geometry"][1:])
            new_p_lists2.append(p_list2)
            self.adjust_polygon_type(p_list2, p_list1)
            merged = True
        return merged

    def connect_two_ways2(self, new_p_lists2, i, j, end1, end2):
        p_list1 = new_p_lists2[i]
        p_list2 = new_p_lists2[j]

        p1 = p_list1["geometry"][end1]
        p2 = p_list2["geometry"][end2]

        l = [(f"({len(p['geometry'])}) {p['nodes'][0]}: {p['geometry'][0]['lat']},{p['geometry'][0]['lon']}-"
              f"{p['nodes'][-1]} {p['geometry'][-1]['lat']},{p['geometry'][-1]['lon']}") for p in new_p_lists2]
        for s in l:
            print(s)

        merge_limit = 180 #0.3
        if self.get_distance(p1, p2) > merge_limit:
            return False

        self.print_connection_area(p1, p2)

        if i == j:
            p_list1["nodes"].append(p_list1["nodes"][0])
            p_list1["geometry"].append(p_list1["geometry"][0])
        elif end2 == -1 and end1 == 0: #p22 == p11:
            p_list2["nodes"].extend(p_list1["nodes"])
            p_list2["geometry"].extend(p_list1["geometry"])
            self.adjust_polygon_type(p_list2, p_list1)
            del new_p_lists2[i]
        elif end2 == 0 and end1 == 0: #p21 == p11:
            p_list1["nodes"] = p_list1["nodes"][::-1]
            p_list1["geometry"] = p_list1["geometry"][::-1]
            p_list1["nodes"].extend(p_list2["nodes"])
            p_list1["geometry"].extend(p_list2["geometry"])
            self.adjust_polygon_type(p_list1, p_list2)
            del new_p_lists2[j]
        elif end2 == 0 and end1 == -1: #p21 == p12:
            p_list1["nodes"].extend(p_list2["nodes"])
            p_list1["geometry"].extend(p_list2["geometry"])
            self.adjust_polygon_type(p_list1, p_list2)
            del new_p_lists2[j]
        elif end2 == -1 and end1 == -1: #p22 == p12:
            p_list1["nodes"] = p_list1["nodes"][::-1]
            p_list2["nodes"].extend(p_list1["nodes"])
            p_list1["geometry"] = p_list1["geometry"][::-1]
            p_list2["geometry"].extend(p_list1["geometry"])
            self.adjust_polygon_type(p_list2, p_list1)
            del new_p_lists2[i]
        merged = True
        return merged


    def print_connection_area(self, p1, p2):
        gap = 0.2
        min_lat = min(p1['lat'], p2['lat'])
        max_lat = max(p1['lat'], p2['lat'])
        min_lon = min(p1['lon'], p2['lon'])
        max_lon = max(p1['lon'], p2['lon'])
        bbox_str = f'{min_lat - gap},{min_lon - gap},{max_lat + gap},{max_lon + gap}'
        query = f'''
            [out:json][timeout:900];  
            area["ISO3166-1"="{self.current_country_code}"]({bbox_str})->.country;
            rel["ISO3166-1"="{self.current_country_code}"]["type"="boundary"]["admin_level"="2"]({bbox_str});
            (
                way(r)["maritime" != "yes"]({bbox_str});
                way(area.country)["natural"="coastline"]({bbox_str});
            );
            out geom;                                            
        '''
        print(query)

    def connect_disconnected_polygons(self, new_p_lists):
        merged = True
        while len(new_p_lists) > 1 and merged:
            pairs = []
            merged = False
            intersect_found = False
            for i, p_list1 in enumerate(new_p_lists):
                geometry1 = p_list1["geometry"]
                nodes1 = p_list1["nodes"]
                if  geometry1[0]['lat'] == geometry1[-1]['lat'] and \
                    geometry1[0]['lon'] == geometry1[-1]['lon']:
                    continue
                pairs.append([i, i, 0, -1, self.get_distance(geometry1[0], geometry1[-1])])
                for j, p_list2 in enumerate(new_p_lists):
                    if j <= i:
                        continue
                    geometry2 = p_list2["geometry"]
                    nodes2 = p_list2["nodes"]
                    if geometry2[0]['lat'] == geometry2[-1]['lat'] and \
                       geometry2[0]['lon'] == geometry2[-1]['lon']:
                        continue
                        
                    if self.do_intersect(nodes1, nodes2):
                        print('intersect found')
                        intersect_found = True
                        for ii in [-1, 0]:
                            for jj in [-1, 0]:
                                g1 = geometry1[ii]
                                g2 = geometry2[jj]
                                distance = self.get_distance(g1, g2)
                                pairs.append([i, j, ii, jj, distance])
                    if intersect_found:
                        break
                if intersect_found:
                    break

            if not intersect_found:
                for i, p_list1 in enumerate(new_p_lists):
                    geometry1 = p_list1["geometry"]
                    if  geometry1[0]['lat'] == geometry1[-1]['lat'] and \
                        geometry1[0]['lon'] == geometry1[-1]['lon']:
                        continue
                    pairs.append([i, i, 0, -1, self.get_distance(geometry1[0], geometry1[-1])])
                    for j, p_list2 in enumerate(new_p_lists):
                        if j <= i:
                            continue
                        geometry2 = p_list2["geometry"]
                        if geometry2[0]['lat'] == geometry2[-1]['lat'] and \
                           geometry2[0]['lon'] == geometry2[-1]['lon']:
                            continue
                        for ii in [-1, 0]:
                            for jj in [-1, 0]:
                                g1 = geometry1[ii]
                                g2 = geometry2[jj]
                                distance = self.get_distance(g1, g2)
                                pairs.append([i, j, ii, jj, distance])

            if len(pairs) > 0:
                pairs = sorted(pairs, key=lambda pair: pair[4])
                merged = self.connect_two_ways2(new_p_lists, pairs[0][0], pairs[0][1], pairs[0][2], pairs[0][3])

        return new_p_lists

    def get_distance(self, g1, g2):
        return math.sqrt((g1['lat'] - g2['lat']) * (g1['lat'] - g2['lat']) + \
                         (g1['lon'] - g2['lon']) * (g1['lon'] - g2['lon']))

    def create_hash(self, p_list):
        d = json.dumps(p_list)
        md5 = hashlib.md5(d.encode('utf-8')).hexdigest()
        return md5

    def deg2num(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (xtile, ytile)

    def deg2xy(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        x = (lon_deg + 180.0) / 360.0 * n
        y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
        return (x, y)

    def num2deg(self, xtile, ytile, zoom):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)

    def latlon_to_texture_xy(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        x = (lon_deg + 180.0) / 360.0 * n
        y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
        return (x, y)

    def get_tile_bbox(self, xtile, ytile):
        t1 = self.num2deg(xtile + 0, ytile + 1, self.scan_zoom)
        t2 = self.num2deg(xtile + 1, ytile + 0, self.scan_zoom)
        bbox = [t1[0], t1[1], t2[0], t2[1]]
        return bbox

    def start_less_end(self, p1, p2):
        if p1['lat'] < p2['lat']:
            return True
        if p1['lat'] == p2['lat'] and p1['lon'] < p2['lon']:
            return True
        return False

    def get_first_last(self, l):
        return (l[0], l[-1])

    def fix_pair(self, pair, new_p_lists):
        pair = [i for i in pair if not new_p_lists[i]["is_maritime"]]
        if len(pair) == 2:
            return pair
        else:
            print("strange pair")
            if len(pair) > 2:
                return pair[:2]
            else:
                return pair

    def adjust_polygon_type(self, p_list1, p_list2):
        if p_list1["is_maritime"] and not p_list2["is_maritime"]:
            p_list1["is_maritime"] = False

    def do_intersect(self, nodes1, nodes2):
        result = set(nodes1).intersection(nodes2)
        for n in result:
            print(f'{len(nodes1)}: {nodes1.index(n)}')
            print(f'{len(nodes2)}: {nodes2.index(n)}')
        return len(result) > 0

    def execute_overpass_query_ex(self, query):
        start_time = time.time()
        result = self.exec_query_json(query, "", False)
        result = result if result is not None else {}
        end_time = time.time()
        time_lapsed = end_time - start_time
        result_pickled = pickle.dumps(result)
        result_size = len(result_pickled)
        del result_pickled
        return result, result_size, time_lapsed

    def create_relations_info(self, osm_json):
        relations = []
        self.collect_all_relations_with_geometry(osm_json, relations)
        relations_info = [relation_info(relation) for relation in relations]
        for ri in relations_info:
            ri.merge_polygons_inside_relation()
        return relations_info

    def collect_all_relations_with_geometry(self, osm_json, relations):
        for element in osm_json.get('elements', []):
            self.collect_all_relations_with_geometry(element, relations)
        if osm_json.get("type", "") == "relation":
            relations.append(osm_json)
        #for member in osm_json.get('members', []):
        #    self.collect_all_relations_with_geometry(member, relations)
        #if osm_json.get("way", "") == "relation":
        #    print(1)
        #pass

    def convert_polygon_tuplexy_to_texture_coords(self, polygons_geo_lat_lon, zoom):
        return [[self.deg2xy(lat_lon['lat'], lat_lon['lon'], zoom) for lat_lon in poly["geometry"]]
                for poly in polygons_geo_lat_lon], []

    def convert_polygon_lat_lon_to_texture_coords(self, polygons_geo_lat_lon, zoom):
        return [[self.deg2xy(lat_lon['lat'], lat_lon['lon'], zoom) for lat_lon in poly["geometry"]]
                for poly in polygons_geo_lat_lon], []
        #return [[self.latlon_to_texture_xy(lat_lon['lat'], lat_lon['lon'], zoom) for lat_lon in poly["geometry"]]
        #        for poly in polygons_geo_lat_lon], []

    def init_tile_bboxes(self):
        if len(self.tile_bboxes) > 0:
            return
        for ytile in range(self.scan_n):
            row_bboxes = []
            for xtile in range(self.scan_n):
                bbox = self.get_tile_bbox(xtile, ytile)
                row_bboxes.append(map_box_info(bbox))
            self.tile_bboxes.append(row_bboxes)

    def collect_polygons(self, geometry, polygons):
        polygons["outer"] = []
        polygons["inner"] = []
        for _, row in geometry.iterrows():
            if isinstance(row["geometry"], MultiPolygon):
                for polygon in row["geometry"].geoms:
                    polygons["outer"].append(
                        #[self.deg2xy(point[1], point[0], zoom) for point in polygon.exterior.coords]
                        [(point[1], point[0]) for point in polygon.exterior.coords]
                    )

                    for interior in polygon.interiors:
                        polygons["inner"].append(
                            #[self.deg2xy(point[1], point[0], zoom) for point in interior.coords]
                            [(point[1], point[0]) for point in interior.coords]
                        )
            elif isinstance(row["geometry"], Polygon):
                polygon = row["geometry"]
                polygons["outer"].append(
                    #[self.deg2xy(point[1], point[0], zoom) for point in polygon.exterior.coords]
                    [(point[1], point[0]) for point in polygon.exterior.coords]
                )
                for interior in polygon.interiors:
                    polygons["inner"].append(
                        #[self.deg2xy(point[1], point[0], zoom) for point in interior.coords]
                        [(point[1], point[0]) for point in interior.coords]
                    )
            else:
                print(2)

