# 민정 모델 개선 실험

- [원본 보존 복사본](model_민정_v10_original.ipynb)
- [전체 결과와 누수 방지 설명](minjung_experiments/RESULTS.md)
- [최종 선택 모델 재학습 노트북](minjung_experiments/v19_selected_seed_ensemble.ipynb)
- 제출 후보 CSV: `minjung_experiments/submission_selected_core.csv` (노트북 실행 시 로컬 생성, Git 제외)
- [버전별 개발 점수](minjung_experiments/development_results.csv)

17개 설정과 seed 평균을 비교했습니다. 내부 확인용 Macro F1은 기준 0.49751에서 선택 모델 0.50098로 올랐습니다. 리더보드 점수는 아직 확인되지 않았고 대회 제출은 하지 않았습니다. test는 최종 예측에만 사용하며, 중복 프로필의 라벨을 덮어쓰는 규칙은 사용하지 않았습니다.
