from geo.osm_tiles import osm_tiles
from objects3D.globe_countries_i18n import globe_countries_i18n
from objects3D.overpass_countries import overpass_countries

from PIL import Image, ImageDraw, ImageFont


class globe_continents(globe_countries_i18n):
    def __init__(self):
        super().__init__()
        self.speed = 0.75

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
        lang = "ru"
        ovp.get_continents_borders(zoom)
        ovp.get_country_borders(zoom)
        ovp.get_continent_labels(zoom, lang)
        ovp.get_ocean_labels(zoom, lang)
        ovp.force_reload_cache = []
        ovp.force_recalc_polygons = []
        #ovp.get_list_of_admin_level_2_borders(True)
        #ovp.get_list_of_countries()
        ovp.get_global_land_polygons(zoom)

        self.fill_all_world(im, ovp, zoom)
        self.draw_land_polygons(im, ovp, zoom)
        self.draw_continent_polygons(im, ovp, zoom)
        self.draw_continent_labels(im, ovp, zoom, lang)
        self.draw_ocean_labels(im, ovp, zoom, lang)
        #self.draw_countries_land_borders(im, ovp, zoom)

        im.save("globe.png")
        im = self.fromMercator(im)
        im = Image.open("globe.png")

        self.ovp = ovp
        return im

    def draw_continent_labels(self, im, ovp, zoom, lang):
        font_size = im.height // 32
        color = (0, 0, 0)
        font = ImageFont.truetype('fonts\\TimesNewRomanRegular.ttf', font_size)
        d = ImageDraw.Draw(im)
        n = 2 ** zoom
        w = im.width
        h = im.height

        for cont_i in ovp.continent_info:
            self.draw_label(color, cont_i, d, font, h, lang, n, w)

    def draw_ocean_labels(self, im, ovp, zoom, lang):
        font_size = im.height // 32
        color = (0, 0, 192)
        font = ImageFont.truetype('fonts\\TimesNewRomanRegular.ttf', font_size)
        d = ImageDraw.Draw(im)
        n = 2 ** zoom
        w = im.width
        h = im.height

        for cont_i in ovp.ocean_info:
            self.draw_label(color, cont_i, d, font, h, lang, n, w)

    def draw_label(self, color, cont_i, d, font, h, lang, n, w):
        xy0 = cont_i["xy"]
        s = cont_i["name"]
        bbox = d.multiline_textbbox((0.0, 0.0), s, font=font, spacing=0, language=lang)
        xy = (int((xy0[0] * w) / n - (bbox[2] - bbox[0] + 1) / 2), int((xy0[1] * h / n) - (bbox[3] - bbox[1] + 1) / 2))
        d.multiline_text(xy, s, font=font, fill=color, spacing=0, language=lang)
        if xy[0] + (bbox[2] - bbox[0] + 1) >= w:
            d.multiline_text((xy[0] - w, xy[1]), s, font=font, fill=color, spacing=0, language=lang)
        if xy[0] < 0:
            d.multiline_text((xy[0] + w, xy[1]), s, font=font, fill=color, spacing=0, language=lang)
