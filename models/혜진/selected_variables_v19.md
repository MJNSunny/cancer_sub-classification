# v19 추가 모델 변수 기록

표현·변수 의미는 [v17 변수](selected_variables_v17.md) 및 [v16 근거](LITERATURE_REVIEW_AND_PREPROCESSING_V16.md)를 따릅니다. 학습 min_df 3·chi2 최대 8,192열·MaxAbs·exact DF 감쇠를 고정하고 선택은 각 학습 fold 안에서만 수행했습니다. 전체 train 선택 목록을 검증 fold에 재사용하지 않았습니다.

최종 모델 저장: **True**.

전체 train 재학습의 추가 모델 열 수:

| model   | family           |   selected_columns |
|:--------|:-----------------|-------------------:|
| cnb     | aa_global        |                181 |
| cnb     | aa_meta          |                690 |
| cnb     | effect           |                625 |
| cnb     | format           |               1164 |
| cnb     | gene             |               1331 |
| cnb     | gene_event_count |                826 |
| cnb     | num              |                 13 |
| cnb     | protein_bin256   |                904 |
| cnb     | protein_bin64    |                463 |
| cnb     | rare_gene        |               1711 |
| cnb     | supported_gene   |                 99 |
| cnb     | variant          |                185 |

실제 전체 변수 목록: `artifacts/v19/new_selected_variables.csv`. 중요도를 인과·병원성으로 해석하지 않습니다.
