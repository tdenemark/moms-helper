import streamlit as st
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os  # Needed to extract file names

# Function to format XML output
def prettify_xml(element):
    """Format the XML output for readability."""
    raw_xml = ET.tostring(element, encoding="utf-8")
    parsed_xml = minidom.parseString(raw_xml)  
    return parsed_xml.toprettyxml(indent="  ")  

# Function to process the uploaded TMX file
def process_tmx(uploaded_file, source_lang, target_lang, trans_model, approval_status):
    """Process the TMX file and return formatted XML as a string."""
    
    # Define namespace handling for `xml:lang`
    namespaces = {"xml": "http://www.w3.org/XML/1998/namespace"}

    # Parse the TMX file while explicitly handling namespaces
    tree = ET.parse(uploaded_file)
    root = tree.getroot()

    # Modify the existing <header> tag instead of duplicating it
    header = root.find("header")
    if header is not None:
        header.set("srclang", source_lang)  # Update source language

    # Process each <tu> entry inside <body>
    for tu in root.findall("body/tu", namespaces):
        # Extract the existing <tuv> elements
        tuv_source = tu.find(f"tuv[@xml:lang='{source_lang}']", namespaces)

        if tuv_source is None:
            continue  # Skip if no source text is found

        # Extract and modify source text
        source_text = tuv_source.find("seg").text.strip() + "*"

        # Find the target language <tuv>
        tuv_target = tu.find(f"tuv[@xml:lang='{target_lang}']", namespaces)
        if tuv_target is None:
            continue  # Skip if target language is missing

        target_text = tuv_target.find("seg").text.strip() + "*"

        # Remove all original <tuv> elements
        tu.clear()
        tu.set("srclang", source_lang)

        # Create new English <tuv> (source_text)
        tuv_source_new = ET.Element("tuv", {"xml:lang": source_lang, "creationId": "source_text"})
        seg_source = ET.SubElement(tuv_source_new, "seg")
        seg_source.text = source_text
        tu.append(tuv_source_new)

        # Create target language <tuv> (improvement_text)
        tuv_improvement = ET.Element("tuv", {"xml:lang": target_lang, "creationId": "improvement_text"})
        seg_improvement = ET.SubElement(tuv_improvement, "seg")
        seg_improvement.text = target_text
        tu.append(tuv_improvement)

        # Create target language <tuv> (target_mt_text)
        tuv_target_mt = ET.Element("tuv", {"xml:lang": target_lang, "creationId": "target_mt_text"})
        seg_target_mt = ET.SubElement(tuv_target_mt, "seg")
        seg_target_mt.text = target_text
        tu.append(tuv_target_mt)

        # Add <prop> elements **outside** the <tuv> entries but inside <tu>
        for prop_type, value in [
            ("source_language", source_lang),
            ("target_language", target_lang),
            ("translation_model", trans_model),
            ("approval_status", approval_status)
        ]:
            prop = ET.SubElement(tu, "prop", {"type": prop_type})
            prop.text = value

    return prettify_xml(root)

# ---- STREAMLIT UI ---- #
st.set_page_config(page_title="TMX File Processor", layout="centered")

st.title("📂 TMX File Processor")
st.write("### Upload a `.tmx` file, enter the details, and download the processed file.")

# File Upload Section
st.subheader("1️⃣ Upload Your TMX File")
uploaded_file = st.file_uploader("🔼 Select a `.tmx` file", type=["tmx"])

# Sidebar for user input
st.sidebar.header("🔧 Configuration Settings")
source_lang = st.sidebar.text_input("🌍 Source Language", "en")
target_lang = st.sidebar.text_input("🌍 Target Language", "es")
trans_model = st.sidebar.text_input("📌 Translation Model (e.g., generic, custom, neural)", "generic")
approval_status = st.sidebar.selectbox("✅ Approval Status", ["APPROVED", "PENDING", "REVIEW"])

# Step 2: Set Processed Filename
if uploaded_file:
    original_filename = os.path.splitext(uploaded_file.name)[0]  # Remove ".tmx"
    default_filename = f"{original_filename}-processed.tmx"

    # Let the user edit the filename before downloading
    st.subheader("2️⃣ Name the Processed File")
    processed_filename = st.text_input("📝 Processed File Name", default_filename)

    # Ensure the filename is valid
    processed_filename = processed_filename.strip().replace(" ", "_")  # Replace spaces with underscores
    if not processed_filename.endswith(".tmx"):
        processed_filename += ".tmx"  # Ensure correct file extension

# Step 3: Process & Download Section
st.subheader("3️⃣ Process and Download")
if uploaded_file and st.button("🚀 Process TMX File"):
    try:
        processed_xml = process_tmx(uploaded_file, source_lang, target_lang, trans_model, approval_status)
        st.success("✅ Processing complete! Click below to download the new file.")

        # Add Download Button with the User's Chosen Filename
        st.download_button("⬇️ Download Processed TMX", processed_xml, processed_filename, "application/xml")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit")
