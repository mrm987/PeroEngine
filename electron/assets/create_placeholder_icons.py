"""간단한 placeholder 아이콘 생성"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, text, output_path):
    """텍스트가 있는 간단한 아이콘 생성"""
    # 배경색: 파란색 그라데이션
    img = Image.new('RGBA', (size, size), (66, 135, 245, 255))
    draw = ImageDraw.Draw(img)
    
    # 원 그리기
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], 
                 fill=(33, 150, 243, 255), outline=(255, 255, 255, 255), width=size//20)
    
    # 텍스트 (P for PeroEngine)
    try:
        # 시스템 폰트 시도
        font_size = size // 2
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # 텍스트 중앙 정렬
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - size // 20
    
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    img.save(output_path)
    print(f"✅ Created: {output_path}")

# 메인 아이콘 생성 (512x512)
print("🎨 Creating placeholder icons...")
create_icon(512, "P", "icon.png")

# 트레이 아이콘 생성 (22x22 작은 버전)
create_icon(22, "P", "tray-icon.png")

print("✅ Placeholder icons created!")
print("   - icon.png (512x512)")
print("   - tray-icon.png (22x22)")
print("\n💡 For production, replace with custom icons.")
