# v18 추가 모델 변수 기록

표현·변수 의미는 [v17 변수](selected_variables_v17.md) 및 [v16 근거](LITERATURE_REVIEW_AND_PREPROCESSING_V16.md)를 따릅니다. 학습 min_df 3·chi2 최대 8,192열·MaxAbs·exact DF 감쇠를 고정하고 선택은 각 학습 fold 안에서만 수행했습니다. 전체 train 선택 목록을 검증 fold에 재사용하지 않았습니다.

최종 모델 저장: **False**.

미채택 실험이므로 최종 전체-train 변수 목록을 생성하지 않았습니다. Fold별로 학습한 변수/모델은 검증용이며 배포 모델이 아닙니다. v17을 유지합니다.

## 후속 진단의 별도 실험용 모델

저장 여부: **True**. 저장 시 실제 목록은 `artifacts/v18/followup_selected_variables.csv`입니다. v17 80%+새 XGB 20%이며 동일 rare_backoff min_df 3·chi2 최대 8,192열을 사용합니다. 원래 gate 미통과를 뒤집는 모델 채택이 아닙니다.
