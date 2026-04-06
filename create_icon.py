from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        margin = size // 8
        draw.ellipse([margin, margin, size - margin, size - margin], 
                     fill='#151515', outline='#333333', width=max(1, size // 32))
        
        eye_margin = size // 4
        eye_y = size // 2
        eye_height = size // 6
        
        draw.arc([eye_margin, eye_y - eye_height, 
                  size - eye_margin, eye_y + eye_height],
                 start=0, end=180, fill='#44ff44', width=max(1, size // 16))
        
        line_y = eye_y
        draw.line([(eye_margin + 2, line_y), (size - eye_margin - 2, line_y)],
                  fill='#ff4444', width=max(1, size // 12))
        
        pupil_size = max(2, size // 16)
        draw.ellipse([size//2 - pupil_size, eye_y - pupil_size,
                      size//2 + pupil_size, eye_y + pupil_size],
                     fill='#ffffff')
        
        images.append(img)
    
    images[0].save('icon.ico', format='ICO', sizes=[(s, s) for s in sizes])
    print("[OK] icon.ico created successfully!")
    
    preview = images[-1].resize((128, 128), Image.Resampling.LANCZOS)
    preview.save('icon_preview.png')
    print("[OK] icon_preview.png created!")

if __name__ == "__main__":
    create_icon()
