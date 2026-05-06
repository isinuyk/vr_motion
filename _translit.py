"""Transliterate Cyrillic text to readable Latin so we can analyze it."""
import sys

UA_MAP = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G', 'Д': 'D', 'Е': 'E',
    'Є': 'Ye', 'Ж': 'Zh', 'З': 'Z', 'И': 'Y', 'І': 'I', 'Ї': 'Yi', 'Й': 'Y',
    'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
    'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch',
    'Ш': 'Sh', 'Щ': 'Shch', 'Ь': "'", 'Ю': 'Yu', 'Я': 'Ya',
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e',
    'є': 'ye', 'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y',
    'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
    'ш': 'sh', 'щ': 'shch', 'ь': "'", 'ю': 'yu', 'я': 'ya',
    'ё': 'yo', 'Ё': 'Yo', 'ы': 'y', 'Ы': 'Y', 'э': 'e', 'Э': 'E',
    'ъ': '', 'Ъ': '',
    '«': '"', '»': '"', '–': '-', '—': '-', '\u2212': '-',
    '\u00a0': ' ', '\u2009': ' ',
}


def translit(text):
    out = []
    for ch in text:
        out.append(UA_MAP.get(ch, ch))
    return "".join(out)


if __name__ == "__main__":
    src = sys.argv[1]
    dst = sys.argv[2]
    with open(src, 'r', encoding='utf-8') as f:
        text = f.read()
    out = translit(text)
    with open(dst, 'w', encoding='ascii', errors='replace') as f:
        f.write(out)
    print(f"Wrote {len(out)} chars to {dst}")
