# 민정 v10 개선 실험 (Claude)

- [원본 보존 복사본](model_민정_v10_원본복사본.ipynb)
- [v0 기준선](model_민정_v10_claude_v0.ipynb) · [v2](model_민정_v10_claude_v2.ipynb) · [v3](model_민정_v10_claude_v3.ipynb) · [v4 (최종)](model_민정_v10_claude_v4.ipynb)
- 버전별 결과 요약: [results/](results/) (`claude_v2.json`, `claude_v3.json`, `claude_v4.json`)
- 실행 기록(설정·패키지 버전·데이터 md5): `run_manifest_claude_<버전>_norm.json`
- [Codex v19와 동일 holdout 비교](../codex/minjung_experiments/COMPARISON_CLAUDE_V4.md)

민정 v10 복사본 위에서 버전마다 실험 하나만 켜고(`VERSION_CFG`) 나머지 조건은 같게 두었습니다. 누수 점검으로 프로필 해시 번호표는 train으로만 만들고 test는 조회만 합니다(원본 v10은 train+test를 합쳐 factorize했습니다).

## 버전별 결과

5-fold OOF Macro F1 (행 단위 분할). `기본`은 모델만, `최종`은 중복 규칙까지 넣은 제출 파이프라인 점수입니다.

| 버전 | 변경점 | 기본 | 최종 (`_dup`) |
|---|---|---:|---:|
| v0 | 변경 없음 (같은 평가 틀로 v10 재실행). 결과 JSON 없음 | – | – |
| v2 | 반복 수를 학습 fold 내부 15%로 정하고, test는 train 100%로 재학습 | 0.47085 | 0.53677 |
| v3 | 형제 암종 쌍(KIRC↔KIPAN, LGG↔GBMLGG) 전용 확률 배율 | 0.47112 | 0.53638 |
| **v4** | XGB 학습률 0.05 + seed 2개(42, 7), LightGBM 추가, LR C 선택 | **0.47729** | **0.54180** |

- v3의 쌍 배율은 중첩 검증 이득이 기준 미달이라 실제로는 적용되지 않았습니다(`pair_applied: false`).
- v4 앙상블 비중: XGB 0.1 / LGB 0.5 / LR 0.4. 클래스별 배율 보정은 중첩 검증에서 손해(0.5005 → 0.4904)라 적용하지 않았습니다.
- v4 노트북 첫 셀에는 "seed 3개"라고 적혀 있지만 실제 설정은 seed 2개입니다.

## 제출 후보 파일

- `submission_claude_v4_norm_core.csv`: 모델 예측만 사용합니다.
- `submission_claude_v4_norm_dup.csv`: 중복 규칙을 적용했습니다. core와 206행이 다르고, 루트 `submission/claude_v4_dup.csv`와 내용이 같습니다(BOM만 다름).
- `submission_codex_v19_plus_dup.csv`: Codex v19 선택 모델 예측에 같은 중복 규칙을 덧씌운 파일입니다. 원본과 202행이 다르고, 대부분 KIRC↔KIPAN, LGG↔GBMLGG 교체입니다.

## 중복 규칙에 대한 주의

개별 코호트(KIRC)와 통합 코호트(KIPAN) 사이의 중복 등록과 일치하는 동일 변이 프로필이 관찰됩니다. 프로필만으로 개별 환자의 동일성을 확정한 것은 아닙니다. 중복 규칙은 "같은 프로필을 가진 다른 train 행의 라벨 → 이 행의 라벨" 표를 train에서만 추정합니다(`dup_table_claude_v4_norm.csv`, 표본 20 이상·확률 0.9 이상만 사용). test는 표 조회에만 씁니다.

OOF +0.065의 대부분이 이 규칙에서 나옵니다. 하지만 이는 동일 프로필의 라벨 구조에 의존하는 후처리 효과이며, 새 환자에 대한 일반화 성능과 구분해야 합니다. Codex 실험은 이 규칙을 쓰지 않았으므로 `_dup` 점수를 Codex 점수와 직접 비교하면 안 됩니다. 규칙 없이 같은 holdout에서 비교하면 v4 0.50012, Codex v19 0.50098로 우열을 가리기 어렵습니다.

## 실행

노트북은 `DATA_DIR = "../../../data"` 기준으로 이 폴더 안에서 실행합니다. v4 CV는 약 21분 걸렸습니다(macOS arm64, xgboost 3.4.1). `.npy`·`.csv` 산출물은 `.gitignore` 대상이라 실행하면 로컬에 다시 생성됩니다.

## Git에서 다시 실행할 때

Python과 주요 패키지 버전은 버전별 `run_manifest_claude_*_norm.json`을 참고하세요. v4는 여기에 LightGBM이 추가로 필요합니다. 이번 비교에 사용한 환경의 LightGBM 버전은 4.7.0입니다.

공개용 노트북에서는 데이터 미리보기 출력만 제거했습니다. 코드와 집계된 성능 출력은 유지했습니다. 원본 복사본은 실행 시 모든 설정을 확인하는 기준으로 보관합니다.

Codex 비교를 재현하려면 먼저 `../codex/minjung_experiments/run_experiments.py`로 로컬 분할·예측 캐시를 생성한 다음 `compare_claude_v4.py`를 실행해야 합니다. 기존 실행 시점의 파일 해시는 당시 기록이며, 공개용 출력 정리 후 파일의 바이트 해시와는 다를 수 있습니다.
