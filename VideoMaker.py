import cv2




def overlay_image_on_frame(frame, image, point_on_frame: tuple):
    frame[point_on_frame[1]:point_on_frame[1] + image.shape[0],
    point_on_frame[0]:point_on_frame[0] + image.shape[1]] = image




