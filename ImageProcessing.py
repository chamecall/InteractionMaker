import cv2
import numpy as np
from Colors import Color

def overlay_image_on_frame(frame, image, point_on_frame: tuple):
    print(frame.shape)
    print(image.shape)
    print(point_on_frame)
    frame[point_on_frame[1]:point_on_frame[1] + image.shape[0],
    point_on_frame[0]:point_on_frame[0] + image.shape[1]] = image


def overlay_text_on_frame(frame, ellipse: list, text_rect: np.ndarray, point_on_frame: tuple):
    ellipse_radii = [int(size) for size in ellipse[1]]
    old_ellipse_pos = ellipse[0]
    new_ellipse_pose = [int(old_ellipse_pos[i] + point_on_frame[i] + ellipse_radii[::-1][i] // 2) for i in range(2)]

    angle = ellipse[2]
    out_ellipse_radii = [axis + 20 for axis in ellipse_radii]
    ellipse = tuple([new_ellipse_pose, out_ellipse_radii, angle])
    cv2.ellipse(frame, ellipse, Color.BLACK, -1)
    ellipse = tuple([new_ellipse_pose, ellipse_radii, angle])
    cv2.ellipse(frame, ellipse, Color.WHITE, -1)

    ellipse_width, ellipse_height = ellipse_radii[1], ellipse_radii[0]
    rect_x_shift_in_ellipse = (ellipse_width - text_rect.shape[1]) // 2
    rect_y_shift_in_ellipse = (ellipse_height - text_rect.shape[0]) // 2
    new_point = [point_on_frame[0] + rect_x_shift_in_ellipse, point_on_frame[1] + rect_y_shift_in_ellipse]
    overlay_image_on_frame(frame, text_rect, new_point)


def draw_det_boxes(frame, boxes):
    for box in boxes:
        bounding_box_size = box[1][2] - box[1][0], box[1][3] - box[1][1]
        cv2.rectangle(frame, tuple(box[1][:2]), tuple(box[1][2:]), 255, 2)