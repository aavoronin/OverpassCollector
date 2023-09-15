"""

import io
import urllib.request
import random
from cairo import ImageSurface, FORMAT_ARGB32, Context
import mercantile

def test_pycairo():

    west = 100.393
    south = 50.986
    east = 111.182
    north = 56.559
    zoom = 5

    tiles = list(mercantile.tiles(west, south, east, north, zoom))

    tile_size = (256, 256)
    # создаем пустое изображение в которое как мозайку будем вставлять тайлы
    # для начала просто попробуем отобразить все четыре тайла в строчку
    map_image = ImageSurface(FORMAT_ARGB32, tile_size[0] * len(tiles), tile_size[1])

    # создаем контекст для рисования
    ctx = Context(map_image)

    for idx, t in enumerate(tiles):
        server = random.choice(['a', 'b', 'c'])  # у OSM три сервера, распределяем нагрузку
        url = 'http://{server}.tile.openstreetmap.org/{zoom}/{x}/{y}.png'.format(
            server=server,
            zoom=t.z,
            x=t.x,
            y=t.y
        )
        # запрашиваем изображение
        response = urllib.request.urlopen(url)

        # создаем cairo изображние
        img = ImageSurface.create_from_png(io.BytesIO(response.read()))

        # рисуем изображение, с правильным сдвигом по оси x
        ctx.set_source_surface(img, idx * tile_size[0], 0)
        ctx.paint()

    # сохраняем собраное изображение в файл
    with open("map.png", "wb") as f:
        map_image.write_to_png(f)


import io
import json
import urllib.request
import random
from cairo import ImageSurface, FORMAT_ARGB32, Context

import mercantile


def get_map(west, south, east, north, zoom):
    tiles = list(mercantile.tiles(west, south, east, north, zoom))

    min_x = min([t.x for t in tiles])
    min_y = min([t.y for t in tiles])
    max_x = max([t.x for t in tiles])
    max_y = max([t.y for t in tiles])

    tile_size = (256, 256)
    # создаем пустое изображение в которое как мозайку будем вставлять тайлы
    # для начала просто попробуем отобразить все четыре тайла в строчку
    map_image = ImageSurface(
        FORMAT_ARGB32,
        tile_size[0] * (max_x - min_x + 1),
        tile_size[1] * (max_y - min_y + 1)
    )

    ctx = Context(map_image)

    for t in tiles:
        server = random.choice(['a', 'b', 'c'])  # у OSM три сервера, распределяем нагрузку
        url = 'http://{server}.tile.openstreetmap.org/{zoom}/{x}/{y}.png'.format(
            server=server,
            zoom=t.z,
            x=t.x,
            y=t.y
        )
        response = urllib.request.urlopen(url)
        img = ImageSurface.create_from_png(io.BytesIO(response.read()))

        ctx.set_source_surface(
            img,
            (t.x - min_x) * tile_size[0],
            (t.y - min_y) * tile_size[0]
        )
        ctx.paint()

    # расчитываем коэффициенты
    bounds = {
        "left": min([mercantile.xy_bounds(t).left for t in tiles]),
        "right": max([mercantile.xy_bounds(t).right for t in tiles]),
        "bottom": min([mercantile.xy_bounds(t) .bottom for t in tiles]),
        "top": max([mercantile.xy_bounds(t).top for t in tiles]),
    }

    # коэффициенты скалирования по оси x и y
    kx = map_image.get_width() / (bounds['right'] - bounds['left'])
    ky = map_image.get_height() / (bounds['top'] - bounds['bottom'])

    # пересчитываем размеры по которым будем обрезать
    left_top = mercantile.xy(west, north)
    right_bottom = mercantile.xy(east, south)
    offset_left = (left_top[0] - bounds['left']) * kx
    offset_top = (bounds['top'] - left_top[1]) * ky
    offset_right = (bounds['right'] - right_bottom[0]) * kx
    offset_bottom = (right_bottom[1] - bounds['bottom']) * ky

    # обрезанное изображение
    map_image_clipped = ImageSurface(
        FORMAT_ARGB32,
        map_image.get_width() - int(offset_left + offset_right),
        map_image.get_height() - int(offset_top + offset_bottom),
    )

    # вставляем кусок исходного изображения
    ctx = Context(map_image_clipped)
    ctx.set_source_surface(map_image, -offset_left, -offset_top)
    ctx.paint()

    return map_image_clipped


west = 100.393
south = 50.986
east = 111.182
north = 56.559
zoom = 7

map_image = get_map(west, south, east, north, zoom)

# рассчитываем координаты углов в веб-меркаоторе
leftTop = mercantile.xy(west, north)
rightBottom = mercantile.xy(east, south)

# расчитываем коэффициенты
kx = map_image.get_width() / (rightBottom[0] - leftTop[0])
ky = map_image.get_height() / (rightBottom[1] - leftTop[1])

# загружаем координаты
with open("route.json") as f:
    route = json.load(f)
coordinates = route['routes'][0]['geometry']['coordinates']

# а теперь порисуем
context = Context(map_image)
for c in coordinates:
    # gps в web-mercator
    x, y = mercantile.xy(c[0], c[1])
    # переводим x, y в координаты изображения
    x = (x - leftTop[0]) * kx
    y = (y - leftTop[1]) * ky
    context.line_to(x, y)

# заливаем наш путь
context.set_source_rgba(1, 0, 0, 0.5)  # красный, полупрозрачный
context.set_line_width(10)  # ширина 10 пикселей
context.stroke()

# сохраняем результат
with open("map_with_route_clipped.png", "wb") as f:
    map_image.write_to_png(f)

"""