# v22 변수 및 학습 선택 기록

검증된 rare_backoff min_df 3·chi2 최대 8,192열을 유지하고 [LightGBM 공식 문서](https://lightgbm.readthedocs.io/en/stable/Parameters.html)의 multiclassova·is_unbalance 설정으로 암종별 binary objective를 사용했습니다. 500회·15 leaves·depth 5로 고정했습니다. 별도 MLP는 hidden 128·alpha 1·180 epoch이며 학습 환자에서만 변이 유전자 10%를 가린 복사본을 추가했습니다. 복사본은 원래 학습 fold에 남고 변수 어휘/빈도는 원본 학습 환자만으로 적합했습니다. augmented 가중치는 원본의 0.5이며 변이량도 가린 입력에 맞춰 다시 계산했습니다. 내부 무작위 validation/early stopping은 사용하지 않았습니다.

최종 조합: `optional_both40`. 새 전체-train 모델 저장: **False**.

독립 학습한 fold 모델들은 비교용입니다. 모든 inner가 기존 기준을 선택하거나 사전 기준을 통과하지 못하면 배포용 새 변수·모델·CSV를 임의로 만들지 않습니다. 기존 v19가 유지됩니다.
