# v29 잔존 모델과 변수

선택 모델: raw_aug_xgb_d5, raw_lr_k2048_C0.1, gated_syn_down_mlp_a1, type_cnb, rich_lr, rich_lgb, rare_cnb, aug_ova, aug_mlp

정규화된 최종 혼합 비중:

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

| model                 |   feature_columns |
|:----------------------|------------------:|
| aug_mlp               |              8192 |
| aug_ova               |              8192 |
| gated_syn_down_mlp_a1 |              1024 |
| rare_cnb              |              8192 |
| raw_aug_xgb_d5        |              2048 |
| raw_lr_k2048_C0.1     |              2048 |
| rich_lgb              |              8192 |
| rich_lr               |              8192 |
| type_cnb              |              4096 |

각 모델의 전처리·변수 표현·하이퍼파라미터는 v25와 동일하며, 전체 목록은 artifacts/v29/selected_variables.csv입니다. 서로 다른 표현의 같은 유전자는 별도 열일 수 있어 열 수를 고유 유전자 수로 해석하지 않습니다. 모델을 제거할 때 원래 비중을 남은 합으로 나눴고 새 가중치 최적화는 하지 않았습니다.
