class ColorHelper:
    @staticmethod
    def water_color_argb():
        return (147, 187, 226, 255)

    @staticmethod
    def defaultland_color_argb():
        return (255, 255, 255, 255)

    @staticmethod
    def get_continent_color(continent_name_en):
        continent_colors = {
            "North America": (255, 165, 0),  # Orange
            "South America": (255, 192, 203),  # Pink
            "Europe": (128, 0, 0),  # Red
            "Africa": (0, 128, 0),  # Green
            "Asia": (255, 255, 0),  # Yellow
            "Oceania": (165, 42, 42),  # Brown
            "Antarctica": (255, 255, 255)  # White
        }
        if continent_name_en in continent_colors:
            return continent_colors[continent_name_en]
        return (255, 255, 255)
