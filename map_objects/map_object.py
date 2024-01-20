class map_object:
    def __init__(self):
        self.label = None
        self.bbox = None

    def load_geometry(self):
        pass

    def init_bbox(self):
        pass

    def init_fill_info(self):
        pass

    def draw_on_globe_texture(self):
        pass

class mo_all_world(map_object):
    def __init__(self):
        super().__init__()

class mo_global_land(map_object):
    def __init__(self):
        super().__init__()

class mo_continent(map_object):
    def __init__(self, continent):
        super().__init__()

class mo_country(map_object):
    def __init__(self, country):
        super().__init__()
