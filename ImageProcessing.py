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


def generate_thought_balloon_by_text(texts: list):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2
    color = Color.BLACK
    thickness = 2
    LINE_SPACING = 8
    text_settings = []
    for text in texts:
        text = text.rstrip()
        (text_width, text_height), shift = cv2.getTextSize(text, font, font_scale, thickness)
        text_height += shift + LINE_SPACING
        text_settings.append(((text_width, text_height), shift, text))

    rect_height = sum([text_size[0][1] for text_size in text_settings]) + LINE_SPACING * (len(texts) - 1)
    rect_width = max(text_settings, key=lambda text_size: text_size[0][0])[0][0]
    text_rect = np.ones([rect_height, rect_width, 3], 'uint8') * 255

    cur_height = -LINE_SPACING
    for (text_width, text_height), shift, text in text_settings:
        cur_height += text_height
        cur_width = (rect_width - text_width) // 2
        cv2.putText(text_rect, text, (cur_width, cur_height), font, font_scale, color, thickness)

    half_rect_width = rect_width // 2
    half_rect_height = rect_height // 2
    ellipse_height_delta = rect_height // 4
    ellipse_points = [(half_rect_width, half_rect_height), (-half_rect_width, half_rect_height), (-half_rect_width,
                                                                                                  -half_rect_height),
                      (half_rect_width, -half_rect_height), (0, half_rect_height + ellipse_height_delta)]

    ellipse_points = np.array(ellipse_points)
    ellipse = cv2.fitEllipse(ellipse_points)
    return ellipse, text_rect


def overlay_img_in_top_right_frame_corner(frame, image):
    print('frame shape', frame.shape)
    print('image shape', image.shape)
    frame_height, frame_width, _ = frame.shape
    image_height, image_width, _ = image.shape
    assert image_height <= frame_height and image_width <= frame_width
    frame[:image_height, frame_width-image_width:] = image