import csv,json,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent
r=list(csv.DictReader((p/'development_results.csv').open()))
s=json.loads((p/'summary.json').read_text());sel=s['selection'];b=sel['best'];h=s['holdout']
lines=['# 민정 v10 개선 실험 결과 — 2026-11-13','',
'원본은 `../model_민정_v10_original.ipynb`에 바이트 단위로 보존했습니다. 원본 노트북을 그대로 재실행한 점수가 아니라, 누수 방지를 보강한 공통 학습 절차로 다시 비교한 결과입니다.','',
'## 선택 결과','',f"- 개발 CV 선택: **{b['version']}** / Macro F1 **{b['cv_macro_f1']:.5f}** / XGB 비중 {b['xgb_weight']:.2f}",f"- seed42+137 평균 개발 점수: **{sel['seed_ensemble_cv']:.5f}**, 최종 채택: {sel['seed_ensemble']}",f"- 최종 확인용 holdout {h['n']}행: 기준 모델 **{h['baseline_macro_f1']:.5f}**, 선택 모델 **{h['selected_macro_f1']:.5f}**, 차이 **{h['selected_macro_f1']-h['baseline_macro_f1']:+.5f}**",'- 기존 Public 최고점 **0.47959**는 사용자 전달 기준입니다. 새 제출의 Public 점수는 알 수 없으며, 대회 제출은 **0회**입니다.','',
'## 실험별 개발 결과','', '| 버전 | 가중치 α(XGB/LR) | LR C | 표현 | 제외 특징 | XGB 비중 | Macro F1 |','|---|---|---|---|---|---|---|']
for q in r:
 a=q['alpha']; la=q.get('lr_alpha') or a
 lines.append(f"| {q['version']} | {a}/{la} | {q['C']} | {q['mode']} | {q['ablate'] or '-'} | {q['xgb_weight']} | {float(q['cv_macro_f1']):.5f} |")
lines += ['', '## 누수 방지와 점수 해석','',
'- test는 최종 후보와 seed 평균 여부를 고정한 뒤에만 읽습니다. 결측치는 고정 문자열 WT로 치환하며, test 통계·라벨 추정·프로필 라벨 매칭·get_dummies를 사용하지 않습니다.',
'- train에서 정규화된 변이 토큰 집합으로 프로필을 묶고, 개발 4,958행과 holdout 1,243행으로 분리했습니다. 개발 단계에서는 그룹 3-fold를 사용했습니다. 각 fold에서 특징 빈도, 사전, TF-IDF, 스케일과 클래스 가중치를 학습 행만으로 적합합니다.',
'- 외부 검증 라벨로 early stopping을 하지 않습니다. XGB는 180회 고정이며, 중복 라벨 덮어쓰기와 사후 클래스별 확률 배율은 제외했습니다. 캐시는 같은 학습행·특징·가중치·seed의 결과만 재사용합니다.',
'- 개발 점수는 17개 후보와 앙상블 비중을 고르는 데 사용했으므로 선택 편향이 있습니다. seed 평균 여부도 개발 데이터에서 결정합니다. frozen_selection.json 저장 이후 baseline과 선택 후보를 holdout에서 한 번씩 확인했습니다. 그 결과로 재튜닝하지 않았습니다.',
'- 확인용 baseline은 원본 설정에 해당하는 balanced, LR C=.1, XGB 40%/LR60%입니다. 표의 개발 baseline 비중은 개발 OOF에서 별도로 선택됩니다.',
'- 그룹 분리 데이터도 과거 팀 실험에 사용됐을 수 있습니다. 완전히 새로운 외부 검증 점수로 해석할 수 없습니다. 기존 5-fold·early stopping·중복 규칙 OOF와 직접 비교해서는 안 됩니다.',
'- 희소행렬을 사용하므로 원본 dense 입력과 XGBoost의 0/결측 분기 표현이 다릅니다. 모든 신규 후보에는 같은 표현을 사용했습니다.',
'- 최종 제출 후보는 전체 train으로 재학습했습니다. 전체 학습 모델의 실제 리더보드 점수는 제출 전까지 알 수 없습니다. holdout에서 악화됐다면 현재 최고 제출을 교체할 근거가 부족합니다.','',
'## 파일과 실행','',
'- `submission_selected_core.csv`: 선택 후보 1개. 중복 라벨 덮어쓰기 없음.',
'- `v11_*.ipynb` ~ `v18_*.ipynb`: 각 설정을 독립적으로 재학습할 수 있는 버전별 노트북. 개발 OOF만 평가하며 test/holdout 정답을 읽지 않습니다.',
'- `run_experiments.py`: 전체 실험 → 후보 고정 → 확인용 평가 → 전체 train 재학습 → test 예측. 원본 복사 노트북의 특징 함수를 읽으므로 해당 파일을 함께 보존해야 합니다.',
'- `development_results.csv`, `*_oof.npz`, `holdout_predictions.npz`, `holdout_classification.txt`: 점수 및 예측 근거.',
'- `split_indices.npz`, `frozen_selection.json`, `manifest.json`, `leakage_audit.json`, `run.log`: 분할·고정 설정·환경·데이터 해시·점검·실행 기록.',
'- 실행 환경: Python '+json.loads((p/'manifest.json').read_text())['python'].split()[0]+'. 패키지 버전은 manifest.json 참고.',
'', '```bash','python run_experiments.py','python audit_pipeline.py','python package_notebooks.py','python build_report.py','```','',
'참고: 사용자가 제공한 [데이콘 부정 제출 및 치팅 공지](https://dacon.io/more/notice/13)는 수기 정답 작성·공정성을 해치는 제출과 소스 검증에 관한 일반 공지입니다. 이 공지만으로 특정 대회의 모든 규정을 확인한 것은 아닙니다.']
(p/'RESULTS.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines[:12]))
