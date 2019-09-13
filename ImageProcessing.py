import cv2

def overlay_image_on_frame(frame, image, point_on_frame: tuple):
    frame[point_on_frame[1]:point_on_frame[1] + image.shape[0],
    point_on_frame[0]:point_on_frame[0] + image.shape[1]] = image


def overlay_text_on_frame(frame, text: str, point_on_frame: tuple):
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 3
    color = (255, 0, 0)
    thickness = 2
    cv2.putText(frame, text, point_on_frame, font, fontScale, color, thickness, cv2.LINE_AA)

