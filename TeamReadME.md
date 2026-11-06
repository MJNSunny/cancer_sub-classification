
---

```markdown
# 🧬 Cancer Sub-Classification Project

암 서브 타입 분류 모델 개발 및 예측을 위한 머신러닝/딥러닝 프로젝트입니다.

---

## 📁 프로젝트 구조 및 협업 워크플로우 (Project Structure & Workflow)

우리 팀은 효율적인 실험과 쾌적한 협업을 위해 **2단계 개발 프로세스**로 프로젝트를 진행합니다.

### 📌 1단계: 자유로운 실험 및 모델/결과물 공유 단계 (현재 진행 중)
깃허브 복잡한 설정이나 충돌을 최소화하기 위해, 초반에는 각자 로컬 환경에서 실험하고 결과물만 명확히 네이밍하여 공유합니다.
* *주의: 대용량 데이터(`data/`)는 깃허브 용량 관리 및 보안을 위해 각자 로컬에만 두고 `.gitignore`로 제외합니다.*

```text
project/
├── data/                    # 각자 로컬에 다운로드하여 보관 (.gitignore 처리)
├── models/                  # 각자 이름이 붙은 피클 파일 모아두는 곳 (예: model_민정.pkl)
├── submission/              # 각자 이름이 붙은 제출 파일 모아두는 곳 (예: submission_민정.csv)
└── notebooks/               # 각자 실험한 Jupyter Notebook (.ipynb 파일) 모아두는 곳

```

### 🚀 2단계: 최종 모델 선정 및 실무형 파이프라인 구조화 (대회 막바지 전환)

팀 내에서 성능이 가장 뛰어난 **최종 모델**이 결정되면, 코드의 재현성(Reproducibility)과 확장성을 위해 아래와 같은 **현업/MLOps 표준 폴더 구조**로 코드를 정돈하고 통합합니다.

```text
project/
├── data/                    # 데이터 (raw / processed 분리 관리)
├── notebooks/               # 탐색적 분석 및 실험용 노트북 보관
├── src/                     # 실제 서비스 및 재현 가능한 파이프라인용 모듈 소스 (.py)
│   ├── features.py          # 공통 피처 엔지니어링 및 전처리 함수
│   ├── train.py             # 최종 모델 학습 스크립트
│   └── predict.py           # 추론 및 최종 submission 생성 스크립트
├── models/                  # 최종 선정된 모델 아티팩트 (model.pkl) 단독 보관
├── pyproject.toml           # 프로젝트 의존성 및 패키지 설정
└── README.md

```

---

## 🤝 팀 협업 규칙 및 Git / PR 원칙 (Rules of Engagement)

서로의 작업을 존중하고 충돌(Conflict) 없는 쾌적한 협업 환경을 유지하기 위해 아래 원칙을 **엄격히 준수**합니다.

1. **파일 업로드 네이밍 규칙**
* `models/`와 `submission/`에 파일을 올릴 때는 파일명에 반드시 본인 이름(아이디)을 포함해 주세요. (예: `model_minjung.pkl`)


2. **데이터 공유**
* 데이터(`.csv`)는 깃허브에 올라가지 않으므로, 데이콘/공유 드라이브를 통해 각자 로컬 `data/` 폴더에 세팅해 주세요.


3. **무단 Merge 금지 & 충돌 사전 해결**
* 사전 상의 없이 일방적으로 Merge하지 않으며, 푸시하기 전 반드시 `git pull`을 실행하여 최신 상태를 유지해 주세요.



> **💡 Note for Team:** 현업 실무 기준에 맞춰 **최종 `README.md` 파일 및 PR(Pull Request) 이력은 가급적 영어로 작성**해 주시는 것을 권장합니다! 혹시 영어 작성에 부담을 느끼거나 어려우시다면 편하게 한국어로 작성해 주세요. **마지막에 제가 직접 깔끔한 비즈니스/개발 영어로 통합 및 교정**해 드리겠습니다. (Feel free to write in Korean if English is difficult; I will consolidate and translate them into professional English at the end!)

---

## ⚠️ 데이터 누수(Data Leakage) 방지 기본 원칙 & 체크리스트

올바른 검증(Validation) 스코어와 안정적인 실전 테스트 성능을 위해 전처리 및 데이터 처리는 아래 원칙을 필수로 지킵니다.

### 📋 한 줄 체크리스트

* [ ] 전처리는 **항상 train 데이터에서만 fit** 한다.
* [ ] valid 와 test 데이터에는 **transform 만** 수행한다.
* [ ] Cross Validation(CV)을 쓸 때는 scaler, imputer, encoder 도 **fold 안에서 다시 fit** 한다.
* [ ] 컬럼 차원을 맞추기 위해 **test 데이터를 먼저 보는 습관을 버린다.**
* [ ] 점수 차이가 작아 보여도, 실제 평가 환경에서는 데이터 누수로 인해 **결과가 크게 바뀔 수 있음**을 명심한다.

> 💡 **Tip:** 단순히 모델 성능만 확인하는 것이 아니라, 전처리와 검증 파이프라인이 얼마나 깨끗하게 설계되었는지 항상 함께 점검해 주세요!

---

### 🛡️ 안전한 데이터 처리 기준표

| 영역 | 안전한 기본 원칙 |
| --- | --- |
| **인코딩 (Encoding)** | `train`에서만 기준 생성, `valid` / `test`는 동일 기준 `transform`만 적용 |
| **스케일링 (Scaling)** | Fold 내부의 `train split`에만 `fit` |
| **결측치 처리 (Imputation)** | 평균, 중앙값, KNN 기준 모두 `train`에서만 계산 후 적용 |
| **파생 변수 (Feature)** | `test` 분포를 미리 보고 구간화(Binning) 등의 기준을 정하지 않기 |
| **최종 점검** | 코드에 `concat(train, test)` 후 `fit`하는 구문이 있는지 가장 먼저 확인 |

---