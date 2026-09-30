"""Tile preview PNGs into a contact sheet: python3 contact.py out.png a.png b.png ..."""
import sys

from PIL import Image, ImageDraw


def main(out, files, cols=2, w=960):
    h = w * 9 // 16
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * w, rows * (h + 24)), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB').resize((w, h), Image.LANCZOS)
        x, y = (i % cols) * w, (i // cols) * (h + 24)
        sheet.paste(im, (x, y))
        d.text((x + 6, y + h + 4), f.split('/')[-1], fill=(255, 255, 255))
    sheet.save(out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
