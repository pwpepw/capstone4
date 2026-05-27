from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
import os
import math


class CaptchaGenerator:
    def __init__(self, width=160, height=60):
        self.width = width
        self.height = height
        self.characters = string.digits + string.ascii_uppercase  # 0-9, A-Z

    def generate_text(self, length=5):
        return ''.join(random.choice(self.characters) for _ in range(length))

    # ── 노이즈 추가 헬퍼 ──────────────────────────────────────────
    def add_noise_lines(self, draw, count=2, color='black'):
        for _ in range(count):
            x1, y1 = random.randint(0, self.width), random.randint(0, self.height)
            x2, y2 = random.randint(0, self.width), random.randint(0, self.height)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

    def add_noise_dots(self, draw, count=50):
        for _ in range(count):
            x, y = random.randint(0, self.width), random.randint(0, self.height)
            draw.point((x, y), fill='black')

    # ── 물결 효과: 픽셀을 sin 곡선만큼 가로로 밀어서 왜곡 ─────────
    def apply_wave_effect(self, image, amplitude=5, frequency=20):
        width, height = image.size
        pixels = image.load()
        new_image = Image.new('RGB', (width, height), color='white')
        new_pixels = new_image.load()

        for y in range(height):
            for x in range(width):
                new_x = x + int(amplitude * math.sin(2 * math.pi * y / frequency))
                if 0 <= new_x < width:
                    new_pixels[new_x, y] = pixels[x, y]

        return new_image

    # ── Level 1: 기본 캡차 ────────────────────────────────────────
    # 텍스트 전체 너비를 재서 정확히 가운데 배치, 노이즈 선 2개
    def level1(self, text=None):
        if text is None:
            text = self.generate_text()

        image = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        y = (self.height - (bbox[3] - bbox[1])) // 2

        draw.text((x, y), text, fill='black', font=font)
        self.add_noise_lines(draw, count=2)

        return image, text

    # ── Level 2: 글자별 회전 추가 ─────────────────────────────────
    # 글자를 하나씩 개별 이미지에 그린 뒤 랜덤 회전하여 붙임
    # step × 글자 수로 전체 너비 계산 → 중앙 시작점 설정
    def level2(self, text=None):
        if text is None:
            text = self.generate_text()

        image = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()

        step = 26
        x_offset = (self.width - len(text) * step) // 2  # 중앙 정렬

        for char in text:
            char_img = Image.new('RGBA', (40, 50), color=(255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_img)
            char_draw.text((10, 10), char, fill='black', font=font)

            rotated = char_img.rotate(random.randint(-30, 30), expand=False, fillcolor=(255, 255, 255, 0))
            image.paste(rotated, (x_offset, 5), rotated)
            x_offset += step

        for _ in range(3):
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.add_noise_lines(draw, count=1, color=color)

        self.add_noise_dots(draw, count=50)

        return image, text

    # ── Level 3: 컬러 글자 + 세로 위치 흔들기 + 물결 + 블러 ───────
    # level2에서 글자 색상 랜덤화, y축 랜덤 이동 추가
    # 마지막에 물결 왜곡과 가우시안 블러로 판독 난이도 상승
    def level3(self, text=None):
        if text is None:
            text = self.generate_text()

        image = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()

        step = 28
        x_offset = (self.width - len(text) * step) // 2  # 중앙 정렬

        for char in text:
            char_img = Image.new('RGBA', (40, 50), color=(255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_img)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            char_draw.text((10, 10), char, fill=color, font=font)

            rotated = char_img.rotate(random.randint(-40, 40), expand=False, fillcolor=(255, 255, 255, 0))
            image.paste(rotated, (x_offset, random.randint(5, 10)), rotated)
            x_offset += step

        for _ in range(5):
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.add_noise_lines(draw, count=1, color=color)

        self.add_noise_dots(draw, count=100)

        image = self.apply_wave_effect(image, amplitude=3, frequency=25)
        image = image.filter(ImageFilter.GaussianBlur(radius=1))

        return image, text

    # ── Level 4: 글자 의도적 중첩 + 강한 왜곡 ────────────────────
    # step=15로 글자 간격을 좁혀 겹치게 만듦 (최고 난이도)
    # 물결 효과 2회 적용, 노이즈도 가장 많음
    def level4(self, text=None):
        if text is None:
            text = self.generate_text()

        image = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()

        step = 15
        char_width = 30  # 마지막 글자 너비 보정
        total_width = (len(text) - 1) * step + char_width
        x_offset = (self.width - total_width) // 2  # 중첩 유지하면서 중앙 정렬

        for char in text:
            char_img = Image.new('RGBA', (40, 50), color=(255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_img)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            char_draw.text((10, 10), char, fill=color, font=font)

            rotated = char_img.rotate(random.randint(-45, 45), expand=False, fillcolor=(255, 255, 255, 0))
            image.paste(rotated, (x_offset, random.randint(0, 15)), rotated)
            x_offset += step

        for _ in range(8):
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.add_noise_lines(draw, count=1, color=color)

        self.add_noise_dots(draw, count=150)

        image = self.apply_wave_effect(image, amplitude=5, frequency=15)
        image = self.apply_wave_effect(image, amplitude=3, frequency=20)
        image = image.filter(ImageFilter.GaussianBlur(radius=1))

        return image, text

    def generate(self, level, text=None):
        methods = {1: self.level1, 2: self.level2, 3: self.level3, 4: self.level4}
        if level not in methods:
            raise ValueError("레벨은 1, 2, 3, 4 중 하나여야 합니다.")
        return methods[level](text)


# ── 메인: 레벨별 폴더에 이미지 생성 ──────────────────────────────
# 파일명 = 정답 텍스트 (예: AB123.png), 중복 시 재생성
if __name__ == "__main__":
    base_path = r"C:\Users\wave\Desktop\train"
    generator = CaptchaGenerator()

    for level in range(1, 5):
        level_folder = os.path.join(base_path, f"level{level}")
        os.makedirs(level_folder, exist_ok=True)

        print(f"레벨 {level} 생성 중...")
        for i in range(1500):
            image, text = generator.generate(level)
            filename = f"{text}.png"
            filepath = os.path.join(level_folder, filename)

            while os.path.exists(filepath):  # 중복 파일명 방지
                text = generator.generate_text()
                filename = f"{text}.png"
                filepath = os.path.join(level_folder, filename)

            image.save(filepath)
            if (i + 1) % 20 == 0:
                print(f"  {i + 1}/1500 생성 완료")

        print(f"레벨 {level} 완료!\n")

    print("모든 CAPTCHA 이미지 생성 완료!")
