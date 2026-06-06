import os
import re
import zipfile
import lxml.html
import xml.etree.ElementTree as ET

def int_to_roman(n):
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ""
    i = 0
    while n > 0:
        for _ in range(n // val[i]):
            roman_num += syb[i]
            n -= val[i]
        i += 1
    return roman_num

def process_inline(elem):
    if elem is None:
        return ""
    if elem.tag in ['script', 'style']:
        return ""
        
    cls = elem.get('class', '')
    if elem.tag == 'p' and ('poem_num' in cls or cls in ['poem_num2', 'poem_num3']):
        return ""
        
    result = elem.text or ""
    for child in elem:
        child_text = process_inline(child)
        if child.tag in ['i', 'em']:
            if child_text.strip():
                result += f"*{child_text}*"
            else:
                result += child_text
        elif child.tag in ['b', 'strong']:
            if child_text.strip():
                result += f"**{child_text}**"
            else:
                result += child_text
        elif child.tag == 'br':
            result += "\n" + child_text
        elif child.tag == 'a':
            href = child.get('href', '')
            if href and child_text.strip():
                result += f"[{child_text}]({href})"
            else:
                result += child_text
        else:
            result += child_text
    result += elem.tail or ""
    return result

def convert_node_to_raw_blocks(node):
    if node is None:
        return []
    
    tag = node.tag
    if tag in ['script', 'style', 'head', 'title', 'meta', 'link']:
        return []
        
    cls = node.get('class', '')
    if tag == 'p' and ('poem_num' in cls or cls in ['poem_num2', 'poem_num3']):
        return []
        
    if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        level = int(tag[1])
        text = process_inline(node).strip()
        if not text:
            return []
        # If it is just a roman numeral (e.g. Canto number in original file), skip to avoid duplication
        # as we are adding our own "# Canto X" headings
        roman_pattern = re.compile(r'^[IVXLCDM]+$')
        if roman_pattern.match(text):
            return []
        return [f"\n{'#' * level} {text}\n"]
        
    if tag == 'p':
        text = process_inline(node).strip()
        if not text:
            return []
        if 'poem_ind' in cls:
            return [f"POEM_IND:{text}"]
        elif 'poem' in cls:
            return [f"POEM_LINE:{text}"]
        else:
            return [f"\n{text}\n"]
            
    if tag == 'li':
        text = process_inline(node).strip()
        if not text:
            return []
        return [f"* {text}"]
        
    if tag in ['ul', 'ol']:
        parts = []
        for child in node:
            parts.extend(convert_node_to_raw_blocks(child))
        if parts:
            return ["\n" + "\n".join(p for p in parts if p.strip()) + "\n"]
        return []
        
    if tag in ['body', 'div', 'section', 'article']:
        parts = []
        for child in node:
            parts.extend(convert_node_to_raw_blocks(child))
        return parts
        
    # Check if there are inline styles or text directly at block level
    text = process_inline(node).strip()
    if text:
        return [f"\n{text}\n"]
    return []

def post_process_blocks(raw_blocks):
    processed = []
    last_was_poem = False
    for block in raw_blocks:
        if block.startswith("POEM_IND:"):
            line = block[len("POEM_IND:"):]
            processed.append("\n" + line)
            last_was_poem = True
        elif block.startswith("POEM_LINE:"):
            line = block[len("POEM_LINE:"):]
            if last_was_poem:
                processed.append(line)
            else:
                processed.append("\n" + line)
            last_was_poem = True
        else:
            processed.append(block)
            last_was_poem = False
            
    content = "\n".join(processed)
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()

def convert_epub(epub_path, output_md_path):
    print(f"Parsing EPUB: {epub_path}")
    if not os.path.exists(epub_path):
        print(f"Error: {epub_path} does not exist.")
        return
        
    with zipfile.ZipFile(epub_path, 'r') as z:
        # Find OPF
        opf_name = [n for n in z.namelist() if n.endswith('.opf')][0]
        root = ET.fromstring(z.read(opf_name))
        ns = {'ns': 'http://www.idpf.org/2007/opf'}
        manifest = {item.get('id'): item.get('href') for item in root.findall('.//ns:item', ns)}
        spine = root.find('.//ns:spine', ns)
        spine_items = [itemref.get('idref') for itemref in spine.findall('.//ns:itemref', ns)]
        
        # Determine the base directory of the OPF file inside the zip
        base_dir = os.path.dirname(opf_name)
        
        md_content_parts = []
        canto_index = 1
        
        # Determine if it is Inferno (34 cantos, starting at cap-008) or others (33 cantos, starting at cap-005)
        is_inferno = "inferno" in epub_path.lower()
        canto_start_num = 8 if is_inferno else 5
        
        for idx, idref in enumerate(spine_items):
            href = manifest.get(idref)
            if not href:
                continue
            
            # Construct the full path inside zip
            full_href_path = os.path.normpath(os.path.join(base_dir, href)) if base_dir else href
            
            # Read XHTML
            if full_href_path not in z.namelist():
                # Try relative directly if base_dir normalization causes mismatch
                full_href_path = href if href in z.namelist() else None
                if not full_href_path:
                    continue
            
            html_bytes = z.read(full_href_path)
            doc = lxml.html.fromstring(html_bytes)
            
            # Semantically check if this is a poem page
            is_poem = any(elem.get('class') in ['poem', 'poem_ind'] for elem in doc.body.iter())
            
            # Extract raw blocks
            raw_blocks = convert_node_to_raw_blocks(doc.body)
            page_text = post_process_blocks(raw_blocks)
            
            # Determine if this chapter is one of the cantos
            # It's a canto if the filename corresponds to the canto range
            # We can extract the file number from the filename
            filename = os.path.basename(full_href_path)
            match = re.search(r'_c(\d+)\.xhtml$', filename)
            is_canto_file = False
            
            if match:
                file_num = int(match.group(1))
                if file_num >= canto_start_num:
                    is_canto_file = True
            
            if is_canto_file:
                roman_num = int_to_roman(canto_index)
                if not is_poem:
                    # Commentary
                    md_content_parts.append(f"\n\n# Canto {roman_num}\n\n## Introduzione e Commento\n\n{page_text}")
                else:
                    # Poem
                    md_content_parts.append(f"\n\n## Testo del Canto\n\n{page_text}")
                    canto_index += 1
            else:
                # Skip index and advertising files or process them normally
                if "ind01" in filename:
                    # We can label the index
                    md_content_parts.append(f"\n\n# Indice\n\n{page_text}")
                elif "pi01" in filename:
                    # Skip publisher advertisements
                    continue
                elif "tp01" in filename or "cov01" in filename:
                    # Cover / Title page
                    if page_text:
                        md_content_parts.append(f"\n\n# {page_text}")
                else:
                    # General introductory files
                    if page_text:
                        md_content_parts.append(f"\n\n{page_text}")
        
        # Combine all parts
        final_markdown = "\n".join(md_content_parts)
        # Final cleanups of consecutive blank lines
        final_markdown = re.sub(r'\n{3,}', '\n\n', final_markdown)
        
        # Write to file
        with open(output_md_path, 'w', encoding='utf-8') as out_f:
            out_f.write(final_markdown.strip() + "\n")
        print(f"Successfully converted and saved: {output_md_path}")

if __name__ == '__main__':
    epubs = [
        ("dante/L'Inferno di Dante - Vittorio Sermonti.epub", "dante/L'Inferno di Dante - Vittorio Sermonti.md"),
        ("dante/Il Purgatorio di Dante - Vittorio Sermonti.epub", "dante/Il Purgatorio di Dante - Vittorio Sermonti.md"),
        ("dante/Il Paradiso di Dante - Vittorio Sermonti.epub", "dante/Il Paradiso di Dante - Vittorio Sermonti.md")
    ]
    for epub, md in epubs:
        convert_epub(epub, md)
