# v21 변수 및 학습 선택 기록

기존에 검증한 hierarchical 표현을 유지하고, 이진 변이 집합 Tanimoto 또는 TF-IDF-RBF 유사도를 사용하는 SVC를 새로 학습했습니다. 커널은 90% 범주형 유사도 + 10% 별도 변이량 RBF로 고정했고 C=4, balanced입니다. softmax(OVR margin/2)는 조합용 점수 정규화이며 독립 데이터로 보정된 posterior가 아닙니다. 따라서 확률 합 검증을 calibration 성능 검증으로 해석하지 않습니다.

최종 조합: `v19_reference`. 새 전체-train 모델 저장: **False**.

독립 학습한 fold 모델들은 비교용입니다. 모든 inner가 기존 기준을 선택하거나 사전 기준을 통과하지 못하면 배포용 새 변수·모델·CSV를 임의로 만들지 않습니다. 기존 v19가 유지됩니다.
