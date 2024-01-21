from PIL import Image, ImageDraw, ImageFont
class FontHelper():
    @staticmethod
    def get_label_font(font_size, lang):
        font = ImageFont.truetype('fonts\\TimesNewRomanRegular.ttf', font_size)
        return font