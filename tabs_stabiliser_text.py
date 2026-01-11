import re

def _collect_unique_links(texts, folder_titles):
    links = []
    seen = set()
    for html_text in texts:
        for folder_title in folder_titles:
            for m in re.finditer(r"<H3[^>]*>(.*?)</H3>", html_text, flags=re.IGNORECASE | re.DOTALL):
                if m.group(1).strip() == folder_title:
                    dl_start = html_text.find("<DL", m.end())
                    if dl_start == -1:
                        continue
                    dl_end = html_text.find("</DL>", dl_start)
                    if dl_end == -1:
                        continue
                    dl_content = html_text[dl_start:dl_end + 5]
                    for a_match in re.finditer(r"<A[^>]*>(.*?)</A>", dl_content, flags=re.IGNORECASE | re.DOTALL):
                        a_tag = a_match.group(0)
                        href_match = re.search(r'href="([^"]+)"', a_tag, flags=re.IGNORECASE)
                        if not href_match:
                            continue
                        href = href_match.group(1).strip()
                        icon_match = re.search(r'icon="data:image[^"]*"', a_tag)
                        if icon_match:
                            a_tag = a_tag.replace(icon_match.group(0), "")
                        key = href
                        if key not in seen:
                            seen.add(key)
                            links.append("<DT>" + a_tag.strip())
    return links

def insert_links_after_h3(html_text, folder_titles, new_links_lines):
    # new_links_lines: list of strings like '<DT><A HREF="...">Title</A>'
    for folder_title in folder_titles:
        h3_match = re.search(
            rf"<H3[^>]*>\s*{re.escape(folder_title)}\s*</H3>",
            html_text,
            flags=re.IGNORECASE,
        )
        if h3_match:
            break

    if not h3_match:
        raise ValueError("H3 folder title not found")
    

    start = h3_match.end()
    dl_match = re.search(r"<DL><p>", html_text[start:], flags=re.IGNORECASE)
    if not dl_match:
        raise ValueError("No <DL><p> after H3")

    dl_start = start + dl_match.start()
    dl_content_start = start + dl_match.end()
    dl_end = html_text.find("</DL>", dl_content_start)
    if dl_end == -1:
        raise ValueError("No closing </DL> for folder")

    insertion = "\n" + "\n".join(new_links_lines) + "\n"
    return html_text[:dl_content_start] + insertion + html_text[dl_end:]

def stabilize_tabs(source_path1, source_path2, folder_titles, output_path):
    with open(source_path1, "r", encoding="utf-8") as f1:
        source1 = f1.read()
    with open(source_path2, "r", encoding="utf-8") as f2:
        source2 = f2.read()
    links = _collect_unique_links(
        (source1, source2),
        ("Bookmarks bar", "Favourites bar"),
    )
    print(f"Collected {len(links)} unique links.")

    new_html = insert_links_after_h3(source1, folder_titles, links)

    with open(output_path, "w", encoding="utf-8") as out_file:
        out_file.write(new_html)





stabilize_tabs(
    r"C:\Users\nikit\Downloads\favourites_10_01_2026.html",
    r"C:\Users\nikit\Downloads\bookmarks_10_01_2026-02.html",
    ("Favourites bar", "Bookmarks bar"),
    "stabilized_bookmarks.html",
)
