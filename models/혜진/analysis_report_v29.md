# v29 — 분류기 축소 실험: v25의 표현을 유지한 제거 비교

## 목적과 고정 조건

v25는 14개 분류기의 중첩 앙상블입니다. 이번 실험은 같은 전처리·변수 표현·하이퍼파라미터·모델별 학습 레시피를 유지하면서 분류기를 제거하는 데 집중했습니다. Geneformer·형제 라벨 반전·COAD prior는 추가하지 않았습니다. 외부 환자 테이블이나 사전학습 가중치를 추가하지 않았습니다.

각 분류기의 기존 v25 최종 비중을 유지하고, 남은 비중만 합 1로 정규화했습니다. 새로운 가중치 grid search나 메타 분류기를 학습하지 않았습니다. 원본 raw·가중 표현·희귀 변이 표현·변수 선별은 해당 분류기를 유지하면 그대로 사용합니다. 다만 서로 다른 분류기가 쓰던 표현을 삭제할 때 그 표현을 소비하는 모델도 함께 제거되는 것이므로, 모든 후보가 완전히 같은 변수 집합을 사용한다는 뜻은 아닙니다.

## 선택과 확인의 분리

- 기존 개발 집합 4,960명에서 그룹 3-fold seed29029로 선택했습니다. 동일 raw/정규화 프로필은 같은 그룹입니다.
- 전체 14개를 fit하고 개별 예측을 저장해 각 모델 하나씩 제외한 영향과 예측 일치율을 계산했습니다. 선택 점수로 모델 수와 후보를 고른 사실을 명시합니다.
- 우선 후보는 rich_lr, aug_ova, aug_mlp의 7개 비어 있지 않은 부분집합입니다. 2~3개 구성도 같은 기준으로 평가했습니다.
- 14개에서 출발한 greedy 제거에서는 각 단계의 허용 오차를 만족하는 제거 중 일반 F1이 가장 높은 것을 택했습니다. 가능한 후보 중 **가장 적은 모델 수**를 선택하고, 같은 수에서는 일반 F1과 합성 조건 성능을 순서대로 비교했습니다.
- 선택 단계 허용치는 평균 F1 -0.003, 최악 fold -0.005, 합성 희귀 변이35 평균 -0.003, 최악 fold -0.01입니다. 이는 공학적 성능/비용 절충 기준이며 임상 동등성 기준이 아닙니다.
- 1차 4개 후보는 seed29030 그룹 5-fold에서 확인했습니다. 실패 후 보수적 9개를 별도 고정하고 seed29032 그룹 5-fold에서 확인했습니다. 각 과정의 baseline을 새로 fit하고 해당 학습 모델만 추출해 비교했습니다.
- 선택한 모델만 별도 재학습한 검사는 1차 4개는 5개 fold, 보수적 9개 후속은 fold0에서 수행했습니다. 최종 배포에서도 선택 모델만 fit했습니다. 제거 모델까지 학습해야 하는 가짜 축소 파이프라인이 아닙니다.
- 선택/확인은 분할이 다르지만 같은 과거 개발 환자를 사용합니다. 독립 외부 환자나 완전히 미관측 검증으로 주장하지 않습니다. 보류 1,241명은 평가하지 않았습니다.

## 분류기 하나씩 제외한 영향 — 선택 단계

| removed                     | label                              | members                                                                                                                                                                          |   count |   mean_f1 |   mean_delta |   worst_fold_delta |   noise35_mean_delta |   noise35_worst_delta | eligible   |
|:----------------------------|:-----------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------:|----------:|-------------:|-------------------:|---------------------:|----------------------:|:-----------|
| legacy_lr                   | remove_legacy_lr                   | legacy_lgb|legacy_extra|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|gated_s3_aug_global_lgb4096|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp   |      13 |  0.478313 |  0.000694867 |       -2.17967e-05 |         -0.000342896 |          -0.00312368  | True       |
| legacy_lgb                  | remove_legacy_lgb                  | legacy_lr|legacy_extra|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|gated_s3_aug_global_lgb4096|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp    |      13 |  0.477812 |  0.000194234 |       -0.00221737  |          0.00223244  |          -4.76565e-05 | True       |
| legacy_extra                | remove_legacy_extra                | legacy_lr|legacy_lgb|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|gated_s3_aug_global_lgb4096|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp      |      13 |  0.478335 |  0.000716731 |        0.000419506 |          0.000111717 |          -0.000543146 | True       |
| gated_s3_aug_lgb            | remove_gated_s3_aug_lgb            | legacy_lr|legacy_lgb|legacy_extra|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|gated_s3_aug_global_lgb4096|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp          |      13 |  0.482528 |  0.00490985  |        0.000826261 |          0.00410338  |           0.000943923 | True       |
| raw_aug_xgb_d5              | remove_raw_aug_xgb_d5              | legacy_lr|legacy_lgb|legacy_extra|gated_s3_aug_lgb|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|gated_s3_aug_global_lgb4096|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp        |      13 |  0.478785 |  0.00116716  |       -0.00164383  |          0.00344735  |           0.00146555  | True       |
| raw_lr_k2048_C0.1           | remove_raw_lr_k2048_C0.1           | legacy_lr|legacy_lgb|legacy_extra|gated_s3_aug_lgb|raw_aug_xgb_d5|gated_syn_down_mlp_a1|gated_s3_aug_global_lgb4096|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp           |      13 |  0.478902 |  0.00128445  |       -0.000119415 |          0.000473816 |          -9.58264e-05 | True       |
| gated_syn_down_mlp_a1       | remove_gated_syn_down_mlp_a1       | legacy_lr|legacy_lgb|legacy_extra|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_s3_aug_global_lgb4096|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp               |      13 |  0.4778   |  0.000182263 |       -0.000155165 |         -0.000902557 |          -0.00214227  | True       |
| gated_s3_aug_global_lgb4096 | remove_gated_s3_aug_global_lgb4096 | legacy_lr|legacy_lgb|legacy_extra|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp                     |      13 |  0.482948 |  0.00533048  |        0.00248868  |          0.00350467  |           0.00125213  | True       |
| type_cnb                    | remove_type_cnb                    | legacy_lr|legacy_lgb|legacy_extra|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|gated_s3_aug_global_lgb4096|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp  |      13 |  0.478535 |  0.000916732 |       -0.00376372  |          0.0023731   |           0.000667506 | True       |
| rich_lr                     | remove_rich_lr                     | legacy_lr|legacy_lgb|legacy_extra|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|gated_s3_aug_global_lgb4096|type_cnb|rich_lgb|rare_cnb|aug_ova|aug_mlp |      13 |  0.478019 |  0.000401533 |        0.000106326 |         -0.00416353  |          -0.0138492   | False      |
| rich_lgb                    | remove_rich_lgb                    | legacy_lr|legacy_lgb|legacy_extra|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|gated_s3_aug_global_lgb4096|type_cnb|rich_lr|rare_cnb|aug_ova|aug_mlp  |      13 |  0.462389 | -0.015229    |       -0.0196918   |          0.0087682   |           0.0020907   | False      |
| rare_cnb                    | remove_rare_cnb                    | legacy_lr|legacy_lgb|legacy_extra|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|gated_s3_aug_global_lgb4096|type_cnb|rich_lr|rich_lgb|aug_ova|aug_mlp  |      13 |  0.478415 |  0.000796722 |       -0.0012707   |         -2.35491e-07 |          -0.00199559  | True       |
| aug_ova                     | remove_aug_ova                     | legacy_lr|legacy_lgb|legacy_extra|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|gated_s3_aug_global_lgb4096|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_mlp |      13 |  0.463744 | -0.0138739   |       -0.0222655   |         -0.0176143   |          -0.0202574   | False      |
| aug_mlp                     | remove_aug_mlp                     | legacy_lr|legacy_lgb|legacy_extra|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|gated_s3_aug_global_lgb4096|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova |      13 |  0.47898  |  0.00136247  |        0.00101859  |         -0.0050588   |          -0.00857349  | False      |

낮은 혼합 비중이나 높은 예측 일치율만으로 필요 없다고 단정하지 않고, 실제 제외 시 clean/noise 변화를 함께 확인했습니다. 예측 일치율 행렬은 `screen_prediction_agreement.csv`입니다. 상관관계는 설명용이고 최종 확인 결과로 모델을 다시 고르지 않았습니다.

## 핵심 1~3개 후보

| label   | members                 |   count |   mean_f1 |   mean_delta |   worst_fold_delta |   noise35_mean_delta |   noise35_worst_delta | eligible   |
|:--------|:------------------------|--------:|----------:|-------------:|-------------------:|---------------------:|----------------------:|:-----------|
| core_1  | rich_lr                 |       1 |  0.37454  |  -0.103078   |         -0.106139  |           -0.043645  |            -0.0594522 | False      |
| core_1  | aug_ova                 |       1 |  0.464612 |  -0.0130056  |         -0.0140379 |            0.0225947 |             0.0152418 | False      |
| core_1  | aug_mlp                 |       1 |  0.37127  |  -0.106348   |         -0.113884  |           -0.0280365 |            -0.0379039 | False      |
| core_2  | rich_lr|aug_ova         |       2 |  0.458801 |  -0.0188172  |         -0.0236127 |            0.0190761 |             0.0120732 | False      |
| core_2  | rich_lr|aug_mlp         |       2 |  0.400838 |  -0.0767805  |         -0.0795637 |           -0.0207241 |            -0.0255864 | False      |
| core_2  | aug_ova|aug_mlp         |       2 |  0.471484 |  -0.00613372 |         -0.0121011 |            0.0377731 |             0.0338173 | False      |
| core_3  | rich_lr|aug_ova|aug_mlp |       3 |  0.452594 |  -0.0250237  |         -0.0310593 |            0.0193102 |             0.0145471 | False      |

## Greedy 제거 경로

| removed                     | label                               | members                                                                                                                                                      |   count |   mean_f1 |   mean_delta |   worst_fold_delta |   noise35_mean_delta |   noise35_worst_delta | eligible   |
|:----------------------------|:------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|--------:|----------:|-------------:|-------------------:|---------------------:|----------------------:|:-----------|
| gated_s3_aug_global_lgb4096 | remove_gated_s3_aug_global_lgb4096  | legacy_lr|legacy_lgb|legacy_extra|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp |      13 |  0.482948 |   0.00533048 |        0.00248868  |           0.00350467 |           0.00125213  | True       |
| legacy_lr                   | greedy_remove_legacy_lr             | legacy_lgb|legacy_extra|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp           |      12 |  0.484667 |   0.00704886 |        0.00416676  |           0.00391144 |          -0.000119997 | True       |
| legacy_extra                | greedy_remove_legacy_extra          | legacy_lgb|gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp                        |      11 |  0.484775 |   0.00715704 |        0.00402808  |           0.00162612 |          -0.000171881 | True       |
| legacy_lgb                  | greedy_remove_legacy_lgb            | gated_s3_aug_lgb|raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp                                   |      10 |  0.48395  |   0.00633166 |        0.00100134  |           0.00517751 |           0.00164092  | True       |
| gated_s3_aug_lgb            | greedy_remove_gated_s3_aug_lgb      | raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova|aug_mlp                                                    |       9 |  0.483738 |   0.00612049 |        0.00397358  |           0.00721167 |           0.00237425  | True       |
| aug_mlp                     | greedy_remove_aug_mlp               | raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|type_cnb|rich_lr|rich_lgb|rare_cnb|aug_ova                                                            |       8 |  0.484777 |   0.00715925 |        0.00485846  |           0.00419213 |          -0.00511436  | True       |
| type_cnb                    | greedy_remove_type_cnb              | raw_aug_xgb_d5|raw_lr_k2048_C0.1|gated_syn_down_mlp_a1|rich_lr|rich_lgb|rare_cnb|aug_ova                                                                     |       7 |  0.484307 |   0.00668951 |        0.00430154  |           0.0059441  |          -0.00289933  | True       |
| raw_lr_k2048_C0.1           | greedy_remove_raw_lr_k2048_C0.1     | raw_aug_xgb_d5|gated_syn_down_mlp_a1|rich_lr|rich_lgb|rare_cnb|aug_ova                                                                                       |       6 |  0.482383 |   0.00476495 |        0.00280954  |           0.0076737  |          -0.00195034  | True       |
| raw_aug_xgb_d5              | greedy_remove_raw_aug_xgb_d5        | gated_syn_down_mlp_a1|rich_lr|rich_lgb|rare_cnb|aug_ova                                                                                                      |       5 |  0.481784 |   0.00416623 |        0.000648425 |           0.00708128 |          -0.00168072  | True       |
| gated_syn_down_mlp_a1       | greedy_remove_gated_syn_down_mlp_a1 | rich_lr|rich_lgb|rare_cnb|aug_ova                                                                                                                            |       4 |  0.480531 |   0.0029134  |       -0.00209469  |           0.00616805 |          -0.00222401  | True       |

## 원래 4개 후보의 실패와 보수적 후속 가설

원래 최소 후보는 rich_lr/rich_lgb/rare_cnb/aug_ova 4개였습니다. seed29030 확인에서 평균 F1은 baseline 0.499909 → compact 0.494153, 차이 -0.005756, 최악 fold -0.015481로 기준을 통과하지 못했습니다. **이 원래 실패 판정은 유지합니다.**

|   fold |   baseline_f1 |   candidate_f1 |       delta |   baseline_accuracy |   candidate_accuracy |   noise35_delta |   full_fit_seconds |   compact_fit_seconds |   full_predict_seconds |   compact_predict_seconds |
|-------:|--------------:|---------------:|------------:|--------------------:|---------------------:|----------------:|-------------------:|----------------------:|-----------------------:|--------------------------:|
|      0 |      0.515671 |       0.500191 | -0.0154805  |            0.498992 |             0.49496  |     0.00873473  |            191.479 |               76.0618 |                4.3626  |                   1.07157 |
|      1 |      0.502945 |       0.497732 | -0.0052131  |            0.485398 |             0.492447 |    -0.00877382  |            193.276 |               76.3642 |                4.14556 |                   1.1255  |
|      2 |      0.474921 |       0.463967 | -0.0109544  |            0.481332 |             0.475277 |     0.000826432 |            187.878 |               76.1648 |                4.07925 |                   0.9633  |
|      3 |      0.515623 |       0.521148 |  0.00552474 |            0.496976 |             0.517137 |     0.0143057   |            199.737 |               73.3177 |                4.67165 |                   1.17484 |
|      4 |      0.490387 |       0.487728 | -0.00265893 |            0.501008 |             0.50504  |     0.0166951   |            186.957 |               66.2446 |                5.23621 |                   1.15876 |

첫 확인 fold에서 최악 허용 손실을 넘긴 것을 본 뒤, 원래 screen greedy 경로 중 기존 비중 85% 이상을 보존하는 최소 구성을 별도 후속 가설로 고정했습니다. 그 결과 9개와 원래 비중 85.951562%가 남았습니다. 85%는 실패 뒤 정한 공학적 보수 조건이며 통계/임상 보장이 아닙니다. 새로운 후속 결과를 보기 전에 파일에 고정했고, 허용 F1·noise 기준은 완화하지 않았습니다.

후속은 **seed29032 그룹 5-fold**로 모든 baseline 모델을 새로 fit했습니다. 같은 과거 개발 환자라 독립 외부 검증이 아니고 적응적 설계 편향이 남습니다. 추론 시간은 5개 fold 모두에서 측정했고, 선택 모델만 별도 fit한 학습비용/예측 동치 벤치마크는 후속 fold0에서만 수행했습니다. 아래 최종 확인 표·모델·CSV는 이 보수적 후속 9개 구성입니다. 원래 4개의 실패를 통과로 바꾸거나 결과가 좋은 쪽을 숨겨 보고하지 않았습니다.

## 후속 고정 구성


선택 모델 **9개 / 기존 14개**:

```json
{
  "raw_aug_xgb_d5": 0.039757130651347956,
  "raw_lr_k2048_C0.1": 0.039757130651347956,
  "gated_syn_down_mlp_a1": 0.039757130651347956,
  "type_cnb": 0.09423912450689888,
  "rich_lr": 0.12565216600919848,
  "rich_lgb": 0.12565216600919848,
  "rare_cnb": 0.06980675889399916,
  "aug_ova": 0.23268919631333057,
  "aug_mlp": 0.23268919631333057
}
```

핵심 3개로 반드시 줄이겠다고 결과를 왜곡하지 않았습니다. 미리 정한 후보와 greedy 경로 안에서 고른 최소 구성입니다. 14개의 모든 부분집합을 전수 탐색한 것은 아니므로 어떤 3개 조합도 불가능하다는 증명은 아닙니다. 성능 차이의 원인을 개별 생물학적 변수의 인과관계로 해석하지 않습니다.

## 보수적 후속 그룹 5-fold 확인 결과

|   fold |   baseline_f1 |   candidate_f1 |        delta |   baseline_accuracy |   candidate_accuracy |   noise35_delta |   full_fit_seconds |   compact_fit_seconds |   full_predict_seconds |   compact_predict_seconds |
|-------:|--------------:|---------------:|-------------:|--------------------:|---------------------:|----------------:|-------------------:|----------------------:|-----------------------:|--------------------------:|
|      0 |      0.517391 |       0.522736 |  0.00534424  |            0.506048 |             0.510081 |      0.00782423 |            217.565 |               150.618 |                4.12286 |                   1.97834 |
|      1 |      0.464802 |       0.464869 |  6.64189e-05 |            0.47379  |             0.475806 |      0.00494417 |            201.459 |               nan     |                4.27675 |                   2.05975 |
|      2 |      0.471048 |       0.469139 | -0.00190906  |            0.470766 |             0.466734 |      0.0111744  |            212.26  |               nan     |                4.39316 |                   1.90632 |
|      3 |      0.49573  |       0.496357 |  0.000627001 |            0.493952 |             0.498992 |      0.0120895  |            193.749 |               nan     |                4.42952 |                   2.22843 |
|      4 |      0.483125 |       0.485161 |  0.00203569  |            0.478831 |             0.481855 |      0.00125129 |            178.062 |               nan     |                4.01887 |                   1.79441 |

- v25 평균 Macro F1: **0.486419**
- 축소 모델 평균 Macro F1: **0.487652**
- 축소 모델 평균 정확도: **48.6694%**
- 평균 차이 **+0.001233**, 최악 fold 차이 **-0.001909**
- 합성 희귀 변이35 평균 차이 **+0.007457**, 최악 fold **+0.001251**
- 고정 pooled OOF 차이 조건부 그룹 bootstrap 95% 구간 `[-0.004331232939197567, 0.007079101943404755]`
- 사전 성능 유지 확인 기준 통과: **True**

확인 기준은 평균 -0.003, 최악 fold -0.005, 조건부 bootstrap 하한>-0.005, noise 평균 -0.003·최악 -0.01입니다. 원래 가설의 유지 기준을 결과에 맞춰 완화하지 않았습니다. bootstrap은 고정 예측의 조건부 구간으로 학습·선택 전체 불확실성을 포함하지 않습니다. 전체 평균 유지가 개별 암종의 안전성을 입증하지 않습니다.

## 비용과 구현

- 동일한 검증 입력 128명, warm-up 후 3회, full/compact 실행 순서를 교대했습니다. 역직렬화 시간은 제외했습니다.
- fold별 추론 시간 비율 중앙값: **0.4798** (낮을수록 빠름).
- 선택 모델만 새로 fit한 시간 비율(실측 1 fold): **0.6923**. 이 fit 타이머는 양쪽 모두 공통 데이터 로드·라이브러리 import·정의 초기화를 제외하며, 처음부터 끝까지의 전체 실행 시간을 뜻하지 않습니다.
- 최종 피클 크기: **129,099,771 bytes**, v25 **200,829,011 bytes**, 비율 **0.6428**.
- compact 구현은 같은 pointwise 파싱을 여러 모델에서 공유합니다. 예측 동치 검사를 했지만 시간 감소를 모델 수 감소 하나만의 효과로 단정하지 않습니다. CPU 두 worker 병렬 부하와 캐시·실행 환경에 따른 타이밍 편차가 남습니다.
- 선택된 모델만 train 전체 6,201명에서 새로 학습했고, 제외 모델은 최종 재학습하지 않았습니다. 원본 full 모델을 숨겨서 compact 객체에 넣지 않았습니다.

## 암종별 사후 진단

| SUBCLASS   |   support |   baseline_f1 |   compact_f1 |        delta |
|:-----------|----------:|--------------:|-------------:|-------------:|
| ACC        |        58 |      0.945455 |     0.945455 |  0           |
| BLCA       |        84 |      0.478261 |     0.467153 | -0.0111076   |
| BRCA       |       629 |      0.556405 |     0.550373 | -0.00603222  |
| CESC       |       124 |      0.365854 |     0.371901 |  0.00604717  |
| COAD       |       179 |      0.744745 |     0.742515 | -0.00222977  |
| DLBC       |        31 |      0.35     |     0.341463 | -0.00853659  |
| GBMLGG     |       369 |      0.355872 |     0.407534 |  0.0516624   |
| HNSC       |       179 |      0.366279 |     0.368272 |  0.00199288  |
| KIPAN      |       412 |      0.363636 |     0.382148 |  0.0185115   |
| KIRC       |       267 |      0.418803 |     0.382022 | -0.0367809   |
| LAML       |       127 |      0.57265  |     0.593886 |  0.0212369   |
| LGG        |       183 |      0.560345 |     0.550336 | -0.0100093   |
| LIHC       |       127 |      0.37751  |     0.385542 |  0.00803213  |
| LUAD       |       148 |      0.475472 |     0.477612 |  0.00214024  |
| LUSC       |       143 |      0.583333 |     0.56446  | -0.0188734   |
| OV         |       203 |      0.423932 |     0.417808 | -0.0061234   |
| PAAD       |        96 |      0.369942 |     0.380435 |  0.0104926   |
| PCPG       |       118 |      0.310078 |     0.30563  | -0.00444749  |
| PRAD       |       213 |      0.343234 |     0.355556 |  0.0123212   |
| SARC       |       159 |      0.210826 |     0.196629 | -0.014197    |
| SKCM       |       221 |      0.857143 |     0.863309 |  0.0061665   |
| STES       |       303 |      0.530541 |     0.538194 |  0.00765343  |
| TGCT       |       100 |      0.531365 |     0.531835 |  0.000469892 |
| THCA       |       260 |      0.733624 |     0.742857 |  0.00923269  |
| THYM       |        68 |      0.25098  |     0.241758 | -0.00922215  |
| UCEC       |       159 |      0.643068 |     0.644776 |  0.00170827  |

위 표는 결과 설명용이며 이 결과로 선택이나 비중을 다시 조정하지 않았습니다. 개별 암종 성능과 작은 클래스의 불확실성을 별도로 검토해야 합니다.

## 저장·재현

- `cencer_v29.ipynb`: 모든 구성 정의·선택·그룹 확인·선택 모델만 전체 학습·저장·최종 추론 포함. worker/core는 노트북이 artifacts 아래 생성하며 외부 프로젝트 Python 파일이 필요하지 않습니다.
- `artifacts/v29/cancer_model_v29_pruned_experimental.pkl`: 선택된 분류기만 포함. predict_frame 입력은 genes_, 출력 확률 순서는 classes_.
- `artifacts/v29/selected_variables.csv`: 각 잔존 모델의 실제 전체 train 변수 목록. 선별은 CV에서 각 학습 fold마다 수행했습니다.
- `submission/혜진_submission_v29_pruned_experimental.csv`: 고정 최종 모델 예측, Public 미확인.
- `requirements-v29.txt`.

연구 프로세스는 test/sample 접근을 차단했고, 마지막 별도 프로세스에서 고정 모델 추론만 수행했습니다. X/* 표기 일관성, 저장 후 재로딩·배치 순서 독립성을 확인했습니다. 기존 legacy-X 가정의 과거 test 관찰 출처는 유지합니다. 기존 데이터·모델·제출 파일을 보존했습니다. v25의 실제 Public은 **0.390417094**이며, 이번 후보가 이를 유지/개선하는지는 미확인입니다. 임상 적용 안전성·확률 보정·미지 암종 검증을 완료했다고 주장하지 않습니다.


<!-- PUBLIC_V29_20261112 -->
## 실제 제출 결과 — v29 (2026-11-12 사용자 보고)

- 제출 파일: `submission/혜진_submission_v29_pruned_experimental.csv`
- Public Macro F1: **0.3917888655**
- 이전 v25 Public **0.390417094** 대비 **+0.0013717715** (약 +0.13718 퍼센트포인트).
- 현재 사용자 보고로 확인된 **혜진 버전의 Public 최고 기록**을 갱신했습니다. 팀 전체 최고 기록이라는 뜻은 아닙니다.
- v29는 v25의 14개 분류기를 9개로 축소하고 기존 상대 가중치를 정규화한 뒤 전체 train에서 재학습한 후보입니다.
- 같은 그룹 5-fold의 평균 F1 차이 +0.001233과 이번 Public 차이는 별개의 결과입니다. 이번 제출 점수는 관측된 소폭 개선이며 일반화 성능의 통계적 우월성을 입증하지 않습니다.
- 점수 출처는 사용자 보고이며 대회 사이트 직접 조회 결과는 아닙니다. 기존 학습 시점 verification JSON의 Public 미확인 기록은 당시 상태로 보존합니다.
