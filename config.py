import os
import logging

def strip_ext(filename):
    base = os.path.basename(filename)
    return os.path.splitext(base)[0]

def load_images_from_directory(directory):
    return { strip_ext(e): e.path for e in os.scandir(directory) if e.is_file() }

states = [ e for e in os.scandir('assets/images') if e.is_dir() ]
static_templates = { d.name: load_images_from_directory(d) for d in states }
logging.debug('Loaded static assets: {}'.format(static_templates))

monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
