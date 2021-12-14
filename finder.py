#!/usr/bin/env python3

# import the necessary packages
import numpy as np
import imutils
import cv2

import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import urllib.request


template = None
TEMPLATE_PATH = "templates/template.png"

# Check image for match
def check_image(url):
    global template
    if template is None:
        template = cv2.imread(TEMPLATE_PATH)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template = cv2.Canny(template, 50, 200)
        print("Template created")
    (tH, tW) = template.shape[:2]
    
    # https://stackoverflow.com/questions/13329445/how-to-read-image-from-in-memory-buffer-stringio-or-from-url-with-opencv-pytho
    def get_opencv_img_from_buffer(buffer, flags):
        bytes_as_np_array = np.frombuffer(buffer.read(), dtype=np.uint8)
        return cv2.imdecode(bytes_as_np_array, flags)

    def get_opencv_img_from_url(url, flags):
        req = urllib.request.Request(url)
        return get_opencv_img_from_buffer(urllib.request.urlopen(req), flags)

    # image = cv2.imread(imagePath)
    image = imutils.url_to_image(url)
    # image = get_opencv_img_from_url(url, None)
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except Exception:
        # print(f"Couldnt get image from {url}")
        return False

    found = None
    # loop over the scales of the image
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        # resize the image according to the scale, and keep track
        # of the ratio of the resizing
        resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
        r = gray.shape[1] / float(resized.shape[1])
        # if the resized image is smaller than the template, then break
        # from the loop
        if resized.shape[0] < tH or resized.shape[1] < tW:
            break

        # detect edges in the resized, grayscale image and apply template
        # matching to find the template in the image
        edged = cv2.Canny(resized, 50, 200)
        result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
        minVal,maxVal,minLoc,maxLoc = cv2.minMaxLoc(result)

        # if we have found a new maximum correlation value, then update
        # the bookkeeping variable
        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)
    # unpack the bookkeeping variable and compute the (x, y) coordinates
    # of the bounding box based on the resized ratio
    if not found:
        return False
    else:
        (_, maxLoc, r) = found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
        # draw a bounding box around the detected result and display the image
        cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
        cv2.imwrite("out/Image.png", image)
        # cv2.waitKey(0)
        return True

# Get images
# https://towardsdatascience.com/image-scraping-with-python-a96feda8af2d
def fetch_image_urls(max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)    
    
    # load the page
    wd.get("https://opensea.io/assets?search[chains][0]=MATIC&search[sortAscending]=false&search[sortBy]=CREATED_DATE")

    thumbnail_results = []
    imglinks = {}
    image_count = 0
    results_start = 0
    links = []
    results = []
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results += wd.find_elements_by_tag_name('article')
        number_results = len(thumbnail_results)
        
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        
        for img in thumbnail_results[results_start:number_results]:
            try:
                # extract ref
                href = ""          
                tag = img.find_element_by_tag_name('a')
                if tag and tag.get_attribute('href'):
                    href = tag.get_attribute('href')

                # extract image urls  
                if href:
                    actual_image = img.find_element_by_class_name('Image--image')
                    if actual_image and actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                        imglinks[actual_image.get_attribute('src')] = href
                        links.append(actual_image.get_attribute('src'))
            except Exception:
                # Just keep swimming
                pass

            image_count = len(imglinks)

            if len(imglinks) >= max_links_to_fetch:
                print(f"Found: {len(imglinks)} image links, done!")
                break
        else:
            print("Found:", len(imglinks), "image links, checking then looking for more ...")
            # Scan collected images
            for link in links:
                if check_image(link):
                    print(link, imglinks[link])
                    results.append((link, imglinks[link]))

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return results


options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

links = fetch_image_urls(10000, driver, 15)
driver.quit()

print(links)