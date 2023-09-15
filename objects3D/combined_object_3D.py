from objects3D.fig_3D_base import fig_3D_base


class combined_object_3D(fig_3D_base):
    def __init__(self):
        super().__init__()

    def add_first_object(self, obj_3D):
        self.verticies = obj_3D.verticies
        self.textureCoordinates = obj_3D.textureCoordinates
        self.surfaces = obj_3D.surfaces
        self.normals = obj_3D.normals
        self.colors = obj_3D.colors
        self.edges = obj_3D.edges

    def merge_next_object(self, obj_3D):
        start_i = len(self.verticies)
        self.verticies.extend(obj_3D.verticies)
        self.textureCoordinates.extend(obj_3D.textureCoordinates)
        self.surfaces.extend([[vertex_index + start_i for vertex_index in surface] for surface in obj_3D.surfaces])
        self.normals.extend(obj_3D.normals)
        self.colors.extend(obj_3D.colors) # T O D O what do we do with colors ?
        self.edges.extend([(edge[0] + start_i, edge[1] + start_i) for edge in obj_3D.edges])