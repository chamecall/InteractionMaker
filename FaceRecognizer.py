import face_recognition
import cv2

class FaceRecognizer:
    def __init__(self):
        pass

    def recognize_faces_on_image(self, image):
        # return in format [((l, t), (r, b)), ...]
        rev_image = image[:, :, ::-1]
        face_locations = face_recognition.face_locations(rev_image, number_of_times_to_upsample=0, model='cnn')
        ret_face_locations = []
        for top, right, bottom, left in face_locations:
            face_location = (left, top), (right, bottom)
            ret_face_locations.append(face_location)

        return ret_face_locations


