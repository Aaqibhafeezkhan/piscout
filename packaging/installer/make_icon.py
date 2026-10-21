"""Draw piscout.ico: a pink circle with "Pi" (same look as the store logo), transparent background."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
PINK = (197, 26, 74, 255)
WHITE = (243, 245, 250, 255)


def main():
    here = Path(__file__).parent
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((24, 24, SIZE - 24, SIZE - 24), fill=PINK)
    font = None
    for name in ("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            font = ImageFont.truetype(name, 560)
            break
        except OSError:
            continue
    d.text((SIZE / 2, SIZE / 2 + 10), "Pi", font=font, fill=WHITE, anchor="mm")
    img.save(here / "piscout.ico", sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])
    print("wrote", here / "piscout.ico")


if __name__ == "__main__":
    main()
