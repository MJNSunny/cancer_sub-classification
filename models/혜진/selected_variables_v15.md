# v15 입력 변수와 선별 근거

raw는 기존 유전자·변이·위치·아미노산 변화·유형·숫자·경로 표현입니다. gene은 gene:/numeric:/module: 접두사만, type은 여기에 type:을 추가한 표현입니다. 숫자 요약에는 변이 수·유형별 비율도 들어가므로 순수 이진 gene-only 모델이 아닙니다. 정확한 표기에 대한 의존을 줄이려는 가설이며 정보 손실로 성능이 떨어질 수도 있습니다.

같은 외부 학습 fold의 해당 두 암종 환자 원본만으로 관측 빈도 3 이상 어휘를 만들고 binary chi2 최대 512개를 선별합니다. MaxAbs도 같은 원본 행렬에 적합합니다. 증강본이나 검증 환자로 어휘/선별/스케일을 재적합하지 않습니다. 각 head와 fold의 실제 입력 수는 아래와 같습니다.

|   fold | config     | pair       |   features |   clean_pair_patients |   augmentation_mean |
|-------:|:-----------|:-----------|-----------:|----------------------:|--------------------:|
|      0 | raw_aug0   | GBMLGG/LGG |        512 |                   368 |                   0 |
|      0 | raw_aug0   | KIPAN/KIRC |        512 |                   453 |                   0 |
|      0 | raw_aug10  | GBMLGG/LGG |        512 |                   368 |                  10 |
|      0 | raw_aug10  | KIPAN/KIRC |        512 |                   453 |                  10 |
|      0 | gene_aug0  | GBMLGG/LGG |        457 |                   368 |                   0 |
|      0 | gene_aug0  | KIPAN/KIRC |        512 |                   453 |                   0 |
|      0 | gene_aug10 | GBMLGG/LGG |        457 |                   368 |                  10 |
|      0 | gene_aug10 | KIPAN/KIRC |        512 |                   453 |                  10 |
|      0 | type_aug0  | GBMLGG/LGG |        512 |                   368 |                   0 |
|      0 | type_aug0  | KIPAN/KIRC |        512 |                   453 |                   0 |
|      0 | type_aug10 | GBMLGG/LGG |        512 |                   368 |                  10 |
|      0 | type_aug10 | KIPAN/KIRC |        512 |                   453 |                  10 |
|      1 | raw_aug0   | GBMLGG/LGG |        512 |                   368 |                   0 |
|      1 | raw_aug0   | KIPAN/KIRC |        512 |                   453 |                   0 |
|      1 | raw_aug10  | GBMLGG/LGG |        512 |                   368 |                  10 |
|      1 | raw_aug10  | KIPAN/KIRC |        512 |                   453 |                  10 |
|      1 | gene_aug0  | GBMLGG/LGG |        474 |                   368 |                   0 |
|      1 | gene_aug0  | KIPAN/KIRC |        512 |                   453 |                   0 |
|      1 | gene_aug10 | GBMLGG/LGG |        474 |                   368 |                  10 |
|      1 | gene_aug10 | KIPAN/KIRC |        512 |                   453 |                  10 |
|      1 | type_aug0  | GBMLGG/LGG |        512 |                   368 |                   0 |
|      1 | type_aug0  | KIPAN/KIRC |        512 |                   453 |                   0 |
|      1 | type_aug10 | GBMLGG/LGG |        512 |                   368 |                  10 |
|      1 | type_aug10 | KIPAN/KIRC |        512 |                   453 |                  10 |
|      2 | raw_aug0   | GBMLGG/LGG |        512 |                   368 |                   0 |
|      2 | raw_aug0   | KIPAN/KIRC |        512 |                   452 |                   0 |
|      2 | raw_aug10  | GBMLGG/LGG |        512 |                   368 |                  10 |
|      2 | raw_aug10  | KIPAN/KIRC |        512 |                   452 |                  10 |
|      2 | gene_aug0  | GBMLGG/LGG |        454 |                   368 |                   0 |
|      2 | gene_aug0  | KIPAN/KIRC |        512 |                   452 |                   0 |
|      2 | gene_aug10 | GBMLGG/LGG |        454 |                   368 |                  10 |
|      2 | gene_aug10 | KIPAN/KIRC |        512 |                   452 |                  10 |
|      2 | type_aug0  | GBMLGG/LGG |        512 |                   368 |                   0 |
|      2 | type_aug0  | KIPAN/KIRC |        512 |                   452 |                   0 |
|      2 | type_aug10 | GBMLGG/LGG |        512 |                   368 |                  10 |
|      2 | type_aug10 | KIPAN/KIRC |        512 |                   452 |                  10 |

최종 제출 후보가 없으므로 전체 train 최종 선별 목록은 새로 만들지 않았습니다. 각 fold의 실험 변수는 그 fold 학습 부분에서 결정되며 서로 같다는 보장은 없습니다. 기존 v10 최종 목록은 selected_variables_v10.md를 참조합니다.
