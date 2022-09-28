"""Written by Élie Goudout for personnal use

The Zevent of 2022 took place from September 9 to September 11.
A "Zevent Place", inspired from /r/place was created. The notable addition to the original concept
is that every pixel had a "level", which could be increased via donation for a price corresponding
to its level.
I was curious to see which pixels were expensive, i.e. which zones were best "defended". This code
allows for fetching level infos from the server. Every pixel level had to be retrieved one by one
due to server-side limitation. Hence, since the canvas contains 490k pixels, I used aiohttp to
send concurrent requests and speed up the process. At the time of the event, the server was very
performant and I could retrieve all pixel level data in about 4 minutes. Since then, performance
has logically decreased since there's no need for as much bandwidth.

!! Security Warning !!
IMPORTANT: If you do use this code, bear in mind that an Authorization token will have to be used.
    Since it is a "Bearer" token, it needs NOT to be shared with or found by anyone!!


This code uses the following convention for x and y indices:
0-----------→ y
|
|
|
|
↓
x

Zevent Place's convention inverts x and y compared to this.
"""


import requests
import brotli # used to read responses from requests 
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import asyncio
import aiohttp
from tqdm import tqdm

base_url = "https://place.zevent.fr"
file = "/graphql"

headers = {
 'Host': 'place-api.zevent.fr',
 'Accept-Encoding': 'gzip, deflate, br',
 'content-type': 'application/json',
 'authorization': '', # READ SECURITY WARNING before filling in!
}

def check_auth(headers):
    """ Checks if user input the authorization key
    Args:
        headers: dict
    Returns:
        True or False accordingly
    """
    if ('authorization' not in headers) or not headers['authorization']:
        print("\n\nYou must add your session authorization key to headers['authorization'].\nYou can find it in dev mode with your browser, after having logged in at 'https://place.zevent.fr' and clicked on a pixel of the canvas. The key will be in the header of a POST request.\nDON'T FORGET to read the SECURITY WARNING at the top of this code snippet first!!\n\n")
        return False
    else:
        return True

async def fetch_pixel_level(pixel, session):
    """ Asynchronously fetches level for one pixel. Upon failure, retries endlessly.

    Args:
        pixel: A 2-tuple (x, y), coordinates on the canvas
        session: Instance of aiohttp.ClientSession

    Returns:
        (x, y, level): 3-tuple. x and y are integers. level should be, but not checked here.
    """
    x, y = pixel
    payload = { # got this from my web browser
        "operationName":"getPixelLevel",
        "variables":{"pixel":{'x':y, 'y':x}}, # inverted x and y due to convention
        "query":"query getPixelLevel($pixel: PixelUpgradeInput!) {getPixelLevel(pixel: $pixel) {x y level coloredBy upgradedBy __typename}}",
        }
    while True:
        tries = 0
        try:
            async with session.post(file, json=payload) as response:
                r = await response.json()
            return (x, y, int(r['data']['getPixelLevel']['level']))
        except Exception as e:
            tries += 1
            if (tries % 10 == 0):
                print(f"Pixel ({x},{y}): failed {n} times. Error: '{e}'\nRetrying...")
            time.sleep(.1)

async def get_level_data_concurrent(sector):
    """ Concurrently fetches data corresponding to the input sector.
        Useful infos: pawelmhm.github.io/asyncio/python/aiohttp/2016/04/22/asyncio-aiohttp.html

    Args:
        sector: A 4-tuple (x1, y1, x2, y2) delimiting a rectangle area in the canvas.
            x1 <= ix < x2
            y1 <= iy < y2
    Returns:
        data: array of np.int_, with data[x,y] corresponding to level of pixel (x1 + x, y1 + y)
    """
    x1, y1, x2, y2 = sector
    h, w = x2 - x1, y2 - y1 # height and width
    data = np.zeros((h, w), dtype=np.int_)
    pixels = [(x1 + x, y1 + y) for x, y in np.ndindex(h, w)] # list of pixels to fetch level from
    # Asynchronously fetch data
    async with aiohttp.ClientSession(base_url=base_url, headers=headers) as session:
        pixels_level_list = await asyncio.gather(*[fetch_pixel_level(pixel, session) for pixel in pixels])
    # Fill in the data matrix to return
    for x, y, level in pixels_level_list:
        try:
            data[x - x1, y - y1] = level
        except Exception as e:
            print(f"Problem on pixel '({x},{y})': level is '{level}'")
    return data

def is_valid(sector):
    """ Checks if the sector is consistent with the 700x700 Zevent Place canvas.

    Args:
        sector: A 4-tuple (x1, y1, x2, y2) delimiting a rectangle area in the canvas.
            x1 <= ix < x2
            y1 <= iy < y2
    Returns:
        True if the sector is valid, False otherwise.
    """
    max_x, max_y = 700, 700
    x1, y1, x2, y2 = sector
    if (x1,y1) in np.ndindex(x2,y2) and (x2,y2) in np.ndindex(max_x + 1, max_y + 1):
        return True
    else:
        print(f"Invalid sector '{sector}': should be inside the {max_x}x{max_y} canvas.")
        return False

def get_level_data(sector):
    """ Retrieves the level data in the sector from the 700x700 Zevent Place.
        A 700x700 canvas has 490k pixels.
        Since one request = one pixel (server limitation) and request->response takes ~.1 second,
        we send concurrent requests. For memory reason, we do this in batches of columns.
    Args:
        sector: A 4-tuple (x1, y1, x2, y2) delimiting the rectangle area to fetch.
            x1 <= ix < x2
            y1 <= iy < y2
    """
    # Returns no data if sector is invalid
    if not is_valid(sector):
        return np.zeros((1,1), dtype=np.int_)
    # Carry on
    max_conc_req = 10000 # somewhat arbitrary
    x1, y1, x2, y2 = sector
    h, w = x2 - x1, y2 - y1 # height and width
    num_col_batch = max_conc_req // h # max number of columns per batch
    num_batches = np.int_(np.ceil(w / num_col_batch))
    data = np.zeros((h, w), dtype=np.int_)
    if check_auth(headers):
        print(f"Sending {h*w} requests in {num_batches} batches")
        # loop over batches. Last batch is potentially incomplete
        for b in tqdm(range(num_batches)):
            y1b = y1 + b * num_col_batch
            y2b = min(y2, y1b + num_col_batch)
            sector_batch = (x1, y1b, x2, y2b)
            data_batch = asyncio.run(get_level_data_concurrent(sector_batch))
            data[:, (y1b - y1):(y2b - y1)] = data_batch
    return data

def plot_level_map_from_data(data, sector):
    """ Plots the level map

    Args:
        data: array-like of integers. Shape should be consistent with sector.
        sector: A 4-tuple (x1, y1, x2, y2) describing the rectangle area from the 700x700 canvas
            data corresponds to.
            x1 <= ix < x2
            y1 <= iy < y2
    """
    x1, y1, x2, y2 = sector
    max_level = np.amax(data)
    title = f"({x1},{y1}) → ({x2},{y2})\nMax: {max_level}"
    if max_level > 0: # else there's nothing but 0's. Nothing to show, go debug!
        plt.imshow(data, norm = LogNorm(), extent=[y1, y2, x2, x1])
        plt.colorbar()
        plt.title(title)
        plt.show()

def plot_level_map(sector):
    """ Retrieves the data with get_level_data and then plots the level map.

    Args:
        sector: A 4-tuple (x1, y1, x2, y2) delimiting rectangle area to plot from the canvas.
            x1 <= ix < x2
            y1 <= iy < y2
    """
    data = get_level_data(sector)
    plot_level_map_from_data(data, sector)

# Use example:
sector = (217, 231, 259, 273)
plot_level_map(sector)

