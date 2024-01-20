import glfw
import cv2
import numpy
import numpy as np
from PIL import ImageDraw, ImageFont
import pygame
from pygame.locals import *
from seaborn import color_palette

from geo.osm_tiles import osm_tiles
from objects3D.cube3D import *
from PIL import Image

from objects3D.overpass_countries import overpass_countries
from objects3D.polygon_fill_info import polygon_fill_info
from objects3D.video3D_base import video_3D_base




class globe_countries_i18n(video_3D_base):


    def __init__(self):
        super().__init__()
        self.init_ok = glfw.init()
        self.speed = 1.0
        self.water_color = (147, 187, 226, 255)
        self.default_land_color = (255, 255, 255, 255)
        self.draw = None
        self.lang = "en"
        self.zoom = 4

    def init_video_params(self):
        super().init_video_params()
        factor = 1
        self.width = int(1920 * factor)
        self.height = int(1080 * factor)
        self.video_width = self.width // factor
        self.video_height = self.height // factor
        self.FPS = 60

        self.first_frames_delay = 0

    def init_scene(self):
        factor = 1
        #self.ball_3D = ball_3D(factor * (2 ** tiles_power), factor * (2 ** tiles_power), 3)
        #self.ball_3D.create_arrays()
        pygame.init()
        display = (self.width, self.height)  # self.expanded_size
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        self.clock = pygame.time.Clock()

        self.create_globe_texture(self.zoom)
        self.sphere_d = int(self.height * 0.8)

        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        c1 = (70/255.0, 130/255.0, 180/255.0)
        glClearColor(c1[0], c1[1], c1[2], 0.0)

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        self.do_initial_offset()
        glLight(GL_LIGHT0, GL_POSITION, (0, 0, self.sphere_d * -5, 0))
        glEnable(GL_DEPTH_TEST)

        self.do_initial_rotation()
        #glRotatef(90, 1, 0, 0)
        #glRotatef(-180, 0, 0, 1)
        glScaled(3, 3, 3)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    def do_initial_offset(self):
        glTranslatef(0, 0, -9)

    def do_initial_rotation(self):
        glRotatef(90, 1, 0, 0)
        glRotatef(-90, 0, 0, 1)
        glRotatef(45, 0, 0, 1)

    def create_globe_texture(self, zoom):
        self.get_globe_texture_image(zoom)
        self.im.save("image.png", 'png')
        self.texture = self.read_texture("image.png", flip_x=True)

    def get_globe_texture_image(self, zoom):
        self.zoom = zoom
        self.init_image_and_ovp()
        #self.im = self.ot.get_world_image_for_globe(zoom, self.ovp.tile_bboxes)

        self.ovp.load()
        self.ovp.selected_countries = ["BR", "AD", "SM", "AL", "SK", "AT", "GB", "AU", "NO", "SE", "JP", "IT", "GR", "DZ", "KZ", "DK", "GL"] #, "RU", "FR"
        #ovp.selected_countries = ["US", "RU", "IT", "CL", "ES", "GE", "PL", "CH", "CA", "GB", "DK", "CZ", "AL", "DE", "KZ", "UG", "GL", "FR"] #[, "US"]
        #ovp.selected_countries = ["KZ", "UG"]
        #ovp.selected_countries = []
        #ovp.get_countries_bounding_boxes()
        self.ovp.get_countries_outer_borders()
        #ovp.get_countries_water_polygons()
        self.ovp.force_reload_cache = []
        self.ovp.force_recalc_polygons = []
        #ovp.get_list_of_admin_level_2_borders(True)

        #ovp.load()
        self.ovp.get_list_of_countries()
        for country_code, country_name in self.ovp.countries_code_name:
            print(f'{country_code} {country_name}')
        #ovp.load_countries_polygons_level4()
        self.ovp.get_global_land_polygons(zoom)

        self.fill_all_world()
        self.draw_land_polygons()
        #self.draw_countries_v3()
        #self.draw_water_v2()
        #self.draw_tiles_info()
        #self.ot.draw_tiles_numbers(self.im, zoom)
        self.post_process_image()

    def post_process_image(self):
        self.im = self.draw._image
        # self.im = self.draw._image
        # self.draw_countries_land_borders()
        self.im.save("globe.png")
        self.fromMercator()
        self.im = Image.open("globe.png")

    def init_image_and_ovp(self):
        self.ovp = overpass_countries(self.lang)
        self.ovp.init_tile_bboxes()
        self.ot = osm_tiles()
        self.im = self.ot.get_world_image(self.zoom)
        self.draw = ImageDraw.Draw(self.im, "RGB")

    def fromMercator(self) -> Image:
        #draw = ImageDraw.Draw(im)
        # img_data = numpy.array(list(im.getdata()), numpy.int8)
        w = self.im.width
        h = self.im.height
        h2 = h // 2
        offset85 = int(h2 * (90.0 - 85.0511) / 90.0)
        #print("offset85=", offset85)
        mercator = Image.open("globe.png")
        #mercator = Image.new('RGBA', (im.width, im.height), (0, 0, 0, 255))
        dH = 1
        # Применить формулу Меркатора
        for i in range(0, h2):
            y = h2 - i
            # cord = (0, h2+y, w, h2+y+1)  # лево, верх, право, низ
            # pic_crop = im.crop(cord)
            if y < h2 / 10:
                dH = 4
            elif y < h2 / 5:
                dH = 3
            elif y < h2 / 3:
                dH = 3
            else:
                dH = 2

            pic_crop = self.im.crop((0, h2 - y, w, h2 - y + dH))
            rezY = self.evaluateLat(y, h2)
            mercator.paste(pic_crop, (0, rezY + offset85))

            pic_crop = self.im.crop((0, h2 + y, w, h2 + y + dH))
            mercator.paste(pic_crop, (0, 2 * h2 - rezY - offset85))

        # зоны выше широты 85
        northEtalon = pic_crop = self.im.crop((0, 0, w, 1))
        for i in range(0, offset85):
            mercator.paste(pic_crop, (0, i))
        southEtalon = pic_crop = self.im.crop((0, h - 2, w, h - 1))
        for i in range(0, offset85):
            mercator.paste(pic_crop, (0, h - i))

        # draw = ImageDraw.Draw(mercator)
        # draw.line((0, h2, w, h2))
        mercator.save("globe.png")

    def evaluateLat(self, y, h2):
        debug = False
        self.pi_div_2 = math.pi / 2.0
        # teta = pi_div_2*(h2 - y)/h2
        #teta = (pi_div_2 - 5.0 / 90.0 * pi_div_2) * (h2 - y) / h2
        self.teta = (self.pi_div_2 - 10.0 / 90.0 * self.pi_div_2) * (h2 - y) / h2
        self.angle = self.teta / 2.0 + self.pi_div_2 / 2.0
        self.angleTan = math.tan(self.angle)
        self.lat = math.log(self.angleTan)
        #rezY = int(h2 * lat / pi_div_2) * 502 // 1000
        self.rezY = int(h2 * self.lat / self.pi_div_2) * 6096 // 10000
        if debug:
            print("y=", y, "rezY=", self.rezY, "h2=", h2, "teta=", self.teta, self.teta * 90 / self.pi_div_2, "angle=", self.angle, "angleTan=",
                  self.angleTan)
        return self.rezY
    def save_2x_globe(self):
        # Convert the image to a NumPy array
        original_array = np.array(self.im)

        # Duplicate each pixel horizontally
        duplicated_array = np.repeat(original_array, 2, axis=1)

        # Create a new image from the duplicated array
        duplicated_image = Image.fromarray(duplicated_array)
        duplicated_image.save("globe_2x.png")

    def get_country_data(self):
        ci_list = []
        for ci in self.ovp.country_data:
            if ci.country_code not in self.ovp.selected_countries and len(self.ovp.selected_countries) > 0:
                continue
            if ci.country_code in self.ovp.loaded_country_codes:
                continue
            if ci.country_code in self.ovp.skip_countrues:
                continue
            ci_list.append(ci)
        return ci_list


    def get_country_colors(self):
        num_colors = len(self.ovp.countries_df)
        colors = color_palette("hls", num_colors)
        return {self.ovp.countries_df.iloc[i]["ISO3166-1"]: tuple(int(c*255) for c in color) for i, color in enumerate(colors)}

    def draw_countries_v3(self):
        self.no_polygons_countries = []
        colors_d = self.get_country_colors()
        i = 0
        for ci in self.get_country_data():
            i += 1
            name_border = f'{ci.country_code} country_border_coastline v8'
            self.ovp.current_country_code = ci.country_code
            polygons_geo_lat_lon = self.ovp.load_polygon_from_cache_v3(name_border, self.zoom)
            if polygons_geo_lat_lon is None or ci.country_code in self.ovp.force_recalc_polygons:  # not in cache
                self.ovp.load_country_border_data_v3(ci, i)
                gb_osm = ci.country_border_coastline_osm_json
                polygons_geo_lat_lon = self.ovp.scan_for_polygons_v3(gb_osm, name_border)
            if polygons_geo_lat_lon is not None:
                texture_polygons = self.ovp.convert_polygon_lat_lon_to_texture_coords(polygons_geo_lat_lon, self.zoom)
                #fi = polygon_fill_info(fill_color=(255,0,0,255) , border_color=(0,0,0,255))
                country_color = self.get_country_color(ci, colors_d)
                fi = polygon_fill_info(fill_color=country_color, border_color=None)
                self.draw_polygons_on_image(texture_polygons, fi)
                del polygons_geo_lat_lon
                del texture_polygons
            else:
                if ci.country_code in self.no_polygons_countries:
                    self.no_polygons_countries.append(ci.country_code)

    def get_country_color(self, ci, colors_d):
        if ci.country_code not in colors_d:
            return (255, 255, 255, 255)
        country_color = colors_d[ci.country_code]
        country_color = (country_color[0], country_color[1], country_color[2], 255)
        return country_color

    def draw_land_polygons(self):
        #outer_polygons = [[self.ovp.deg2xy(point[0], point[1], self.zoom) for point in poly]
        #    for poly in self.ovp.global_land_polygons_xy["outer"]]
        fi = polygon_fill_info(fill_color=self.default_land_color, border_color=None)
        p = [self.convert_polygons_from_lat_lon(self.ovp.global_land_polygons_xy["outer"])]
        self.draw_polygons_on_image(p, fi)

        #inner_polygons = [[self.ovp.deg2xy(point[0], point[1], self.zoom) for point in poly]
        #    for poly in self.ovp.global_land_polygons_xy["inner"]]
        fi = polygon_fill_info(fill_color=self.water_color, border_color=None)
        self.draw_polygons_on_image([self.convert_polygons_from_lat_lon(
            self.ovp.global_land_polygons_xy["inner"])], fi)

    def draw_continent_polygons(self):
        continent_colors = {
            "North America": (255, 165, 0),  # Orange
            "South America": (255, 192, 203),  # Pink
            "Europe": (128, 0, 0),  # Red
            "Africa": (0, 128, 0),  # Green
            "Asia": (255, 255, 0),  # Yellow
            "Oceania": (165, 42, 42),  # Brown
            "Antarctica": (255, 255, 255)  # White
        }
        for continent in continent_colors.keys():
            if continent not in self.ovp.global_continent_polygons_xy:
                continue
            fi = polygon_fill_info(fill_color=continent_colors[continent], border_color=None)
            self.draw_polygons_on_image([self.convert_polygons_from_lat_lon(
                self.ovp.global_continent_polygons_xy[continent]["outer"])], fi)
            fi = polygon_fill_info(fill_color=self.water_color, border_color=None)
            self.draw_polygons_on_image([self.convert_polygons_from_lat_lon(
                self.ovp.global_continent_polygons_xy[continent]["inner"])], fi)

    def draw_countries_land_borders(self):
        # land_border_color = (64, 64, 64, 128)
        land_border_color = (255, 255, 255, 128)
        fi = polygon_fill_info(fill_color=None, border_color=land_border_color, width=3)
        self.draw_polygons_on_image([self.ovp.global_country_land_borders["outer"]], fi)

    def draw_water_v2(self):
        self.no_polygons_countries = []
        i = 0
        for ci in self.get_country_data(self.ovp):
            i += 1
            name_water = f'{ci.country_code} water v8'
            ci.load_country_lake_data()
            self.ovp.current_country_code = ci.country_code
            polygons_geo_lat_lon = ci.water_200000_polygons
            if polygons_geo_lat_lon is not None:
                fi = polygon_fill_info(fill_color="blue", border_color=None)
                texture_polygons = self.ovp.convert_polygon_lat_lon_to_texture_coords(polygons_geo_lat_lon, zoom)
                self.draw_polygons_on_image(texture_polygons, fi)
                del polygons_geo_lat_lon
                del texture_polygons

    def draw_countries_v2(self, im, ovp, zoom):
        self.no_polygons_countries = []
        i = 0
        for country_code, country_name_en in ovp.countries_code_name:  # country_code in countries: #["AU"]: #
            if country_code not in ovp.selected_countries and len(ovp.selected_countries) > 0:
                continue
            if country_code in ovp.loaded_country_codes:
                continue
            if country_code in ovp.skip_countrues:
                continue
            i += 1
            name_border = f'{country_code} country_border_coastline v5'
            name_water = f'{country_code} water'

            ovp.current_country_code = country_code
            polygons = ovp.load_polygon_from_cache_v2(name_border, zoom)
            if polygons is None or country_code in ovp.force_recalc_polygons:  # not in cache
                ovp.load_country_border_data_v2(country_code, country_name_en, i)
                if country_code in ovp.country_border_coastline_osm_json:
                    gb_osm = ovp.country_border_coastline_osm_json[country_code]
                    polygons = ovp.scan_for_polygons_v2(gb_osm, zoom, name_border)
            if polygons is not None:
                fi = polygon_fill_info(fill_color=(255, 0, 0, 255), border_color=(0, 0, 0, 255))
                self.draw_polygons_on_image(polygons, fi)
                del polygons
            else:
                if country_code in self.no_polygons_countries:
                    self.no_polygons_countries.append(country_code)

            polygons = ovp.load_polygon_from_cache(name_water, zoom)
            if polygons is None and country_code in ovp.water_osm_json:  # not in cache
                gb_osm = ovp.water_osm_json[country_code]
                polygons = ovp.scan_for_polygons(gb_osm, zoom, name_water)
            if polygons is not None:
                fi = polygon_fill_info(fill_color="blue", border_color=None)
                self.draw_polygons_on_image(polygons, fi)
                del polygons

            ovp.loaded_country_codes.append(country_code)
            print(f'{country_code} {country_name_en} painted on map')

        print(f'countries without polygon')
        for country_code in self.no_polygons_countries:
            print(country_code)
        print(f'=========================')

    def iterate_scene(self, frame, el):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # Zoom in and out with mouse wheel
            # if event.type == pygame.MOUSEBUTTONDOWN:
            #    if event.button == 4:  # wheel rolled up
            #        glScaled(1.05, 1.05, 1.05)
            #    if event.button == 5:  # wheel rolled down
            #        glScaled(0.95, 0.95, 0.95)

        self.do_rotation(el, frame)

        # Creates Sphere and wraps texture
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        qobj = gluNewQuadric()
        gluQuadricTexture(qobj, GL_TRUE)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        gluSphere(qobj, 1, self.sphere_d // 4, self.sphere_d // 4)
        gluDeleteQuadric(qobj)
        glDisable(GL_TEXTURE_2D)

        # Displays pygame window
        pygame.display.flip()
        pygame.time.wait(1)

        # self.clock.tick(60)
        glReadPixels(0, 0, self.width, self.height, GL_BGR, GL_UNSIGNED_BYTE, array=frame)
        pass

    def do_rotation(self, el, frame):
        glRotatef(el[0], el[1], el[2], el[3])

    def read_texture(self, filename, flip_x=False, flip_y=False):

        img = Image.open(filename)
        #img_data = numpy.array(list(img.getdata()), numpy.int8)
        img_data = numpy.asarray(img, dtype=numpy.int8)
        if flip_x and flip_y:
            img_data = img_data.reshape(img.size[0], img.size[1], 3)
            img_data = img_data[::-1, ::-1, :]
        elif flip_x:
            img_data = img_data.reshape(img.size[0], img.size[1], 3)
            img_data = img_data[:, ::-1, :]
        elif flip_y:
            img_data = img_data.reshape(img.size[0], img.size[1], 3)
            img_data = img_data[::-1, ::, :]
        textID = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, textID)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                     img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        return textID

    def post_process_frame(self, frame):
        frame1 = cv2.resize(frame, (self.video_width, self.video_height), interpolation=cv2.INTER_AREA)
        # frame1 = cv2.GaussianBlur(frame1, (1, 1), cv2.BORDER_DEFAULT)
        return frame1

    def get_data_array(self):
        #for bb_data in self.ovp.countries_bboxes:
        #    print(f'code: {bb_data["code"]} name en: {bb_data["name_en"]} bbox={bb_data["bbox"].bbox}')

        a = np.concatenate(
            (
                [[1 / self.speed, 0, 0, 1] for _ in range(int(140 * self.speed))],
                [[1 / self.speed, 0, 1, 0] for _ in range(int(120 * self.speed))],
                [[1 / self.speed, 0, -1, 0] for _ in range(int(240 * self.speed))],
                [[1 / self.speed, 0, 1, 0] for _ in range(int(120 * self.speed))],
                [[1 / self.speed, 0, 0, 1] for _ in range(int(100 * self.speed))],
                [[1 / self.speed, 1, 0, 0] for _ in range(int(120 * self.speed))],
                [[1 / self.speed, -1, 0, 0] for _ in range(int(240 * self.speed))],
                [[1 / self.speed, 1, 0, 0] for _ in range(int(120 * self.speed))],
                [[1 / self.speed, 0, 0, 1] for _ in range(int(120 * self.speed))],
            ), axis=0)
        return a

    def draw_polygons_on_image(self, polygons, fill_info):
        n = 2 ** self.zoom
        w = self.im.width
        h = self.im.height
        for poly in polygons[0]:
            xys = [((xy0[0] * w) / n, (xy0[1] * h / n)) for xy0 in poly]
            #minx = min([xy[0] for xy in xys])
            #miny = min([xy[1] for xy in xys])
            #maxx = max([xy[0] for xy in xys])
            #maxy = max([xy[1] for xy in xys])
            self.draw_polygon_on_image_core(fill_info, xys)

        #return self.im

    def draw_polygon_on_image_core(self, fill_info, xys):
        if fill_info.border_color is None:  # filled polygon without border
            self.draw.polygon(xy=xys, fill=fill_info.fill_color)
        elif fill_info.fill_color is not None:  # filled polygon with border
            self.draw.polygon(xy=xys, fill=fill_info.fill_color, outline=fill_info.border_color)
        else:
            pass
            # draw.polygon(xy=xys, fill=None, outline=fill_info.border_color, width = 3)

    def apply_masked_drawing(self, mask, stamp):

        # Access the underlying image
        image = self.draw._image

        # Convert the image and the mask to numpy arrays
        image_np = np.array(image)
        #mask_np = np.array(mask)
        #stamp_np = np.array(stamp)

        # Perform bitwise AND operation between the image and the mask
        masked_image_np = np.bitwise_and(image_np, mask)

        # Perform bitwise OR operation between the result and the stamp
        result_np = np.bitwise_or(masked_image_np, stamp)

        # Convert the result back to a PIL image
        # Create a new ImageDraw object with the updated image
        self.draw = ImageDraw.Draw(Image.fromarray(result_np))

    def draw_polygon_on_2images_core(self, draws, fill_infos, xys):
        for i in range(len(draws)):
            draw = draws[i]
            fill_info = fill_infos[i]
            if fill_info.border_color is None:  # filled polygon without border
                draw.polygon(xy=xys, fill=fill_info.fill_color)
            elif fill_info.fill_color is not None:  # filled polygon with border
                draw.polygon(xy=xys, fill=fill_info.fill_color, outline=fill_info.border_color)
            else:
                pass

    def draw_tiles_info(self):
        self.countries_names = {}
        font_size_1 = 36 if self.zoom >= 6 else 20
        font_size_2 = (font_size_1 * 2) // 3
        font = ImageFont.truetype('fonts\\arial.ttf', font_size_1)
        font2 = ImageFont.truetype('fonts\\arial.ttf', font_size_2)
        n_tiles = len(self.ovp.tile_bboxes)
        for (xtile, ytile) in self.ovp.get_list_of_tiles():
            bbox_info = self.ovp.tile_bboxes[ytile][xtile]

            text_xy = (15 + (self.im.width * xtile) // n_tiles, 15 + (self.im.height * ytile) // n_tiles)
            self.draw.text(text_xy, f'{xtile} {ytile}', font=font, align="left", fill=(0, 0, 0))

            bbox_str = bbox_info.bbox_str_short()
            text_xy = (15 + (self.im.width * xtile) // n_tiles, 45 + (self.im.height * ytile) // n_tiles)
            self.draw.text(text_xy, bbox_str, font=font, align="left", fill=(0, 0, 0))

    def fill_all_world(self):
        polygons = [[[-180,-90],[-180,90],[180,90],[180,-90]]]
        polygons = [[(p[1], p[0]) for p in polygons[0]]]
        fi = polygon_fill_info(fill_color=self.water_color, border_color=None)
        p = self.convert_polygons_from_lat_lon(polygons)
        self.draw_polygons_on_image([p], fi)


    def convert_polygons_from_lat_lon(self, polygons_lat_lon):
        return [[self.ovp.deg2xy(point[1], point[0], self.zoom) for point in poly] for poly in polygons_lat_lon]




