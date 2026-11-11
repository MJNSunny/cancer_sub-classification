# v27 최종 변수

| family   |   columns |
|:---------|----------:|
| cnt      |         6 |
| frac     |         6 |
| g        |      4171 |
| gf       |      1536 |
| hs       |      2747 |
| log      |         1 |
| n        |         1 |
| sig      |         6 |
| t        |      2407 |

Geneformer 평균 768열 + 최댓값 768열은 LR 전용입니다. 추정 치환 proxy 6열은 tree와 LR 모두에 있습니다. gene/trunc/hotspot 빈도 선별은 각 학습 fold 안에서 수행했습니다. 전체 최종 목록은 artifacts/v27/selected_variables.csv이며, 전체 train의 최종 목록을 CV fold에 재사용하지 않았습니다.
