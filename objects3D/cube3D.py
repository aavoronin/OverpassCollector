import math
from OpenGL.GL import *
from OpenGL.GLU import *
from objects3D.fig_3D_base import fig_3D_base

class cube_3D(fig_3D_base):
    def __init__(self):
        super().__init__()

    def translate(self, dx, dy, dz):
        self.verticies = [(x + dx, y + dy, z + dz) for (x, y, z) in self.verticies]

    def create_arrays(self):
        self.verticies = [
            (1, -1, -1),  # 0
            (1, 1, -1),  # 1
            (-1, 1, -1),  # 2
            (-1, -1, -1),  # 3
            (1, -1, 1),  # 4
            (1, 1, 1),  # 5
            (-1, -1, 1),  # 6
            (-1, 1, 1),  # 7
        ]

        self.textureCoordinates = ((0, 0), (0, 1), (1, 1), (1, 0))

        self.surfaces = [
            (0, 1, 2, 3),
            (3, 2, 7, 6),
            (6, 7, 5, 4),
            (4, 5, 1, 0),
            (1, 5, 7, 2),
            (4, 0, 3, 6),
        ]

        self.normals = [
            (0, 0, -1),  # surface 0
            (-1, 0, 0),  # surface 1
            (0, 0, 1),  # surface 2
            (1, 0, 0),  # surface 3
            (0, 1, 0),  # surface 4
            (0, -1, 0)  # surface 5
        ]

        self.colors = [
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
        ]

        self.edges = [
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
        ]





class cube_3D(fig_3D_base):
    def __init__(self):
        super().__init__()

    def create_arrays(self):
        self.verticies = [
            (1, -1, -1),  # 0
            (1, 1, -1),  # 1
            (-1, 1, -1),  # 2
            (-1, -1, -1),  # 3
            (1, -1, 1),  # 4
            (1, 1, 1),  # 5
            (-1, -1, 1),  # 6
            (-1, 1, 1),  # 7
        ]

        self.textureCoordinates = ((0, 0), (0, 1), (1, 1), (1, 0))

        self.surfaces = [
            (0, 1, 2, 3),
            (3, 2, 7, 6),
            (6, 7, 5, 4),
            (4, 5, 1, 0),
            (1, 5, 7, 2),
            (4, 0, 3, 6),
        ]

        self.normals = [
            (0, 0, -1),  # surface 0
            (-1, 0, 0),  # surface 1
            (0, 0, 1),  # surface 2
            (1, 0, 0),  # surface 3
            (0, 1, 0),  # surface 4
            (0, -1, 0)  # surface 5
        ]

        self.colors = [
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
        ]

        self.edges = [
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
        ]






class plane_surface_3D(fig_3D_base):
    def __init__(self, length, depth, height):
        super().__init__()
        self.length = length
        self.depth = depth
        self.height = height

    def create_arrays(self):
        self.verticies = [
            (+self.length, -self.depth, -self.height),  # 0
            (+self.length, +self.depth, -self.height),  # 1
            (-self.length, +self.depth, -self.height),  # 2
            (-self.length, -self.depth, -self.height),  # 3
            (+self.length, -self.depth, +self.height),  # 4
            (+self.length, +self.depth, +self.height),  # 5
            (-self.length, -self.depth, +self.height),  # 6
            (-self.length, +self.depth, +self.height),  # 7
        ]

        self.textureCoordinates = ((0, 0), (0, 1), (1, 1), (1, 0))

        self.surfaces = [
            (0, 1, 2, 3),
            (3, 2, 7, 6),
            (6, 7, 5, 4),
            (4, 5, 1, 0),
            (1, 5, 7, 2),
            (4, 0, 3, 6),
        ]

        self.normals = [
            (0, 0, -1),  # surface 0
            (-1, 0, 0),  # surface 1
            (0, 0, 1),  # surface 2
            (1, 0, 0),  # surface 3
            (0, 1, 0),  # surface 4
            (0, -1, 0)  # surface 5
        ]

        self.colors = [
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
        ]

        self.edges = [
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
        ]

lat_pole_gap = 0.0001
lat_pole_gap_180 = 180.0 - lat_pole_gap * 2

class globe_tile:
    def __init__(self, i_lat, i_lon, nlattitude, nlongittude, r):
        self.r = r
        self.nlattitude = nlattitude
        self.nlongittude = nlongittude
        self.i_lat = i_lat
        self.i_lon = i_lon
        self.i_lat1 = (i_lat + 1)
        self.i_lon1 = (i_lon + 1)
        self.min_lat = ((lat_pole_gap_180 * self.i_lat ) / (nlattitude) - 90.0 + lat_pole_gap)
        self.max_lat = ((lat_pole_gap_180 * self.i_lat1) / (nlattitude) - 90.0 + lat_pole_gap)
        self.min_lon = ((360.0 * self.i_lon ) / nlongittude - 180.0)
        self.max_lon = ((360.0 * self.i_lon1) / nlongittude - 180.0)

class globe_point:
    def __init__(self, i_lat, i_lon, nlattitude, nlongittude, r):
        self.nlattitude = nlattitude
        self.nlongittude = nlongittude
        self.i_lat = i_lat
        self.i_lon = i_lon
        self.lat = ((lat_pole_gap_180 * self.i_lat) / (nlattitude - 1) - 90.0)
        self.lon = ((360.0 * self.i_lon) / nlongittude - 180.0)
        self.r = r

    def __str__(self):
        return f'p{self.n}({self.lat}, {self.lon} {self.r})'

class ball_3D(fig_3D_base):
    def __init__(self, nlattitude=18, nlongittude=18, r=1):
        super().__init__()
        self.r = r
        self.nlattitude = nlattitude
        self.nlongittude = nlongittude

    def create_arrays(self):
        self.points = [globe_point(i_lat, i_lon, self.nlattitude + 1, self.nlongittude, self.r) for i_lon in range(self.nlongittude + 1) for i_lat in range(self.nlattitude + 1)]
        for i in range(len(self.points)):
            self.points[i].n = i
        #print(self.points)
        self.tiles = [globe_tile(i_lat, i_lon, self.nlattitude, self.nlongittude, self.r) for i_lon in range(self.nlongittude) for i_lat in range(self.nlattitude)]
        for i, t in enumerate(self.tiles):
            t.indexes = [-1,-1,-1,-1]
            for p in self.points:
                if t.i_lat == p.i_lat and t.i_lon == p.i_lon:
                    t.indexes[0] = p.n
                if t.i_lat == p.i_lat and t.i_lon1 == p.i_lon:
                    t.indexes[1] = p.n
                if t.i_lat1 == p.i_lat and t.i_lon1== p.i_lon:
                    t.indexes[2] = p.n
                if t.i_lat1 == p.i_lat and t.i_lon == p.i_lon:
                    t.indexes[3] = p.n
            if (t.indexes[2] == -1):
                pass

        self.verticies = [self.normalize(self.geodetic_to_ecef(p.lat, p.lon, self.r)) for p in self.points]
        self.verticies = [(self.r * v[0], self.r * v[1], self.r * v[2]) for v in self.verticies]

        self.textureCoordinates = ((0, 0), (0, 1), (1, 1), (1, 0))

        self.surfaces = [(t.indexes[0],t.indexes[1],t.indexes[2],t.indexes[3]) for t in self.tiles]

        #print(self.verticies)
        #print(self.surfaces)

        self.normals = [self.get_normal(s[0], s[1], s[2], s[3]) for s in self.surfaces]

        self.colors = [
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
        ]

        self.edges = [
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
        ]

    def get_normal(self, v0, v1, v2, v3):
        xyz = (
            (self.verticies[v0][0] + self.verticies[v1][0] + self.verticies[v2][0] + self.verticies[v3][0]) / 4.0, # x
            (self.verticies[v0][1] + self.verticies[v1][1] + self.verticies[v2][1] + self.verticies[v3][1]) / 4.0, # y
            (self.verticies[v0][2] + self.verticies[v1][2] + self.verticies[v2][2] + self.verticies[v3][2]) / 4.0  # z
        )
        if xyz[0] == 0.0 and xyz[1] == 0.0 and xyz[2] == 0.0:
            print(xyz)
        xyz = self.normalize(xyz)
        return xyz

    def normalize(self, xyz):
        r = math.sqrt(xyz[0] * xyz[0] + xyz[1] * xyz[1] + xyz[2] * xyz[2])
        xyz = (xyz[0] / r, xyz[1] / r, + xyz[2] / r)
        return xyz

    def place_textures(self):
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        for i_surface, surface in enumerate(self.surfaces):
            x = 0
            glNormal3fv(self.normals[i_surface])
            for i_vertex, vertex in enumerate(surface):
                x += 1
                point = self.points[vertex]
                x = ((point.nlongittude - point.i_lon) * 1.0) / point.nlongittude
                y = (point.i_lat * 1.0) / point.nlattitude
                glTexCoord2fv((x, y))
                #glTexCoord2fv(self.textureCoordinates[i_vertex])
                glVertex3fv(self.verticies[vertex])
        glEnd()

        #glColor3fv(self.colors[0])
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verticies[vertex])
        glEnd()



class sphrere(fig_3D_base):
    def __init__(self, nlattitude=18, nlongittude=18, r=1):
        super().__init__()
        self.r = r
        self.nlattitude = nlattitude
        self.nlongittude = nlongittude

    def create_arrays(self):
        self.points = [globe_point(i_lat, i_lon, self.nlattitude + 1, self.nlongittude, self.r) for i_lon in range(self.nlongittude + 1) for i_lat in range(self.nlattitude + 1)]
        for i in range(len(self.points)):
            self.points[i].n = i
        print(self.points)
        self.tiles = [globe_tile(i_lat, i_lon, self.nlattitude, self.nlongittude, self.r) for i_lon in range(self.nlongittude) for i_lat in range(self.nlattitude)]
        for t in self.tiles:
            t.indexes = [-1,-1,-1,-1]
            for p in self.points:
                if t.i_lat == p.i_lat and t.i_lon == p.i_lon:
                    t.indexes[0] = p.n
                if t.i_lat == p.i_lat and t.i_lon1 == p.i_lon:
                    t.indexes[1] = p.n
                if t.i_lat1 == p.i_lat and t.i_lon1== p.i_lon:
                    t.indexes[2] = p.n
                if t.i_lat1 == p.i_lat and t.i_lon == p.i_lon:
                    t.indexes[3] = p.n
            if (t.indexes[2] == -1):
                pass

        self.verticies = [self.normalize(self.geodetic_to_ecef(p.lat, p.lon, self.r)) for p in self.points]
        self.verticies = [(self.r * v[0], self.r * v[1], self.r * v[2]) for v in self.verticies]

        self.textureCoordinates = ((0, 0), (0, 1), (1, 1), (1, 0))

        self.surfaces = [(t.indexes[0],t.indexes[1],t.indexes[2],t.indexes[3]) for t in self.tiles]

        #print(self.verticies)
        #print(self.surfaces)

        self.normals = [self.get_normal(s[0], s[1], s[2], s[3]) for s in self.surfaces]

        self.colors = [
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
        ]

        self.edges = [
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
        ]

    def get_normal(self, v0, v1, v2, v3):
        xyz = (
            (self.verticies[v0][0] + self.verticies[v1][0] + self.verticies[v2][0] + self.verticies[v3][0]) / 4.0, # x
            (self.verticies[v0][1] + self.verticies[v1][1] + self.verticies[v2][1] + self.verticies[v3][1]) / 4.0, # y
            (self.verticies[v0][2] + self.verticies[v1][2] + self.verticies[v2][2] + self.verticies[v3][2]) / 4.0  # z
        )
        if xyz[0] == 0.0 and xyz[1] == 0.0 and xyz[2] == 0.0:
            print(xyz)
        xyz = self.normalize(xyz)
        return xyz

    def normalize(self, xyz):
        r = math.sqrt(xyz[0] * xyz[0] + xyz[1] * xyz[1] + xyz[2] * xyz[2])
        xyz = (xyz[0] / r, xyz[1] / r, + xyz[2] / r)
        return xyz

    def place_textures(self):

        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        for i_surface, surface in enumerate(self.surfaces):
            x = 0
            glNormal3fv(self.normals[i_surface])
            for i_vertex, vertex in enumerate(surface):
                x += 1
                point = self.points[vertex]
                x = ((point.nlongittude - point.i_lon) * 1.0) / point.nlongittude
                y = (point.i_lat * 1.0) / point.nlattitude
                glTexCoord2fv((x, y))
                #glTexCoord2fv(self.textureCoordinates[i_vertex])
                glVertex3fv(self.verticies[vertex])
        glEnd()

        #glColor3fv(self.colors[0])
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verticies[vertex])
        glEnd()


