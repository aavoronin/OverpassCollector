import math

from objects3D.globe_continents import globe_continents


class globe_continents2(globe_continents):
    def __init__(self):
        super().__init__()
        self.factor = 1.0
        self.lang = "ru"
        self.speed = 1.8
        self.zoom = 6


    def convert_polygons_from_lat_lon(self, polygons_lat_lon):
        #return [[self.ovp.deg2xy(point[0], point[1], self.zoom) for point in poly] for poly in polygons_lat_lon]
        return [[self.ovp.deg_2_texture_xy(point[0], point[1], self.im.width, self.im.height)
                 for point in poly] for poly in polygons_lat_lon]

    def convert_text_polygon_point(self, p, bc, font_h, bh, lat, xy2):
        #return (
        #    ((p[0] - bc[0]) * font_h / bh / abs(math.cos(lat * math.pi / 180.0))) + xy2[0],
        #    ((p[1] - bc[1]) * font_h / bh / abs(math.cos(lat * math.pi / 180.0))) + xy2[1]
        #)
        return (
            ((p[0] - bc[0]) * font_h / bh / abs(math.cos(lat * math.pi / 180.0))) + xy2[0],
            ((p[1] - bc[1]) * font_h / bh) + xy2[1]
        )

    def draw_polygons_on_image(self, polygons, fill_info):
        n = 2 ** self.zoom
        w = self.im.width
        h = self.im.height
        for poly in polygons[0]:
            #xys = [((xy0[0] * w) / n, (xy0[1] * h / n)) for xy0 in poly]
            self.draw_polygon_on_image_core(fill_info, poly)
        #return self.im

    def convert_text_polygons(self, font_h, w, h, outer_polygons_for_text, outer_polygons, inner_polygons, lat, lon, n, xy0):
        # Get the minimum rotated rectangle that encloses the merged polygon
        t_bbox = outer_polygons_for_text.minimum_rotated_rectangle
        bw = t_bbox.bounds[2] - t_bbox.bounds[0]
        bh = t_bbox.bounds[3] - t_bbox.bounds[1]
        bc = ((t_bbox.bounds[2] + t_bbox.bounds[0]) // 2, (t_bbox.bounds[3] + t_bbox.bounds[1]) // 2)
        # xy = (int((xy0[0] * w) / n - (bbox[2] - bbox[0] + 1) / 2), int((xy0[1] * h / n) - (bbox[3] - bbox[1] + 1) / 2))
        #xy2 = (int((xy0[0] * w) / n), int((xy0[1] * h / n)))
        globe_text_outer_polygon = [
            [
                self.convert_text_polygon_point(p, bc, font_h, bh, lat, xy0)
                for p in poly.exterior.coords
            ]
            for poly in outer_polygons]
        globe_text_inner_polygons = [
            [
                self.convert_text_polygon_point(p, bc, font_h, bh, lat, xy0)
                for p in poly.exterior.coords
            ]
            for poly in inner_polygons]
        min_maxes = [
            (min([p[0] for p in poly]), min([p[1] for p in poly]), max([p[0] for p in poly]), max([p[1] for p in poly]))
            for poly in globe_text_outer_polygon
        ]
        return globe_text_inner_polygons, globe_text_outer_polygon

    def get_globe_texture_image(self, zoom):
        self.zoom = zoom
        self.init_image_and_ovp()
        self.ovp.load()
        self.select_objects_to_load()

        self.ovp.get_global_land_polygons(self.ovp)
        self.ovp.get_continents_borders(self.ovp)
        self.ovp.get_country_borders()
        self.ovp.get_continent_labels(self.large_labels_base_size)
        self.ovp.get_ocean_labels(self.large_labels_base_size)

        self.fill_all_world()
        self.draw_land_polygons()
        self.draw_continent_polygons()
        self.draw_continent_labels()
        self.draw_ocean_labels()

        self.post_process_image()

    def post_process_image(self):
        self.im = self.draw._image
        self.im.save("globe.png")
