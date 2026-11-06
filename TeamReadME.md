요청하신 내용을 반영하여, 최종 `README.md` 파일과 PR 이력은 가급적 **영어**로 작성해 주시되, 혹시 어려우신 경우 마지막에 직접 영어로 통합해 주겠다는 안내 멘트를 포함한 완성본 마크다운을 작성해 드립니다.

---

```markdown
# 🧬 Cancer Sub-Classification Project

암 서브 타입 분류 모델 개발 및 예측을 위한 머신러닝/딥러닝 프로젝트입니다.

---

## 📁 프로젝트 구조 (Directory Structure)

```text
project/
├── data/                    # 제공된 데이터 파일
│   ├── train.csv
│   └── test.csv
├── notebooks/               # EDA 및 실험용 Jupyter Notebook
│   ├── eda.ipynb
│   ├── baseline_model.ipynb
│   └── feature_engineering.ipynb
├── src/                     # 모듈화된 소스 코드
│   ├── preprocess.py        # 데이터 전처리
│   ├── train.py             # 모델 학습
│   └── predict.py           # 예측 및 submission 생성
├── models/                  # 학습 완료된 모델 저장 (.pkl, .pt 등)
│   └── model.pkl
├── submission/              # 해커톤/대회 제출용 파일
│   └── submission.csv
├── README.md
└── requirements.txt

```

### 💡 모델 관리 및 개발 워크플로우 (Model Management Workflow)

프로젝트 진행 시 코드 및 모델 파일은 아래 2단계 절차를 거쳐 관리합니다.

* **1단계: 실험 및 개별 모델링 (`models/` 단독 활용)**
* 아이디어 검증, 피처 엔지니어링, 파라미터 튜닝 등 개별 실험 단계에서는 생성된 모델 파일 및 관련 코드를 우선 `models/` 폴더 하위에 자유롭게 보관하고 공유합니다.
* 빠른 실험과 결과 공유를 최우선으로 진행합니다.


* **2단계: 최종 선정 및 파이프라인 구조화**
* 팀 내 논의를 통해 최종 모델이 선정되면 다음과 같이 역할에 맞게 코드를 정돈하여 정식 구조에 배치합니다:
* `notebooks/`: 최종 모델 선정을 위한 실험 과정과 EDA, 시각화 정리
* `src/`: 최종 선정 모델을 학습(`train.py`), 전처리(`preprocess.py`), 예측(`predict.py`)하는 완성된 공통 파이프라인 모듈화
* `models/`: 완성된 파이프라인이 로드하여 사용할 최종 가중치 모델(`model.pkl`)만 최상단에 배치





---

## 🤝 팀 협업 및 Git / PR 원칙 (Rules of Engagement)

서로의 작업을 존중하고 충돌(Conflict) 없는 쾌적한 협업 환경을 유지하기 위해 아래 원칙을 **엄격히 준수**합니다.

1. **무단 Merge 금지 & 독단적 처리 금지**
* 사전 상의 없이 말없이 병합(Merge)하거나, 특정 팀원 1인이 일방적으로 모든 PR을 Merge하지 않습니다.
* 모든 PR은 **최소 1인 이상의 리뷰 및 팀 승인**을 거친 후 병합합니다.


2. **Conflict(충돌) 사전 해결 및 팀 논의**
* PR을 생성하거나 Merge하기 전, 반드시 로컬에서 최신 `main` 브랜치를 pull/rebase하여 Conflict를 먼저 해결합니다.
* 코드 충돌이나 중복 작업 영역이 발생하는 경우, **즉시 팀원들과 논의 후 병합 방향을 결정**합니다.


3. **효율적인 역할 분담 (無理한 분할 자제)**
* 나누기 모호하거나 의존성이 높은 작업은 억지로 분할하여 충돌을 야기하지 않습니다.
* 1인 담당 단위로 명확히 나눌 수 있는 모듈(EDA, 전처리, 모델링, 파이프라인 등)별로 역할을 분담하여 작업 영역 간 겹침을 최소화합니다.



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
