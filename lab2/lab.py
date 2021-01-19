#!/usr/bin/env python3
import math

from PIL import Image

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)


# COPIED FROM LAB1 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


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
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# VARIOUS FILTERS


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def color_filt(image):
        red, green, blue, result = [{"height": image["height"],
                                     "width": image["width"],
                                     "pixels": []} for _ in range(4)]

        for r, g, b in image["pixels"]:
            red["pixels"].append(r)
            green["pixels"].append(g)
            blue["pixels"].append(b)

        result["pixels"] = list(zip(filt(red)["pixels"], filt(green)[
                                "pixels"], filt(blue)["pixels"]))

        return result

    return color_filt


def make_blur_filter(n):

    def blur_filt(image):
        return blurred(image, n)

    return blur_filt


def make_sharpen_filter(n):

    def sharpen_filt(image):
        return sharpened(image, n)

    return sharpen_filt


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def cascade(image):
        for f in filters:
            image = f(image)

        return image

    return cascade


# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image.
    """
    result = {"height": image["height"],
              "width": image["width"],
              "pixels": image["pixels"].copy()}

    for _ in range(ncols):
        grey = greyscale_image_from_color_image(result)
        edges = compute_energy(grey)
        cem = cumulative_energy_map(edges)
        seam = minimum_energy_seam(cem)
        result = image_without_seam(result, seam)

    return result


# Optional Helper Functions for Seam Carving

def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    result = {"height": image["height"],
              "width": image["width"]}

    result["pixels"] = [round(0.299 * r + 0.587 * g + 0.114 * b)
                        for r, g, b in image["pixels"]]

    return result


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """

    return edges(grey)


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g. the output of the compute_energy function),
    computes a "cumulative energy map" as described in the lab 2 writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    result = {"height": energy["height"],
              "width": energy["width"],
              "pixels": []}

    for h in range(energy["height"]):
        for w in range(energy["width"]):
            val1 = get_pixel(energy, h, w)

            if h == 0:
                val2 = 0
            else:
                val2 = min(get_pixel(result, h - 1, w - 1),
                           get_pixel(result, h - 1, w),
                           get_pixel(result, h - 1, w + 1))

            result["pixels"].append(val1 + val2)

    return result


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    def append_min(part_row):
        min_val = 1e10

        for w in part_row:
            if w <= 0:
                w = 0
            elif w >= cem["width"]:
                w = cem["width"] - 1

            if get_pixel(cem, h, w) < min_val:
                min_val = get_pixel(cem, h, w)
                min_idx = (h, w)
        indices.append(min_idx)

        return min_idx

    indices = []

    for h in reversed(range(cem["height"])):
        # find minimum value of last row

        if h == cem["height"] - 1:
            min_idx = append_min(range(cem["width"]))
        else:
            # get adjacents
            adjs = [min_idx[1] + t for t in [-1, 0, 1]]
            min_idx = append_min(adjs)
    indices.reverse()

    return indices


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    result = {"height": image["height"],
              "width": image["width"] - 1,
              "pixels": []}

    count = 0

    for h in range(image["height"]):
        for w in range(image["width"]):
            if (h, w) not in seam:
                result["pixels"].append(get_pixel(image, h, w))
                count += 1

    return result


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES

#  Copied from lab1 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def load_greyscale_image(filename):
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


def save_greyscale_image(image, filename, mode='PNG'):
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
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size

        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
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
