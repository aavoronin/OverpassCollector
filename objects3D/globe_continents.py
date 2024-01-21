import math

import cv2
import numpy as np

from objects3D.globe_countries_i18n import globe_countries_i18n
from shapely.geometry import Polygon, MultiPolygon
from PIL import Image, ImageDraw, ImageFont
from objects3D.polygon_fill_info import polygon_fill_info


class globe_continents(globe_countries_i18n):
    def __init__(self):
        super().__init__()
        self.speed = 0.8

    def get_globe_texture_image(self, zoom):
        self.zoom = zoom
        self.init_image_and_ovp()
        self.ovp.load()
        self.select_objects_to_load()

        self.ovp.get_global_land_polygons()
        self.ovp.get_continents_borders()
        self.ovp.get_country_borders()
        self.ovp.get_continent_labels(self.large_labels_base_size)
        self.ovp.get_ocean_labels(self.large_labels_base_size)

        self.fill_all_world()
        self.draw_land_polygons()
        self.draw_continent_polygons()
        self.draw_continent_labels()
        self.draw_ocean_labels()

        self.post_process_image()

    def select_objects_to_load(self):
        self.ovp.selected_countries = ["BR", "AD", "SM", "AL", "SK", "AT", "GB", "AU", "NO", "SE", "JP", "IT", "GR",
                                       "DZ", "KZ", "DK", "GL"]  # , "RU", "FR"
        self.ovp.selected_countries = ["KZ", "UG"]
        # ovp.selected_countries = []
        # ovp.get_countries_bounding_boxes()
        self.large_labels_base_size = self.im.height // 64

    def draw_continent_labels(self):
        color = (0, 0, 0)
        font_size = self.im.height // 64
        font_size2 = 256
        font = ImageFont.truetype('fonts\\TimesNewRomanRegular.ttf', font_size)
        font2 = ImageFont.truetype('fonts\\TimesNewRomanRegular.ttf', font_size2)

        n = 2 ** self.zoom
        w = self.im.width
        h = self.im.height

        label_info = self.ovp.continent_info
        self.draw_labels_core(color, font2, h, label_info, n, w)

    def draw_ocean_labels(self):
        color = (0, 0, 192)
        font_size = self.im.height // 128
        font_size2 = 256
        font = ImageFont.truetype('fonts\\TimesNewRomanRegular.ttf', font_size)
        font2 = ImageFont.truetype('fonts\\TimesNewRomanRegular.ttf', font_size2)

        n = 2 ** self.zoom
        w = self.im.width
        h = self.im.height
        label_info = self.ovp.ocean_info

        self.draw_labels_core(color, font2, h, label_info, n, w)

    def init_masks(self):
        self.im_mask = np.full_like(self.im, 255)
        self.im_mask_img = Image.fromarray(self.im_mask)
        self.im_mask_img_draw = ImageDraw.Draw(self.im_mask_img)

        self.im_stamp = np.zeros_like(self.im)
        self.im_stamp_img = Image.fromarray(self.im_stamp)
        self.im_stamp_img_draw = ImageDraw.Draw(self.im_stamp_img)

    def draw_labels_core(self, color, font2, h, label_info, n, w):

        #self.im_mask = np.full_like(self.im, 255)
        #self.im_mask_img = Image.fromarray(self.im_mask)
        #self.im_mask_img_draw = ImageDraw.Draw(self.im_mask_img)

        #self.im_stamp = np.zeros_like(self.im)
        #self.im_stamp_img = Image.fromarray(self.im_stamp)
        #self.im_stamp_img_draw = ImageDraw.Draw(self.im_stamp_img)
        self.init_masks()

        fi_letter_color = polygon_fill_info(fill_color=color, border_color=None)
        fi_black = polygon_fill_info(fill_color=(0,0,0), border_color=None)
        fi_white = polygon_fill_info(fill_color=(255,255,255), border_color=None)

        for cont_i in label_info:
            # self.draw_label(color, cont_i, font, h, lang, n, w)
            self.draw_label_polygons(cont_i, font2, w, h, n,
                                     fi_letter_color, fi_black, fi_white)

        #self.im_mask_img_draw._image.save("mask.png")
        #im_stamp_img_draw._image.save("stamp.png")

        self.apply_masks()
        #self.draw = ImageDraw.Draw(
        #    Image.fromarray(np.array(self.draw._image) &
        #                    np.array(self.im_mask_img_draw._image) |
        #                    np.array(self.im_stamp_img_draw._image)))

        #self.draw._image.save("masked.png")
        #self.apply_masked_drawing(self.im_mask, self.im_stamp)

    def apply_masks(self):
        self.draw = ImageDraw.Draw(
            Image.fromarray(np.array(self.draw._image) &
                            np.array(self.im_mask_img_draw._image) |
                            np.array(self.im_stamp_img_draw._image)))

    def convert_text_polygon_point(self, p, bc, font_h, bh, lat, xy2):
        return (
            ((p[0] - bc[0]) * font_h / bh / abs(math.cos(lat * math.pi / 180.0))) + xy2[0],
            ((p[1] - bc[1]) * font_h / bh / abs(math.cos(lat * math.pi / 180.0))) + xy2[1]
        )

    def draw_label_polygons(self, cont_i, font2, w, h, n,
                            fi_letter_color, fi_black, fi_white):
        #xy0 = self.ovp.deg2xy(cont_i['lat'], cont_i['lon'], self.zoom)
        xy0 = self.convert_polygons_from_lat_lon([[[cont_i['lat'], cont_i['lon']]]])[0][0]

        lat = cont_i["lat"]
        lon = cont_i["lon"]
        s = cont_i["name"]
        font_h = cont_i["size"] * cont_i["lines"]
        #lines = cont_i["lines"]

        inner_polygons, outer_polygons, outer_polygons_for_text = self.get_text_polygons(font2, s)

        globe_text_inner_polygons, globe_text_outer_polygon = \
            self.convert_text_polygons(font_h, w, h, outer_polygons_for_text, outer_polygons, inner_polygons, lat, lon, n, xy0)

        for poly in globe_text_outer_polygon:
            min_x = min([p[0] for p in poly])
            max_x = max([p[0] for p in poly])
            if min_x < w and max_x >= 0:
                #self.draw_polygon_on_image_core(fi, poly)
                self.draw_polygon_on_2images_core([self.im_mask_img_draw, self.im_stamp_img_draw], [fi_black, fi_letter_color], poly)
            if min_x < 0:
                poly1 = [(p[0] + w, p[1]) for p in poly]
                #self.draw_polygon_on_image_core(fi, poly1)
                self.draw_polygon_on_2images_core([self.im_mask_img_draw, self.im_stamp_img_draw], [fi_black, fi_letter_color], poly1)
            if max_x >= w:
                poly2 = [(p[0] - w, p[1]) for p in poly]
                #self.draw_polygon_on_image_core(fi, poly2)
                self.draw_polygon_on_2images_core([self.im_mask_img_draw, self.im_stamp_img_draw], [fi_black, fi_letter_color], poly2)

        for poly in globe_text_inner_polygons:
            min_x = min([p[0] for p in poly])
            max_x = max([p[0] for p in poly])
            if min_x < w and max_x >= 0:
                #self.draw_polygon_on_image_core(fi, poly)
                self.draw_polygon_on_2images_core([self.im_mask_img_draw, self.im_stamp_img_draw], [fi_white, fi_black], poly)
            if min_x < 0:
                poly1 = [(p[0] + w, p[1]) for p in poly]
                self.draw_polygon_on_2images_core([self.im_mask_img_draw, self.im_stamp_img_draw], [fi_white, fi_black], poly1)
            if max_x >= w:
                poly2 = [(p[0] - w, p[1]) for p in poly]
                #self.draw_polygon_on_image_core(fi, poly2)
                self.draw_polygon_on_2images_core([self.im_mask_img_draw, self.im_stamp_img_draw], [fi_white, fi_black], poly2)

    def convert_text_polygons(self, font_h, w, h, outer_polygons_for_text, outer_polygons, inner_polygons, lat, lon, n, xy0):
        # Get the minimum rotated rectangle that encloses the merged polygon
        t_bbox = outer_polygons_for_text.minimum_rotated_rectangle
        bw = t_bbox.bounds[2] - t_bbox.bounds[0]
        bh = t_bbox.bounds[3] - t_bbox.bounds[1]
        bc = ((t_bbox.bounds[2] + t_bbox.bounds[0]) // 2, (t_bbox.bounds[3] + t_bbox.bounds[1]) // 2)
        # xy = (int((xy0[0] * w) / n - (bbox[2] - bbox[0] + 1) / 2), int((xy0[1] * h / n) - (bbox[3] - bbox[1] + 1) / 2))
        xy2 = (int((xy0[0] * w) / n), int((xy0[1] * h / n)))
        globe_text_outer_polygon = [
            [
                self.convert_text_polygon_point(p, bc, font_h, bh, lat, xy2)
                for p in poly.exterior.coords
            ]
            for poly in outer_polygons]
        globe_text_inner_polygons = [
            [
                self.convert_text_polygon_point(p, bc, font_h, bh, lat, xy2)
                for p in poly.exterior.coords
            ]
            for poly in inner_polygons]
        min_maxes = [
            (min([p[0] for p in poly]), min([p[1] for p in poly]), max([p[0] for p in poly]), max([p[1] for p in poly]))
            for poly in globe_text_outer_polygon
        ]
        return globe_text_inner_polygons, globe_text_outer_polygon

    def get_text_polygons(self, font2, s):
        bbox2 = self.draw.multiline_textbbox((0.0, 0.0), s, font=font2, spacing=0, align='center', language=self.lang)
        factor = 2
        w2, h2 = factor * int(bbox2[2] - bbox2[0] + 1), factor * int(bbox2[3] - bbox2[1] + 1)
        img_ar = np.zeros((h2, w2), dtype=np.uint8)
        text_box_img = Image.fromarray(img_ar, 'L')
        text_box_img_draw = ImageDraw.Draw(text_box_img)
        text_box_img_draw.multiline_text((0.0, 0.0), s, font=font2, fill=255, spacing=0, align='center', language=self.lang)
        img_ar = np.array(text_box_img)
        # Convert the image to binary.
        binary_img = img_ar > 128
        # Find contours in the binary image.
        contours, _ = cv2.findContours(binary_img.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Approximate the contours to polygons.
        polygons0 = [cv2.approxPolyDP(cnt, 1, True) for cnt in contours]
        polygons = [Polygon([(p[0][0], p[0][1]) for p in poly]) for poly in polygons0]
        # Assuming 'polygons' is a list of shapely Polygon objects
        outer_polygons = []
        inner_polygons = []
        # First iteration: Mark polygons that are contained by any other polygon
        for i, polygon1 in enumerate(polygons):
            for polygon2 in polygons[:i] + polygons[i + 1:]:
                if polygon2.contains(polygon1):
                    inner_polygons.append(polygon1)
                    break
        # Second iteration: Create the list of outer polygons
        for polygon in polygons:
            if polygon not in inner_polygons:
                outer_polygons.append(polygon)
        # Assuming outer_polygons is your list of polygons
        outer_polygons_for_text = MultiPolygon(outer_polygons)
        return inner_polygons, outer_polygons, outer_polygons_for_text

    def draw_label(self, color, cont_i, font, h, lang, n, w):
        xy0 = cont_i["xy"]
        s = cont_i["name"]
        bbox = self.draw.multiline_textbbox((0.0, 0.0), s, font=font, spacing=0, language=lang)
        xy = (int((xy0[0] * w) / n - (bbox[2] - bbox[0] + 1) / 2), int((xy0[1] * h / n) - (bbox[3] - bbox[1] + 1) / 2))
        self.draw.multiline_text(xy, s, font=font, fill=color, spacing=0, language=lang)
        if xy[0] + (bbox[2] - bbox[0] + 1) >= w:
            self.draw.multiline_text((xy[0] - w, xy[1]), s, font=font, fill=color, spacing=0, language=lang)
        if xy[0] < 0:
            self.draw.multiline_text((xy[0] + w, xy[1]), s, font=font, fill=color, spacing=0, language=lang)

