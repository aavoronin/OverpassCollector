import math
import pygame
from OpenGL.GL import *

# https://www.youtube.com/watch?v=H-RCv-bbfa8&t=552s
# https://www.youtube.com/watch?v=2fcO9RUOGg4
# http://bazaar.launchpad.net/~mcfletch/pyopengl-demo/trunk/files/48/PyOpenGL-Demo/NeHe
# https://stackoverflow.com/questions/47913978/texture-wrapping-an-entire-sphere-in-pyopengl
class fig_3D_base:
    def __init__(self):
        self.verticies = []
        self.textureCoordinates = []
        self.surfaces = []
        self.normals = []
        self.colors = []
        self.edges = []
        self.textures = []

    def create_arrays(self):
        pass

    def init_texture(self, file_name):
        image = pygame.image.load(file_name)
        return self.init_texture_from_image(image)

    def init_texture_from_image(self, image):
        datas = pygame.image.tostring(image, 'RGBA')
        texID = glGenTextures(1)
        self.textures.append(texID)
        glBindTexture(GL_TEXTURE_2D, texID)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.get_width(), image.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE,
                     datas)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glEnable(GL_TEXTURE_2D)
        return texID

    def place_textures(self):
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        for i_surface, surface in enumerate(self.surfaces):
            x = 0
            glNormal3fv(self.normals[i_surface])
            for i_vertex, vertex in enumerate(surface):
                x += 1
                glTexCoord2fv(self.textureCoordinates[i_vertex])
                glVertex3fv(self.verticies[vertex])
        glEnd()

        #glColor3fv(self.colors[0])
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verticies[vertex])
        glEnd()

    def translate(self, dx, dy, dz):
        self.verticies = [(x + dx, y + dy, z + dz) for (x, y, z) in self.verticies]



    def geodetic_to_ecef(self, lat, lon, h):
        a = 6378137.0
        b = 6356752.3142
        b = a
        f = (a - b) / a
        e_sq = f * (2 - f)

        # (lat, lon) in WSG-84 degrees
        # h in meters
        lamb = math.radians(lat)
        phi = math.radians(lon)
        s = math.sin(lamb)
        N = a / math.sqrt(1 - e_sq * s * s)

        sin_lambda = math.sin(lamb)
        cos_lambda = math.cos(lamb)
        sin_phi = math.sin(phi)
        cos_phi = math.cos(phi)

        x = (h + N) * cos_lambda * cos_phi
        y = (h + N) * cos_lambda * sin_phi
        z = (h + (1 - e_sq) * N) * sin_lambda

        xyz = (x / a, y / a, z / a)
        small = 0.00001
        return (0.0 if xyz[0] < small and xyz[0] > -small else xyz[0],
                0.0 if xyz[1] < small and xyz[1] > -small else xyz[1],
                0.0 if xyz[2] < small and xyz[2] > -small else xyz[2])

