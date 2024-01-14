from geo.osm_tiles import osm_tiles
from objects3D.globe_countries_i18n import globe_countries_i18n
from objects3D.overpass_countries import overpass_countries

from PIL import Image, ImageDraw, ImageFont


class globe_continents(globe_countries_i18n):
    def __init__(self):
        super().__init__()
        self.speed = 2.5

    def get_globe_texture_image(self, zoom):
        ovp = overpass_countries()
        ovp.init_tile_bboxes()

        ot = osm_tiles()
        im = ot.get_world_empty_image_for_globe(zoom)

        ovp.load()
        ovp.selected_countries = ["BR", "AD", "SM", "AL", "SK", "AT", "GB", "AU", "NO", "SE", "JP", "IT", "GR", "DZ", "KZ", "DK", "GL"] #, "RU", "FR"
        ovp.selected_countries = ["KZ", "UG"]
        #ovp.selected_countries = []
        #ovp.get_countries_bounding_boxes()
        ovp.get_continents_borders(zoom)
        ovp.get_country_borders(zoom)
        ovp.force_reload_cache = []
        ovp.force_recalc_polygons = []
        #ovp.get_list_of_admin_level_2_borders(True)

        #ovp.get_list_of_countries()
        ovp.get_global_land_polygons(zoom)

        self.fill_all_world(im, ovp, zoom)
        self.draw_land_polygons(im, ovp, zoom)
        self.draw_continent_polygons(im, ovp, zoom)
        #self.draw_countries_land_borders(im, ovp, zoom)

        im.save("globe.png")
        im = self.fromMercator(im)
        im = Image.open("globe.png")

        self.ovp = ovp
        return im