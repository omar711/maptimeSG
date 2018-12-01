"""
    Logic for converting between lat/lon, pixel coordinates, and quadkeys.
    Based on documentation at: https://msdn.microsoft.com/en-us/library/bb259689.aspx?f=255&MSPPError=-2147217396
"""

from math import floor, log, pi, pow, sin

EARTH_RADIUS = 6378137;
MIN_LATITUDE = -85.05112878;
MAX_LATITUDE = 85.05112878;
MIN_LONGITUDE = -180;
MAX_LONGITUDE = 180;

def clip(value, min_value, max_value):
    return min(max(value, min_value), max_value)


def map_size(level_of_detail):
    return pow(2, level_of_detail)


def lat_lon_to_pixel_xy(latitude, longitude, level_of_detail):
    latitude = clip(latitude, MIN_LATITUDE, MAX_LATITUDE)
    longitude = clip(longitude, MIN_LONGITUDE, MAX_LONGITUDE)

    pixel_size = 256 * map_size(level_of_detail)

    x = (longitude + 180) / 360 * pixel_size; 
    sinLatitude = sin(latitude * pi / 180)
    y = (0.5 - log((1 + sinLatitude) / (1 - sinLatitude)) / (4 * pi)) * pixel_size

    pixel_x = int(clip(x + 0.5, 0, pixel_size - 1))
    pixel_y = int(clip(y + 0.5, 0, pixel_size - 1))

    return (pixel_x, pixel_y)


def pixel_xy_to_tile_xy(pixel_x, pixel_y):
    tile_x = floor(pixel_x / 256)
    tile_y = floor(pixel_y / 256)
    return (tile_x, tile_y)


def tile_xy_to_quadkey(tile_x, tile_y, level_of_detail):
    quadkey = ""
    for i in reversed(range(level_of_detail)):
        digit = 0
        mask = 1 << i

        if (tile_x & mask) != 0:
            digit = digit + 1

        if (tile_y & mask) != 0:
            digit = digit + 2

        quadkey = quadkey + str(digit)
        
    return quadkey
