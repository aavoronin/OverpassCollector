import hashlib
import math
import time
import geopandas as gpd

from map_objects.ColorHelper import ColorHelper
from map_objects.FontHelper import FontHelper
from map_objects.TextPolygonsHelper import TextPolygonsHelper
from objects3D.overpass_countries import overpass_countries
from objects3D.polygon_fill_info import polygon_fill_info

class map_object:

    def __init__(self):
        self.label = None
        self.bbox = None
        self.polygons = None
        self.fi = None
        self.fi_inner = None
        self.label_info = None
        self.object_type = "unknown"
        self.fi_letter_color = polygon_fill_info(fill_color=ColorHelper.unknown_color(), border_color=None)

    def get_label_font(self, ovp):
        font_size = 256
        font2 = FontHelper.get_label_font(font_size, ovp.lang)
        return font2

    def load_geometry(self, ovp: overpass_countries):
        pass

    def load_labels(self, ovp: overpass_countries, label_size):
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

    def draw_label_on_globe_texture(self, ovp, im_mask_img_draw, im_stamp_img_draw):
        if self.label_info is None:
            return
        font = self.get_label_font(ovp)
        TextPolygonsHelper.draw_label_polygons(ovp, self.label_info, font,
                                               self.fi_letter_color, im_mask_img_draw, im_stamp_img_draw)

class mo_all_world(map_object):
    def __init__(self):
        super().__init__()
        self.object_type = "all_world"


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
        self.object_type = "all_land"

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
        self.object_type = "continent"
        self.fi_letter_color = polygon_fill_info(fill_color=ColorHelper.continent_label_color_argb(), border_color=None)

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

    def load_labels(self, ovp: overpass_countries, label_size):
        if len(ovp.continent_info) == 0:
            ovp.get_continent_labels(label_size)
        for li in ovp.continent_info:
            if li["name_en"] == self.continent_name_en:
                self.label_info = li
                break

class mo_ocean(map_object):
    def __init__(self, ocean_name_en):
        super().__init__()
        self.ocean_name_en = ocean_name_en
        self.object_type = "ocean"
        self.fi_letter_color = polygon_fill_info(fill_color=ColorHelper.ocean_label_color_argb(), border_color=None)

    def load_labels(self, ovp: overpass_countries, label_size):
        if len(ovp.ocean_info) == 0:
            ovp.get_ocean_labels(label_size)
        for li in ovp.ocean_info:
            if li["name_en"] == self.ocean_name_en:
                self.label_info = li
                break


class mo_country(map_object):
    def __init__(self, country):
        super().__init__()
        self.object_type = "country"
