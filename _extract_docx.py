"""Extract text + comments from a DOCX file (UTF-8)."""
import sys
import os
import zipfile
from xml.etree import ElementTree as ET

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}


def extract_docx(path):
    out = []
    out.append(f"=== FILE: {path} ===")
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        # Main document
        with z.open("word/document.xml") as f:
            tree = ET.parse(f)
        root = tree.getroot()
        # Build a map of comment IDs -> commentRangeStart positions
        body_text_parts = []

        # Walk through all paragraphs
        for para in root.iter(f"{{{NS['w']}}}p"):
            # Identify comment range starts inside the paragraph
            text_buffer = []
            comment_starts = []
            comment_ends = []
            comment_refs = []
            for elem in para.iter():
                tag = elem.tag.split("}")[-1]
                if tag == "commentRangeStart":
                    cid = elem.get(f"{{{NS['w']}}}id")
                    comment_starts.append(cid)
                elif tag == "commentRangeEnd":
                    cid = elem.get(f"{{{NS['w']}}}id")
                    comment_ends.append(cid)
                elif tag == "commentReference":
                    cid = elem.get(f"{{{NS['w']}}}id")
                    comment_refs.append(cid)
                elif tag == "t":
                    text_buffer.append(elem.text or "")
                elif tag == "tab":
                    text_buffer.append("\t")
                elif tag == "br":
                    text_buffer.append("\n")
            line = "".join(text_buffer)
            # Style identification
            pPr = para.find(f"{{{NS['w']}}}pPr")
            style = ""
            if pPr is not None:
                pStyle = pPr.find(f"{{{NS['w']}}}pStyle")
                if pStyle is not None:
                    style = pStyle.get(f"{{{NS['w']}}}val", "")
            prefix = ""
            if style:
                prefix = f"[STYLE:{style}] "
            if comment_starts or comment_refs:
                prefix += f"[COMMENT_IDS_HERE: {','.join(comment_starts + comment_refs)}] "
            body_text_parts.append(prefix + line)

        out.append("\n--- BODY ---")
        out.extend(body_text_parts)

        # Comments
        if "word/comments.xml" in names:
            out.append("\n--- COMMENTS ---")
            with z.open("word/comments.xml") as f:
                ctree = ET.parse(f)
            croot = ctree.getroot()
            for c in croot.iter(f"{{{NS['w']}}}comment"):
                cid = c.get(f"{{{NS['w']}}}id")
                author = c.get(f"{{{NS['w']}}}author")
                date = c.get(f"{{{NS['w']}}}date")
                text_buffer = []
                for t in c.iter(f"{{{NS['w']}}}t"):
                    text_buffer.append(t.text or "")
                txt = "".join(text_buffer)
                out.append(f"[COMMENT id={cid} author={author} date={date}]: {txt}")

        # Track changes (revisions): w:ins, w:del
        ins_list = list(root.iter(f"{{{NS['w']}}}ins"))
        del_list = list(root.iter(f"{{{NS['w']}}}del"))
        if ins_list or del_list:
            out.append("\n--- TRACKED CHANGES ---")
            for ins in ins_list:
                author = ins.get(f"{{{NS['w']}}}author", "")
                txt = "".join(t.text or "" for t in ins.iter(f"{{{NS['w']}}}t"))
                if txt.strip():
                    out.append(f"[INS by {author}]: {txt}")
            for d in del_list:
                author = d.get(f"{{{NS['w']}}}author", "")
                txt = "".join(t.text or "" for t in d.iter(f"{{{NS['w']}}}delText"))
                if txt.strip():
                    out.append(f"[DEL by {author}]: {txt}")

    return "\n".join(out)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        if os.path.isfile(p):
            print(extract_docx(p))
            print()
