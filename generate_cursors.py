import os
import struct
import io
from PIL import Image, ImageDraw

def create_cursor_file(image: Image.Image, hotspot: tuple, out_path: str):
    """Encodes a PIL RGBA image into a valid Windows .cur file with hotspot."""
    png_bytes = io.BytesIO()
    image.save(png_bytes, format='PNG')
    png_data = png_bytes.getvalue()
    
    width = image.width if image.width < 256 else 0
    height = image.height if image.height < 256 else 0
    
    # CUR header (6 bytes) + 1 directory entry (16 bytes) = 22 bytes
    header = struct.pack('<HHH', 0, 2, 1)  # reserved=0, type=2 (cursor), count=1
    direntry = struct.pack('<BBBBHHII', 
                           width, height, 0, 0, 
                           int(hotspot[0]), int(hotspot[1]), 
                           len(png_data), 22)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, 'wb') as f:
        f.write(header)
        f.write(direntry)
        f.write(png_data)

def generate_palette_cursors(output_dir: str, primary_rgb: tuple, size: int = 64):
    """Generates high-contrast low-vision cursors for a given primary RGB color."""
    os.makedirs(output_dir, exist_ok=True)
    s = size / 64.0
    cx = size // 2
    prefix = 'red' if primary_rgb[0] > 200 and primary_rgb[1] < 100 else 'yellow'

    # 1. Arrow
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pts = [
        (0, 0),
        (0, int(48*s)),
        (int(14*s), int(36*s)),
        (int(24*s), int(60*s)),
        (int(32*s), int(56*s)),
        (int(22*s), int(32*s)),
        (int(38*s), int(32*s))
    ]
    # Outlines
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            draw.polygon([(x+dx, y+dy) for x, y in pts], fill=(0, 0, 0, 255))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            draw.polygon([(x+dx, y+dy) for x, y in pts], fill=(255, 255, 255, 255))
    inner_pts = [(int(x*0.88 + 2*s), int(y*0.88 + 2*s)) for x, y in pts]
    draw.polygon(inner_pts, fill=(*primary_rgb, 255))
    create_cursor_file(img, (0, 0), os.path.join(output_dir, f'{prefix}_arrow.cur'))

    # 2. Hand
    img_hand = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw_h = ImageDraw.Draw(img_hand)
    h_pts = [
        (int(18*s), int(4*s)), (int(24*s), int(4*s)), (int(24*s), int(22*s)),
        (int(30*s), int(16*s)), (int(36*s), int(16*s)), (int(36*s), int(26*s)),
        (int(42*s), int(20*s)), (int(48*s), int(20*s)), (int(48*s), int(30*s)),
        (int(54*s), int(26*s)), (int(58*s), int(26*s)), (int(58*s), int(42*s)),
        (int(48*s), int(58*s)), (int(20*s), int(58*s)), (int(10*s), int(44*s)),
        (int(10*s), int(30*s)), (int(18*s), int(24*s))
    ]
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            draw_h.polygon([(x+dx, y+dy) for x, y in h_pts], fill=(0, 0, 0, 255))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            draw_h.polygon([(x+dx, y+dy) for x, y in h_pts], fill=(255, 255, 255, 255))
    inner_h_pts = [(int(x*0.88 + 3*s), int(y*0.88 + 3*s)) for x, y in h_pts]
    draw_h.polygon(inner_h_pts, fill=(*primary_rgb, 255))
    create_cursor_file(img_hand, (int(21*s), int(4*s)), os.path.join(output_dir, f'{prefix}_hand.cur'))

    # 3. High-Vis Barbell I-Beam
    img_beam = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw_b = ImageDraw.Draw(img_beam)
    beam_w = max(4, int(6*s))
    bar_w = max(12, int(20*s))
    top = int(10*s)
    bottom = int(54*s)
    
    draw_b.rectangle([cx - bar_w - 2, top - 2, cx + bar_w + 2, top + 5], fill=(0, 0, 0, 255))
    draw_b.rectangle([cx - bar_w - 2, bottom - 5, cx + bar_w + 2, bottom + 2], fill=(0, 0, 0, 255))
    draw_b.rectangle([cx - beam_w - 2, top, cx + beam_w + 2, bottom], fill=(0, 0, 0, 255))
    draw_b.rectangle([cx - bar_w - 1, top - 1, cx + bar_w + 1, top + 4], fill=(255, 255, 255, 255))
    draw_b.rectangle([cx - bar_w - 1, bottom - 4, cx + bar_w + 1, bottom + 1], fill=(255, 255, 255, 255))
    draw_b.rectangle([cx - beam_w - 1, top, cx + beam_w + 1, bottom], fill=(255, 255, 255, 255))
    draw_b.rectangle([cx - bar_w, top, cx + bar_w, top + 3], fill=(*primary_rgb, 255))
    draw_b.rectangle([cx - bar_w, bottom - 3, cx + bar_w, bottom], fill=(*primary_rgb, 255))
    draw_b.rectangle([cx - beam_w, top, cx + beam_w, bottom], fill=(*primary_rgb, 255))
    create_cursor_file(img_beam, (cx, cx), os.path.join(output_dir, f'{prefix}_ibeam.cur'))

    # 4. Crosshair
    img_cross = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw_c = ImageDraw.Draw(img_cross)
    draw_c.ellipse([cx - int(18*s), cx - int(18*s), cx + int(18*s), cx + int(18*s)], outline=(0,0,0,255), width=max(3, int(4*s)))
    draw_c.ellipse([cx - int(18*s)+1, cx - int(18*s)+1, cx + int(18*s)-1, cx + int(18*s)-1], outline=(*primary_rgb, 255), width=max(2, int(2*s)))
    draw_c.line([(cx, int(8*s)), (cx, size - int(8*s))], fill=(*primary_rgb, 255), width=max(2, int(3*s)))
    draw_c.line([(int(8*s), cx), (size - int(8*s), cx)], fill=(*primary_rgb, 255), width=max(2, int(3*s)))
    create_cursor_file(img_cross, (cx, cx), os.path.join(output_dir, f'{prefix}_cross.cur'))

    # 5. Move & Resize
    img_move = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw_m = ImageDraw.Draw(img_move)
    draw_m.ellipse([cx-int(6*s), cx-int(6*s), cx+int(6*s), cx+int(6*s)], fill=(*primary_rgb, 255), outline=(0,0,0,255), width=2)
    draw_m.line([(cx, int(6*s)), (cx, size-int(6*s))], fill=(*primary_rgb, 255), width=max(3, int(4*s)))
    draw_m.line([(int(6*s), cx), (size-int(6*s), cx)], fill=(*primary_rgb, 255), width=max(3, int(4*s)))
    create_cursor_file(img_move, (cx, cx), os.path.join(output_dir, f'{prefix}_move.cur'))
    create_cursor_file(img_move, (cx, cx), os.path.join(output_dir, f'{prefix}_sizens.cur'))
    create_cursor_file(img_move, (cx, cx), os.path.join(output_dir, f'{prefix}_sizewe.cur'))
    create_cursor_file(img_move, (cx, cx), os.path.join(output_dir, f'{prefix}_sizenwse.cur'))
    create_cursor_file(img_move, (cx, cx), os.path.join(output_dir, f'{prefix}_sizenesw.cur'))

    # 6. Unavailable / No
    img_no = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw_no = ImageDraw.Draw(img_no)
    r = int(20*s)
    draw_no.ellipse([cx-r-2, cx-r-2, cx+r+2, cx+r+2], fill=(0,0,0,255))
    draw_no.ellipse([cx-r, cx-r, cx+r, cx+r], fill=(255,255,255,255))
    draw_no.ellipse([cx-r+2, cx-r+2, cx+r-2, cx+r-2], outline=(*primary_rgb, 255), width=max(4, int(6*s)))
    draw_no.line([(cx-int(14*s), cx-int(14*s)), (cx+int(14*s), cx+int(14*s))], fill=(*primary_rgb, 255), width=max(4, int(5*s)))
    create_cursor_file(img_no, (cx, cx), os.path.join(output_dir, f'{prefix}_no.cur'))

def generate_red_cursors(output_dir: str, size: int = 64):
    generate_palette_cursors(output_dir, (255, 25, 25), size)

def generate_yellow_cursors(output_dir: str, size: int = 64):
    generate_palette_cursors(output_dir, (255, 220, 0), size)

if __name__ == '__main__':
    base = os.path.dirname(os.path.abspath(__file__))
    generate_red_cursors(os.path.join(base, 'cursors', 'red'), 64)
    generate_yellow_cursors(os.path.join(base, 'cursors', 'yellow'), 64)
    print("Generated all cursor schemes.")
