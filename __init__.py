#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2021 Grant Hadlich
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE. 
from bs4 import BeautifulSoup

import requests
import os
from urllib.request import urlretrieve

def download_files(base_url, destination_folder):
    """
    Downloads all images from a given URL.

    Parameters
    ----------
    base_url : str
        The base URL to download from.
    destination_folder : str
        The folder to save the images to.

    Returns
    -------
    count : int
        The number of images downloaded.
    suffix : str
        The last part of the image name.
    """
    os.makedirs(destination_folder, exist_ok=True)

    # Make the base url is complete
    if base_url[-1] != "/":
        base_url += "/"

    # somehow requests is caching, doing with wget instead
    # headers = { 
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
    # 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    # 'Accept-Language' : 'en-US,en;q=0.5', 
    # 'Accept-Encoding' : 'gzip', 
    # 'DNT' : '1', # Do Not Track Request Header 
    # 'Connection' : 'close',
    # 'Cache-Control' : 'private, max-age=0, no-cache'}

    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 YaBrowser/19.6.1.153 Yowser/2.5 Safari/537.36",
    #     "Cache-Control": "no-cache, max-age=0",  # disable caching
    # }

    # # Setup Requests
    # r  = requests.get(base_url, headers=headers)
    # data = r.text

    destination_index = os.path.join(destination_folder, "index.html")

    os.system(f"wget --no-cache --no-cookies -O {destination_index} -q {base_url}")

    if (os.path.exists(destination_index) == False):
        return 0, ""

    data = ""

    with open(destination_index,'r') as file:
        data = file.read()
 
    soup = BeautifulSoup(data, features="lxml")

    # Keep track of number of images downloaded and last name
    count = 0
    image = ""

    image_list = []

    # Collect all relevant links
    for link in soup.find_all('a'):
        image = link.get('href')
        if (".gif" in image or ".png" in image or ".jpg" in image):
            # print(base_url + image)
            image_list.append(image)

    # Retreive the images
    for image in image_list:
        try:
            save_path = os.path.abspath(os.path.join(destination_folder, image))
            url = base_url + image
            if (os.path.exists(save_path) == False):
                urlretrieve(url, save_path)
            count += 1
        except:
            #print(f"Failed: {base_url + image}")
            pass

    if (len(image_list) > 0):
        suffix = image_list[0][-4:]
    else:
        suffix = ""

    return count, suffix

def download_images_and_create_animation(base_url, destination_folder, output_filename, framerate=30, hold_last_frame_duration_s=0):
    """
    Downloads images from a given URL and creates an animation from them.

    Parameters
    ----------
    base_url : str
        The URL to download images from.
    destination_folder : str
        The folder to download the images to.
    output_filename : str
        The name of the output file.
    framerate : int, optional
        The framerate of the animation.
    hold_last_frame_duration_s : int, optional
        The duration to hold the last frame of the animation.

    Returns
    -------
    animation_path : str
        The path to the animation.
    """

    count, suffix = download_files(base_url, destination_folder)

    # If there were more than two images, attempt to create an animation
    if (count > 1):
        images_path = os.path.abspath(os.path.join(destination_folder, "*"+suffix))
        animation_path = os.path.abspath(os.path.join(destination_folder, output_filename))
        if hold_last_frame_duration_s > 0:
            hold = f"-vf tpad=stop_mode=clone:stop_duration={hold_last_frame_duration_s}"
        else:
            hold = ""
        try:
            _ = os.system(f"ffmpeg -y -hide_banner -loglevel error -framerate {framerate} -pattern_type glob -i '{images_path}' -c:v libx264 -pix_fmt yuv420p {hold} {animation_path}")
            return animation_path
        except:
            return None

    return None

if __name__ == "__main__":
    # base_url = "https://services.swpc.noaa.gov/images/animations/lasco-c3/lasco/"
    # destination_folder = "./animation/lasco-c3/2021-09-12"
    # output_filename = "animation.mp4"
    # framerate = 30
    # download_images_and_create_animation(base_url, destination_folder, output_filename, framerate=framerate)

    # base_url = "https://services.swpc.noaa.gov/images/animations/ctipe/tec/"
    # destination_folder = "./animation/electrons/2021-09-12"
    # output_filename = "animation.mp4"
    # framerate = 30
    # download_images_and_create_animation(base_url, destination_folder, output_filename, framerate=framerate, hold_last_frame_duration_s=3)

    # base_url = "https://services.swpc.noaa.gov/images/animations/suvi/secondary/304/"
    # destination_folder = "./animation/sun/2021-09-12"
    # output_filename = "animation.mp4"
    # framerate = 30
    # download_images_and_create_animation(base_url, destination_folder, output_filename, framerate=framerate)

    base_url = "https://services.swpc.noaa.gov/images/animations/ovation/north/"
    destination_folder = "./animation/aurora/2021-09-17"
    output_filename = "animation.mp4"
    framerate = 60
    download_images_and_create_animation(base_url, destination_folder, output_filename, framerate=framerate, hold_last_frame_duration_s=3)
