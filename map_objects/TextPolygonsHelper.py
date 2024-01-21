import math

import cv2
import numpy as np
from shapely import MultiPolygon, Polygon
from PIL import Image, ImageDraw, ImageFont

from objects3D.polygon_fill_info import polygon_fill_info


class TextPolygonsHelper():

    measuring_img_ar = np.zeros((1, 1), dtype=np.uint8)
    measuring_text_box_img = Image.fromarray(measuring_img_ar, 'L')
    measuring_draw = ImageDraw.Draw(measuring_text_box_img)
    fi_black = polygon_fill_info(fill_color=(0, 0, 0), border_color=None)
    fi_white = polygon_fill_info(fill_color=(255, 255, 255), border_color=None)

    @staticmethod
    def convert_polygons_from_lat_lon(ovp, polygons_lat_lon, w, h):

        #return [[self.ovp.deg2xy(point[0], point[1], self.zoom) for point in poly] for poly in polygons_lat_lon]
        return [[ovp.deg_2_texture_xy(point[0], point[1], w, h)
                 for point in poly] for poly in polygons_lat_lon]

    @staticmethod
    def convert_text_polygon_point(p, bc, font_h, bh, lat, xy2):
        return (
            ((p[0] - bc[0]) * font_h / bh / abs(math.cos(lat * math.pi / 180.0))) + xy2[0],
            ((p[1] - bc[1]) * font_h / bh) + xy2[1]
        )

    @staticmethod
    def convert_text_polygons(font_h, w, h, outer_polygons_for_text, outer_polygons, inner_polygons, lat, lon, xy0):
        # Get the minimum rotated rectangle that encloses the merged polygon
        t_bbox = outer_polygons_for_text.minimum_rotated_rectangle
        bw = t_bbox.bounds[2] - t_bbox.bounds[0]
        bh = t_bbox.bounds[3] - t_bbox.bounds[1]
        bc = ((t_bbox.bounds[2] + t_bbox.bounds[0]) // 2, (t_bbox.bounds[3] + t_bbox.bounds[1]) // 2)
        # xy = (int((xy0[0] * w) / n - (bbox[2] - bbox[0] + 1) / 2), int((xy0[1] * h / n) - (bbox[3] - bbox[1] + 1) / 2))
        #xy2 = (int((xy0[0] * w) / n), int((xy0[1] * h / n)))
        xy2 = xy0
        globe_text_outer_polygon = [
            [
                TextPolygonsHelper.convert_text_polygon_point(p, bc, font_h, bh, lat, xy2)
                for p in poly.exterior.coords
            ]
            for poly in outer_polygons]
        globe_text_inner_polygons = [
            [
                TextPolygonsHelper.convert_text_polygon_point(p, bc, font_h, bh, lat, xy2)
                for p in poly.exterior.coords
            ]
            for poly in inner_polygons]
        min_maxes = [
            (min([p[0] for p in poly]), min([p[1] for p in poly]), max([p[0] for p in poly]), max([p[1] for p in poly]))
            for poly in globe_text_outer_polygon
        ]
        return globe_text_inner_polygons, globe_text_outer_polygon

    @staticmethod
    def get_text_polygons(font2, s, lang):
        bbox2 = TextPolygonsHelper.measuring_draw.multiline_textbbox(
            (0.0, 0.0), s, font=font2, spacing=0, align='center', language=lang)
        factor = 2
        w2, h2 = factor * int(bbox2[2] - bbox2[0] + 1), factor * int(bbox2[3] - bbox2[1] + 1)
        img_ar = np.zeros((h2, w2), dtype=np.uint8)
        text_box_img = Image.fromarray(img_ar, 'L')
        text_box_img_draw = ImageDraw.Draw(text_box_img)
        text_box_img_draw.multiline_text((0.0, 0.0), s, font=font2, fill=255, spacing=0, align='center', language=lang)
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


    @staticmethod
    def draw_label_polygons(ovp, cont_i, font2, fi_letter_color,
                            im_mask_img_draw, im_stamp_img_draw):

        w = im_mask_img_draw._image.width
        h = im_mask_img_draw._image.height

        xy0 = TextPolygonsHelper.convert_polygons_from_lat_lon(ovp, [[[cont_i['lat'], cont_i['lon']]]], w, h)[0][0]

        lat = cont_i["lat"]
        lon = cont_i["lon"]
        s = cont_i["name"]
        font_h = cont_i["size"] * cont_i["lines"]

        inner_polygons, outer_polygons, outer_polygons_for_text = TextPolygonsHelper.get_text_polygons(font2, s, ovp.lang)

        globe_text_inner_polygons, globe_text_outer_polygon = \
            TextPolygonsHelper.convert_text_polygons(font_h, w, h, outer_polygons_for_text,
                                                     outer_polygons, inner_polygons, lat, lon, xy0)

        for poly in globe_text_outer_polygon:
            min_x = min([p[0] for p in poly])
            max_x = max([p[0] for p in poly])
            if min_x < w and max_x >= 0:
                #self.draw_polygon_on_image_core(fi, poly)
                TextPolygonsHelper.draw_polygon_on_2images_core([im_mask_img_draw, im_stamp_img_draw],
                                                                [TextPolygonsHelper.fi_black,
                                                                 fi_letter_color], poly)
            if min_x < 0:
                poly1 = [(p[0] + w, p[1]) for p in poly]
                #self.draw_polygon_on_image_core(fi, poly1)
                TextPolygonsHelper.draw_polygon_on_2images_core([im_mask_img_draw, im_stamp_img_draw],
                                                                [TextPolygonsHelper.fi_black,
                                                                 fi_letter_color], poly1)
            if max_x >= w:
                poly2 = [(p[0] - w, p[1]) for p in poly]
                #self.draw_polygon_on_image_core(fi, poly2)
                TextPolygonsHelper.draw_polygon_on_2images_core([im_mask_img_draw, im_stamp_img_draw],
                                                                [TextPolygonsHelper.fi_black,
                                                                 fi_letter_color], poly2)

        for poly in globe_text_inner_polygons:
            min_x = min([p[0] for p in poly])
            max_x = max([p[0] for p in poly])
            if min_x < w and max_x >= 0:
                #self.draw_polygon_on_image_core(fi, poly)
                TextPolygonsHelper.draw_polygon_on_2images_core([im_mask_img_draw, im_stamp_img_draw],
                                                                [TextPolygonsHelper.fi_white,
                                                                 TextPolygonsHelper.fi_black], poly)
            if min_x < 0:
                poly1 = [(p[0] + w, p[1]) for p in poly]
                TextPolygonsHelper.draw_polygon_on_2images_core([im_mask_img_draw, im_stamp_img_draw],
                                                                [TextPolygonsHelper.fi_white,
                                                                 TextPolygonsHelper.fi_black], poly1)
            if max_x >= w:
                poly2 = [(p[0] - w, p[1]) for p in poly]
                #self.draw_polygon_on_image_core(fi, poly2)
                TextPolygonsHelper.draw_polygon_on_2images_core([im_mask_img_draw, im_stamp_img_draw],
                                                                [TextPolygonsHelper.fi_white,
                                                                 TextPolygonsHelper.fi_black], poly2)

    @staticmethod
    def draw_polygon_on_2images_core(draws, fill_infos, xys):
        for i in range(len(draws)):
            draw = draws[i]
            fill_info = fill_infos[i]
            if fill_info.border_color is None:  # filled polygon without border
                draw.polygon(xy=xys, fill=fill_info.fill_color)
            elif fill_info.fill_color is not None:  # filled polygon with border
                draw.polygon(xy=xys, fill=fill_info.fill_color, outline=fill_info.border_color)
            else:
                pass