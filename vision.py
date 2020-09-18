import cv2
from mss import mss
from PIL import Image
import numpy as np

class Vision:
    def __init__(self, static_templates, monitor):
        def load_images(images):
            return { k: cv2.imread(v, 0) for (k, v) in images.items() }
        self.templates = { k: load_images(v) for (k, v) in static_templates.items() }
        self.monitor = monitor
        self.screen = mss()
        self.frame = None

    def _convert_rgb_to_bgr(self, img):
        return img[:, :, ::-1]

    def take_screenshot(self):
        sct_img = self.screen.grab(self.monitor)
        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
        img = np.array(img)
        img = self._convert_rgb_to_bgr(img)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img_gray

    def refresh_frame(self):
        self.frame = self.take_screenshot()

    def _match_template(self, img_grayscale, template, threshold=0.9):
        """
        Matches template image in a target grayscaled image
        """

        res = cv2.matchTemplate(img_grayscale, template, cv2.TM_CCOEFF_NORMED)
        matches = np.where(res >= threshold)
        return matches


    def find_template(self, state, name, image=None, threshold=0.9):
        if image is None:
            if self.frame is None:
                self.refresh_frame()

            image = self.frame

        return self._match_template(
            image,
            self.templates[state][name],
            threshold
        )
