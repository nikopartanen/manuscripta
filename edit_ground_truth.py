# These function handle the ground truth files in different ways

import xml.etree.cElementTree as ET

from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
import sklearn as sk
from skimage import filters
from statistics import mean

from mikatools import *

def load_image(path):
    image = Image.open(path)
    return(image)

def extract_line_array(pil_image, height, width, top, left):

    cropped_example = pil_image.crop((int(left), int(top), int(left) + int(width), int(top) + int(height)))

    cropped_example_bw = cropped_example.convert("L")
    
    image_array = np.array(cropped_example_bw)
    
    threshold_otsu = filters.threshold_otsu(image_array)

    image_array_binarized = binarize_array(image_array, threshold_otsu)
    
    return(image_array_binarized)

def binarize_array(numpy_array, threshold):
    """Binarize a numpy array."""
    for i in range(len(numpy_array)):
        for j in range(len(numpy_array[0])):
            if numpy_array[i][j] > threshold:
                numpy_array[i][j] = 255
            else:
                numpy_array[i][j] = 0
    return(numpy_array)

def get_bbox(points, top_adjustment = 60, bottom_adjustment = 20):

    bbox = {}

    w = []
    h = []

    for p in points.split(' '):

        w.append(int(p.split(',')[0]))
        h.append(int(p.split(',')[1]))

    bbox['bottom'] = int(mean(h)) + bottom_adjustment
    bbox['left'] = min(w)
    bbox['right'] = max(w)
    bbox['top'] = int(mean(h)) - top_adjustment
    bbox['width'] = bbox['right'] - bbox['left']
    bbox['height'] = top_adjustment + bottom_adjustment
    
    return bbox

def read_page(page_file):
    
    tree = ET.parse(page_file)
    root = tree.getroot()

    xmlns = {'page': '{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}'}
    
    data = []

    max_height = root.find('.//{page}Page'.format(**xmlns)).get('imageHeight')
    max_width = root.find('.//{page}Page'.format(**xmlns)).get('imageWidth')

    for block in root.iterfind('.//{page}TextRegion'.format(**xmlns)):
        
        block_id = block.get('id')

        for line in block.iterfind('.//{page}TextLine'.format(**xmlns)):

            content = {}

            content['baseline'] = line.find('./{page}Baseline'.format(**xmlns)).get('points')
            content["height"] = get_bbox(content['baseline'])['height']
            content["width"] = get_bbox(content['baseline'])['width']
            content["top"] = get_bbox(content['baseline'])['top']
            content["left"] = get_bbox(content['baseline'])['left']
            content["max_height"] = max_height
            content["max_width"] = max_width
            content["file_path"] = str(page_file)

            line_string = line.find('./{page}TextEquiv/{page}Unicode'.format(**xmlns)).text

            content["text"] = line_string
            
            data.append(content)
        
    return data

# Example
# This plots an image with line bounding boxes around it
# If the lines are alright, we can save them and their text 
# into files and train, for example, Calamari models

image = load_image("ground_truth/RU_NLR_ONL_3097_sel_-_page_68.tif")
page = read_page("ground_truth/RU_NLR_ONL_3097_sel_-_page_68.xml")

for line in page:
    
    draw = ImageDraw.Draw(image) 
    draw.rectangle((line['left'], line['top'], line['left'] + line['width'], line['top'] + line['height']), fill=None, outline=None, width=1)

# Ground truth example

output_dir = 'ground_truth_lines'

for file in Path("ground_truth").glob("*xml"):
    
    page = read_page(file)
    # depends from file format, of course
    image = load_image(file.with_suffix('.tif'))
    
    for line in page:
        
        try:
        
            line_array = extract_line_array(image,  line['height'], line['width'], line['top'], line['left'])

            output_path = f"{output_dir}/{Path(line['file_path']).stem}_{line['height']}_{line['width']}_{line['top']}_{line['left']}.png"

            image_from_array = Image.fromarray(line_array)
            image_from_array.save(output_path)

            text_file = open(Path(output_path).with_suffix('.gt.txt'), "w")
            text_file.write(line['text'])
            text_file.close()
        
        except:
            
            print(f'problem with {line}')

# The most common problem we encounter is that line has no text.
# There are surely better ways to skip or handle those. Anyway, 
# the images often have weird problems so monitoring this is good.

# Creating ground truth
# Here we want to end up with a directory structure:
# experiment/01/train
# experiment/01/test
# experiment/01/val
# And so on, so that it is reasonably easy to keep track of
# each experiment and data that was used

from sklearn.model_selection import train_test_split
import shutil

def generate_experiment(train, test, val, exp = '01'):
    
    Path(f"exp/{exp}/train").mkdir(parents=True, exist_ok=True)
    Path(f"exp/{exp}/test").mkdir(parents=True, exist_ok=True)
    Path(f"exp/{exp}/val").mkdir(parents=True, exist_ok=True)

    for file in train:

        basename = str(file.stem).replace('.gt', '')

        shutil.copy(src = str(file), dst = f"exp/{exp}/train/{basename}.gt.txt")
        shutil.copy(src = str(file).replace('gt.txt', 'png'), dst = f"exp/{exp}/train/{basename}.png")

    for file in test:

        basename = str(file.stem).replace('.gt', '')

        shutil.copy(src = str(file), dst = f"exp/{exp}/test/{basename}.gt.txt")
        shutil.copy(src = str(file).replace('gt.txt', 'png'), dst = f"exp/{exp}/test/{basename}.png")

    for file in val:

        basename = str(file.stem).replace('.gt', '')

        shutil.copy(src = str(file), dst = f"exp/{exp}/val/{basename}.gt.txt")
        shutil.copy(src = str(file).replace('gt.txt', 'png'), dst = f"exp/{exp}/val/{basename}.png")

# Example

# train_data = []

# for line in sorted(Path("ground_truth_lines/").rglob("*gt.txt")):
    
#    train_data.append(line)

# train, test = train_test_split(train_data, test_size=0.10, random_state=42)
# val, test = train_test_split(test, test_size=0.50, random_state=42)

# generate_experiment(train, test, val, exp = '01')
