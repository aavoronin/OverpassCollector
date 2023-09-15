import datetime
import hashlib
import pickle
import time

from objects3D.overpass_base import overpass_base


class country_info(overpass_base):
    def __init__(self, country_osm_data):
        super().__init__()
        self.country_osm_data = country_osm_data
        self.outer_ways = []
        self.inner_ways = []
        self.subarea_relations = []
        self.subarea_nodes = []
        self.collections = []
        self.land_areas = []
        self.node_admin_center = []
        self.relation_admin_center = []
        self.label = []
        self.outer_relations = []
        self.type = None
        self.id = None
        self.bounds = None
        self.tags = {}
        self.non_maritime_border = []
        self.coastline = []
        self.water_200000 = []

    def parse(self, bboxes):
        d = self.country_osm_data

        self.type = d.get("type")
        self.id = d.get("id")
        self.bounds = d.get("bounds")
        self.tags = d.get("tags", {})
        self.country_code = self.tags.get("ISO3166-1")

        for member in d.get("members", {}):
            member_type = member.get("type", "")
            member_role = member.get("role", "")

            if member_type == "way" and member_role == "outer":
                self.outer_ways.append(member)
            elif member_type == "way" and member_role == "inner":
                self.inner_ways.append(member)
            elif member_type == "relation" and member_role == "subarea":
                self.subarea_relations.append(member)
            elif member_type == "relation" and member_role == "outer":
                self.outer_relations.append(member)
            elif member_type == "nodes" and member_role == "subarea":
                self.subarea_nodes.append(member)
            elif member_type == "relation" and member_role == "collection":
                self.collections.append(member)
            elif member_type == "relation" and member_role == "land_area":
                self.land_areas.append(member)
            elif member_type == "node" and member_role == 'admin_centre':
                self.node_admin_center.append(member)
            elif member_type == "relation" and member_role == 'admin_centre':
                self.relation_admin_center.append(member)
            elif member_type == "node" and member_role == 'label':
                self.label.append(member)
            else:
                print(f'unknown_member {member_type} {member_role}')

        print(f"{self.tags.get('ISO3166-1')}, {self.tags.get('name:en')} id={self.id} outer={len(self.outer_ways)} "
              f"inner={len(self.inner_ways)} suba={len(self.subarea_relations)} landa={len(self.land_areas)} "
              f"col={len(self.collections)}")

    def load_country_borders(self):
        relation_id = self.id
        start_time = time.time()

        query = f"""
            [out:json][timeout:900];
            rel({relation_id});
            (
                way(r)["maritime" != "yes"];
            );
            out geom;
        """

        try:
            result = self.exec_query_json(query, "", False)
            self.non_maritime_border = result if result is not None else {}
            end_time = time.time()
            time_lapsed = end_time - start_time
            result_pickled = pickle.dumps(result)
            self.non_maritime_border_data_size = result_pickled
            print(
                f'{self.country_code} non maritime: {len(result_pickled)} {datetime.datetime.now()} ({time_lapsed} secs)')
            del result_pickled
        except Exception as e:
            print(e)

        start_time = time.time()
        query = f"""
            [out:json][timeout:900];
            rel({relation_id});map_to_area->.country;
            rel({relation_id});
            (
                way(area.country)["natural"="coastline"];
            );
            out geom;
        """

        try:
            result = self.exec_query_json(query, "", False)
            self.coastline = result if result is not None else {}
            end_time = time.time()
            time_lapsed = end_time - start_time
            result_pickled = pickle.dumps(result)
            self.coastline_data_size = result_pickled
            print(
                f'{self.country_code} coastline: {len(result_pickled)} {datetime.datetime.now()} ({time_lapsed} secs)')
            del result_pickled
        except Exception as e:
            print(e)

    def get_water_osm(self):
        if self.water_200000 is None:
            return []
        if "elements" not in self.water_200000:
            return []
        return self.water_200000['elements']
        result = []
        for element in self.water_200000['elements']:
            if "members" not in element:
                continue
            for member in element["members"]:
                if "geometry" in member and "role" in member and member["role"] == "outer":
                    result.append(member)
        return result

    def load_country_lake_data(self):
        query = f'''   
            [out:json][timeout:900];  
            rel({self.id});map_to_area->.country;
            rel({self.id});
            (
                rel(area.country)["water"="lake"](if: length() > 200000);
			    rel(area.country)["water"="reservoir"](if: length() > 200000);
            );
            out geom;            
        '''
        polygons = self.load_overpass_results_and_create_polygons(
            query, f"{self.country_code} water 200000:")
        self.water_200000_polygons = polygons

    def load_overpass_results_and_create_polygons(self, query, log_data):

        try:
            qp = f'{query} /*polygons*/'
            md5 = hashlib.md5(qp.encode('utf-8')).hexdigest()
            fname = f"{self.cache_path}\\{str(md5)}.zlib"
            polygons = self.try_load_from_cache(fname)
            if polygons is not None:
                return polygons
        except Exception as err:
            print(f"error: {err} {query}")

        try:
            result, result_size, time_lapsed = self.execute_overpass_query_ex(query)
            print(f'{log_data} {result_size} {datetime.datetime.now()} ({time_lapsed} secs)')
            relations = self.create_relations_info(result)
            polygons = [polygon for rel in relations for polygon in rel.outer_polygons]
            self.save_to_cache(fname, polygons)
            return polygons
        except Exception as err:
            print(f"error: {err} {query}")


