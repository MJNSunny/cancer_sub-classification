# 혜진 v7: 전처리 비교 보고서

## 목표와 결과
복합 치환 파싱, 동의/비동의 변이 채널 분리, 많은 변이량에만 적용하는 부분 정규화를 10개 설정으로 비교했습니다. v6를 고정 대조군으로 사용했습니다. 신규 후보 채택: **False**, 1차 선택 `v6plus_split_syn_aug_lgb_0.25`, 최종 계획 `[('v6_reference', 1.0)]`.

| 지표 | v6 | v7 선택 후보 |
| --- | ---: | ---: |
| 개발 CV Macro F1 | 0.435576 | 0.437561 |
| 희귀 변이 스트레스 F1 | 0.345775 | 0.348028 |
| 선택 점수 | 0.408408 | 0.410689 |

유지모델(v6) 재현 홀드아웃 Macro F1 0.472989, 정확도 0.463336, weighted F1 0.467778. 반복 관측한 홀드아웃이며 독립 성능이 아닙니다. 새 분할(seed=71)도 같은 개발 환자의 재분할입니다. Public 점수는 아직 확인하지 않았습니다.

## 파싱 점검
{
  "train": {
    "tokens": 255164,
    "unparsed_tokens": 173,
    "expanded_complex_tokens": 176,
    "missing_cells": 0,
    "remaining_other_tokens_v7": 0,
    "remaining_other_unique_v7": 0
  },
  "test": {
    "tokens": 337512,
    "unparsed_tokens": 31,
    "expanded_complex_tokens": 29,
    "missing_cells": 237,
    "remaining_other_tokens_v7": 2,
    "remaining_other_unique_v7": 2
  }
}

복합 표기는 범위와 서열 길이가 모두 일치할 때만 개별 치환으로 전개합니다. 불완전한 표기를 추측하거나 위치를 임의로 ±몇 칸 맞추지 않습니다. 학습 결측은 없어 결측 전용 변수의 유효성을 입증하기 어렵습니다. train/test 파싱 요약과 미해석 전체 토큰은 artifacts/v7/parser_audit.json 및 train_unparsed_tokens.csv, test_unparsed_tokens.csv에 있습니다. test 기술통계는 사전·변수 선택·모델 적합에 사용하지 않았습니다.

## 파생변수와 보정
v6의 gene/variant/position/type/aa/supported/numeric/module 표현을 유지하는 대조 후보를 만들고, silent_gene, nonsyn_gene, trunc_gene, unparsed_gene 및 동의 변이만 있는 유전자 비율·동의/비동의가 함께 있는 유전자 비율·미해석 유전자 비율을 추가하는 후보를 비교했습니다. missing은 WT와 구분합니다. split_syn은 동의 변이를 삭제하지 않고 별도 채널에 보존합니다.

cap 보정은 학습 환자 변이 유전자 수의 75% 분위수를 기준으로 초과 행에서만 변이 블록을 (기준/변이량)^power로 줄이며 power 1/0.5를 비교했습니다. 원시 변이 개수·비율·경로 요약은 보존합니다. 기준은 fold 학습에서만 적합합니다.

신규 LR 입력 2,048개, 신규 LightGBM 입력 4,096개입니다. ANOVA와 완전 동일 열 제거는 학습에서만 수행하고 숫자·경로 요약을 보존합니다. 최종 채택 여부와 실제 모델 목록은 model_sizes.json을 보세요. 시험한 전처리가 모두 최종 적용된 것은 아닙니다.

## 검증과 진단
원본 프로필을 그룹으로 묶은 기존 개발 3-fold에서 clean 0.6/희귀 관측 변이 추가 0.3/중복 주석 0.1로 비교했습니다. v6 비중 75% 또는 50%인 제한된 혼합을 시험하고, 선택 점수 +0.002·clean 하락 0.002 이하 기준을 적용했습니다. 통과 후보는 비율을 고정한 뒤 seed=71에서 재점검합니다. 실패하면 v6를 유지합니다. 증강에서 라벨이 유지된다는 가정과 반복 탐색의 선택 편향이 있습니다.

변이량별 진단은 development_burden_report.csv, 암종별 성능은 development_class_report.csv, 많이 헷갈리는 암종 조합은 development_confusions.csv에 있습니다. v6와 v7_candidate 접두사로 구분했습니다. 구간별 환자 수와 암종 구성이 달라 macro F1 수치를 단순 비교하지 않도록 전체 26종 기준과 실제 존재하는 암종 기준을 함께 기록했습니다.

## 산출물과 재현
cencer_v7.ipynb 하나에서 모든 처리·선별·학습·저장을 실행합니다. 프로젝트 Python 파일이나 이전 모델 피클은 필수가 아닙니다. 캐시가 있으면 첫 fold 재학습 일치를 확인한 완료 v6 OOF를 재사용하고, 선택 후 전체 train fit도 재사용할 수 있습니다. 없으면 전부 재학습합니다. 전체 train 캐시는 CV/홀드아웃/재분할에서 금지합니다. 원본 데이터와 requirements-v7.txt 환경은 필요합니다. 최종 모델 artifacts/v7/cancer_model_v7.pkl, 제출 submission/혜진_submission_v7.csv, 변수 전체 목록 artifacts/v7/final_features.csv, 변수별 중요도 final_feature_importance.csv를 생성합니다. 피클은 프로젝트 코드 없는 임시 폴더에서 전체 test 2,546명의 CSV·ID·배치 재현성을 검증했습니다. 모델 크기 83.09 MiB입니다. artifacts는 기존 방침대로 Git에서 제외합니다.

## EDA와 최종 변수 해석 파일

eda_by_class.csv에는 암종별 환자 수·변이 유전자 수 평균/중앙값/최대값, eda_mutated_gene_burden.csv에는 train/test 기술통계, eda_missing_by_gene.csv에는 유전자별 결측 수가 있습니다. test 통계는 설명에만 사용합니다.

final_feature_importance.csv는 실제 최종 변수별 트리 중요도, 최대 절대 선형 계수 또는 신경망 첫 층 가중치 norm입니다. 모델 사이에서 수치 크기를 직접 비교할 수 없으며, 임상적 인과성이나 개별 환자의 기여도를 뜻하지 않습니다. 상위 10개씩은 top_features_by_model.csv에 있습니다.

![Development CV comparison](artifacts/v7/validation_comparison_v7.png)

## 원본 프로필 정답 모호성

동일 원본 변이 프로필인데 암종이 다른 그룹 447개, 해당 행 1005개를 확인했습니다. 원본 프로필을 기준으로 함께 묶어 검증에서 분리했고, 정답을 복사하는 규칙으로 사용하지 않았습니다. 전체 학습 데이터를 암기해도 구분할 수 없는 사례의 기술통계이며 test 성능 추정치가 아닙니다.

## 채택 실패 시 산출물

신규 후보가 채택되지 않은 경우 주 모델과 제출 파일은 v6를 유지합니다. artifacts/v7/cancer_model_v7.pkl 및 submission_v7.csv는 최종 유지 모델(v6)의 재현 확인용이며 새로운 예측 모델을 뜻하지 않습니다. 동일한 답안지를 새 제출로 배포하지 않습니다.

## 전처리별 단독 CV 결과

| candidate | clean | noise | score |
| --- | --- | --- | --- |
| channels_aug_lgb | 0.4232 | 0.3394 | 0.3981 |
| resolved_aug_lgb | 0.4226 | 0.3395 | 0.3976 |
| split_syn_aug_lgb | 0.4198 | 0.3338 | 0.3940 |
| split_syn_lr_C0.1 | 0.3969 | 0.2762 | 0.3607 |
| split_syn_lr_C0.5 | 0.3984 | 0.2671 | 0.3590 |
| channels_lr | 0.3927 | 0.2748 | 0.3573 |
| resolved_lr | 0.3919 | 0.2619 | 0.3529 |
| channels_sqrt_lr | 0.3851 | 0.2555 | 0.3462 |
| channels_cap_lr_C0.5 | 0.3896 | 0.2411 | 0.3450 |
| channels_cap_lr_C0.1 | 0.3740 | 0.2380 | 0.3332 |

단독 후보를 v6 앙상블과 직접 비교한 표입니다. 실제 채택 판단에는 미리 정한 v6 혼합 후보와 재분할 점수를 사용했습니다. 표기 정합성 개선만으로 성능 향상을 보장하지 않습니다.

## 변이량별 개발 OOF 정확도

| burden | n | present_classes | v6_accuracy | candidate_accuracy |
| --- | --- | --- | --- | --- |
| 1-10 | 1985 | 25 | 0.4191 | 0.4176 |
| 11-30 | 1873 | 24 | 0.3994 | 0.4036 |
| 31-100 | 796 | 20 | 0.4887 | 0.5013 |
| 101+ | 306 | 21 | 0.6699 | 0.6797 |

후보는 1차 CV에서 고른 고정 후보이며 미채택일 수도 있습니다. 구간별 환자와 암종 구성이 달라 구간 간 점수 차이를 변이량의 인과효과로 해석하지 않습니다.

## v6의 주요 오분류 조합

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
