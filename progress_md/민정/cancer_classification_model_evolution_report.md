# 암종 분류 모델(Cancer Classification Model) v6 ~ v13 버전에 대한 종합 보고서

---

## 1. 개요 및 프로젝트 목표
본 프로젝트는 환자의 지노믹 변이 데이터(SNV, InDel, CNV 등) 및 유전자 패널 프로필을 바탕으로 암종(Cancer Type)을 정확하게 예측하고 분류하는 머신러닝 시스템을 개발하는 것을 목표로 합니다. 

v6 버전부터 v13 버전에 이르기까지 **(1) 도메인 지식(생물학적/의학적 지식) 기반 피처 엔지니어링**, **(2) 타깃 누수(Data Leakage) 차단 및 엄격한 그룹 분할 검증**, **(3) 다변화된 앙상블 기법 및 확률 보정**, **(4) 배포 안정성 확보**를 중심으로 고도화가 진행되었습니다.

---

## 2. 버전별 핵심 변경점 상세 요약

| 버전 | 핵심 테마 | 주요 변경 사항 및 기술적 특징 |
| :--- | :--- | :--- |
| **v6** | **변이 정규화 및 가이드 기반 피처 도입** | • `EGFR E746_A750del` 등 인프레임(Inframe) 변이 전용 토큰 추가 (`gene\|inframe`, `gene\|위치_inframe` 등)<br>• 임상 가이드 기반 동반변이 콤보 피처(`cb_*`) 및 TMB 분절 기준(5 / 30) 도입<br>• 변이 정규화 함수(`canon`) 및 `NORMALIZE_TOKENS`를 적용해 중복 표기 정리<br>• 불안정했던 EM 사전확률 보정 로직을 제거하고 CV 함수화 및 콤보 Ablation 셀 구조 구축 |
| **v7** | **앙상블 다양화 및 OOF 확률 보정** | • XGBoost(부스팅), Logistic Regression(선형) 외 3번째 모델로 배깅 계열의 **ExtraTrees** (`USE_ET`) 도입<br>• CUPLR 기법을 차용한 **Isotonic / Temperature Scaling** 보정 기법을 OOF 교차 적합 체계 내에서 비교하고, 실질적 이득이 있는 경우에만 선택 적용 |
| **v8** | **엄격한 CV 분할 (Group K-Fold)** | • 데이터셋 내 동일/쌍둥이(Twin) 프로필로 인해 검증 점수가 과도하게 부풀려지는 현상 차단<br>• 프로필 해시(Hash) 기준의 **Group K-Fold (`StratifiedGroupKFold`)** 도입<br>• 라벨을 강제로 수정하던 기존 쌍둥이 규칙을 기본 OFF(`USE_TWIN=False`)로 전환하고 진단용으로만 활용 |
| **v9** | **희소 변이 샘플 대응 및 누수 없는 KNN** | • 변이 수가 적은 샘플(0개, 2개 이하, TMB_LOW)의 분류 성능을 위한 희소성 메타 피처 (`sp_*`) 구축<br>• Jaccard 유사도 기반 **KNN 피처 (`knn_p_*`)** 추가<br>• KNN 계산 시 완전 동일 프로필(자기 자신 및 중복 행)을 탐색에서 제외하여 **타깃 누수(Target Leakage) 완벽 차단** |
| **v10** | **학습형 중복 처리 및 중첩 검증(Nested CV)** | • 하드코딩된 중복 처리 규칙 대신 **Leave-One-Out 학습 표** 기반의 학습형 규칙(`USE_DUP_RULE`) 도입<br>• 클래스별 확률 배율 보정에 **Nested CV**를 도입하여 과적합 방지<br>• 무작위 분할과 그룹 분할 점수를 동시 비교하는 정직한 리포팅 시스템 구축 및 실험 재현성을 위한 `run_manifest` JSON 출력 추가 |
| **v11 & v12** | **생물학적 변이 고도화 및 LGBM 도입** | • 오분류 패턴 보완을 위한 **LightGBM**을 앙상블 멤버로 추가<br>• 미스센스 변이의 물리화학적 변화량(Grantham Score, 전하·소수성·부피 변화 등) 계산 피처 추가<br>• 대립유전자 핫스팟 토큰(`USE_HS_ALLELE`), 경로별 절단 변이 유전자 분리(`USE_PW_TYPE`), 경로 간 동반 변이(`USE_PW_PAIR`) 피처 추가<br>• 그룹 분할 기반 자동 Ablation 프로세스를 통한 검증 피처 선별 |
| **v13** | **시드 평균, 행 정규화 및 파이프라인 완성** | • LightGBM 자동 설치 및 시드 평균(Seed Averaging)으로 예측 안정성 향상<br>• 스케일 불균형을 맞추기 위한 **행 L2 정규화 Logistic Regression (`lrn`)** 도입<br>• 실제 그룹 CV 상에서 검증된 우수 피처 조합(`USE_HS_ALLELE` 등) 선별 적용<br>• 현업 제출용 `_core` 모델과 규칙 적용형 `_dup` 모델을 분리 생성하고 적대적 검증(Adversarial Validation) 기반 데이터 분포 검증 수행 |

---

## 3. 핵심 기술 및 모듈별 상세 분석

### 3.1. 피처 엔지니어링 (Feature Engineering)
1. **변이 정규화 (Normalization)**:
   - `canon()` 함수를 통한 변이 표기 표준화 (`NORMALIZE_TOKENS`).
   - 동일 셀 내 중복 발생 변이의 필터링 및 토큰 표준화를 통해 입력 데이터 정형화.
2. **생물학적 변이 특성 추출 (Physicochemical & Structural Features)**:
   - **Grantham Score**: 아미노산 치환 시 물리화학적 거리(전하, 소수성, 아미노산 크기/부피 차이)를 정량화하여 변이의 치명도 반영.
   - **대립유전자 핫스팟 (`USE_HS_ALLELE`)**: 단순 유전자 단위 핫스팟을 넘어 특정 아미노산 위치 및 변이 종류 단위로 토큰화.
   - **경로 분석 (`USE_PW_TYPE`, `USE_PW_PAIR`)**: 주요 암 억제/진증 경로(DDR, RTK/RAS, PI3K 등) 내 절단 변이 유전자를 분리하고, 경로 간 동반 변이를 피처 생성에 활용.
3. **희소성 메타 피처 및 KNN 피처**:
   - `sp_*`: 변이가 적거나 관찰되지 않은 샘플(TMB Low / 0개 변이)을 식별하기 위한 메타 피처.
   - `knn_p_*`: Jaccard 거리 기반 유사 프로필 암종 확률 계산. 이때 **자기 자신 및 Identical/Twin 행을 제외**하여 타깃 누수를 원천 방지함.

### 3.2. 검증 체계 (Validation Strategy)
- **Stratified Group K-Fold**:
  - 동일/유사 유전자 프로필 해시(`NORM_HASH`)를 그룹 식별자로 지정하여 동일 환자 또는 중복 샘플이 Train과 Validation에 동시에 들어가는 현상(Data Leakage)을 완벽하게 방지.
- **Nested CV & Ablation Study**:
  - 확률 보정(Probability Calibration) 시 발생할 수 있는 데이터 누수를 막기 위해 중첩 검증 구조 적용.
  - 신규 피처 추가 시 무조건 채택하지 않고, 그룹 CV 점수의 향상 여부를 판단하는 자동 Ablation 프로세스 구축.

### 3.3. 모델링 및 앙상블 (Modeling & Ensemble)
- **다양한 알고리즘 조합**:
  1. **Gradient Boosting**: XGBoost, LightGBM (시드 평균화 적용으로 변동성 최소화)
  2. **Bagging**: ExtraTrees Classifier
  3. **Linear**: Row-L2 Normalized Logistic Regression (`lrn`)
- **확률 보정 (Probability Calibration)**:
  - Isotonic Regression 및 Temperature Scaling을 CV 내부 OOF(Out-of-Fold) 예측에 적용해 예측 확률의 캘리브레이션을 상시 검증.

### 3.4. 파이프라인 배포 및 데이터 관리 (Operationalization)
- **`run_manifest.json`**: 실행 시점의 하이퍼파라미터, 사용된 피처 플래그, CV 점수 및 무작위 분할 점수를 기록하여 완벽한 재현성(Reproducibility) 확보.
- **이중 제출 파일 분리**:
  - 순수 모델 예측치 기반의 **`_core` 제출 파일** (안정적인 배포용).
  - 중복 학습 규칙이 반영된 **`_dup` 제출 파일** (후처리 규칙 적용용).

---

## 4. 결론 및 발전 방향
v6부터 v13까지의 고도화를 통해 모델의 예측 성능뿐만 아니라, **검증의 신뢰도(Group CV 도입)**와 **도메인 지식의 깊이(물리화학적 피처 및 동반변이 콤보)**가 대폭 향상되었습니다. 

향후 버전 확장 시에는 적대적 검증(Adversarial Validation) 결과를 더욱 적극적으로 활용하여 Train/Test 간의 분포 불균형을 해소하고, 차원 축소 기법(UMAP/t-SNE 기반 메타 피처)과의 연계를 고려해볼 수 있습니다.