캡차 이미지에 대해 **SVM, CNN, CRNN+CTC** 모델을 비교하여 인식 성능을 분석하는 프로젝트입니다.  
또한 캡차 왜곡 수준(Level 1~4)에 따른 성능 변화를 함께 확인합니다.

---

## 1. 프로젝트 개요

이 프로젝트는 텍스트 캡차 인식 문제를 대상으로
- SVM
- CNN
- CRNN+CTC

세 가지 모델의 성능을 비교합니다.
실험은 Google Colab 환경에서 진행하며, 합성 데이터를 이용해 캡차 이미지를 생성하고 전처리 후 학습합니다.

## 2. 목적

이 프로젝트의 목적은  **왜곡된 캡차 환경에서 어떤 모델이 더 강건하게 인식하는지 비교하는 것**입니다.

---

## 3. 폴더 구조

```
data/
  sample_captcha/        ← 샘플 CAPTCHA 이미지
    level1/
    level2/
    level3/
    level4/

docs/                    ← 개발 계획서, 기능 명세서 등 문서


models/                  ← 학습 완료된 모델 파일 (.pkl / .pth)
  svm/
    svm.pkl
  cnn/
    cnn.pth
  crnn_ctc/
    crnn_ctc.pth
  crnn_attention/
    crnn_attention.pth

pythoncode/              ← 모델 구현 코드 (.py)
  svm/
    svm.py
  cnn/
    cnn.py
  crnn_ctc/
    crnn_ctc.py
  crnn_attention/
    crnn_attention.py

README.md                ← 프로젝트 설명
```

---

## 4. 실험 대상

- 문자 집합: 0~9, A~Z
- 총 36개 클래스
- 5자 고정 길이 캡차
- 왜곡 수준: Level 1 ~ Level 4

---

## 5. 사용 환경

- Google Colab
- Python
- Pillow
- scikit-learn
- TensorFlow / Keras
- matplotlib

※ 라이브러리는 실험 진행 중 일부 변경될 수 있습니다.

---

## 6. 평가 지표

다음 3가지를 중심으로 평가합니다.

1. 이미지 정확도  (전체 정확도)
   - 전체 5글자가 모두 맞았는지 확인
2. 글자 정확도  
   - 개별 글자 단위로 얼마나 맞았는지 확인
3. 학습 시간  
   - 모델별 학습 속도 비교

추후 실험 결과에 따라
- 추론 시간
- 혼동 행렬
도 추가로 고려해볼 예정입니다.

---

## 7. 한계점 및 제약

- 합성 데이터 기반이므로 실제 서비스 CAPTCHA와 차이가 있을 수 있습니다.
- 36개 클래스와 5자 고정 길이로 실험하므로, 가변 길이 CAPTCHA는 포함하지 않습니다.
- 왜곡 수준은 공식 기준이 없어 연구 목적에 맞게 자체 정의하였으며, 실제 CAPTCHA와는 차이가 있을 수 있습니다.

---

## 8. 실행 계획

1. `generator.py`로 캡차 생성
2. `preprocessing.py`로 전처리
3. `experiment.py`에서 SVM, CNN, CRNN+CTC 순차 실행
4. `result.json`에 결과 저장 & `visualize.py`로 그래프 생성
5. `report` 파일로 최종 정리

---
