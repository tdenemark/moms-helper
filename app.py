import streamlit as st
import xml.etree.ElementTree as ET
from xml.dom import minidom

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

    # Ensure the root <tmx> tag includes srclang
    root.attrib["srclang"] = source_lang

    for tu in root.findall("body/tu", namespaces):
        tuv_en = tu.find(".//tuv[@xml:lang='en-us']", namespaces)

        if tuv_en is None:
            continue  # Skip if no English text is found

        en_text = tuv_en.find("seg").text.strip() + "*"

        # Find all non-English <tuv> elements
        other_tuvs = [tuv for tuv in tu.findall("tuv", namespaces) if tuv.get("{http://www.w3.org/XML/1998/namespace}lang") != "en-us"]

        # Remove all original <tuv> elements
        tu.clear()
        tu.set("srclang", source_lang)

        # Create new English <tuv> (source_text)
        tuv_source = ET.Element("tuv", {"xml:lang": "en", "creationId": "source_text"})
        seg_source = ET.SubElement(tuv_source, "seg")
        seg_source.text = en_text
        tu.append(tuv_source)

        # Process each target language
        for tuv in other_tuvs:
            lang_code = tuv.get("{http://www.w3.org/XML/1998/namespace}lang")  
            target_text = tuv.find("seg").text.strip() + "*"

            tuv_improvement = ET.Element("tuv", {"xml:lang": lang_code, "creationId": "improvement_text"})
            seg_improvement = ET.SubElement(tuv_improvement, "seg")
            seg_improvement.text = target_text
            tu.append(tuv_improvement)

            tuv_target_mt = ET.Element("tuv", {"xml:lang": lang_code, "creationId": "target_mt_text"})
            seg_target_mt = ET.SubElement(tuv_target_mt, "seg")
            seg_target_mt.text = target_text
            tu.append(tuv_target_mt)

        # Add properties
        for prop_type, value in [
            ("source_language", source_lang),
            ("target_language", target_lang),
            ("translation_model", trans_model),
            ("approval_status", approval_status)
        ]:
            prop = ET.SubElement(tu, "prop", {"type": prop_type})
            prop.text = value

    return prettify_xml(root)
