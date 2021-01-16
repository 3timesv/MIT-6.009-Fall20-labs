#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y):
    """
    Given an image representation and x and y coordinates,
    it returns the pixel value at given coordinates
    """

    if x < 0:
        x = 0
    elif x >= image["height"]:
        x = image["height"] - 1

    if y < 0:
        y = 0
    elif y >= image["width"]:
        y = image["width"] - 1

    return image['pixels'][x * image["width"] + y]


def set_pixel(image, c):
    """
    Given an image representation and pixel value 'c',
    it appends that pixel value to image.
    """
    image['pixels'].append(c)


def apply_per_pixel(image, func):
    """
    Apply given 'func' to every pixel of 'image'
    """
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
    }

    for x in range(image['height']):
        for y in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, newcolor)

    return result


def inverted(image):
    """
    Invert the pixels of image i.e do (255 - pixel)
    """

    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS

def correlate(image, kernel):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    kernel : [k0, k1, k2, ... , k(n*n)] ( kernel of shape n*n )
    """
    result = image.copy()
    result["pixels"] = []

    kernel_len = int(len(kernel)**(1/2))
    kernel_len_half = kernel_len // 2

    for x in range(image["height"]):
        for y in range(image["width"]):
            o = 0

            for h in range(kernel_len):
                for w in range(kernel_len):
                    o += get_pixel(image, x + h - kernel_len_half, y + w - kernel_len_half) * \
                        kernel[h * kernel_len + w]

            print("x", x, "y", y, "o", o)
            result["pixels"].append(o)

    return result


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    result = image.copy()
    result["pixels"] = []

    for pixel in image["pixels"]:

        pixel = round(pixel)

        if pixel > 255:
            pixel = 255
        elif pixel < 0:
            pixel = 0

        result["pixels"].append(pixel)

    return result


# FILTERS

def blurred(image, n, clip_and_round=True):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    def get_box_blur(n):
        return [1/(n*n)] * n*n

    kernel = get_box_blur(n)

    # then compute the correlation of the input image with that kernel
    correlated = correlate(image, kernel)

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.

    if clip_and_round:
        return round_and_clip_image(correlated)

    return correlated


def sharpened(image, n):
    """
    Given image and kernel size 'n', apply unsharp mask to it,
    and return new sharpened image without mutating input image.
    """
    blurred_image = blurred(image, n, False)

    sharpened_image = image.copy()

    zipped_i_b = zip(image["pixels"], blurred_image["pixels"])
    sharpened_image["pixels"] = [2*i - b for i, b in zipped_i_b]

    return round_and_clip_image(sharpened_image)


def edges(image):
    """
    Apply Sobel filter to given image, and return the resulting image,
    do not modify input image.
    """

    kernel_x = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
    kernel_y = [-1, -2, -1, 0, 0, 0, 1, 2, 1]

    out_x = correlate(image, kernel_x)
    out_y = correlate(image, kernel_y)

    out_xy = {"height": image["height"],
              "width": image["width"],
              "pixels": []}

    out_xy["pixels"] = [(x**2 + y**2)**(1/2)
                        for x, y in zip(out_x["pixels"], out_y["pixels"])]

    return round_and_clip_image(out_xy)

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES


def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()

        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size

        return {'height': h, 'width': w, 'pixels': pixels}


def save_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])

    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    pass
