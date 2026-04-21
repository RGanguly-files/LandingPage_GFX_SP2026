import streamlit as st
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Castor Bean Weight Estimator", layout="centered")

# --- Session State Management ---
# We use this to store harvest tags "in-memory" for the prototype
if 'harvests' not in st.session_state:
    st.session_state.harvests = []

def add_harvest(name):
    if name and name not in [h['name'] for h in st.session_state.harvests]:
        st.session_state.harvests.append({
            "name": name,
            "created_at": datetime.now()
        })

# --- UI Header ---
st.title("🌱 Castor Bean Weight Estimator")
st.markdown("""
Upload photos of beans on a flat surface with your **reference marker** and **depth stick** visible.
""")

# --- Sidebar: Harvest Management ---
with st.sidebar:
    st.header("Harvest Tracking")
    new_harvest = st.text_input("Create New Harvest Tag", placeholder="e.g., NorthField_April_26")
    if st.button("Create Tag"):
        add_harvest(new_harvest)
        st.success(f"Tag '{new_harvest}' created!")

# --- Main Form ---
with st.form("upload_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        farmer_name = st.text_input("Farmer Name/ID")
        stage = st.selectbox("Processing Stage", [
            "Whole Dried Pods", 
            "Partially Shelled", 
            "Cleaned Beans (Final)"
        ])
    
    with col2:
        # Filter for tags created recently (or just show all for this prototype)
        harvest_options = [h['name'] for h in st.session_state.harvests]
        selected_tag = st.selectbox("Attach to Harvest Tag", ["None"] + harvest_options)
        
    uploaded_file = st.file_uploader("Upload Bean Photo", type=["jpg", "jpeg", "png"])
    
    submitted = st.form_submit_button("Send for AI & OpenCV Analysis")

# --- Processing Logic (Placeholder) ---
if submitted:
    if not uploaded_file or not farmer_name:
        st.error("Please provide both a farmer name and a photograph.")
    else:
        # This is where your backend integration happens
        st.divider()
        st.success(f"File successfully received for {farmer_name}!")
        
        # UI Mockup of the Processing Pipeline
        cols = st.columns(3)
        cols[0].metric("Status", "Image Received")
        cols[1].metric("Pipeline", "OpenCV + Vision AI")
        cols[2].metric("Tag", selected_tag)
        
        st.info("The image is being processed using OpenCV for pixels-to-cm calibration and depth stick interpretation...")
        
        # Display the uploaded image
        st.image(uploaded_file, caption=f"Processing: {selected_tag if selected_tag != 'None' else 'Unlabeled Harvest'}")

# --- Data Consistency Preview ---
if st.session_state.harvests:
    with st.expander("View Recent Harvest Logs"):
        st.table(st.session_state.harvests)