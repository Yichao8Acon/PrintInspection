import cv2 as cv
import numpy as np


def threshold(img, threshold_range):
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, thresh_img = cv.threshold(img_gray, threshold_range[0], threshold_range[1], cv.THRESH_BINARY)
    return thresh_img


def crop_roi(img, x, y, w, h):
    return img[y:y + h, x:x + w]


def rotate_image_full(image, angle):
    h, w = image.shape[:2]
    target_size = (image.shape[1], image.shape[0])
    # Calculate the center of the image
    center = (w // 2, h // 2)

    # Get the rotation matrix
    rotation_matrix = cv.getRotationMatrix2D(center, angle, 1.0)

    # Calculate the new bounding dimensions
    cos = np.abs(rotation_matrix[0, 0])
    sin = np.abs(rotation_matrix[0, 1])

    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # Adjust the rotation matrix to account for translation
    rotation_matrix[0, 2] += (new_w / 2) - center[0]
    rotation_matrix[1, 2] += (new_h / 2) - center[1]

    # Perform the rotation with the new bounds
    rotated_image = cv.warpAffine(image, rotation_matrix, (new_w, new_h))
    resized_image = cv.resize(rotated_image, target_size, interpolation=cv.INTER_LINEAR)
    return rotated_image


def find_black_white_black_transitions(binary_img, direction=0):
    transitions = []
    line = []
    search_range = 0
    height, width = binary_img.shape
    if direction == 0:
        line_pos = height // 2
        line = binary_img[line_pos]
        search_range = width
    elif direction == 1:
        line_pos = width // 2
        line = binary_img[:, line_pos]
        search_range = height

    in_black = False
    in_white = False
    start_white = None

    for x in range(search_range):
        pixel = line[x]

        if pixel == 0:  # Black pixel
            if not in_black:
                if in_white:
                    # Transition from white to black
                    end_white = x - 1
                    transitions.append(((start_white, line_pos), (end_white, line_pos)))
                    in_white = False
                in_black = True
        else:  # White pixel
            if in_black:
                # Transition from black to white
                start_white = x
                in_black = False
                in_white = True

    if direction == 1:
        # Swap x and y for vertical direction
        transitions = [((y, x), (end_y, end_x)) for ((x, y), (end_x, end_y)) in transitions]

    return transitions
