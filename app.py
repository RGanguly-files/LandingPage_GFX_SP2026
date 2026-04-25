import streamlit as st
import cv2
import numpy as np
from PIL import Image
import cv2.aruco as aruco

st.title("Castor Bean Estimator")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # --- LOAD IMAGE ---
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image_cv = cv2.imdecode(file_bytes, 1)

    image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
    st.image(image_rgb, caption="Uploaded Image", use_column_width=True)

    st.write("Image shape:", image_cv.shape)

    # --- MARKER DETECTION ---
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, parameters)

    corners, ids, rejected = detector.detectMarkers(gray)

    pixels_per_cm = None

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
        st.warning("No marker detected → scale unavailable")

    # --- BEAN SEGMENTATION ---
    hsv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2HSV)

    # Adjust these ranges based on your bean + tarp colors
    lower_beans = np.array([10, 50, 20])
    upper_beans = np.array([30, 255, 255])

    mask = cv2.inRange(hsv, lower_beans, upper_beans)

    kernel = np.ones((5, 5), np.uint8)
    mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)

    st.image(mask_clean, caption="Bean Segmentation Mask")

    bean_pixels = cv2.countNonZero(mask_clean)
    st.write("Bean area (pixels):", bean_pixels)

    bean_area_cm2 = None
    if pixels_per_cm:
        cm_per_pixel = 1 / pixels_per_cm
        bean_area_cm2 = bean_pixels * (cm_per_pixel ** 2)
        st.write("Bean area (cm²):", bean_area_cm2)
    else:
        st.warning("Cannot compute real area without marker")

    # --- STICK DETECTION ---
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    stick_mask = mask1 + mask2
    st.image(stick_mask, caption="Stick Mask")

    contours, _ = cv2.findContours(stick_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    depth_cm = None

    if contours and pixels_per_cm:
        largest = max(contours, key=cv2.contourArea)

        x, y, w, h = cv2.boundingRect(largest)
        st.write("Stick height (pixels):", h)

        image_box = image_cv.copy()
        cv2.rectangle(image_box, (x, y), (x + w, y + h), (0, 255, 0), 2)

        image_box = cv2.cvtColor(image_box, cv2.COLOR_BGR2RGB)
        st.image(image_box, caption="Detected Stick")

        depth_cm = h / pixels_per_cm
        st.write("Estimated depth (cm):", depth_cm)

    else:
        st.warning("Cannot estimate depth (missing stick or marker)")

    # --- VOLUME + WEIGHT ---
    if bean_area_cm2 and depth_cm:
        volume_cm3 = bean_area_cm2 * depth_cm

        # Placeholder density (you will calibrate this later)
        density = 0.6  # g/cm³ approx → adjust later

        weight_kg = (volume_cm3 * density) / 1000

        st.write("Estimated volume (cm³):", volume_cm3)
        st.write("Estimated weight (kg):", weight_kg)

    else:
        st.warning("Final weight cannot be computed yet")