# https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
# http://a.tile.openstreetmap.org/3/3/2.png
# "http://overpass-api.de/api/map?bbox=-180,-90,180,90"
import os.path
import random
import time
import urllib
from io import BytesIO

import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont


class osm_tiles:
    def __init__(self):
        self.servers = [
            "http://a.tile.openstreetmap.org",
            "http://b.tile.openstreetmap.org",
            "http://c.tile.openstreetmap.org",
        ]
        self.tile_cache = geo_cache()

    def get_tile_image(self, z, x, y):
        fname = self.get_image_filename(x, y, z)
        image = self.tile_cache.get_from_cache(fname)
        if image is None:
            n_retries = 10
            while n_retries > 0:
                try:
                    server = random.choice(self.servers)
                    url = f'{server}/{z}/{x}/{y}.png'
                    #response = urllib.request.urlopen(url)
                    #response = requests.get(url, stream=True)
                    req = urllib.request.Request(url)
                    req.add_header('User-Agent', 'Mozilla/7.0')
                    response = urllib.request.urlopen(req)

                    image = Image.open(BytesIO(response.read()))
                    print(f'downloaded {url}')

                    #@response = requests.get(url, stream=True)
                    #image = Image.open(BytesIO(response.content))
                    #im_data = requests.get(url, stream=True).raw
                    #image = Image.open(im_data)
                    break
                except Exception as e:
                    print(e)
                    time.sleep(10)
                    n_retries - 1
                    if n_retries <= 0:
                        raise
            self.tile_cache.save_to_cache(image, fname)

        return image

    def get_image_filename(self, x, y, z):
        return f'osm_tile_{z}_{x}_{y}.png'

    def get_world_image(self, z, draw_tile_numbers = False):
        fname = f'world_z_{z}.png'
        n_tiles = pow(2, z)
        self.tiles_grid = [[self.get_tile_image(z, x, y) for x in range(n_tiles)] for y in range(n_tiles)]
        self.total_width = self.tiles_grid[0][0].shape[0] * n_tiles
        self.total_height = self.tiles_grid[0][0].shape[1] * n_tiles
        #self.total_height = (int)(self.tiles_grid[0][0].shape[1] * n_tiles / (85.0511 / 90.0))

        #self.total_height_tiles = self.tiles_grid[0][0].shape[1] * n_tiles
        #self.total_height = (int)(self.tiles_grid[0][0].shape[1] * n_tiles / (85.0511 / 90.0))
        total_image = Image.new(mode="RGB", size=(self.total_width, self.total_height))
        if draw_tile_numbers:
            font = ImageFont.truetype('fonts\\arial.ttf', 36)
        #y_running = (self.total_height - self.total_height_tiles) // 2
        y_running = 0
        for y in range(n_tiles):
            x_running = 0
            for x in range(n_tiles):
                im = self.tiles_grid[y][x]
                im1 = Image.fromarray(im[:, :, ::-1])
                draw = ImageDraw.Draw(im1)
                if draw_tile_numbers:
                    draw.text((15, 15), f'{x} {y}', font=font, align="left", fill=(0,0,0))
                total_image.paste(im1, (x_running, y_running, x_running + im.shape[0], y_running + im.shape[1]))
                x_running += im.shape[1]
                del im1
                self.tiles_grid[y][x] = None
            y_running += im.shape[0]
        del self.tiles_grid

        self.tile_cache.save_to_cache(total_image, fname)
        return total_image

    def get_world_image_for_globe(self, z, bboxes, draw_tile_numbers = False):
        fname = f'world_z_{z}.png'
        n_tiles = pow(2, z)
        self.tiles_grid = [[self.get_tile_image(z, x, y) for x in range(n_tiles)] for y in range(n_tiles)]
        self.total_width = self.tiles_grid[0][0].shape[0] * n_tiles
        self.total_height = self.total_width // 2 #self.tiles_grid[0][0].shape[1] * n_tiles
        total_image = Image.new(mode="RGB", size=(self.total_width, self.total_height))
        if draw_tile_numbers:
            font = ImageFont.truetype('fonts\\arial.ttf', 36)
        y_running = 0
        for y in range(n_tiles):
            x_running = 0
            for x in range(n_tiles):
                im = self.tiles_grid[y][x]

                bbox = bboxes[y][x]

                im1 = Image.fromarray(im[:, :, ::-1])
                draw = ImageDraw.Draw(im1)
                if draw_tile_numbers:
                    draw.text((15, 15), f'{x} {y}', font=font, align="left", fill=(0,0,0))
                total_image.paste(im1, (x_running, y_running, x_running + im.shape[0], y_running + im.shape[1]))
                x_running += im.shape[1]
                del im1
                self.tiles_grid[y][x] = None
            y_running += im.shape[0]
        del self.tiles_grid

        self.tile_cache.save_to_cache(total_image, fname)
        return total_image


    def draw_tiles_numbers(self, z, total_image):
        n_tiles = pow(2, z)
        font = ImageFont.truetype('fonts\\arial.ttf', 36)
        draw = ImageDraw.Draw(total_image)

        for y in range(n_tiles):
            for x in range(n_tiles):
                text_xy = (15 + (total_image.width * x) // n_tiles, 15 + (total_image.height * y) // n_tiles)
                draw.text(text_xy, f'{x} {y}', font=font, align="left", fill=(0,0,0))

class geo_cache:
    def __init__(self):
        self.folder = "c:\\Cache\\cache_geo\\"

    def get_from_cache(self, image_filename):
        try:
            fname = os.path.join(self.folder, image_filename)
            if os.path.isfile(fname):
                image = cv2.imread(fname)
                return image
            return None
        except:
            return None

    def save_to_cache(self, image, image_filename):
        fname = os.path.join(self.folder, image_filename)
        image.save(fname, 'png')
