# v28 형제 라벨 구조 별도 감사 — 기본 모델에 미적용

실제 train만 읽어 확인했습니다. test는 열지 않았고 정답 반전 규칙을 제출에 넣지 않았습니다.

```json
{
  "train_only": true,
  "raw_identical_profile_groups": 451,
  "multi_label_duplicate_groups": 447,
  "duplicate_group_label_sets": {
    "KIPAN / KIRC": 272,
    "GBMLGG / LGG": 173,
    "BRCA / CESC / GBMLGG / KIPAN / KIRC / LAML / LGG / LUSC / PAAD / PCPG / PRAD / SARC / STES / THCA / THYM": 1,
    "LGG / THCA": 1,
    "LAML": 3,
    "KIPAN": 1
  },
  "random_row_5fold_diagnostic": [
    {
      "fold": 0,
      "matched_rows": 147,
      "correct_under_flip": 146,
      "conditional_accuracy": 0.9931972789115646
    },
    {
      "fold": 1,
      "matched_rows": 145,
      "correct_under_flip": 145,
      "conditional_accuracy": 1.0
    },
    {
      "fold": 2,
      "matched_rows": 143,
      "correct_under_flip": 143,
      "conditional_accuracy": 1.0
    },
    {
      "fold": 3,
      "matched_rows": 148,
      "correct_under_flip": 147,
      "conditional_accuracy": 0.9932432432432432
    },
    {
      "fold": 4,
      "matched_rows": 134,
      "correct_under_flip": 134,
      "conditional_accuracy": 1.0
    }
  ],
  "random_matched_total": 717,
  "random_conditional_accuracy": 0.99721059972106,
  "group_5fold_matches": [
    {
      "fold": 0,
      "matched_rows": 0
    },
    {
      "fold": 1,
      "matched_rows": 0
    },
    {
      "fold": 2,
      "matched_rows": 0
    },
    {
      "fold": 3,
      "matched_rows": 0
    },
    {
      "fold": 4,
      "matched_rows": 0
    }
  ],
  "test_examined": false,
  "rule_applied_to_submission": false,
  "limitations": "identical observed mutation profiles do not establish patient identity; random-row diagnostic measures duplicate-structure exploitation and cannot establish independent patient generalization; opposite label on competition test not guaranteed; official competition rule page could not be retrieved due anti-bot challenge, no approval inferred"
}
```

같은 변이 프로필과 환자 동일성은 구분해야 합니다. 무작위 행 분할에서 동일 프로필이 양쪽에 남을 때의 조건부 정확도는 중복 구조를 이용한 진단이며, 새로운 환자에 대한 성능이 아닙니다. 그룹 분할에서는 이 규칙의 효과를 측정할 수 없습니다. test의 반대 라벨이 항상 정답이라는 보장도 없으며, 이번 v28 기본 예측에는 적용하지 않았습니다.

[해당 대회 규칙 페이지](https://dacon.io/competitions/official/236355/overview/rules)는 자동 접근 시 JavaScript/로봇 확인으로 본문을 읽지 못했습니다. 다른 대회의 일반 규칙으로 허용 또는 금지를 대신 판정하지 않았습니다.
