import cv2
import numpy as np
from Colors import Color

def overlay_image_on_frame_by_box(frame, image, box: tuple):
    # box - (tl_x, tl_y, br_x, br_y)
    half_img_height, half_img_width = [image.shape[:2][i] // 2 for i in range(2)]
    tr_point = [box[2], box[1]]
    # if image doesn't fit at the top
    if tr_point[1] < half_img_height:
        # we just maximize it up
        tr_point[1] = 0
    else:
        tr_point[1] -= half_img_height

    tr_point[0] -= half_img_width

    point = tr_point
    overlay_image_on_frame_by_tr_point(frame, image, point)

def overlay_image_on_frame_by_center_point(frame, image, point: tuple):
    # point - [x, y]
    # image.shape - (height, width, channels)
    half_img_height, half_img_width = [image.shape[:2][i] // 2 for i in range(2)]

    frame[point[1] - half_img_height:point[1] + half_img_height, point[0] - half_img_width:point[0] + half_img_width] = image

def overlay_image_on_frame_by_tr_point(frame, image, point: tuple):
    # point - [x, y]
    # image.shape - (height, width, channels)

    frame[point[1]:point[1] + image.shape[0], point[0]:point[0] + image.shape[1]] = image

def overlay_text_on_frame(frame, ellipse: list, text_rect: np.ndarray, box: tuple):
    tr_point = box[2], box[1]

    ellipse_radii = [int(size) for size in ellipse[1]]
    old_ellipse_pos = ellipse[0]
    new_ellipse_pos = old_ellipse_pos[0] + tr_point[0] + ellipse_radii[1] // 2,\
                    old_ellipse_pos[1] + tr_point[1]

    angle = ellipse[2]
    out_ellipse_radii = [axis + 20 for axis in ellipse_radii]
    ellipse = tuple([new_ellipse_pos, out_ellipse_radii, angle])
    cv2.ellipse(frame, ellipse, Color.BLACK, -1)
    ellipse = tuple([new_ellipse_pos, ellipse_radii, angle])
    cv2.ellipse(frame, ellipse, Color.WHITE, -1)

    ellipse_width, ellipse_height = ellipse_radii[1], ellipse_radii[0]
    rect_x_shift_in_ellipse = (ellipse_width - text_rect.shape[1]) // 2 + text_rect.shape[1] // 2
    rect_y_shift_in_ellipse = (ellipse_height - text_rect.shape[0] // 2) - text_rect.shape[0]
    new_point = [tr_point[0] + rect_x_shift_in_ellipse, tr_point[1] - rect_y_shift_in_ellipse]
    overlay_image_on_frame_by_center_point(frame, text_rect, new_point)


def draw_det_boxes(frame, boxes):
    for box in boxes:
        cv2.rectangle(frame, tuple(box[1][:2]), tuple(box[1][2:]), Color.YELLOW, 5)