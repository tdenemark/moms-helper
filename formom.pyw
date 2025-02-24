import xml.etree.ElementTree as ET
from xml.dom import minidom
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

def prettify_xml(element):
    """Format the XML output for readability."""
    raw_xml = ET.tostring(element, encoding="utf-8")
    parsed_xml = minidom.parseString(raw_xml)  # Parse for formatting
    return parsed_xml.toprettyxml(indent="  ")  # Return pretty-printed XML

def get_user_input():
    """Prompt the user for language and metadata details."""
    root = tk.Tk()
    root.withdraw()

    source_language = simpledialog.askstring("Input", "Enter source language (e.g., en):")
    target_language = simpledialog.askstring("Input", "Enter target language (e.g., fr):")
    translation_model = simpledialog.askstring("Input", "Enter translation model (e.g., generic):")
    approval_status = simpledialog.askstring("Input", "Enter approval status (e.g., APPROVED):")

    if not all([source_language, target_language, translation_model, approval_status]):
        messagebox.showerror("Error", "All fields are required!")
        return None  # Exit if any input is missing

    return source_language, target_language, translation_model, approval_status

def process_tmx(input_file, source_lang, target_lang, trans_model, approval_status):
    """Process the TMX file, apply formatting, and correctly structure properties."""
    
    # Define namespace handling for `xml:lang`
    namespaces = {"xml": "http://www.w3.org/XML/1998/namespace"}

    # Parse the TMX file
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Ensure the root <tmx> tag includes srclang
    root.attrib["srclang"] = source_lang

    # Process each <tu> entry inside <body>
    for tu in root.findall("body/tu", namespaces):
        # Extract the existing <tuv> elements
        tuv_en = tu.find("tuv[@xml:lang='en-us']", namespaces)

        if tuv_en is None:
            continue  # Skip if no English text is found

        # Extract and modify English text
        en_text = tuv_en.find("seg").text.strip() + "*"

        # Find all non-English <tuv> elements
        other_tuvs = [tuv for tuv in tu.findall("tuv", namespaces) if tuv.get("{http://www.w3.org/XML/1998/namespace}lang") != "en-us"]

        # Remove all original <tuv> elements
        tu.clear()

        # Set the correct `srclang` attribute
        tu.set("srclang", source_lang)

        # Create new English <tuv> (source_text)
        tuv_source = ET.Element("tuv", {"xml:lang": "en", "creationId": "source_text"})
        seg_source = ET.SubElement(tuv_source, "seg")
        seg_source.text = en_text
        tu.append(tuv_source)

        # Process each target language
        for tuv in other_tuvs:
            lang_code = tuv.get("{http://www.w3.org/XML/1998/namespace}lang")  # Keep original language code
            target_text = tuv.find("seg").text.strip() + "*"

            # Create improvement_text entry
            tuv_improvement = ET.Element("tuv", {"xml:lang": lang_code, "creationId": "improvement_text"})
            seg_improvement = ET.SubElement(tuv_improvement, "seg")
            seg_improvement.text = target_text
            tu.append(tuv_improvement)

            # Create target_mt_text entry
            tuv_target_mt = ET.Element("tuv", {"xml:lang": lang_code, "creationId": "target_mt_text"})
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

    # Save the modified TMX file with pretty formatting
    output_file = input_file.replace(".tmx", "_processed.tmx")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(prettify_xml(root))

    return output_file

# GUI to pick file and process
def main():
    root = tk.Tk()
    root.withdraw()
    
    input_file = filedialog.askopenfilename(filetypes=[("TMX Files", "*.tmx")])
    if not input_file:
        return
    
    # Get user input
    user_input = get_user_input()
    if not user_input:
        return  # Exit if the user canceled

    try:
        output_file = process_tmx(input_file, *user_input)
        messagebox.showinfo("Success", f"Processed file saved:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

if __name__ == "__main__":
    main()
