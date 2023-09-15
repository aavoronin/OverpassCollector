class map_box_info:
    def __init__(self, bbox):
        self.bbox = bbox

    def bbox_str(self):
        return f"{self.bbox[0]},{self.bbox[1]},{self.bbox[2]},{self.bbox[3]}"

    def bbox_str_short(self):
        return f"{round(self.bbox[0], 2)},{round(self.bbox[1], 2)},{round(self.bbox[2], 2)},{round(self.bbox[3], 2)}"