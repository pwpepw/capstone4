"""
captcha_ablation_only.py
========================
Ablation 전용 CAPTCHA 데이터셋 생성기

모델 특성:
  SVM, CNN        : 분할 기반  → 블러/웨이브가 분할을 망가뜨림
  CRNN+CTC        : 비분할     → 모든 변수가 모델 성능에 직접 영향
  CRNN+Attention  : 비분할     → 모든 변수가 모델 성능에 직접 영향

Ablation 기준점:
  SVM  → Lv2 기준 (블러/웨이브 없는 상태에서 추가)
  CNN  → Lv3 기준 (블러/웨이브를 버텼고 Lv4에서 붕괴)
  CRNN+CTC / Attention → 결과 확인 후 결정
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
import os
import math


# ── 공통 설정 ─────────────────────────────────────────────────────
WIDTH, HEIGHT = 160, 60
CHARS = string.digits + string.ascii_uppercase  # 0-9, A-Z
COUNT = 1000   # 변수 단계별 생성 장수


# ══════════════════════════════════════════════════════════════════
# 핵심 생성기 클래스
# ══════════════════════════════════════════════════════════════════

class AblationGenerator:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width  = width
        self.height = height

    def _text(self):
        return ''.join(random.choice(CHARS) for _ in range(5))

    def _font(self, size=30):
        for path in ["arial.ttf", "Arial.ttf"]:
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
        return ImageFont.load_default()

    def _lines(self, draw, count):
        for _ in range(count):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)
            color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
            draw.line([(x1,y1),(x2,y2)], fill=color, width=1)

    def _dots(self, draw, count):
        for _ in range(count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            draw.point((x,y), fill='black')

    def _wave(self, image, amplitude, frequency):
        w, h = image.size
        src  = image.load()
        dst_img = Image.new('RGB', (w, h), color='white')
        dst = dst_img.load()
        for y in range(h):
            for x in range(w):
                nx = x + int(amplitude * math.sin(2 * math.pi * y / frequency))
                if 0 <= nx < w:
                    dst[nx, y] = src[x, y]
        return dst_img

    # ─────────────────────────────────────────────────────────────
    # SVM Ablation 기반 이미지 생성 (기준점: Lv2)
    #
    # Lv2 고정값: 회전±30°, 선3개, 점50개, 블러없음, 웨이브없음
    # 변경 변수 : blur_radius / wave_configs
    # ─────────────────────────────────────────────────────────────
    def svm_base(self, blur_radius=0, wave_configs=None, text=None):
        """
        SVM Ablation 기본 생성기
        blur_radius : 0 = 블러 없음 / 0.5, 1, 2, 3
        wave_configs: None or [(amp, freq), ...]
        """
        if text is None:
            text = self._text()
        if wave_configs is None:
            wave_configs = []

        image = Image.new('RGB', (self.width, self.height), color='white')
        draw  = ImageDraw.Draw(image)
        font  = self._font()

        step     = 26
        x_offset = (self.width - len(text) * step) // 2

        for char in text:
            ci = Image.new('RGBA', (40, 50), color=(255,255,255,0))
            cd = ImageDraw.Draw(ci)
            cd.text((10,10), char, fill='black', font=font)
            rot = ci.rotate(random.randint(-30, 30),
                            expand=False, fillcolor=(255,255,255,0))
            image.paste(rot, (x_offset, 5), rot)
            x_offset += step

        self._lines(draw, count=3)
        self._dots(draw, count=50)

        for amp, freq in wave_configs:
            image = self._wave(image, amp, freq)

        if blur_radius > 0:
            image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        return image, text

    # ─────────────────────────────────────────────────────────────
    # CNN Ablation 기반 이미지 생성 (기준점: Lv3)
    #
    # Lv3 고정값: 회전±40°, 선5개, 점100개, 블러1, 웨이브3/25
    # 변경 변수 : rotation_range / wave_configs / overlap
    # ─────────────────────────────────────────────────────────────
    def cnn_base(self, rotation_range=40, wave_configs=None,
                 overlap=False, text=None):
        """
        CNN Ablation 기본 생성기
        rotation_range: 회전각 범위 (±)
        wave_configs  : [(amp, freq), ...] — Lv3 기본은 [(3,25)]
        overlap       : True = 글자 중첩 (step=15), False = 일반 (step=28)
        """
        if text is None:
            text = self._text()
        if wave_configs is None:
            wave_configs = [(3, 25)]   # Lv3 기본값

        image = Image.new('RGB', (self.width, self.height), color='white')
        draw  = ImageDraw.Draw(image)
        font  = self._font()

        step = 15 if overlap else 28
        if overlap:
            char_width  = 30
            total_width = (len(text) - 1) * step + char_width
            x_offset    = (self.width - total_width) // 2
        else:
            x_offset = (self.width - len(text) * step) // 2

        for char in text:
            ci = Image.new('RGBA', (40, 50), color=(255,255,255,0))
            cd = ImageDraw.Draw(ci)
            color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
            cd.text((10,10), char, fill=color, font=font)
            rot = ci.rotate(random.randint(-rotation_range, rotation_range),
                            expand=False, fillcolor=(255,255,255,0))
            image.paste(rot, (x_offset, random.randint(5,10)), rot)
            x_offset += step

        self._lines(draw, count=5)
        self._dots(draw, count=100)

        for amp, freq in wave_configs:
            image = self._wave(image, amp, freq)

        # Lv3 기준 블러=1 고정
        image = image.filter(ImageFilter.GaussianBlur(radius=1))

        return image, text


# ══════════════════════════════════════════════════════════════════
# 폴더 저장 헬퍼
# ══════════════════════════════════════════════════════════════════

def save_dataset(folder, gen_func, count=COUNT):
    """
    gen_func: 인자 없이 호출하면 (image, text) 반환하는 함수
    중복 텍스트 방지 후 저장
    """
    os.makedirs(folder, exist_ok=True)
    generated = set()
    i = 0
    while i < count:
        image, text = gen_func()
        if text in generated:
            continue
        generated.add(text)
        image.save(os.path.join(folder, f"{text}.png"))
        i += 1
        if i % 200 == 0:
            print(f"  {i}/{count}")
    print(f"  ✅ 완료: {os.path.basename(folder)}")


# ══════════════════════════════════════════════════════════════════
# SVM Ablation 데이터셋 생성
# 기준점: Lv2 (회전±30°, 선3, 점50, 블러없음, 웨이브없음)
# 변경 변수: 블러 / 웨이브
# ══════════════════════════════════════════════════════════════════

def generate_svm_ablation(base_path, count=COUNT):
    gen  = AblationGenerator()
    root = os.path.join(base_path, "ablation_svm")

    tasks = [
        # ── 블러 실험 (웨이브 없음 고정) ──────────────────────────
        # "블러 몇에서 투영 분할이 무너지는가"
        ("blur_none",  lambda: gen.svm_base(blur_radius=0,   wave_configs=[])),
        ("blur_0.5",   lambda: gen.svm_base(blur_radius=0.5, wave_configs=[])),
        ("blur_1",     lambda: gen.svm_base(blur_radius=1,   wave_configs=[])),
        ("blur_2",     lambda: gen.svm_base(blur_radius=2,   wave_configs=[])),
        ("blur_3",     lambda: gen.svm_base(blur_radius=3,   wave_configs=[])),

        # ── 웨이브 실험 (블러 없음 고정) ──────────────────────────
        # "웨이브 몇에서 투영 분할이 무너지는가"
        ("wave_none",       lambda: gen.svm_base(blur_radius=0, wave_configs=[])),
        ("wave_3_25",       lambda: gen.svm_base(blur_radius=0, wave_configs=[(3,25)])),
        ("wave_5_15",       lambda: gen.svm_base(blur_radius=0, wave_configs=[(5,15)])),
        ("wave_5_15_3_20",  lambda: gen.svm_base(blur_radius=0, wave_configs=[(5,15),(3,20)])),
    ]

    print("\n[SVM Ablation 생성 시작]")
    for folder_name, func in tasks:
        print(f"\n  → {folder_name}")
        save_dataset(os.path.join(root, folder_name), func, count)

    print(f"\n✅ SVM Ablation 완료: {root}")


# ══════════════════════════════════════════════════════════════════
# CNN Ablation 데이터셋 생성
# 기준점: Lv3 (회전±40°, 선5, 점100, 블러1, 웨이브3/25)
# 변경 변수: 회전 / 웨이브 강화 / 중첩
# ══════════════════════════════════════════════════════════════════

def generate_cnn_ablation(base_path, count=COUNT):
    gen  = AblationGenerator()
    root = os.path.join(base_path, "ablation_cnn")

    tasks = [
        # ── 회전각 실험 (나머지 Lv3 고정) ─────────────────────────
        # Lv3(±40°)에서 버텼으니 그 이상 구간 탐색
        ("rotation_40",  lambda: gen.cnn_base(rotation_range=40,  wave_configs=[(3,25)], overlap=False)),
        ("rotation_55",  lambda: gen.cnn_base(rotation_range=55,  wave_configs=[(3,25)], overlap=False)),
        ("rotation_70",  lambda: gen.cnn_base(rotation_range=70,  wave_configs=[(3,25)], overlap=False)),
        ("rotation_85",  lambda: gen.cnn_base(rotation_range=85,  wave_configs=[(3,25)], overlap=False)),

        # ── 웨이브 강화 실험 (나머지 Lv3 고정) ────────────────────
        # Lv3(3/25)에서 버텼으니 웨이브를 강화해가며 붕괴 지점 탐색
        ("wave_3_25",      lambda: gen.cnn_base(wave_configs=[(3,25)],          overlap=False)),
        ("wave_5_15",      lambda: gen.cnn_base(wave_configs=[(5,15)],          overlap=False)),
        ("wave_5_15_3_20", lambda: gen.cnn_base(wave_configs=[(5,15),(3,20)],   overlap=False)),

        # ── 중첩 실험 (나머지 Lv3 고정) ───────────────────────────
        # Lv4에서 중첩이 추가됨 → 중첩만 추가했을 때 얼마나 무너지는가
        ("overlap_off",  lambda: gen.cnn_base(wave_configs=[(3,25)], overlap=False)),
        ("overlap_on",   lambda: gen.cnn_base(wave_configs=[(3,25)], overlap=True)),
    ]

    print("\n[CNN Ablation 생성 시작]")
    for folder_name, func in tasks:
        print(f"\n  → {folder_name}")
        save_dataset(os.path.join(root, folder_name), func, count)

    print(f"\n✅ CNN Ablation 완료: {root}")


# ══════════════════════════════════════════════════════════════════
# 메인
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    base_path = r"C:\Users\wave\Desktop\train"

    generate_svm_ablation(base_path, count=COUNT)
    generate_cnn_ablation(base_path, count=COUNT)

    print("\n모든 Ablation 데이터셋 생성 완료!")
    print(f"경로: {base_path}")
    print("""
생성된 폴더 구조:
train/
├── ablation_svm/
│   ├── blur_none/       ← 블러 없음 (기준)
│   ├── blur_0.5/        ← 블러 0.5
│   ├── blur_1/          ← 블러 1 (Lv3 수준)
│   ├── blur_2/
│   ├── blur_3/
│   ├── wave_none/       ← 웨이브 없음 (기준)
│   ├── wave_3_25/       ← 웨이브 3/25 (Lv3 수준)
│   ├── wave_5_15/
│   └── wave_5_15_3_20/
└── ablation_cnn/
    ├── rotation_40/     ← 회전 ±40° (기준)
    ├── rotation_55/
    ├── rotation_70/
    ├── rotation_85/
    ├── wave_3_25/       ← 웨이브 3/25 (기준)
    ├── wave_5_15/
    ├── wave_5_15_3_20/
    ├── overlap_off/     ← 중첩 없음 (기준)
    └── overlap_on/      ← 중첩 있음 (Lv4 수준)
    """)
