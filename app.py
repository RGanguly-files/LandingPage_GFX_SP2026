import streamlit as st
import cv2
import numpy as np
from PIL import Image
import cv2.aruco as aruco

st.title("Castor Bean Estimator")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image_cv = cv2.imdecode(file_bytes, 1)

    image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
    st.image(image_rgb, caption="Uploaded Image", use_column_width=True)

    st.write("Image shape:", image_cv.shape)

    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, parameters)

    corners, ids, rejected = detector.detectMarkers(gray)

    if ids is not None:
        st.write("Marker detected!")

        image_marked = image_cv.copy()
        aruco.drawDetectedMarkers(image_marked, corners, ids)

        image_marked = cv2.cvtColor(image_marked, cv2.COLOR_BGR2RGB)
        st.image(image_marked, caption="Detected Marker")

        marker_corners = corners[0][0]
        width_pixels = np.linalg.norm(marker_corners[0] - marker_corners[1])

        st.write("Marker width in pixels:", width_pixels)

        pixels_per_cm = width_pixels / 10.16
        st.write("Pixels per cm:", pixels_per_cm)

    else:
        st.warning("No marker detected")