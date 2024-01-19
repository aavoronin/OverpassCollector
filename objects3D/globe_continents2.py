import math
import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_0 import glRotatef

from objects3D.globe_continents import globe_continents
from geopy.distance import great_circle, Distance
from pyproj import Proj, transform
from pyproj import Geod
from geopy import Point
from geopy.distance import geodesic
import math
from geographiclib.geodesic import Geodesic

class globe_continents2(globe_continents):
    def __init__(self):
        super().__init__()
        self.factor = 1.0
        self.lang = "ru"
        self.speed = 1.8
        self.zoom = 4


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

    def do_rotation(self, el, frame):

        #az, ax, ay = self.calculate_rotations(self.current_lat, self.current_lon, 0, 0)
        #if az != 0:
        #    glRotatef(az, 0, 0, 1)
        #if ax != 0:
        #    glRotatef(-ax, 1, 0, 0)
        #if ay != 0:
        #    glRotatef(-ay, 0, 1, 0)
        #az, ax, ay = self.calculate_rotations(0, 0, el[0], el[1])
        #if az != 0:
        #    glRotatef(az, 0, 0, 1)
        #if ax != 0:
        #    glRotatef(-ax, 1, 0, 0)
        #if ay != 0:
        #    glRotatef(-ay, 0, 1, 0)

        glRotatef(+self.current_lat * math.cos(math.radians(-self.current_lon)), 1, 0, 0)
        glRotatef(+self.current_lat * math.sin(math.radians(-self.current_lon)), 0, 1, 0)
        glRotatef(-self.current_lon, 0, 0, 1)
        self.current_lat = el[0]
        self.current_lon = el[1]
        glRotatef(+self.current_lon, 0, 0, 1)
        glRotatef(-self.current_lat * math.sin(math.radians(-self.current_lon)), 0, 1, 0)
        glRotatef(-self.current_lat * math.cos(math.radians(-self.current_lon)), 1, 0, 0)
        #glRotatef(-self.current_lat, 1, 0, 0)

        #self.current_lat_lon
        #glRotatef(el[1], el[1], el[2], el[3])
        #glRotatef((+self.current_lat - self.initial_angle_x), 1, 0, 0)
        #glRotatef((-self.current_lon - self.initial_angle_z), 0, 0, 1)
        #glRotatef((+self.current_lon + self.initial_angle_z), 0, 0, 1)
        #glRotatef((-self.current_lat + self.initial_angle_x), 1, 0, 0)
        #glRotatef(0.25, 1, 0, 0)
        #glRotatef(0.5, 0, 0, 1)

    def calculate_rotations(self, lat0, lon0, new_lat, new_lon):

        # Convert latitudes and longitudes to radians
        lat0 = np.deg2rad(lat0)
        lon0 = np.deg2rad(lon0)
        new_lat = np.deg2rad(new_lat)
        new_lon = np.deg2rad(new_lon)

        # Calculate rotations
        az = new_lon - lon0
        ax = new_lat - lat0
        ay = 0  # Assuming the globe's axis is aligned with the y-axis

        # Adjust rotations
        az += np.pi if az < 0 else 0
        ax += np.pi if ax < 0 else 0
        ay += np.pi if ay < 0 else 0

        return np.rad2deg(az), np.rad2deg(ax), np.rad2deg(ay)

    def do_initial_rotation(self):
        self.initial_angle_x = 90
        self.initial_angle_z = -180
        glRotatef(self.initial_angle_x, 1, 0, 0)
        glRotatef(self.initial_angle_z, 0, 0, 1)


    def get_data_array(self):
        #for bb_data in self.ovp.countries_bboxes:
        #    print(f'code: {bb_data["code"]} name en: {bb_data["name_en"]} bbox={bb_data["bbox"].bbox}')

        self.current_lat = 0.0
        self.current_lon = 0.0
        a_xyz = (90, 0, -180)
        lat, lon = 0.0, 0.0
        a = []
        rotate_frames = 250
        for continent in ["Asia", "Africa", "South America", "North America", "Europe", "Oceania", "Antarctica"]:
            bbox = self.ovp.global_continent_bboxes[continent]
            new_lat, new_lon = bbox["center_lat"], bbox["center_lon"]
            path = self.generate_path(lat, lon, new_lat, new_lon, rotate_frames)
            for r in path:
                a.append(r)
                print(f'({r[0]:.3f},{r[1]:.3f})')
            for _ in range(len(path) // 3):
                a.append(path[-1])
            #[[1 / self.speed, 0, 0, 1] for _ in range(int(140 * self.speed))],
            #print(continent, new_lat, new_lon)
            lat, lon = new_lat, new_lon
        r = []
        for i in range(len(a) - 1):
            az = a[i + 1][1] - a[i][1]
            ax = a[i + 1][0] - a[i][0]
            r.append([az, 0, 0, 1])
            r.append([-ax, 1, 0, 0])

        print(1)

        return a

    def generate_path(self, lat0, lon0, new_lat, new_lon, n):

        # Create a Geodesic object
        geod = Geodesic.WGS84

        # Calculate total distance
        total_distance = geod.Inverse(lat0, lon0, new_lat, new_lon)['s12']

        # Calculate distance per step
        step_distance = total_distance / n

        # Calculate initial azimuth
        azimuth = geod.Inverse(lat0, lon0, new_lat, new_lon)['azi1']

        # Initialize path with start point
        path = [(lat0, lon0)]

        # Generate remaining points
        for i in range(1, n):
            # Calculate current distance
            current_distance = i * step_distance

            # Calculate current point
            d = geod.Direct(lat0, lon0, azimuth, current_distance)
            lat2, lon2 = d['lat2'], d['lon2']

            # Add current point to path
            path.append((lat2, lon2))

        # Add end point to path
        path.append((new_lat, new_lon))

        return path

"""
        # Create points
        p0 = Point(lat0, lon0)
        p1 = Point(new_lat, new_lon)

        # Calculate total distance
        total_distance = geodesic((lat0, lon0), (new_lat, new_lon)).meters

        # Calculate distance per step
        step_distance = total_distance / n

        # Calculate initial bearing
        lat1 = math.radians(lat0)
        lon1 = math.radians(lon0)
        lat2 = math.radians(new_lat)
        lon2 = math.radians(new_lon)

        dlon = lon2 - lon1

        x = math.cos(lat2) * math.sin(dlon)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

        initial_bearing = math.degrees(math.atan2(x, y))
        initial_bearing = (initial_bearing + 360) % 360

        # Initialize path with start point
        path = [p0]

        # Generate remaining points
        for i in range(1, n):
            # Calculate current distance
            current_distance = i * step_distance

            ## Calculate current point
            #current_point = geodesic(p0, p1).destination(current_distance, initial_bearing)
            # Calculate current point
            g = geodesic((lat0, lon0), (new_lat, new_lon))
            frac = current_distance / g.meters
            lats, lons = g.destination(Point(lat0, lon0), initial_bearing, Distance(current_distance))

            Direct(self, lat1, lon1, azi1, s12,
                   outmask=GeodesicCapability.STANDARD):


            current_point = Point(lats, lons)

        # Add current point to path
        path.append(current_point)

    # Add end point to path
    path.append(p1)

    return path


"""