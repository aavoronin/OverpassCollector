import glfw
import cv2
import numpy
import numpy as np
from OpenGL.GL import glLight, glLightfv
from OpenGL.raw.GLUT import glutSwapBuffers, glutPostRedisplay, glutSolidSphere
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
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
from PIL import Image
from objects3D.video3D_base import video_3D_base


class video_3D_test(video_3D_base):

    def __init__(self):
        super().__init__()

    def loadTexture(self):
        textureSurface = pygame.image.load('textures\\wall.jpg')
        textureData = pygame.image.tostring(textureSurface, "RGB", 1)
        width = textureSurface.get_width()
        height = textureSurface.get_height()

        glEnable(GL_TEXTURE_2D)
        texid = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, texid)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        return texid

    def draw_cube(self, lines=False):
        if lines:
            glBegin(GL_LINES)
            for edge in self.edges:
                glColor3fv((1, 1, 1))
                for vertex in edge:
                    glVertex3fv(self.vertices[vertex])
            glEnd()
        else:
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0)
            glVertex3f(-1.0, -1.0, 1.0)
            glTexCoord2f(1.0, 0.0)
            glVertex3f(1.0, -1.0, 1.0)
            glTexCoord2f(1.0, 1.0)
            glVertex3f(1.0, 1.0, 1.0)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(-1.0, 1.0, 1.0)
            glTexCoord2f(1.0, 0.0)
            glVertex3f(-1.0, -1.0, -1.0)
            glTexCoord2f(1.0, 1.0)
            glVertex3f(-1.0, 1.0, -1.0)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(1.0, 1.0, -1.0)
            glTexCoord2f(0.0, 0.0)
            glVertex3f(1.0, -1.0, -1.0)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(-1.0, 1.0, -1.0)
            glTexCoord2f(0.0, 0.0)
            glVertex3f(-1.0, 1.0, 1.0)
            glTexCoord2f(1.0, 0.0)
            glVertex3f(1.0, 1.0, 1.0)
            glTexCoord2f(1.0, 1.0)
            glVertex3f(1.0, 1.0, -1.0)
            glTexCoord2f(1.0, 1.0)
            glVertex3f(-1.0, -1.0, -1.0)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(1.0, -1.0, -1.0)
            glTexCoord2f(0.0, 0.0)
            glVertex3f(1.0, -1.0, 1.0)
            glTexCoord2f(1.0, 0.0)
            glVertex3f(-1.0, -1.0, 1.0)
            glTexCoord2f(1.0, 0.0)
            glVertex3f(1.0, -1.0, -1.0)
            glTexCoord2f(1.0, 1.0)
            glVertex3f(1.0, 1.0, -1.0)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(1.0, 1.0, 1.0)
            glTexCoord2f(0.0, 0.0)
            glVertex3f(1.0, -1.0, 1.0)
            glTexCoord2f(0.0, 0.0)
            glVertex3f(-1.0, -1.0, -1.0)
            glTexCoord2f(1.0, 0.0)
            glVertex3f(-1.0, -1.0, 1.0)
            glTexCoord2f(1.0, 1.0)
            glVertex3f(-1.0, 1.0, 1.0)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(-1.0, 1.0, -1.0)
            glEnd()

    def init_scene(self):
        # https://www.youtube.com/watch?v=R4n4NyDG2hI
        self.verticies = (
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, -1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, -1, 1),
            (-1, 1, 1)
        )

        self.edges = (
            (0, 1),
            (0, 3),
            (0, 4),
            (2, 1),
            (2, 3),
            (2, 7),
            (6, 3),
            (6, 4),
            (6, 7),
            (5, 1),
            (5, 4),
            (5, 7)
        )

        # pygame.init()
        # display = (self.width, self.height)
        # pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

        # self.loadTexture()
        # gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        # glTranslatef(0.0, 0.0, -5)

        pygame.init()
        display = (self.width, self.height)
        screen = pygame.display.set_mode(
            display, pygame.DOUBLEBUF | pygame.OPENGL | pygame.OPENGLBLIT)

        self.loadTexture()

        gluPerspective(45, display[0] / display[1], 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)

    def Cube(self):
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verticies[vertex])
        glEnd()

    def iterate_scene(self, frame, el):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.Cube()
        pygame.display.flip()
        pygame.time.wait(1)
        glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE, array=frame)

        # im = np.frombuffer(im, np.uint8)
        # im.shape = self.width, self.height, 3

    def create_subframes(self):
        i = 0
        data_arr = self.get_data_array()
        self.init_scene()
        # frame = np.tile(np.array(self.background_color, dtype=np.uint8), (self.height, self.width, 1))
        # self.iterate_scene(frame, el)

        for el in data_arr:
            info = f'{i:5d} frame: {self.current_frame} time: {self.current_frame // self.FPS // 60:02d}:{(self.current_frame // self.FPS) % 60:02d}'
            print(info)
            if i > self.limit:
                break

            frame = np.tile(np.array(self.background_color, dtype=np.uint8), (self.height, self.width, 1))
            self.iterate_scene(frame, el)
            # image = cv2.imread(self.captured_frame_file_name)

            if i == 0:
                repeat = self.first_frames_delay
            else:
                repeat = 1
            for _ in range(0, repeat):
                self.video.write(frame)
                self.current_frame += 1
            i += 1

    def get_data_array(self):
        return range(1000)


'''
class video_3D_test2(video_3D_base):

    def __init__(self):
        super().__init__()
        self.init_ok = glfw.init()

    def init_scene(self):
        if not self.init_ok:
            raise Exception('glfw not initialized')

        self.window = glfw.create_window(720, 600, "Pyopengl Texturing Cube", None, None)

        if not self.window:
            glfw.terminate()
            return

        glfw.make_context_current(self.window)
        #https://github.com/totex/PyOpenGL_tutorials/blob/master/video_09_texturing_quad.py
        #https://codeloop.org/python-modern-opengl-texturing-rotating-cube/

        #        positions         colors          texture coords
        cube = [-0.5, -0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
                0.5, -0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
                0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
                -0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

                -0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
                0.5, -0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
                0.5, 0.5, -0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
                -0.5, 0.5, -0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

                0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
                0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
                0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
                0.5, -0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

                -0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
                -0.5, -0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
                -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
                -0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

                -0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
                0.5, -0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
                0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
                -0.5, -0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

                0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
                -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
                -0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
                0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0]

        # convert to 32bit float

        cube = np.array(cube, dtype=np.float32)

        indices = [0, 1, 2, 2, 3, 0,
                   4, 5, 6, 6, 7, 4,
                   8, 9, 10, 10, 11, 8,
                   12, 13, 14, 14, 15, 12,
                   16, 17, 18, 18, 19, 16,
                   20, 21, 22, 22, 23, 20]

        indices = np.array(indices, dtype=np.uint32)

        VERTEX_SHADER = """

                  #version 330

                  in vec3 position;
                  in vec3 color;
                  in vec2 InTexCoords;

                  out vec3 newColor;
                  out vec2 OutTexCoords;

                  uniform mat4 transform; 

                  void main() {

                    gl_Position = transform * vec4(position, 1.0f);
                   newColor = color;
                   OutTexCoords = InTexCoords;

                    }


              """

        FRAGMENT_SHADER = """
               #version 330

                in vec3 newColor;
                in vec2 OutTexCoords;

                out vec4 outColor;
                uniform sampler2D samplerTex;

               void main() {

                  outColor = texture(samplerTex, OutTexCoords);

               }

           """

        # Compile The Program and shaders

        self.shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
                                                  OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER))

        # Create Buffer object in gpu
        VBO = glGenBuffers(1)
        # Bind the buffer
        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER, cube.itemsize * len(cube), cube, GL_STATIC_DRAW)

        # Create EBO
        EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.itemsize * len(indices), indices, GL_STATIC_DRAW)

        # get the position from  shader
        position = glGetAttribLocation(self.shader, 'position')
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, cube.itemsize * 8, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        # get the color from  shader
        color = glGetAttribLocation(self.shader, 'color')
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, cube.itemsize * 8, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        texCoords = glGetAttribLocation(self.shader, "InTexCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, cube.itemsize * 8, ctypes.c_void_p(24))
        glEnableVertexAttribArray(texCoords)

        # Texture Creation
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        # Set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # Set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # load image
        image = Image.open("textures\\crate.jpg")
        img_data = np.array(list(image.getdata()), np.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glEnable(GL_TEXTURE_2D)

        glUseProgram(self.shader)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)

    def Cube(self):
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verticies[vertex])
        glEnd()

    def iterate_scene(self, frame, el):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        rot_x = pyrr.Matrix44.from_x_rotation(0.5 * glfw.get_time())
        rot_y = pyrr.Matrix44.from_y_rotation(0.8 * glfw.get_time())

        transformLoc = glGetUniformLocation(self.shader, "transform")
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, rot_x * rot_y)

        # Draw Cube

        glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)

        glfw.swap_buffers(self.window)

    def create_subframes(self):
        i = 0
        data_arr = self.get_data_array()
        self.init_scene()
        #frame = np.tile(np.array(self.background_color, dtype=np.uint8), (self.height, self.width, 1))
        #self.iterate_scene(frame, el)

        for el in data_arr:
            info = f'{i:5d} frame: {self.current_frame} time: {self.current_frame // self.FPS // 60:02d}:{(self.current_frame // self.FPS) % 60:02d}'
            print(info)
            if i > self.limit:
                break

            frame = np.tile(np.array(self.background_color, dtype=np.uint8), (self.height, self.width, 1))
            if glfw.window_should_close(self.window):
                break
            self.iterate_scene(frame, el)
            # image = cv2.imread(self.captured_frame_file_name)

            if i == 0:
                repeat = self.first_frames_delay
            else:
                repeat = 1
            for _ in range(0, repeat):
                self.video.write(frame)
                self.current_frame += 1
            i += 1
        glfw.terminate()

    def get_data_array(self):
        return range(1000)

'''


class video_3D_test3(video_3D_base):

    def __init__(self):
        super().__init__()
        self.init_ok = glfw.init()

    def init_scene(self):
        self.verticies = (
            (1, -1, -1),  # 0
            (1, 1, -1),  # 1
            (-1, 1, -1),  # 2
            (-1, -1, -1),  # 3
            (1, -1, 1),  # 4
            (1, 1, 1),  # 5
            (-1, -1, 1),  # 6
            (-1, 1, 1),  # 7
        )

        self.textureCoordinates = ((0, 0), (0, 1), (1, 1), (1, 0))

        self.surfaces = (
            (0, 1, 2, 3),
            (3, 2, 7, 6),
            (6, 7, 5, 4),
            (4, 5, 1, 0),
            (1, 5, 7, 2),
            (4, 0, 3, 6),
        )

        self.normals = [
            (0, 0, -1),  # surface 0
            (-1, 0, 0),  # surface 1
            (0, 0, 1),  # surface 2
            (1, 0, 0),  # surface 3
            (0, 1, 0),  # surface 4
            (0, -1, 0)  # surface 5
        ]

        self.colors = (
            (1, 1, 1),
            (0, 1, 0),
            (0, 0, 1),
            (0, 1, 0),
            (0, 0, 1),
            (1, 0, 1),
            (0, 1, 0),
            (1, 0, 1),
            (0, 1, 0),
            (0, 0, 1),
        )

        self.edges = (
            (0, 1),
            (0, 3),
            (0, 4),
            (2, 1),
            (2, 3),
            (2, 7),
            (6, 3),
            (6, 4),
            (6, 7),
            (5, 1),
            (5, 4),
            (5, 7),
        )

        pygame.init()
        display = (self.width, self.height)  # self.expanded_size
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        self.clock = pygame.time.Clock()

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        glTranslatef(0, 0, -5)

        # glLight(GL_LIGHT0, GL_POSITION,  (0, 0, 1, 0)) # directional light from the front
        glLight(GL_LIGHT0, GL_POSITION, (5, 5, 5, 1))  # point light from the left, top, front
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

        glEnable(GL_DEPTH_TEST)

        image = pygame.image.load('textures\\crate.jpg')
        datas = pygame.image.tostring(image, 'RGBA')
        texID = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texID)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.get_width(), image.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE,
                     datas)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        glEnable(GL_TEXTURE_2D)

    def Cube(self):
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        for i_surface, surface in enumerate(self.surfaces):
            x = 0
            glNormal3fv(self.normals[i_surface])
            for i_vertex, vertex in enumerate(surface):
                x += 1
                #
                glTexCoord2fv(self.textureCoordinates[i_vertex])
                glVertex3fv(self.verticies[vertex])
        glEnd()

        glColor3fv(self.colors[0])
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verticies[vertex])
        glEnd()

    def iterate_scene(self, frame, el):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glRotatef(1, 3, 1, 1)
        self.Cube()

        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)

        pygame.display.flip()
        self.clock.tick(60)
        glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE, array=frame)
        pass

    def create_subframes(self):
        i = 0
        data_arr = self.get_data_array()
        self.init_scene()
        # frame = np.tile(np.array(self.background_color, dtype=np.uint8), (self.height, self.width, 1))
        # self.iterate_scene(frame, el)

        for el in data_arr:
            info = f'{i:5d} frame: {self.current_frame} time: {self.current_frame // self.FPS // 60:02d}:{(self.current_frame // self.FPS) % 60:02d}'
            print(info)
            if i > self.limit:
                break

            # frame = np.tile(np.array(self.background_color, dtype=np.uint8), (self.expanded_size[0], self.expanded_size[1], 1))
            frame = np.tile(np.array(self.background_color, dtype=np.uint8), (self.height, self.width, 1))
            self.iterate_scene(frame, el)
            frame = frame[::-1, :, ::-1]  # flip y and flip colors
            # frame = cv2.resize(frame[:, :, [2, 1, 0]], (self.width, self.height), interpolation=cv2.INTER_AREA)

            if i == 0:
                repeat = self.first_frames_delay
            else:
                repeat = 1
            for _ in range(0, repeat):
                self.video.write(frame)
                self.current_frame += 1
            i += 1

    def get_data_array(self):
        return range(300)


class video_3D_test4(video_3D_base):

    def __init__(self):
        super().__init__()
        self.init_ok = glfw.init()

    def init_scene(self):

        self.combined_object = combined_object_3D()
        n_cubes = 4
        cube_shift = 2.5
        self.cubes = [cube_3D() for _ in range(n_cubes)]
        for i, cube in enumerate(self.cubes):
            cube.create_arrays()
            cube.translate(0, 0, i * cube_shift - (cube_shift * len(self.cubes)) / 2.0)
            self.combined_object.merge_next_object(cube)

        pygame.init()
        display = (self.width, self.height)  # self.expanded_size
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        self.clock = pygame.time.Clock()

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        glTranslatef(0, 0, -12)

        # glLight(GL_LIGHT0, GL_POSITION,  (0, 0, 1, 0)) # directional light from the front
        glLight(GL_LIGHT0, GL_POSITION, (5, 5, 5, 1))  # point light from the left, top, front
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

        glEnable(GL_DEPTH_TEST)

        self.combined_object.init_texture('textures\\crate.jpg')
        # self.cubes[0].init_texture('textures\\crate.jpg')

    def iterate_scene(self, frame, el):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glRotatef(1, 3, 1, 1)
        self.combined_object.place_textures()

        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)

        pygame.display.flip()
        self.clock.tick(60)
        glReadPixels(0, 0, self.width, self.height, GL_BGR, GL_UNSIGNED_BYTE, array=frame)
        pass

    def get_data_array(self):
        return range(300)


class video_3D_test5(video_3D_base):

    def __init__(self):
        super().__init__()
        self.init_ok = glfw.init()
        self.font10 = ImageFont.truetype("fonts\\timesbd.ttf", 10)
        image = self.create_image_number_grid(10, 6)
        cv2.imwrite("c:\\Py\\ScrapeWiki\\textures\\num_cells.png", image)
        pass

    def init_scene(self):

        self.object = plane_surface_3D(2, 1, 0.005)
        self.object.create_arrays()

        pygame.init()
        display = (self.width, self.height)  # self.expanded_size
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        self.clock = pygame.time.Clock()

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        glTranslatef(0, 0, -12)

        # glLight(GL_LIGHT0, GL_POSITION,  (0, 0, 1, 0)) # directional light from the front
        glLight(GL_LIGHT0, GL_POSITION, (5, 5, 5, 1))  # point light from the left, top, front
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

        glEnable(GL_DEPTH_TEST)

        self.object.init_texture("textures\\num_cells.png")
        # self.cubes[0].init_texture('textures\\crate.jpg')

    def iterate_scene(self, frame, el):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glRotatef(1, 3, 1, 1)
        self.object.place_textures()

        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)

        pygame.display.flip()
        self.clock.tick(60)
        glReadPixels(0, 0, self.width, self.height, GL_BGR, GL_UNSIGNED_BYTE, array=frame)
        pass

    def get_data_array(self):
        return range(300)

    def create_image_number_grid(self, width, height):
        cell_size = (64, 64)
        img_ar = np.zeros((height * cell_size[0], width * cell_size[1], 3), dtype=np.uint8)
        pli = Image.fromarray(img_ar)
        draw = ImageDraw.Draw(pli)
        for yy in range(height):
            for xx in range(width):
                n = yy * width + xx
                s = str(n)
                color = ((n % 2) * 255, ((n // 2) % 2) * 255, ((n // 4) % 2) * 255)
                draw.rectangle((cell_size[0] * xx, cell_size[1] * yy, cell_size[1], cell_size[0]), fill=color,
                               outline=(255, 255, 255))
                w0, h0 = draw.multiline_textsize(s, font=self.font10, spacing=0)
                draw.text(xy=(cell_size[0] // 2 - w0 // 2, cell_size[1] // 2 - h0 // 2), text=s,
                          font=self.font10, align='center', fill='black')
        return np.array(pli)


class video_3D_test6(video_3D_base):

    def __init__(self):
        super().__init__()
        self.init_ok = glfw.init()

    def init_scene(self):

        self.ball_3D = ball_3D(48, 96, 3)
        self.ball_3D.create_arrays()

        pygame.init()
        display = (self.width, self.height)  # self.expanded_size
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        self.clock = pygame.time.Clock()

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        # glTranslatef(0, 0, -12)
        glTranslatef(0, 0, -12)

        # glLight(GL_LIGHT0, GL_POSITION,  (+100, 0, 100, 0))
        glLight(GL_LIGHT0, GL_POSITION, (0, 0, 100, 0))

        # glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
        # glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

        glEnable(GL_DEPTH_TEST)

        # self.ball_3D.init_texture('textures\\crate.jpg')
        # self.ball_3D.init_texture('textures\\wall.jpg')
        self.ball_3D.init_texture('textures\\world.jpg')
        glRotatef(90, 1, 0, 0)
        glRotatef(-90, 0, 0, 1)

    def iterate_scene(self, frame, el):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # glRotatef(1, 3, 1, 1)
        glRotatef(1, 0, 0, 3)
        self.ball_3D.place_textures()

        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)

        pygame.display.flip()
        self.clock.tick(60)
        glReadPixels(0, 0, self.width, self.height, GL_BGR, GL_UNSIGNED_BYTE, array=frame)
        pass

    def get_data_array(self):
        return range(1000)


class video_3D_test7(video_3D_base):

    def __init__(self):
        super().__init__()
        self.init_ok = glfw.init()

    def init_video_params(self):
        super().init_video_params()
        # self.width = int(1280 * 2)
        # self.height = int(720 * 2)

    def init_scene(self):

        self.ball_3D = ball_3D(36, 72, 3)
        self.ball_3D.create_arrays()

        pygame.init()
        display = (self.width, self.height)  # self.expanded_size
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        self.clock = pygame.time.Clock()

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        # glTranslatef(0, 0, -12)
        glTranslatef(0, 0, -9)

        # glLight(GL_LIGHT0, GL_POSITION,  (+100, 0, 100, 0))
        glLight(GL_LIGHT0, GL_POSITION, (0, 0, 100, 0))

        # glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
        # glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

        glEnable(GL_DEPTH_TEST)

        # self.ball_3D.init_texture('textures\\crate.jpg')
        # self.ball_3D.init_texture('textures\\wall.jpg')
        # self.ball_3D.init_texture('textures\\world3.jpg')

        ot = osm_tiles()
        im = ot.get_world_image(3)
        im.save("image.png", 'png')
        self.ball_3D.init_texture('image.png')

        glRotatef(90, 1, 0, 0)
        glRotatef(-90, 0, 0, 1)
        glRotatef(45, 0, 0, 1)

    def iterate_scene(self, frame, el):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glRotatef(el[0], el[1], el[2], el[3])
        self.ball_3D.place_textures()

        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)

        pygame.display.flip()
        self.clock.tick(60)
        glReadPixels(0, 0, self.width, self.height, GL_BGR, GL_UNSIGNED_BYTE, array=frame)
        pass

    def post_process_frame(self, frame):
        frame1 = cv2.resize(frame, (self.video_width, self.video_height), interpolation=cv2.INTER_AREA)
        # frame1 = cv2.GaussianBlur(frame1, (1, 1), cv2.BORDER_DEFAULT)
        return frame1

    def get_data_array(self):
        a = np.concatenate(
            (
                [[1, 0, 0, 1] for _ in range(180)],
                [[1, 0, 1, 0] for _ in range(90)],
                [[1, 0, -1, 0] for _ in range(180)],
                [[1, 0, 1, 0] for _ in range(90)],
                [[1, 0, 0, 1] for _ in range(180)]
            ), axis=0)
        return a


class video_3D_test8(video_3D_base):

    def __init__(self):
        super().__init__()
        self.init_ok = glfw.init()
        self.speed = 2.0

    def init_video_params(self):
        super().init_video_params()
        self.FPS = 30

    def init_scene(self):

        tiles_power = 4
        factor = 2
        self.ball_3D = ball_3D(factor * (2 ** tiles_power), factor * (2 ** tiles_power), 3)
        self.ball_3D.create_arrays()

        pygame.init()
        display = (self.width, self.height)  # self.expanded_size
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        self.clock = pygame.time.Clock()

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        # glTranslatef(0, 0, -12)
        glTranslatef(0, 0, -9)

        # glLight(GL_LIGHT0, GL_POSITION,  (+100, 0, 100, 0))
        glLight(GL_LIGHT0, GL_POSITION, (0, 0, 100, 0))

        # glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
        # glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

        glEnable(GL_DEPTH_TEST)

        # self.ball_3D.init_texture('textures\\crate.jpg')
        # self.ball_3D.init_texture('textures\\wall.jpg')
        # self.ball_3D.init_texture('textures\\world3.jpg')

        ot = osm_tiles()
        im = ot.get_world_image(tiles_power)
        im.save("image.png", 'png')
        self.ball_3D.init_texture('image.png')
        self.texture_placed = False

        glRotatef(90, 1, 0, 0)
        glRotatef(-90, 0, 0, 1)
        glRotatef(45, 0, 0, 1)

    def iterate_scene(self, frame, el):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glRotatef(el[0], el[1], el[2], el[3])
        self.ball_3D.place_textures()

        # if not self.texture_placed:
        #    self.ball_3D.place_textures()
        #    self.texture_placed = True

        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)

        pygame.display.flip()
        # self.clock.tick(60)
        glReadPixels(0, 0, self.width, self.height, GL_BGR, GL_UNSIGNED_BYTE, array=frame)
        pass

    def post_process_frame(self, frame):
        frame1 = cv2.resize(frame, (self.video_width, self.video_height), interpolation=cv2.INTER_AREA)
        # frame1 = cv2.GaussianBlur(frame1, (1, 1), cv2.BORDER_DEFAULT)
        return frame1

    def get_data_array(self):
        a = np.concatenate(
            (
                [[1 / self.speed, 0, 0, 1] for _ in range(int(180 * self.speed))],
                [[1 / self.speed, 1, 1, 0] for _ in range(int(120 * self.speed))],
                [[1 / self.speed, -1, -1, 0] for _ in range(int(240 * self.speed))],
                [[1 / self.speed, 1, 1, 0] for _ in range(int(120 * self.speed))],
                [[1 / self.speed, 0, 0, 1] for _ in range(int(180 * self.speed))]
            ), axis=0)
        return a


class video_3D_test9(video_3D_base):

    def __init__(self):
        super().__init__()
        self.init_ok = glfw.init()
        self.speed = 1.0

    def init_video_params(self):
        super().init_video_params()
        factor = 2
        self.width = int(1920 * factor)
        self.height = int(1080 * factor)
        self.video_width = self.width // factor
        self.video_height = self.height // factor
        self.FPS = 60

    def init_scene(self):

        tiles_power = 3
        factor = 2
        self.ball_3D = ball_3D(factor * (2 ** tiles_power), factor * (2 ** tiles_power), 3)
        self.ball_3D.create_arrays()
        pygame.init()
        display = (self.width, self.height)  # self.expanded_size
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        self.clock = pygame.time.Clock()

        ot = osm_tiles()
        im = ot.get_world_image(tiles_power)
        im.save("image.png", 'png')
        # self.ball_3D.init_texture('image.png')

        self.texture = self.read_texture("image.png", flip_x=True)
        self.sphere_d = int(self.height * 0.8)

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        glTranslatef(0, 0, -9)
        glLight(GL_LIGHT0, GL_POSITION, (0, 0, self.sphere_d * -5, 0))
        glEnable(GL_DEPTH_TEST)

        glRotatef(90, 1, 0, 0)
        glRotatef(-90, 0, 0, 1)
        glRotatef(45, 0, 0, 1)
        glScaled(3, 3, 3)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

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

        glRotatef(el[0], el[1], el[2], el[3])

        # Creates Sphere and wraps texture
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        qobj = gluNewQuadric()
        gluQuadricTexture(qobj, GL_TRUE)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        gluSphere(qobj, 1, self.sphere_d, self.sphere_d)
        gluDeleteQuadric(qobj)
        glDisable(GL_TEXTURE_2D)

        # Displays pygame window
        pygame.display.flip()
        pygame.time.wait(10)

        # self.clock.tick(60)
        glReadPixels(0, 0, self.width, self.height, GL_BGR, GL_UNSIGNED_BYTE, array=frame)
        pass

    def read_texture(self, filename, flip_x=False, flip_y=False):

        img = Image.open(filename)
        img_data = numpy.array(list(img.getdata()), numpy.int8)
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



