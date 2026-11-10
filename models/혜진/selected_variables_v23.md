# v23 변수 및 학습 선택 기록

v22의 알려진 희귀 변이 진단 하락을 관찰한 뒤 별도 적응 탐색을 추가했습니다. 손실과 모델 크기는 v22처럼 고정하고, 학습 fold 원본만으로 support가 2 이하인 missense/synonymous/synonymous_block 풀을 만듭니다. 라벨을 보지 않고 유전자 10%를 WT처럼 가리고 평균 20개의 희귀 변이를 추가한 복사본을 학습에만 사용했습니다. 희귀성을 정상·생식세포·비병원성 판정으로 해석하지 않습니다. 어휘·DF·선별·스케일은 원본 학습 환자만으로 적합하고 증강 행은 그 DF의 추론 역할로 변환했습니다. 원본과 복사본 가중치는 1:0.5이며 총 가중치 크기를 보존했습니다. 별도 새 분할에서는 다른 난수와 더 강한 평균 35개 추가 조건도 고정해 확인합니다. 알려진 공격에 맞춘 적응의 편향이 있고 이 합성 입력을 실제 test 분포라고 주장하지 않습니다.

최종 조합: `optional_both40`. 새 전체-train 모델 저장: **False**.

독립 학습한 fold 모델들은 비교용입니다. 모든 inner가 기존 기준을 선택하거나 사전 기준을 통과하지 못하면 배포용 새 변수·모델·CSV를 임의로 만들지 않습니다. 기존 v19가 유지됩니다.

## 별도 후속 진단 모델

조합 `optional_both40`, 저장 **True**. 저장 시 실제 선택 변수는 `artifacts/v23/followup_selected_variables.csv`입니다. 사전 1차 기준 미달은 유지합니다.

## 실제 후속 모델 변수군

| model   | family           |   selected_columns |
|:--------|:-----------------|-------------------:|
| mlp     | aa_global        |                181 |
| mlp     | aa_meta          |                690 |
| mlp     | effect           |                625 |
| mlp     | format           |               1164 |
| mlp     | gene             |               1331 |
| mlp     | gene_event_count |                826 |
| mlp     | num              |                 13 |
| mlp     | protein_bin256   |                904 |
| mlp     | protein_bin64    |                463 |
| mlp     | rare_gene        |               1711 |
| mlp     | supported_gene   |                 99 |
| mlp     | variant          |                185 |
| ova     | aa_global        |                181 |
| ova     | aa_meta          |                690 |
| ova     | effect           |                625 |
| ova     | format           |               1164 |
| ova     | gene             |               1331 |
| ova     | gene_event_count |                826 |
| ova     | num              |                 13 |
| ova     | protein_bin256   |                904 |
| ova     | protein_bin64    |                463 |
| ova     | rare_gene        |               1711 |
| ova     | supported_gene   |                 99 |
| ova     | variant          |                185 |

각 추가 모델은 원본 학습 환자에서 선별한 최대 8,192열을 사용합니다. 전체 목록은 `artifacts/v23/followup_selected_variables.csv`, 기존 v19 변수는 v19 변수 기록을 따릅니다. 전체 train 변수 목록을 CV fold에 재사용하지 않았습니다.
