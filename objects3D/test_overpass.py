import sys
import time
from data.languages import languages
from objects3D.overpass_base import overpass_base
from objects3D.overpass_countries import overpass_countries


def test_overpass1():
    ovp = overpass_base()
    query = """
            way(50.746,7.154,50.748,7.157) ["highway"];
            (._;>;);
            out body;
        """
    query = """
        [out:xml];
        relation["boundary"="continent"]["name:ru"="Антарктида"];
        out geom;
    """
    for country in ["Гондурас", "Германия", "Польша", "Россия"]:
        for i in range(3):
            start_time = time.time()
            query = f'''relation["boundary"="administrative"]["admin_level"="2"]["name:ru"="{country}"];
                out geom;    
            '''
            result = ovp.exec_query_json(query)
            end_time = time.time()
            time_lapsed = end_time - start_time
            print(f'json {country} {time_lapsed} {sys.getsizeof(result)}')

    for country in ["Гондурас", "Германия", "Польша", "Россия"]:
        for i in range(3):
            start_time = time.time()
            query = f'''relation["boundary"="administrative"]["admin_level"="2"]["name:ru"="{country}"];
                out geom;    
            '''
            result = ovp.exec_query_xml(query)
            end_time = time.time()
            time_lapsed = end_time - start_time
            print(f'xml {country} {time_lapsed} {sys.getsizeof(result)}')

    """
    for country in ["Гондурас", "Германия", "Польша", "Россия"]:
        for i in range(3):
            start_time = time.time()
            query = f'''relation["boundary"="administrative"]["admin_level"="2"]["name:ru"="{country}"];
                out geom;    
            '''
            result = ovp.exec_query_geojson(query)
            end_time = time.time()
            time_lapsed = end_time - start_time
            print(f'{country} {time_lapsed} {len(result) if result is not None else 0}')
    """

    for country in ["Гондурас", "Германия", "Польша", "Россия"]:
        for i in range(3):
            start_time = time.time()
            query = f'''relation["boundary"="administrative"]["admin_level"="2"]["name:ru"="{country}"];
                out geom;    
            '''
            result = ovp.exec_query_json(query)
            end_time = time.time()
            time_lapsed = end_time - start_time
            print(f'json {country} {time_lapsed} {sys.getsizeof(result)}')


    for country in ["Гондурас", "Германия", "Польша", "Россия"]:
        for i in range(3):
            start_time = time.time()
            csv_format = 'csv(name,"ISO3166-1",' + ",".join([f'"name:{lang[0]}"' for lang in languages]) + ')'
            query = 'relation["admin_level" = "2"][boundary = administrative];out;'
            #     "ISO3166-1": "HN",
            #     "ISO3166-1:alpha2": "HN",
            #     "ISO3166-1:alpha3": "HN
            result = ovp.exec_query_csv_format(query, csv_format)
            end_time = time.time()
            time_lapsed = end_time - start_time
            print(f'csv {country} {time_lapsed} {sys.getsizeof(result)}')



    #ovp.dump_query_result(result)
    pass

def test_overpass2():
    ovp = overpass_countries()
    ovp.load()
    ovp.get_list_of_countries()
    ovp.load_countries_polygons()
    print(ovp.real_countries)
    pass
