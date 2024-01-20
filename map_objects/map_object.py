import hashlib
import time
import geopandas as gpd

from map_objects.ColorHelper import ColorHelper
from objects3D.overpass_countries import overpass_countries
from objects3D.polygon_fill_info import polygon_fill_info


class map_object:
    def __init__(self):
        self.label = None
        self.bbox = None
        self.polygons = None
        self.fi = None
        self.fi_inner = None

    def load_geometry(self, ovp: overpass_countries):
        pass

    def load_label(self, ovp: overpass_countries):
        pass

    def init_bbox(self):
        pass

    def init_fill_info(self):
        pass

    def draw_on_globe_texture(self, ovp, draw):
        pass

    def get_lat_lon_polygons(self):
        return self.polygons

    def get_fi(self):
        return self.fi

    def draw_outer_polygons_on_texture(self, ovp, draw):
        #outer_polygons = ovp.convert_polygons_from_lat_lon(self.polygons["outer"])

        outer_polygons = [[ovp.deg_2_texture_xy(point[0], point[1], draw._image.width, draw._image.height)
                 for point in poly] for poly in self.polygons["outer"]]

        for xys in outer_polygons:
            self.draw_polygon_core(draw, xys, self.fi)

    def draw_inner_polygons_on_texture(self, ovp, draw):
        outer_polygons = [[ovp.deg_2_texture_xy(point[0], point[1], draw._image.width, draw._image.height)
                 for point in poly] for poly in self.polygons["inner"]]

        for xys in outer_polygons:
            self.draw_polygon_core(draw, xys, self.fi_inner)

    def draw_polygon_core(self, draw, xys, fi: polygon_fill_info):
        if fi is None:  # filled polygon without border
            draw.polygon(xy=xys, fill=fi.fill_color)
        elif fi is not None:  # filled polygon with border
            draw.polygon(xy=xys, fill=fi.fill_color, outline=fi.border_color)
        else:
            pass

    def init_fill_info(self):
        self.fi = polygon_fill_info(fill_color=ColorHelper.defaultland_color_argb(), border_color=None)
        self.fi_inner = polygon_fill_info(fill_color=ColorHelper.water_color_argb(), border_color=None)

class mo_all_world(map_object):
    def __init__(self):
        super().__init__()

    def load_geometry(self, ovp):
        polygons = [[-180, -90], [-180, 90], [180, 90], [180, -90]]
        self.polygons = { "outer": [[(p[1], p[0]) for p in polygons]], "inner": [] }

    def draw_on_globe_texture(self, ovp, draw):
        self.draw_outer_polygons_on_texture(ovp, draw)

    def init_fill_info(self):
        self.fi = polygon_fill_info(fill_color=ColorHelper.water_color_argb(), border_color=None)

class mo_global_land(map_object):
    def __init__(self):
        super().__init__()

    def load_geometry(self, ovp):
        ovp.get_global_land_polygons()
        self.polygons = ovp.global_land_polygons_xy

    def init_fill_info(self):
        self.fi = polygon_fill_info(fill_color=ColorHelper.defaultland_color_argb(), border_color=None)
        self.fi_inner = polygon_fill_info(fill_color=ColorHelper.water_color_argb(), border_color=None)

    def draw_on_globe_texture(self, ovp, draw):
        self.draw_outer_polygons_on_texture(ovp, draw)
        self.draw_inner_polygons_on_texture(ovp, draw)

class mo_continent(map_object):
    def __init__(self, continent_name_en):
        super().__init__()
        self.continent_name_en = continent_name_en

    def init_fill_info(self):
        self.fi = polygon_fill_info(
            fill_color=ColorHelper.get_continent_color(self.continent_name_en), border_color=None)
        self.fi_inner = polygon_fill_info(fill_color=ColorHelper.water_color_argb(), border_color=None)

    def load_geometry(self, ovp):
        if ovp.global_continent_polygons_xy is None:
            ovp.get_continents_borders()
        self.polygons = ovp.global_continent_polygons_xy[self.continent_name_en]

    def draw_on_globe_texture(self, ovp, draw):
        self.draw_outer_polygons_on_texture(ovp, draw)
        self.draw_inner_polygons_on_texture(ovp, draw)

    def load_label(self, ovp: overpass_countries, label_size):
        ovp.get_ocean_labels(label_size)

    def draw_label(self, ovp, draw):
        pass


class mo_ocean(map_object):
    def __init__(self, country):
        super().__init__()

    def load_label(self, ovp: overpass_countries, label_size):
        ovp.get_ocean_labels(label_size)

    def draw_label(self, ovp, draw):
        pass


class mo_country(map_object):
    def __init__(self, country):
        super().__init__()
