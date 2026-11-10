# v14 선별 기준과 최종 변수 상태

최종 제출 후보를 채택하지 않았으므로 새 전체-train 최종 변수 목록·모델은 없습니다. v10의 기존 목록은 selected_variables_v10.md를 참조합니다.

실험용 이진 head는 쌍 학습 부분의 빈도 3 이상 raw 유전자/variant/position/type/aa/numeric/module 표현을 쓰고, binary chi2 상위 512개를 해당 fold 안에서 고릅니다. 각 fold의 목록은 달라집니다. LR만 해당 학습 행렬로 MaxAbs 스케일을 적합하며 tree는 원본 선택 행렬을 사용합니다. class_weight balanced 대 empirical은 목적 비교이며 인과·생물학적 유전자 역할을 확정하지 않습니다. 확률 빈도 보정은 fold 학습 라벨 수에만 의존하고 test나 예측 class 개수에는 의존하지 않습니다. 환자별 혼합 비중은 사용하지 않았습니다.

개별 pair/알고리즘/fold별 환자·변수 수: artifacts/v14/pair_feature_audit.csv. 모든 파라미터는 protocol.json, pair_protocol.json과 노트북에 있습니다.
