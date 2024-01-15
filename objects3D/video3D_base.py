import glfw
import cv2
import numpy
import numpy as np
from OpenGL.GL import glLight, glLightfv
from OpenGL.raw.GLUT import glutSwapBuffers, glutPostRedisplay, glutSolidSphere
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from PIL.Image import MAX_IMAGE_PIXELS
from vpython import *
from cv2 import VideoWriter_fourcc, VideoWriter
import pygame
from pygame.locals import *
from PIL import Image
from OpenGL.GL import *
from OpenGL.GLU import *
from geo.osm_tiles import osm_tiles
from objects3D.combined_object_3D import combined_object_3D
from objects3D.cube3D import *
#import OpenGL.GL.shaders
#import pyrr
from PIL import Image
#from OpenGL_accelerate import *
#from OpenGL_accelerate import numpy_formathandler

#https://www.youtube.com/watch?v=Mwzz-Y6t-v8

class video_3D_base:

    def __init__(self):
        self.down_message_img = None
        self.bottom_message = ["no message"]
        self.create_by_message = "by Alexey Voronin"
        self.fast = False
        self.limit = 3600 * 60 * 12

    def gen_video_from_data(self):
        self.init_video_params()
        self.generate_video()

    def set_output_file(self, file_name: str = './noise2.avi'):
        self.videoFile = file_name

    def init_video_writer(self):
        self.fourcc = VideoWriter_fourcc(*'MP42')
        self.video = VideoWriter(self.videoFile, self.fourcc, float(self.FPS), (self.video_width, self.video_height))

    def close_video_writer(self):
        self.video.release()

    def init_video_params(self):
        self.width = int(1280)
        self.height = int(720)
        self.video_width = self.width
        self.video_height = self.height
        self.FPS = 60
        self.resolution_expand = 4.0
        self.expanded_size = (int(self.height * self.resolution_expand), int(self.width * self.resolution_expand))

        self.background_color = (255, 255, 255)
        self.fore_color = (0, 0, 0)
        self.countour_color = (255, 0, 0)

        self.frames_per_element = 240
        self.first_frames_delay = 240
        self.last_frames_delay = 360
        self.current_frame = 0

        if self.fast:
            self.FPS = 10
            self.frames_per_element = 40
            self.first_frames_delay = 40
            self.last_frames_delay = 60
        else:
            self.FPS = 50
            self.frames_per_element = 50
            self.first_frames_delay = 50
            self.last_frames_delay = 150

    def generate_video(self):
        self.init_video_writer()
        self.create_subframes()
        self.close_video_writer()

    def gen_video_from_data(self):
        self.init_video_params()
        self.generate_video()

    def post_process_frame(self, frame):
        return frame

    def placeImage(self, im1, im2, x, y):
        w = len(im2[0])
        h = len(im2)
        if y + h > len(im1):
            h -= y + h - len(im1)
        if x < 0:
            im2 = im2[0:h, -x:w + x]
            w = w + x
            x = 0
        if x + w > len(im1[0]):
            w -= x + w - len(im1[0])
        if h <= 0 or w <= 0:
            return
        im1[y:y + h, x:x + w] = im2[0:h, 0:w]

    def resizeImage(self, im2, size, method=cv2.INTER_AREA):
        return cv2.resize(im2, None, fx=size, fy=size, interpolation=method)  #

    def create_subframes(self):
        i = 0
        self.init_scene()
        data_arr = self.get_data_array()
        #frame = np.tile(np.array(self.background_color, dtype=np.uint8), (self.height, self.width, 1))
        #self.iterate_scene(frame, el)

        for el in data_arr:
            info = f'{i:5d} frame: {self.current_frame} time: {self.current_frame // self.FPS // 60:02d}:{(self.current_frame // self.FPS) % 60:02d}'
            print(info)
            if i > self.limit:
                break

            #frame = np.tile(np.array(self.background_color, dtype=np.uint8), (self.expanded_size[0], self.expanded_size[1], 1))
            frame = np.tile(np.array(self.background_color, dtype=np.uint8), (self.height, self.width, 1))
            self.iterate_scene(frame, el)
            frame = frame[::-1, :, ::+1] #flip y and flip colors
            frame = self.post_process_frame(frame)
            #frame = cv2.resize(frame[:, :, [2, 1, 0]], (self.width, self.height), interpolation=cv2.INTER_AREA)

            if i == 0:
                repeat = self.first_frames_delay
            else:
                repeat = 1
            for _ in range(0, repeat):
                self.video.write(frame)
                self.current_frame += 1
            i += 1

