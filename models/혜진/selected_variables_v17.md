# v17 최종 추가 모델 입력 변수

전체 목록은 `artifacts/v17/new_selected_variables.csv`와 저장 피클에 보관합니다. 기존 구성 모델의 변수 의미는 [v6 변수 기록](selected_variables_v6.md), 새 변이 표현의 정의는 [v16 문헌 보고서](LITERATURE_REVIEW_AND_PREPROCESSING_V16.md)를 따릅니다.

선택은 학습 fold에서 min_df 3·chi2 최대 8,192열로 수행합니다. MaxAbs는 학습 부분에만 적합하고 exact 변이는 그 뒤 DF/(DF+5)로 감쇠합니다. 최종 전체-train 변수 목록을 검증 fold에 재사용하지 않았습니다. 이 실험은 8,192가 모든 문제에서 최적임을 증명하지 않습니다.

## 추가 모델별 실제 열 수

| model   | family           |   selected_columns |
|:--------|:-----------------|-------------------:|
| lr      | aa_global        |                181 |
| lr      | aa_meta          |                690 |
| lr      | effect           |                625 |
| lr      | format           |               1164 |
| lr      | gene             |               1331 |
| lr      | gene_event_count |                826 |
| lr      | num              |                 13 |
| lr      | protein_bin256   |                904 |
| lr      | protein_bin64    |                463 |
| lr      | rare_gene        |               1711 |
| lr      | supported_gene   |                 99 |
| lr      | variant          |                185 |
| lgb     | aa_global        |                181 |
| lgb     | aa_meta          |                690 |
| lgb     | effect           |                625 |
| lgb     | format           |               1164 |
| lgb     | gene             |               1331 |
| lgb     | gene_event_count |                826 |
| lgb     | num              |                 13 |
| lgb     | protein_bin256   |                904 |
| lgb     | protein_bin64    |                463 |
| lgb     | rare_gene        |               1711 |
| lgb     | supported_gene   |                 99 |
| lgb     | variant          |                185 |

## 전체 train 재학습 모델의 중요도 상위 40개씩

LR 값은 변환된 입력의 클래스별 계수 절댓값 최댓값이고 LightGBM 값은 분할 사용 횟수입니다. 모델 간 수치 크기를 비교하거나 인과·병원성으로 해석하지 않습니다. 이 순위로 다시 선택·튜닝하지 않았습니다.

| model   | feature                     |   importance | metric                                   |
|:--------|:----------------------------|-------------:|:-----------------------------------------|
| lr      | num:log_unseen_events       |      5.9499  | max_abs_coefficient_on_transformed_input |
| lr      | num:log_observed_genes      |      2.47191 | max_abs_coefficient_on_transformed_input |
| lr      | num:log_unique_events       |      2.28195 | max_abs_coefficient_on_transformed_input |
| lr      | gene:APC                    |      2.22508 | max_abs_coefficient_on_transformed_input |
| lr      | num:log_rare_events         |      2.16886 | max_abs_coefficient_on_transformed_input |
| lr      | num:log_raw_tokens          |      2.1624  | max_abs_coefficient_on_transformed_input |
| lr      | num:log_resolved_components |      2.15685 | max_abs_coefficient_on_transformed_input |
| lr      | format:APC:stop_gained      |      2.06116 | max_abs_coefficient_on_transformed_input |
| lr      | rare_gene:GPR87             |      2.04544 | max_abs_coefficient_on_transformed_input |
| lr      | gene:TP53                   |      1.85373 | max_abs_coefficient_on_transformed_input |
| lr      | gene:DSC2                   |      1.84918 | max_abs_coefficient_on_transformed_input |
| lr      | num:log_frameshift          |      1.7649  | max_abs_coefficient_on_transformed_input |
| lr      | num:log_missense            |      1.70731 | max_abs_coefficient_on_transformed_input |
| lr      | format:MYH10:synonymous     |      1.64179 | max_abs_coefficient_on_transformed_input |
| lr      | num:log_synonymous          |      1.54563 | max_abs_coefficient_on_transformed_input |
| lr      | gene:MYH10                  |      1.51947 | max_abs_coefficient_on_transformed_input |
| lr      | gene:MAP7                   |      1.48533 | max_abs_coefficient_on_transformed_input |
| lr      | format:NF1:frameshift       |      1.4844  | max_abs_coefficient_on_transformed_input |
| lr      | protein_bin256:VHL:0        |      1.46319 | max_abs_coefficient_on_transformed_input |
| lr      | gene:ABCA2                  |      1.46196 | max_abs_coefficient_on_transformed_input |
| lr      | gene:TG                     |      1.4557  | max_abs_coefficient_on_transformed_input |
| lr      | format:FLNC:missense        |      1.43434 | max_abs_coefficient_on_transformed_input |
| lr      | protein_bin256:APC:5        |      1.41275 | max_abs_coefficient_on_transformed_input |
| lr      | gene:VHL                    |      1.38544 | max_abs_coefficient_on_transformed_input |
| lr      | num:fraction_frameshift     |      1.3841  | max_abs_coefficient_on_transformed_input |
| lr      | gene:ATRX                   |      1.36523 | max_abs_coefficient_on_transformed_input |
| lr      | gene:FLNC                   |      1.33205 | max_abs_coefficient_on_transformed_input |
| lr      | aa_meta:IDH1:R>H            |      1.3311  | max_abs_coefficient_on_transformed_input |
| lr      | variant:IDH1:R132H          |      1.3121  | max_abs_coefficient_on_transformed_input |
| lr      | format:ATRX:stop_gained     |      1.29095 | max_abs_coefficient_on_transformed_input |
| lr      | gene:BRCA1                  |      1.28536 | max_abs_coefficient_on_transformed_input |
| lr      | gene:MAGI2                  |      1.26869 | max_abs_coefficient_on_transformed_input |
| lr      | aa_meta:BRAF:V>E            |      1.26205 | max_abs_coefficient_on_transformed_input |
| lr      | num:log_duplicate_tokens    |      1.24867 | max_abs_coefficient_on_transformed_input |
| lr      | variant:BRAF:V600E          |      1.24269 | max_abs_coefficient_on_transformed_input |
| lr      | format:PIK3CA:missense      |      1.23187 | max_abs_coefficient_on_transformed_input |
| lr      | gene:TUBGCP5                |      1.21173 | max_abs_coefficient_on_transformed_input |
| lr      | protein_bin64:AKR1C2:1      |      1.20693 | max_abs_coefficient_on_transformed_input |
| lr      | gene:E2F8                   |      1.20259 | max_abs_coefficient_on_transformed_input |
| lr      | gene:NOTCH1                 |      1.19801 | max_abs_coefficient_on_transformed_input |
| lgb     | num:log_unseen_events       |   4070       | LightGBM_split_count                     |
| lgb     | num:fraction_frameshift     |   3810       | LightGBM_split_count                     |
| lgb     | num:log_missense            |   2636       | LightGBM_split_count                     |
| lgb     | num:log_synonymous          |   2394       | LightGBM_split_count                     |
| lgb     | num:log_observed_genes      |   2297       | LightGBM_split_count                     |
| lgb     | num:log_rare_events         |   1632       | LightGBM_split_count                     |
| lgb     | num:log_resolved_components |   1606       | LightGBM_split_count                     |
| lgb     | num:log_raw_tokens          |   1569       | LightGBM_split_count                     |
| lgb     | aa_global:R>H               |   1553       | LightGBM_split_count                     |
| lgb     | aa_global:R>C               |   1120       | LightGBM_split_count                     |
| lgb     | gene:TP53                   |   1090       | LightGBM_split_count                     |
| lgb     | aa_global:R>Q               |   1070       | LightGBM_split_count                     |
| lgb     | aa_global:L>L               |   1039       | LightGBM_split_count                     |
| lgb     | aa_global:E>K               |    922       | LightGBM_split_count                     |
| lgb     | num:log_frameshift          |    909       | LightGBM_split_count                     |
| lgb     | aa_global:A>T               |    841       | LightGBM_split_count                     |
| lgb     | aa_global:R>W               |    833       | LightGBM_split_count                     |
| lgb     | num:log_stop_gained         |    806       | LightGBM_split_count                     |
| lgb     | aa_global:A>V               |    805       | LightGBM_split_count                     |
| lgb     | aa_global:E>Q               |    719       | LightGBM_split_count                     |
| lgb     | aa_global:D>N               |    695       | LightGBM_split_count                     |
| lgb     | aa_global:P>P               |    665       | LightGBM_split_count                     |
| lgb     | aa_global:R>*               |    652       | LightGBM_split_count                     |
| lgb     | aa_global:A>A               |    621       | LightGBM_split_count                     |
| lgb     | aa_global:V>I               |    611       | LightGBM_split_count                     |
| lgb     | aa_global:P>L               |    607       | LightGBM_split_count                     |
| lgb     | aa_global:T>M               |    593       | LightGBM_split_count                     |
| lgb     | aa_global:G>G               |    526       | LightGBM_split_count                     |
| lgb     | num:log_duplicate_tokens    |    494       | LightGBM_split_count                     |
| lgb     | aa_global:S>F               |    492       | LightGBM_split_count                     |
| lgb     | aa_global:A>S               |    490       | LightGBM_split_count                     |
| lgb     | aa_global:F>F               |    490       | LightGBM_split_count                     |
| lgb     | aa_global:S>S               |    484       | LightGBM_split_count                     |
| lgb     | num:log_unique_events       |    479       | LightGBM_split_count                     |
| lgb     | aa_global:V>V               |    476       | LightGBM_split_count                     |
| lgb     | aa_global:R>L               |    453       | LightGBM_split_count                     |
| lgb     | gene:VHL                    |    430       | LightGBM_split_count                     |
| lgb     | aa_global:V>M               |    420       | LightGBM_split_count                     |
| lgb     | gene_event_count:TP53       |    417       | LightGBM_split_count                     |
| lgb     | aa_global:T>T               |    415       | LightGBM_split_count                     |
