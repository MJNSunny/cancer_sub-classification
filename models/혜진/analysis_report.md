# 암환자 유전체 변이 기반 암종 분류 분석 보고서

## 1. 목적과 결과
유전자별 WT/변이 문자열만으로 데이터셋의 SUBCLASS 26개를 예측했다. 공식 평가 지표가 제공되지 않아 macro F1을 선택 기준으로 삼았다. 최고 성능의 전역적 보장을 의미하는 “최적”이 아니라, 아래 명시된 후보와 검증 범위에서 가장 좋은 구성을 선택했다.

- 선택된 모델: full_lr_balanced, full_extratrees. 둘이면 각 모델 확률을 0.5씩 평균한다.
- 개발 세트 3-fold 최고 평균 macro F1: 0.41833.
- 모델 선택에 사용하지 않은 홀드아웃 1241명: macro F1 **0.42370**, accuracy **0.42788**, weighted F1 **0.42912**.
- 고정된 홀드아웃 예측의 클래스별 층화 bootstrap 500회 조건부 95% 구간: [0.39208, 0.44994]. 모델 재학습 변동과 데이터 출처 차이를 반영하지 않는다.
- 최종 모델은 전체 학습 데이터로 재학습했고 피클 직렬화 후 재로딩 예측 일치를 확인했다. 테스트 정답이 없어 테스트 성능과 리더보드 성능은 알 수 없다.

## 2. 데이터 스키마와 정합성
실제 파일 기준 train 6,201행 × 4,386열, test 2,546행 × 4,385열이다. 문제 설명의 6,199 유전자와 다르게 실제 유전자는 **4,384개**다. train과 test의 유전자 이름 및 순서, 제출 ID 순서를 검증했다. 원본은 변경하지 않았다.

| 컬럼 | 의미 | 처리 및 이유 |
| --- | --- | --- |
| ID | 샘플 식별자 | 유일성과 제출 정렬 검증에만 사용. 모델 제외 |
| SUBCLASS | 학습 정답, 문자열 26종 | 목적변수. 입력 변수에서 제외 |
| 유전자 심볼 4,384개 | 해당 유전자의 WT 또는 변이 표기 문자열 | 변이 유무/토큰/위치/유형으로 변환 |
| WT | 기준형으로 표기된 셀 | 변이 특성 0. 결측과 별도로 처리 |
| 결측 | 미기록 셀 | missing:유전자 변수로 분리. 관측되지 않으면 빈도 필터로 제외 |

본 파일에는 나이, 성별, 병기, 조직, 변이 대립유전자 빈도, 시퀀싱 깊이, 표본 출처/배치 정보가 없다. 아미노산 표기만으로 유전자 기능 손상 여부나 원인 변이를 확정하지 않는다. 각 유전자 컬럼의 통계와 의미는 `artifacts/gene_dictionary.csv`에 한 행씩 제공한다: gene=원본 컬럼명, train_mutated/test_mutated=비-WT 환자 수, train_rate/test_rate=비-WT 비율, train_unique=훈련값 종류 수, missing=훈련 결측 수, test_minus_train_rate=테스트-학습 비율 차이. 이 파일은 4,384개 모든 컬럼을 포함한다. 유전자별 생물학적 기능 주석은 제공 데이터에 없으므로 임의로 작성하지 않았다.

학습에는 결측이 없어 최종 사전에 missing:G 변수가 없다. 테스트 결측은 파서에서 분리하지만 미등록 특성으로 무시되며 변이 이벤트로 세지 않는다. 따라서 이번 최종 모델은 테스트 결측의 불확실성을 별도로 학습하지 못하고, 해당 셀에서 알려진 변이 특성은 WT처럼 0이 되는 한계가 있다.

## 3. EDA 결과
- 학습 WT 셀 비율: 99.1948%. 매우 희소하므로 CSR 희소행렬로 학습한다.
- 학습 결측 0, 테스트 결측 237개.
- 학습 상수 유전자 154개. 희귀/무변이 변수는 폴드별 빈도 기준으로 제거한다.
- 동일 원본 프로파일에 속한 학습 행 1016개; 정답이 서로 다른 중복 그룹 447개.
- 테스트 중 학습과 동일한 프로파일 266개. 이를 정답 복사에 사용하지 않았다.
- 학습 환자의 비-WT 유전자 수 평균 35.30, 중앙값 14.0, 최대 2393; 테스트 평균 78.13, 중앙값 28.0, 최대 2784.

변이가 많은 샘플을 자동 제거하지 않았다. 높은 변이량은 분류 신호일 수도 있으므로 log1p로 규모 영향을 완화했다. 이 값은 분석된 4,384개 컬럼 내 변이 수이며 임상적 TMB가 아니다. 테스트 분포 비교는 기술통계에만 사용했고, 단어 사전/빈도/모델 적합은 테스트를 사용하지 않았다.

### 클래스 분포
| SUBCLASS | count |
| --- | --- |
| BRCA | 786 |
| KIPAN | 515 |
| GBMLGG | 461 |
| STES | 379 |
| KIRC | 334 |
| THCA | 324 |
| SKCM | 276 |
| PRAD | 266 |
| OV | 253 |
| LGG | 229 |
| HNSC | 223 |
| COAD | 223 |
| SARC | 198 |
| UCEC | 198 |
| LUAD | 184 |
| LUSC | 178 |
| LIHC | 158 |
| LAML | 158 |
| CESC | 155 |
| PCPG | 147 |
| TGCT | 124 |
| PAAD | 120 |
| BLCA | 104 |
| THYM | 98 |
| ACC | 72 |
| DLBC | 38 |

가장 작은 클래스는 표본이 적어 분할별 성능 분산이 크다. 전체 정확도만 높아지는 모델을 피하기 위해 클래스별 F1을 같은 비중으로 평균했다. class_weight='balanced' 후보도 실제 비교했다. 라벨 간 임상적 계층은 데이터에 없으므로 이름이 비슷해도 합치지 않았다.

### 클래스별 변이량
| SUBCLASS | count | mean | median | min | max |
| --- | --- | --- | --- | --- | --- |
| ACC | 72 | 39.43056 | 24.00000 | 10 | 396 |
| BLCA | 104 | 70.49038 | 54.00000 | 3 | 382 |
| BRCA | 786 | 17.43766 | 9.00000 | 0 | 853 |
| CESC | 155 | 44.12903 | 20.00000 | 0 | 480 |
| COAD | 223 | 73.12108 | 23.00000 | 5 | 1631 |
| DLBC | 38 | 67.42105 | 30.00000 | 3 | 704 |
| GBMLGG | 461 | 12.53579 | 11.00000 | 0 | 121 |
| HNSC | 223 | 40.56951 | 31.00000 | 1 | 386 |
| KIPAN | 515 | 16.04272 | 15.00000 | 0 | 246 |
| KIRC | 334 | 13.32934 | 13.00000 | 0 | 35 |
| LAML | 158 | 3.05696 | 3.00000 | 0 | 10 |
| LGG | 229 | 8.68996 | 8.00000 | 0 | 121 |
| LIHC | 158 | 31.33544 | 25.00000 | 2 | 286 |
| LUAD | 184 | 58.04348 | 40.50000 | 4 | 285 |
| LUSC | 178 | 69.52809 | 57.00000 | 0 | 579 |
| OV | 253 | 14.59289 | 12.00000 | 1 | 47 |
| PAAD | 120 | 36.28333 | 14.00000 | 0 | 2393 |
| PCPG | 147 | 4.42857 | 4.00000 | 0 | 10 |
| PRAD | 266 | 7.70301 | 6.00000 | 0 | 205 |
| SARC | 198 | 12.83333 | 9.00000 | 0 | 387 |
| SKCM | 276 | 132.53261 | 85.50000 | 3 | 2025 |
| STES | 379 | 81.84169 | 41.00000 | 0 | 1076 |
| TGCT | 124 | 16.71774 | 16.00000 | 2 | 127 |
| THCA | 324 | 4.25000 | 4.00000 | 0 | 25 |
| THYM | 98 | 4.37755 | 2.00000 | 0 | 152 |
| UCEC | 198 | 133.96970 | 18.00000 | 3 | 1861 |

### 변이 비율 상위 25개 유전자
| gene | train_mutated | train_rate | test_mutated | test_rate | train_unique | missing | test_minus_train_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TP53 | 1770 | 0.28544 | 1051 | 0.41280 | 664 | 0 | 0.12737 |
| PIK3CA | 686 | 0.11063 | 343 | 0.13472 | 208 | 0 | 0.02409 |
| RYR2 | 643 | 0.10369 | 361 | 0.14179 | 621 | 0 | 0.03810 |
| SYNE1 | 642 | 0.10353 | 444 | 0.17439 | 613 | 0 | 0.07086 |
| PCLO | 593 | 0.09563 | 351 | 0.13786 | 567 | 0 | 0.04223 |
| RYR1 | 473 | 0.07628 | 326 | 0.12804 | 455 | 0 | 0.05177 |
| SPTA1 | 461 | 0.07434 | 240 | 0.09427 | 440 | 0 | 0.01992 |
| KMT2D | 451 | 0.07273 | 492 | 0.19324 | 418 | 0 | 0.12051 |
| IDH1 | 441 | 0.07112 | 124 | 0.04870 | 34 | 0 | -0.02241 |
| BRAF | 438 | 0.07063 | 230 | 0.09034 | 93 | 0 | 0.01970 |
| DMD | 406 | 0.06547 | 225 | 0.08837 | 392 | 0 | 0.02290 |
| ATRX | 395 | 0.06370 | 149 | 0.05852 | 309 | 0 | -0.00518 |
| DST | 393 | 0.06338 | 262 | 0.10291 | 371 | 0 | 0.03953 |
| RELN | 377 | 0.06080 | 220 | 0.08641 | 365 | 0 | 0.02561 |
| APC | 367 | 0.05918 | 706 | 0.27730 | 331 | 0 | 0.21811 |
| PTEN | 367 | 0.05918 | 173 | 0.06795 | 270 | 0 | 0.00877 |
| PKHD1 | 360 | 0.05806 | 214 | 0.08405 | 341 | 0 | 0.02600 |
| AHNAK | 349 | 0.05628 | 774 | 0.30401 | 336 | 0 | 0.24773 |
| COL6A3 | 347 | 0.05596 | 254 | 0.09976 | 327 | 0 | 0.04381 |
| PLEC | 347 | 0.05596 | 284 | 0.11155 | 326 | 0 | 0.05559 |
| MXRA5 | 329 | 0.05306 | 224 | 0.08798 | 322 | 0 | 0.03493 |
| VHL | 326 | 0.05257 | 72 | 0.02828 | 145 | 0 | -0.02429 |
| NF1 | 315 | 0.05080 | 136 | 0.05342 | 287 | 0 | 0.00262 |
| FBN2 | 304 | 0.04902 | 193 | 0.07581 | 284 | 0 | 0.02678 |
| PEG3 | 302 | 0.04870 | 166 | 0.06520 | 288 | 0 | 0.01650 |

이 순위는 변이 빈도 순위이며 예측 기여도 순위가 아니다. 유전자의 길이, 측정 편향, 변이 발생률 등은 이 데이터만으로 분리할 수 없다.

### 학습/테스트 변이 비율 차이 상위 20개
| gene | train_rate | test_rate | test_minus_train_rate |
| --- | --- | --- | --- |
| TCHH | 0.03435 | 0.28830 | 0.25395 |
| AHNAK | 0.05628 | 0.30401 | 0.24773 |
| APC | 0.05918 | 0.27730 | 0.21811 |
| CACNA1A | 0.03774 | 0.18932 | 0.15158 |
| CPEB2 | 0.00613 | 0.14611 | 0.13998 |
| MAGEE1 | 0.01806 | 0.15397 | 0.13591 |
| TP53 | 0.28544 | 0.41280 | 0.12737 |
| KDM6B | 0.01435 | 0.13983 | 0.12547 |
| KMT2D | 0.07273 | 0.19324 | 0.12051 |
| TUBGCP6 | 0.01935 | 0.13904 | 0.11969 |
| HLA-A | 0.01516 | 0.12647 | 0.11131 |
| UBC | 0.01193 | 0.11862 | 0.10668 |
| HLA-B | 0.01242 | 0.10094 | 0.08853 |
| MUC1 | 0.00387 | 0.08837 | 0.08450 |
| PABPC1 | 0.01435 | 0.09387 | 0.07952 |
| MTCH2 | 0.00435 | 0.08288 | 0.07852 |
| CACNA1B | 0.03225 | 0.10762 | 0.07537 |
| NLGN2 | 0.01000 | 0.08366 | 0.07366 |
| SYNE1 | 0.10353 | 0.17439 | 0.07086 |
| RUNX1 | 0.01064 | 0.07777 | 0.06713 |

차이는 표본 변동과 클래스 비율 변화 모두로 생길 수 있다. 테스트 라벨이 없어 원인을 확정하거나 이를 근거로 유전자를 임의 삭제하지 않았다. 클래스별 유전자 비율 전체는 `gene_class_mutation_rates.csv`, 차트는 아래 파일에 저장했다.

![EDA](artifacts/eda.png)
![암종별 유전자 변이 비율](artifacts/class_gene_heatmap.png)

## 4. 파생변수 사전과 설계 근거
| 변수 이름 규칙 | 수식/정의 | 관점 및 이유 | 한계 |
| --- | --- | --- | --- |
| gene:G | 유전자 G에 비-WT 문자열이면 1 | 안정적인 유전자 단위 신호 | 변이 종류 소실 |
| variant:G:T | 유전자 G의 공백 분리 토큰 T 존재 | 반복되는 정확한 변이 포착 | 드문 토큰 과적합 |
| position:G:N | 토큰 첫 숫자 N의 존재 | 같은 위치의 다른 치환 공유 | 다른 전사체/좌표 불명 |
| type:G:K | 유전자별 표기 유형 K 존재 | 종류별 손상 패턴의 통계적 구분 | 기능 판정 아님 |
| numeric:log_mutated_genes | log(1+비-WT 유전자 수) | 환자 변이량과 긴 꼬리 완화 | 배치/측정 차이 민감 |
| numeric:log_events | log(1+토큰 수) | 한 유전자의 여러 이벤트 반영 | 공백 분리 가정 |
| numeric:multi_event_excess | log(1+max(이벤트 수-변이 유전자 수,0)) | 복수 이벤트 정도 | 임상적 클론성 아님 |
| numeric:log_K | log(1+유형 K 토큰 수) | 환자별 유형 구성 | 파서 품질 의존 |
| numeric:fraction_K | 유형 K 수/max(총 토큰 수,1) | 변이량과 구성 비율 분리 | 극소수 변이에서 불안정 |
| numeric:log_mean_position | log(1+숫자 위치 평균), 없으면 0 | 위치 분포의 탐색적 요약 | 유전자 길이 표준화 불가 |
| module:M | log(1+그룹 내 변이 유전자 수) | 연관 유전자 집합의 집계 | 불완전 수작업 그룹, 활성도 아님 |
| missing:G | 결측이면 1 | 측정 누락과 WT 구분 | 관측 빈도 부족 시 제거 |

유형 K는 frameshift(fs 포함), stop(* 포함), deletion(del 포함), insertion(ins 포함), synonymous(정규식 `[A-Z][0-9]+[A-Z]`에서 양쪽 아미노산 같음), substitution(다름), other이다. 이 순서로 우선 분류한다. 예: R132H=substitution, V600E=substitution, R213*=stop, K16fs=frameshift, L42L=synonymous. 정규식에서 유전체 치환의 생물학적 결과나 splice 변이를 추론하지 않는다. 위치·토큰·유형은 값 1인 존재 특성이고, 전역 개수는 토큰 기준이다. 같은 토큰 반복은 존재 특성에는 한 번, 개수에는 반복 반영된다.

### 탐색적 유전자 그룹의 정확한 구성

- `p53_cellcycle`: TP53, RB1, CDKN2A, CDKN2B, CDK4, CDK6, CCND1, ATM, CHEK2. 데이터 내 8개. 누락: ATM.

- `rtk_ras_mapk`: EGFR, ERBB2, ERBB3, KRAS, NRAS, HRAS, BRAF, NF1, MAP2K1, MAP2K2, KIT, PDGFRA, FGFR2, FGFR3. 데이터 내 8개. 누락: KRAS, NRAS, MAP2K1, MAP2K2, PDGFRA, FGFR2.

- `pi3k_mtor`: PIK3CA, PIK3R1, PTEN, AKT1, MTOR, TSC1, TSC2, STK11. 데이터 내 6개. 누락: PIK3R1, STK11.

- `dna_repair`: BRCA1, BRCA2, PALB2, ATM, ATR, CHEK2, MLH1, MSH2, MSH6, PMS2, POLE, POLD1. 데이터 내 8개. 누락: PALB2, ATM, ATR, MSH6.

- `chromatin`: ARID1A, ARID1B, ARID2, PBRM1, SMARCA4, BAP1, SETD2, KMT2A, KMT2C, KMT2D, ATRX. 데이터 내 2개. 누락: ARID1A, ARID1B, ARID2, PBRM1, SMARCA4, BAP1, SETD2, KMT2A, KMT2C.

- `wnt`: APC, CTNNB1, AXIN1, AXIN2, RNF43. 데이터 내 4개. 누락: RNF43.

- `metabolism`: IDH1, IDH2, SDHB, SDHC, SDHD, FH, VHL. 데이터 내 7개. 누락: 없음.

그룹은 중복될 수 있다(예: ATM). 개별 유전자 정보와 합산 지표를 함께 제공하는 탐색적 모델링 선택으로, 외부 검증된 경로 데이터베이스를 사용한 enrichment 분석이 아니다.

## 5. 검증 설계와 모델 비교
1. 고정 seed=42로 StratifiedGroupKFold 5개 중 첫 폴드를 홀드아웃으로 잠금. 동일한 원본 변이 프로파일 해시를 그룹으로 사용해 중복 행의 교차 누수를 막았다. 분할 ID는 split_manifest.csv에 기록했다.
2. 나머지 개발 세트에서 동일 그룹을 유지하는 3-fold 교차검증. 동일 폴드로 모든 후보를 비교했다. 변이 단어 사전과 출현 환자 수 필터(min_df=3)는 각 훈련 폴드에서만 학습했다.
3. dummy(사전확률), 유전자 이진 LR, 토큰 LR, full LR(C=0.25/1/4), balanced LR, ComplementNB(alpha=0.5), averaged SGD(log loss), ExtraTrees 300개를 비교했다. 같은 full 모드 안에서만 C를 변경했다.
4. 개발 CV 상위 두 단일 모델의 확률 동일 평균 앙상블 한 개를 추가 비교했다. 이 앙상블 구성 자체는 같은 CV 결과에 적응하므로 CV 최댓값은 다소 낙관적일 수 있다. 최종 홀드아웃이 선택 이후의 별도 평가다.
5. 평균 macro F1이 가장 큰 후보를 선택하고 홀드아웃을 평가했다. 최초 max_iter=400 실행에서 LR 수렴 경고가 발생해, 분할·후보·선택 규칙을 그대로 두고 모든 LR의 반복 상한만 2,000으로 늘려 전체 실험을 재실행했다. 첫 결과는 `artifacts/initial_maxiter400/`에 보관했다. 초기 홀드아웃은 이미 관측됐으므로 최종 홀드아웃은 수치적 수렴 보완 후 재평가라는 한계가 있다. 홀드아웃 점수로 C/가중치/변수/앙상블 구성을 조정하지 않았다.
6. 선택한 설정으로 전체 6,201명을 재학습하고 테스트를 예측했다.

| model | macro_f1 | std | accuracy |
| --- | --- | --- | --- |
| blend_top2 | 0.41833 | 0.00666 | 0.43609 |
| full_lr_balanced | 0.39223 | 0.00416 | 0.42157 |
| full_extratrees | 0.39009 | 0.00845 | 0.39758 |
| full_lr_c025 | 0.37549 | 0.00812 | 0.43004 |
| full_lr_c1 | 0.37399 | 0.00346 | 0.42157 |
| full_lr_c4 | 0.36515 | 0.00617 | 0.40806 |
| full_sgd | 0.35853 | 0.00544 | 0.41351 |
| tokens_lr | 0.33088 | 0.00275 | 0.38710 |
| binary_lr | 0.31115 | 0.00242 | 0.37218 |
| full_nb | 0.28537 | 0.01265 | 0.36169 |
| dummy | 0.00866 | 0.00002 | 0.12681 |

동일 C=1에서 binary → tokens의 평균 macro F1 차이는 +0.01974, tokens → full은 +0.04311였다. full에서 class_weight='balanced' 적용 차이는 +0.01824였다. 정확한 변이 정보와 환자 단위 요약을 함께 쓰는 표현이 이번 분할에서 유리했다. 다만 이 비교는 여러 변수 묶음을 동시에 추가한 것으로 개별 파생변수의 유효성을 분리하지 않는다. 앙상블은 선형 결정 경계와 트리의 상호작용 표현을 결합하는 후보이며, 그 상보성의 실증 근거는 단일 모델 대비 CV macro F1 개선이다.

std는 폴드 간 표준편차이며 신뢰구간이 아니다. blend_top2의 accuracy는 개발 OOF 전체 기준, 다른 행은 폴드 accuracy 평균이다. 최종 선택에는 macro F1만 사용했다. 정규화/결측 대체/오버샘플링은 추가 사용하지 않았다. 모든 생성 값이 음이 아니므로 ComplementNB 입력 요건을 만족한다. LightGBM은 설치 후 libomp 런타임이 없어 실행 불가였고 후보 성능 비교에는 포함하지 않았다. CatBoost/XGBoost/딥러닝/외부 데이터는 사용하지 않았다. 전체 탐색 공간의 최적임을 주장하지 않는다.

## 6. 최종 사용 변수와 선택 이유
최종 모델은 **full_lr_balanced, full_extratrees**다. 실제 피팅된 전체 변수 목록은 `artifacts/final_features.csv`에 저장했고, 모델별 원본 변수 목록도 별도로 저장했다. fold 내 3명 이상 출현한 범주 특성만 유지하므로 희귀 토큰을 억제하면서 재현되는 변이 신호를 활용한다. numeric/module 특성은 빈도와 무관하게 유지한다. min_df는 비영(0 아님) 값을 가진 환자 수 기준이다. 각 모델의 변수 수는 다음과 같다.

| model | family | feature_count |
| --- | --- | --- |
| full_extratrees | gene | 4215 |
| full_extratrees | module | 7 |
| full_extratrees | numeric | 18 |
| full_extratrees | position | 4171 |
| full_extratrees | type | 10783 |
| full_extratrees | variant | 2254 |
| full_lr_balanced | gene | 4215 |
| full_lr_balanced | module | 7 |
| full_lr_balanced | numeric | 18 |
| full_lr_balanced | position | 4171 |
| full_lr_balanced | type | 10783 |
| full_lr_balanced | variant | 2254 |

binary/tokens/full 비교는 표현 방식의 제거 실험이다. full이 선택되었더라도 full 내 모든 변수 각각의 인과적 기여가 입증된 것은 아니다. 반대로 선택되지 않은 표현도 생물학적으로 무의미하다는 뜻은 아니다. 모든 4,384개 유전자에서 후보를 만들되, 실제 입력은 최종 빈도 필터를 통과한 변수에 한정한다. ID는 출처/순서 편향 위험, SUBCLASS는 정답 누수 때문에 입력에서 제외했다. 테스트에만 나타난 미등록 변이는 학습된 사전에 없으므로 무시되지만 알려진 유전자/유형/숫자 집계는 계산된다.

### 각 모델의 상위 25개 실제 변수
| feature | family | model | importance | strongest_class |
| --- | --- | --- | --- | --- |
| numeric:log_mutated_genes | numeric | full_extratrees | 0.03149 | nan |
| numeric:log_events | numeric | full_extratrees | 0.02958 | nan |
| numeric:log_substitution | numeric | full_extratrees | 0.02413 | nan |
| numeric:log_synonymous | numeric | full_extratrees | 0.01833 | nan |
| gene:TP53 | gene | full_extratrees | 0.01461 | nan |
| type:APC:stop | type | full_extratrees | 0.01443 | nan |
| gene:VHL | gene | full_extratrees | 0.01371 | nan |
| numeric:log_frameshift | numeric | full_extratrees | 0.01280 | nan |
| variant:IDH1:R132H | variant | full_extratrees | 0.01241 | nan |
| position:BRAF:600 | position | full_extratrees | 0.01176 | nan |
| gene:PTEN | gene | full_extratrees | 0.01095 | nan |
| numeric:log_mean_position | numeric | full_extratrees | 0.01042 | nan |
| numeric:fraction_frameshift | numeric | full_extratrees | 0.00977 | nan |
| position:IDH1:132 | position | full_extratrees | 0.00911 | nan |
| numeric:log_stop | numeric | full_extratrees | 0.00880 | nan |
| gene:APC | gene | full_extratrees | 0.00870 | nan |
| variant:BRAF:V600E | variant | full_extratrees | 0.00861 | nan |
| numeric:multi_event_excess | numeric | full_extratrees | 0.00861 | nan |
| numeric:fraction_synonymous | numeric | full_extratrees | 0.00835 | nan |
| numeric:fraction_substitution | numeric | full_extratrees | 0.00831 | nan |
| module:p53_cellcycle | module | full_extratrees | 0.00683 | nan |
| type:PIK3CA:substitution | type | full_extratrees | 0.00676 | nan |
| position:LRIG1:24 | position | full_extratrees | 0.00641 | nan |
| numeric:fraction_stop | numeric | full_extratrees | 0.00628 | nan |
| gene:IDH1 | gene | full_extratrees | 0.00616 | nan |
| gene:TP53 | gene | full_lr_balanced | 0.57926 | OV |
| module:metabolism | module | full_lr_balanced | 0.39901 | KIRC |
| gene:VHL | gene | full_lr_balanced | 0.39545 | KIRC |
| numeric:multi_event_excess | numeric | full_lr_balanced | 0.39538 | CESC |
| numeric:log_frameshift | numeric | full_lr_balanced | 0.39218 | KIPAN |
| module:p53_cellcycle | module | full_lr_balanced | 0.39203 | PAAD |
| numeric:log_substitution | numeric | full_lr_balanced | 0.37413 | LUSC |
| numeric:log_mutated_genes | numeric | full_lr_balanced | 0.35077 | LUSC |
| type:PIK3CA:substitution | type | full_lr_balanced | 0.32753 | UCEC |
| numeric:log_synonymous | numeric | full_lr_balanced | 0.31733 | ACC |
| type:TP53:substitution | type | full_lr_balanced | 0.31425 | GBMLGG |
| module:pi3k_mtor | module | full_lr_balanced | 0.30688 | UCEC |
| position:IDH1:132 | position | full_lr_balanced | 0.30494 | LGG |
| module:wnt | module | full_lr_balanced | 0.30406 | COAD |
| module:rtk_ras_mapk | module | full_lr_balanced | 0.29414 | LGG |
| numeric:log_events | numeric | full_lr_balanced | 0.29282 | LUSC |
| numeric:log_mean_position | numeric | full_lr_balanced | 0.29189 | OV |
| gene:PTEN | gene | full_lr_balanced | 0.28046 | UCEC |
| position:BRAF:600 | position | full_lr_balanced | 0.27910 | THCA |
| gene:PIK3CA | gene | full_lr_balanced | 0.27838 | UCEC |
| numeric:log_stop | numeric | full_lr_balanced | 0.27724 | LUSC |
| variant:BRAF:V600E | variant | full_lr_balanced | 0.27140 | THCA |
| variant:IDH1:R132H | variant | full_lr_balanced | 0.26847 | LGG |
| gene:ATRX | gene | full_lr_balanced | 0.25937 | SARC |
| type:IDH1:substitution | type | full_lr_balanced | 0.25474 | LGG |

LR importance는 26개 클래스 계수 절댓값 평균이다. strongest_class는 가장 큰 양의 상대 계수를 가진 클래스다. 표준화하지 않은 변수의 계수이므로 서로 단위가 다른 특성끼리 중요도를 절대 비교하지 않는다. 상관된 변수 간 계수 분배와 정규화 영향을 받으며 인과관계가 아니다. ExtraTrees가 선택되면 impurity 중요도로 산출하며 카디널리티 편향이 있을 수 있다. NB/SGD 계수 미제공 상황은 NA로 남긴다. 클래스별 상위 양의 계수는 `*_class_coefficients.csv`에 기록한다. 이는 검증 permutation/SHAP 중요도가 아니다.

## 7. 홀드아웃 오류 분석
독립 홀드아웃 macro F1과 개발 최고 CV 평균의 차이는 +0.00537였다. 두 수치가 비슷해도 테스트의 변이량 분포 차이 때문에 동일한 테스트 성능을 보장하지 않는다. 그룹을 보존하는 층화는 클래스 비율을 정확히 맞추지는 못하므로 support도 함께 확인해야 한다.

THYM의 F1은 0.00000, recall은 0.00000(support=30)로 이번 홀드아웃에서 특히 취약했다. PAAD F1 0.17647, LUAD F1 0.19355도 낮았다. 반면 ACC F1 0.88889, SKCM F1 0.85437, COAD F1 0.80000는 상대적으로 높았다. 소수 클래스에서의 높은 점수 역시 작은 검증 표본에 대한 결과다. 이 관측 후 모델이나 가중치를 변경하지 않았다.

낮은 클래스별 F1 10개:
| index | precision | recall | f1-score | support |
| --- | --- | --- | --- | --- |
| THYM | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| PAAD | 0.30000 | 0.12500 | 0.17647 | 24.00000 |
| LUAD | 0.23077 | 0.16667 | 0.19355 | 36.00000 |
| SARC | 0.24242 | 0.20513 | 0.22222 | 39.00000 |
| CESC | 0.31818 | 0.22581 | 0.26415 | 31.00000 |
| LAML | 0.19266 | 0.67742 | 0.30000 | 31.00000 |
| KIRC | 0.35294 | 0.26866 | 0.30508 | 67.00000 |
| LIHC | 0.36000 | 0.29032 | 0.32143 | 31.00000 |
| TGCT | 0.33333 | 0.33333 | 0.33333 | 24.00000 |
| PCPG | 0.26415 | 0.48276 | 0.34146 | 29.00000 |

### 가장 많은 오분류 방향 20개
| true | prediction | count |
| --- | --- | --- |
| THYM | LAML | 30 |
| KIRC | KIPAN | 28 |
| GBMLGG | LGG | 28 |
| KIPAN | KIRC | 25 |
| THCA | LAML | 18 |
| BRCA | OV | 13 |
| PRAD | PCPG | 11 |
| BRCA | PRAD | 11 |
| LGG | GBMLGG | 10 |
| BRCA | KIPAN | 10 |
| TGCT | KIPAN | 8 |
| HNSC | STES | 8 |
| GBMLGG | KIPAN | 8 |
| THCA | PRAD | 8 |
| SARC | PRAD | 8 |
| KIPAN | BRCA | 8 |
| LUSC | STES | 8 |
| BRCA | PCPG | 8 |
| UCEC | BRCA | 7 |
| BRCA | LAML | 7 |

true는 실제 라벨, prediction은 예측 라벨이다. 건수 순위는 클래스 규모의 영향을 받으므로 위의 클래스별 recall/precision 및 행 정규화 혼동행렬과 함께 해석한다. 서로 역방향의 혼동 건수가 같을 필요는 없다.

해당 클래스들은 모델이 구분하기 어려운 표본이거나 표본 수 부족의 영향을 받는다. 유사 라벨이나 기원 조직에 대한 외부 메타데이터가 없으므로 실제 혼동의 생물학적 원인을 단정하지 않는다. 클래스별 recall이 낮으면 실제 환자를 놓치는 패턴, precision이 낮으면 다른 클래스가 유입되는 패턴이다. `holdout_classification_report.csv`와 `holdout_predictions.csv`에서 전체 클래스 및 개별 오류를 확인할 수 있다. confidence는 보정되지 않은 모델 확률 최댓값으로 임상적 신뢰도가 아니다.

![정규화 혼동행렬](artifacts/holdout_confusion.png)

## 8. 저장물과 실행 방법
- `cencer.ipynb`: EDA → 파생변수 → CV → 홀드아웃 → 전체 재학습 → 피클 저장 → 보고서 생성. 실행 결과 포함.
- 전처리기와 보고서 생성 함수는 `cencer.ipynb` 안에 직접 정의되어 있다. `mutation_model.py`, `report_writer.py`, `build_notebook.py`, `execute_notebook.py` 없이 실행할 수 있다.
- `artifacts/cancer_model.pkl`: models(전처리 포함 Pipeline 리스트), classes, genes, selected, seed, holdout_metrics, python 필드를 포함한 딕셔너리.
- `artifacts/submission.csv`: 원본 sample_submission ID 순서 및 열을 그대로 유지한 테스트 2,546건 예측.
- `artifacts/test_probabilities.csv`: 클래스 순서와 ID가 포함된 예측 확률.
- `artifacts/final_features.csv`, `gene_dictionary.csv`, `gene_class_mutation_rates.csv`: 최종 변수 전체 및 원본 컬럼 전체 통계.
- `artifacts/cv_folds.csv`, `model_comparison.csv`, `holdout_metrics.json`, `holdout_classification_report.csv`, `split_manifest.csv`: 검증 증거.
- `requirements-lock.txt`: 실행 환경 패키지 버전. 프로젝트 `.venv`를 IDE 커널로 선택할 수 있다.
- `predict.py`: 별도 프로세스에서 피클을 로딩하여 입력 CSV의 제출 예측을 생성한다.
- `verify_artifacts.py`: 피클 재로딩 전체 테스트 예측·확률 일치, ID 순서, 홀드아웃 지표 재계산, 그룹 간 분할 누수, 선택 모델 수렴, 노트북 오류를 점검한다. 실행 후 `artifacts/verification.json`에 해시와 환경/검증 결과를 남긴다.

`cencer.ipynb`와 `data/` 폴더를 같은 디렉터리에 두고, 의존 라이브러리가 설치된 커널에서 **Run All**을 실행한다. 별도 Python 파일을 먼저 실행할 필요가 없다. EDA, 파생변수 생성/필터링, CV 모델 선별, 검증, 전체 재학습, 피클/제출 파일/본 보고서 저장까지 모든 코드가 노트북에 있다. 모델의 절대 경로와 다운로드 링크는 저장 셀에서 출력한다. cloudpickle은 사용자 정의 전처리 코드를 피클에 함께 담는다.

```python
import pickle
import numpy as np
import pandas as pd
# cloudpickle을 포함한 학습 환경 라이브러리 필요. 별도 프로젝트 .py 파일 불필요.
with open('artifacts/cancer_model.pkl', 'rb') as f:
    bundle = pickle.load(f)
test = pd.read_csv('data/test.csv')
X = test[bundle['genes']]
p = sum(m.predict_proba(X) for m in bundle['models']) / len(bundle['models'])
pred = bundle['classes'][p.argmax(axis=1)]
```

신뢰할 수 있는 피클만 로딩한다. 재현은 동일 데이터/환경/seed를 전제로 하며 다른 라이브러리 버전의 피클 호환을 보장하지 않는다. 커널 실행은 로컬 포트 생성 권한이 필요할 수 있다.

## 9. 한계와 후속 개선
이 결과는 해커톤 데이터의 오프라인 분류 실험이다. 출처별 분할, 외부 코호트 검증, 임상적 진단 성능은 평가하지 않았다. 동일 프로파일 그룹화가 출처/환자/배치 누수를 완전히 해결하지는 않는다. 임상적 암종 관계를 라벨 이름으로 추론해 합치지 않았다. 수작업 그룹, 변이 파서, 하이퍼파라미터 범위는 제한적이다. 유전자 기능/전사체/경로 주석이 주어지면 출처를 검증하여 확장할 수 있다. 공식 대회 지표와 외부 데이터 허용 범위가 확인되면 평가 목표와 후보 범위를 조정하되, 새로운 선택 이후에는 새로운 독립 검증이 필요하다. 테스트 정답/리더보드에 맞춰 검증 결과를 보정하지 않았다.

전체 4,384개 유전자의 개별 통계·최종 사용 변수 수·탐색적 모듈은 [전체 유전자 컬럼 사전](gene_dictionary.md)에서 볼 수 있다.

## 노트북 단독 실행 및 모델 독립 로딩 검증

EDA·파생변수 생성/필터링·교차검증 모델 선별·홀드아웃 평가·전체 재학습·모델/제출 저장·보고서 작성 코드가 모두 cencer.ipynb에 포함되어 있습니다. 별도 프로젝트 Python 파일 없이 실행됩니다. cloudpickle로 전처리 클래스 코드를 피클에 포함했습니다. 프로젝트 파일이 없는 임시 폴더의 새 Python 프로세스에서 pickle.load와 테스트 4건 추론을 수행했고 mutation_model/report_writer 모듈 없이 성공했습니다. 검증 결과는 artifacts/standalone_model_check.json에 기록했습니다.
