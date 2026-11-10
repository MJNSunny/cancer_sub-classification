# 혜진 v8: Cancer Genome Guide 기반 실험

## 결과
초기 8개에 기존 구성 입력을 보존한 대조 4개를 추가한 신규 모델 12개와 쌍별 전문가 4개를 학습하고, 제한된 혼합·확률 재분배 계획을 같은 그룹 3-fold에서 비교했습니다. 1차 후보 `v6_reference`, 최종 채택 **False**, 최종 구성 `{'kind': 'blend', 'members': [('v6_reference', 1.0)]}`입니다.

| metric | v6 | v8_candidate |
| --- | --- | --- |
| clean | 0.43558 | 0.43558 |
| noise | 0.34577 | 0.34577 |
| duplicate | 0.43330 | 0.43330 |
| score | 0.40841 | 0.40841 |

유지 모델(v6; 신규 후보 평가 아님)의 기존 홀드아웃 Macro F1 0.472989, 정확도 0.463336, weighted F1 0.467778. 이 홀드아웃은 이미 여러 번 관측했으므로 독립 최종 성능이 아닙니다. v8 Public은 아직 확인하지 않았습니다.

## 문서 해석과 실측
가이드는 전체 train을 분석한 자료로, 유전자·핫스팟·조합 후보 설계에 참고했습니다. 전체 학습 정보를 본 문서에서 후보를 골랐으므로 설계 선택 편향이 있습니다. 검증 점수를 독립 새 데이터 성능으로 해석하지 않습니다.

| gene | feature | target | all_carriers | target_carriers | target_fraction_among_carriers | target_mutation_rate |
| --- | --- | --- | --- | --- | --- | --- |
| APC | any_mutation | COAD | 367 | 160 | 0.43597 | 0.71749 |
| APC | stop_or_fs_not_all_deletions | COAD | 218 | 155 | 0.71101 | 0.69507 |
| VHL | any_mutation | KIRC | 326 | 151 | 0.46319 | 0.45210 |
| VHL | stop_or_fs_not_all_deletions | KIRC | 172 | 83 | 0.48256 | 0.24850 |
| IDH1 | any_mutation | LGG | 441 | 180 | 0.40816 | 0.78603 |
| IDH1 | stop_or_fs_not_all_deletions | LGG | 2 | 0 | 0.00000 | 0.00000 |
| BRAF | any_mutation | THCA | 438 | 186 | 0.42466 | 0.57407 |
| BRAF | stop_or_fs_not_all_deletions | THCA | 9 | 0 | 0.00000 | 0.00000 |
| NPM1 | any_mutation | LAML | 56 | 41 | 0.73214 | 0.25949 |
| NPM1 | stop_or_fs_not_all_deletions | LAML | 40 | 40 | 1.00000 | 0.25316 |
| TP53 | any_mutation | OV | 1770 | 190 | 0.10734 | 0.75099 |
| TP53 | stop_or_fs_not_all_deletions | OV | 518 | 47 | 0.09073 | 0.18577 |

APC stop/fs 표기 보유자 중 COAD 비율은 약 71.1%였으며, 가이드의 95% 이상이라는 확정 규칙을 사용하지 않았습니다. 위 비율은 P(암종|표기)로 임상적 specificity(TN/(TN+FP))가 아닙니다. test의 COAD 수가 570명이라는 주장도 정답으로 사용하지 않았습니다. 관측 변이 유전자 수는 mutations/Mb TMB가 아니며, 성별·흡연·CNV 증폭·바이러스 정보는 원본에 없어 추정하지 않았습니다.

## 새 변수와 근거
유전자 존재, 정확한 표지 위치, stop/fs, 동반 변이, 관측 WT 조합을 후보로 추가했습니다. BRAF V600 등 표지와 log1p(변이 유전자 수)의 곱은 표지의 맥락을 선형 모델도 표현하게 합니다. 단일 유전자나 변이량을 정답 규칙으로 쓰지 않습니다. stop/fs는 관측 표기이며 병원성·기능 상실을 확정하지 않습니다. 가이드 목록과 정확한 조합은 guide_features.json과 노트북에 포함했습니다.

암종별 지문 점수는 외부 학습의 유전자 빈도와 라벨로 계산한 양의 log-odds 차이입니다. 최소 관측 5명/해당 암종 3명, 빈도/(빈도+20) 축소, 암종별 상위 8개를 사용합니다. 학습 입력은 내부 그룹 3-fold에서 해당 그룹의 라벨을 제외한 cross-fitting으로 만들고, 증강 입력도 같은 내부 통계로 변환했습니다. 검증/test는 외부 학습 전체 통계를 사용합니다. 임상적 드라이버 판정이나 사전 확정 암종이 아닙니다.

초기 모델의 새 변수는 빈도 기준을 통과한 뒤 2,048/4,096개 예산 안에 포함해 보호했습니다. 추가 대조 4개는 기존 구성 모델의 선택 변수 2,048/4,096개를 그대로 유지하고 가이드/지문 변수만 덧붙였으며, 기준과 완전히 같은 열은 제외했습니다. 따라서 입력 수가 늘 수 있습니다. 초기 결과를 보고 추가한 적응 탐색이므로 선택 편향이 있습니다. 숫자·경로 요약을 보존하고 기존 변이량을 지우지 않았습니다. LightGBM 증강은 학습에서만 관측한 희귀 변이를 평균 10개 추가하고 원본/증강 가중치 1/0.5를 사용합니다. 증강이 라벨을 유지한다는 가정은 한계입니다.

## 쌍별 전문가
GBMLGG/LGG, KIPAN/KIRC, LUAD/LUSC, THCA/SKCM의 두 라벨만으로 각각 LR을 학습했습니다. 해당 두 암종의 기존 확률 합을 보존한 채 내부 비율만 alpha 0.25/0.5로 조정합니다. 대상 2쌍/4쌍을 비교했습니다. test의 암종 비율을 강제로 맞추거나 단서가 있다는 이유로 정답을 덮어쓰지 않습니다. 원본 프로필이 같아도 정답이 다른 사례는 이 방법만으로 모두 해결할 수 없습니다.

## 검증·선택
v6를 고정 대조군으로 사용하고 clean 0.6/희귀 관측 변이 스트레스 0.3/중복 주석 0.1을 유지했습니다. 1차 점수 +0.002 이상, clean 하락 0.002 이하인 후보를 고정한 뒤 seed=71에서 확인합니다. 재분할 점수가 v6 이상이며 clean 하락 0.002 이하여야 채택합니다. seed=71은 v7에서도 관측한 같은 개발 환자의 분할이며 독립 새 환자는 아닙니다. 여러 버전의 반복 탐색에 따른 선택 편향이 있습니다.

1차 기준을 넘는 후보가 없어 재분할 확인을 생략했습니다.

모든 적합·선별·통계·스케일러는 해당 학습에서만 계산했습니다. v6 캐시는 원본 ID/프로필/클래스·분할 확인과 첫 fold 실제 재학습 일치를 거친 완료 OOF만 재사용합니다. 전체 train 모델 캐시는 선택 후 최종 전체 학습에만 허용하며 CV·홀드아웃에는 금지합니다. 캐시가 없거나 CACHE_V6=False면 전부 재학습합니다. 원본 데이터 SHA256과 재현 환경을 verification.json에 기록했습니다.

## 후보별 결과
| candidate | clean | noise | duplicate | score |
| --- | --- | --- | --- | --- |
| v6plus_raw_guide_aug_lgb4096_0.25 | 0.43222 | 0.35581 | 0.43222 | 0.40930 |
| pair_scope2_a0.25 | 0.43622 | 0.34579 | 0.43423 | 0.40890 |
| pair_scope2_a0.5 | 0.43686 | 0.34440 | 0.43417 | 0.40885 |
| v6plus_preserved_lgb_plus_guide_0.25 | 0.43244 | 0.35272 | 0.43183 | 0.40846 |
| v6_reference | 0.43558 | 0.34577 | 0.43330 | 0.40841 |
| v6plus_preserved_lr_plus_guide_0.25 | 0.43468 | 0.34714 | 0.43353 | 0.40831 |
| pair_scope4_a0.25 | 0.43558 | 0.34469 | 0.43248 | 0.40800 |
| v6plus_preserved_lgb_plus_guide_fingerprint_0.25 | 0.43307 | 0.35044 | 0.43027 | 0.40800 |
| v6plus_guide_only_lr_C0.1_0.25 | 0.43401 | 0.34493 | 0.43261 | 0.40714 |
| v6plus_preserved_lgb_plus_guide_0.5 | 0.43023 | 0.35183 | 0.43067 | 0.40675 |
| pair_scope4_a0.5 | 0.43445 | 0.34189 | 0.43191 | 0.40643 |
| v6plus_preserved_lr_plus_guide_fingerprint_0.25 | 0.43392 | 0.34331 | 0.43081 | 0.40643 |
| v6plus_raw_guide_fingerprint_aug_lgb_0.25 | 0.42966 | 0.34959 | 0.42768 | 0.40544 |
| v6plus_raw_guide_aug_lgb2048_0.25 | 0.42799 | 0.35122 | 0.42984 | 0.40514 |
| v6plus_raw_guide_lr_0.25 | 0.43325 | 0.33872 | 0.43211 | 0.40478 |
| v6plus_raw_guide_aug_lgb4096_0.5 | 0.42855 | 0.34815 | 0.42619 | 0.40419 |
| v6plus_guide_only_lr_C1_0.25 | 0.43101 | 0.34021 | 0.42740 | 0.40341 |
| preserved_lgb_plus_guide | 0.42670 | 0.34302 | 0.42670 | 0.40160 |
| v6plus_guide_fingerprint_only_lr_0.25 | 0.42869 | 0.33865 | 0.42774 | 0.40159 |
| v6plus_preserved_lr_plus_guide_0.5 | 0.42963 | 0.33559 | 0.42787 | 0.40124 |
| v6plus_raw_guide_aug_lgb2048_0.5 | 0.42371 | 0.34821 | 0.42423 | 0.40111 |
| v6plus_preserved_lgb_plus_guide_fingerprint_0.5 | 0.42605 | 0.34092 | 0.42585 | 0.40049 |
| v6plus_raw_guide_fingerprint_lr_0.25 | 0.42960 | 0.33053 | 0.42895 | 0.39981 |
| v6plus_raw_guide_fingerprint_aug_lgb_0.5 | 0.42308 | 0.33968 | 0.42265 | 0.39802 |
| v6plus_guide_only_lr_C0.1_0.5 | 0.42063 | 0.34511 | 0.42029 | 0.39794 |
| v6plus_preserved_lr_plus_guide_fingerprint_0.5 | 0.42691 | 0.32051 | 0.42625 | 0.39492 |
| v6plus_raw_guide_lr_0.5 | 0.42121 | 0.31419 | 0.42123 | 0.38910 |
| raw_guide_aug_lgb4096 | 0.41411 | 0.32631 | 0.41411 | 0.38777 |
| raw_guide_aug_lgb2048 | 0.40901 | 0.33049 | 0.40901 | 0.38545 |
| preserved_lgb_plus_guide_fingerprint | 0.40902 | 0.32903 | 0.40902 | 0.38502 |
| v6plus_guide_fingerprint_only_lr_0.5 | 0.40754 | 0.32843 | 0.40709 | 0.38376 |
| v6plus_raw_guide_fingerprint_lr_0.5 | 0.41771 | 0.30190 | 0.41882 | 0.38308 |
| v6plus_guide_only_lr_C1_0.5 | 0.40723 | 0.32349 | 0.40772 | 0.38215 |
| raw_guide_fingerprint_aug_lgb | 0.40507 | 0.32007 | 0.40507 | 0.37957 |
| preserved_lr_plus_guide | 0.40488 | 0.31278 | 0.40488 | 0.37725 |
| preserved_lr_plus_guide_fingerprint | 0.39650 | 0.29146 | 0.39650 | 0.36499 |
| raw_guide_fingerprint_lr | 0.37879 | 0.25799 | 0.37879 | 0.34255 |
| raw_guide_lr | 0.37496 | 0.25922 | 0.37496 | 0.34024 |
| guide_fingerprint_only_lr | 0.35196 | 0.28124 | 0.35196 | 0.33075 |
| guide_only_lr_C1 | 0.33548 | 0.27407 | 0.33548 | 0.31706 |
| guide_only_lr_C0.1 | 0.32147 | 0.27816 | 0.32147 | 0.30848 |

## 모델·파일
cencer_v8.ipynb 하나에 모든 코드가 들어 있습니다. requirements-v8.txt 환경과 공유 data/가 필요합니다. 프로젝트 Python 파일이나 이전 모델 피클은 필수가 아닙니다. 모델 artifacts/v8/cancer_model_v8.pkl 크기는 83.09 MiB, 분류기 입력 슬롯 합은 16,384개로 고유 유전자 수와 다릅니다.

실제 변수·의미·중요도는 selected_variables_v8.md와 final_feature_dictionary.csv, 전체 유전자 관측 통계는 gene_dictionary_v8.md에 있습니다. 지문 점수가 최종 채택된 경우 실제 학습 표지는 final_fingerprint_markers.csv에 기록했습니다. 중요도 크기는 다른 모델 사이에서 직접 비교할 수 없고 인과적 기여도가 아닙니다.

피클은 프로젝트 코드 없는 임시 폴더에서 로딩해 test 2,546개의 CSV·ID·확률·배치 일치를 확인했습니다. 미채택 시 주 모델과 제출은 v6로 유지하며 artifacts/v8의 피클/CSV는 재현 확인용입니다. 동일 예측을 새 제출로 배포하지 않습니다. artifacts는 기존 방침대로 Git에서 제외합니다.

## 주요 오분류 조합(v6 개발 OOF)

| true | predicted | count |
| --- | --- | --- |
| GBMLGG | LGG | 154 |
| KIPAN | KIRC | 140 |
| BRCA | OV | 78 |
| BRCA | PRAD | 50 |
| KIPAN | PRAD | 41 |
| BRCA | PCPG | 40 |
| PRAD | PCPG | 38 |
| THCA | PCPG | 36 |
| PAAD | OV | 36 |
| SARC | PRAD | 35 |

## 변이량별 정확도(v6 개발 OOF)

| burden | n | present_classes | accuracy | macro_f1_present_classes |
| --- | --- | --- | --- | --- |
| 1-10 | 1985 | 25 | 0.41914 | 0.24240 |
| 11-30 | 1873 | 24 | 0.39936 | 0.35228 |
| 31-100 | 796 | 20 | 0.48869 | 0.44463 |
| 101+ | 306 | 21 | 0.66993 | 0.29642 |
구간별 환자·암종 구성이 달라 구간 간 차이를 변이량의 인과효과로 해석하지 않습니다.

![Development CV](artifacts/v8/validation_comparison_v8.png)

## 미채택 실험용 후보

주 모델은 v6를 유지합니다. `pair_scope2_a0.5`는 메인 채택 기준을 넘지 못한 **실험용** 후보입니다. 개발 CV에서 원본 F1과 종합 점수가 v6보다 높았던 조합 중 원본 F1이 가장 높은 것을 기록했습니다. 재분할·새 홀드아웃·Public 개선은 확인하지 않았습니다. 안정적인 성능 향상이나 메인 모델 채택을 뜻하지 않습니다.

| metric | v6 | experimental |
| --- | --- | --- |
| clean | 0.43558 | 0.43686 |
| noise | 0.34577 | 0.34440 |
| duplicate | 0.43330 | 0.43417 |
| score | 0.40841 | 0.40885 |

구성 `{'kind': 'pair', 'scope': 2, 'alpha': 0.5}`. 파일 `submission/혜진_submission_v8_experimental.csv`, 모델 `artifacts/v8/cancer_model_v8_experimental.pkl`입니다. 테스트 예측 변경은 40개이며 정답 증가 수가 아닙니다. 독립 폴더에서 전체 test CSV·ID·배치 일치를 검사했습니다. 기본 v8 CSV는 v6 재현용이고, 실제로 다른 답안은 experimental 파일입니다. 실험용 모델의 새 변수는 experimental_pair_features.csv에 있습니다.
