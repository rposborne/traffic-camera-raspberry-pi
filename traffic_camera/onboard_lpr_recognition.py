from typing import Literal
import json
import os

from ultralytics import YOLO
import cv2

import easyocr

from traffic_camera.lpr_utils import read_license_plate

# Initialize the OCR reader
reader = easyocr.Reader(["en"], gpu=False)


ONBOARD_LPR = "onboard_lpr"
LPR_SERVICE = "lpr_service"
ONBOARD_WITH_FALLBACK = "onboard_with_fallback"

LPR_MODES = [ONBOARD_LPR, LPR_SERVICE, ONBOARD_LPR]

# load models
# Check if ncnn models exist
if not os.path.exists("yolo11n_ncnn_model"):
    coco_model = YOLO("yolo11n.pt")
    coco_model.export(format="ncnn")

if not os.path.exists("license_plate_detector_ncnn_model"):
    license_plate_detector = YOLO("license_plate_detector.pt")
    license_plate_detector.export(format="ncnn")


# get abs path to model
path_yolo = os.path.abspath("yolo11n_ncnn_model")
print(path_yolo)

ncnn_model = YOLO(path_yolo)

path_license_plate = os.path.abspath("license_plate_detector_ncnn_model")
print(path_license_plate)
ncnn_license_plate_detector = YOLO(path_license_plate)


def onboard_lpr_to_file(
    queue,
    e,
    mode: Literal["onboard_lpr", "lpr_service", "onboard_with_fallback"] = ONBOARD_LPR,
):
    while True:  # Runs daemon (background) process
        # Collect the data from the queue from move_files_to_path

        if not queue.empty() and e.is_set():
            files = queue.get()

            for file in files:
                try:
                    perform_local_lpr(file)
                except Exception as error:
                    print(f"Error processing file {file}: {error}")
                    continue
            e.clear()


def write_to_file(results, file):
    with open(file + ".json", "w") as f:
        json.dump(results, f)


def perform_local_lpr(file):
    # load image file
    # cap = cv2.VideoCapture('./sample.mp4')
    print(file)
    print(os.path.exists(file))
    image = cv2.imread(file)

    vehicles = [2, 3, 5, 7]

    results = {}
    # detect vehicles
    all_detections = ncnn_model(image)
    # import ipdb; ipdb.set_trace()
    detections = all_detections[0]

    # for detection in detections.boxes.data.tolist():
    #     x1, y1, x2, y2, score, class_id = detection
    #     if int(class_id) in vehicles:
    #         detections_.append([x1, y1, x2, y2, score])
    # print(detections)
    # track vehicles
    # track_ids = mot_tracker.update(np.asarray(detections_), [])
    # detect license plates

    license_plates = ncnn_license_plate_detector(image)[0]

    results = {"objects": []}
    for detection in detections.boxes.data.tolist():
        xcar1, ycar1, xcar2, ycar2, score, class_id = detection

        results["objects"].append(
            {
                "bbox": [xcar1, ycar1, xcar2, ycar2],
                "class_id": class_id,
                "score": score,
            }
        )

        if int(class_id) not in vehicles:
            continue

        car_id = float(xcar1 + ycar1 + xcar2 + ycar2 + class_id)

        for license_plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = license_plate

            # assign license plate to car
            # xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, np.asarray(detections_))

            # crop license plate
            license_plate_crop = image[int(y1) : int(y2), int(x1) : int(x2), :]

            # process license plate
            license_plate_crop_gray = cv2.cvtColor(
                license_plate_crop, cv2.COLOR_BGR2GRAY
            )
            _, license_plate_crop_thresh = cv2.threshold(
                license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV
            )

            # read license plate number
            license_plate_text, license_plate_text_score = read_license_plate(
                license_plate_crop_thresh
            )

            if license_plate_text is not None:
                results[car_id] = {
                    "car": {"bbox": [xcar1, ycar1, xcar2, ycar2]},
                    "license_plate": {
                        "bbox": [x1, y1, x2, y2],
                        "text": license_plate_text,
                        "bbox_score": score,
                        "text_score": license_plate_text_score,
                    },
                }

                print(results[car_id])

    write_to_file(results, file)


if __name__ == "__main__":
    perform_local_lpr("./test_lpr_image.jpg")
