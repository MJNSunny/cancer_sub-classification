# 버전별 제출 CSV 내보내기 기록

<!-- CURRENT_STATUS_20261112 -->
## 현재 상태 (2026-11-12 기준)

아래 표가 최신 제출 상태입니다. 이 표 아래의 날짜별 기록은 당시 상태로 보존하며, 그 안의 “Public 미확인/오늘 제출할 파일” 표현은 작성 시점 기준입니다.

| 버전 | 제출 CSV | 상태 | Public |
| --- | --- | --- | ---: |
| v1 | 미확인 (아래 주석) | 실제 제출 확인, 파일 대응 미확인 | 0.2765425197 |
| v3 | `혜진_submission_v3.csv` | 실제 제출 확인 | 0.2998780222 |
| v4 | `혜진_submission_v4.csv` | 실제 제출 확인 | 0.3169555443 |
| v10 | `혜진_submission_v10_clean_experimental.csv` | 실제 제출 확인 | 0.3493803489 |
| v19 | `혜진_submission_v19_experimental.csv` | 실제 제출 확인 | 0.3664759128 |
| v25 | `혜진_submission_v25_legacy_stop_retrained.csv` | 실제 제출 확인 (2026-11-11 보고) | 0.390417094 |
| **v29** | `혜진_submission_v29_pruned_experimental.csv` | 실제 제출 확인 (2026-11-12 보고)·**현재 확인된 Public 최고** | **0.3917888655** |

- Public은 모두 혜진님이 알려준 실제 제출 결과이며 대회 사이트를 직접 조회한 값은 아닙니다.
- **같은 내용의 CSV:** v24 = v25 (SHA-256 `e1302a79…0e1a`), v30 = v31 (SHA-256 `cfbd7073…57af`). 2026-11-12에 다시 확인했습니다. v24는 따로 제출한 기록이 없지만 답안은 v25와 같습니다.
- **v1 파일 대응은 추가 확인이 필요합니다.** v1 Public 점수는 확인됐지만, 원래 v1 피클·CSV는 구분해 복원하지 못했습니다(아래 “별도 CSV를 만들지 않은 기록”). 따라서 현재 `혜진_submission.csv`가 실제 제출 파일이라는 원본 근거가 없습니다. 이 파일은 Git에서 2026-11-06 커밋 `eb31696`(“1차”)에 추가된 뒤 바뀌지 않았지만, 그 사실이 제출 파일과 같다는 증명은 아닙니다.
- **Public 미확인:** v2, v5, v6, v7, v8 기준/실험용, v9, v10 기준, v12 두 종, v13, v16, v17, v18 후속, v23 후속, v24, v26~v28, v30~v31.
- v6는 과거 기본 모델 CSV로 보존합니다. 확인된 Public 최고 모델(v29)과 구분합니다.
- 버전 간 Public 차이는 여러 변경을 함께 담은 결과이며 특정 변경 하나의 효과로 해석하지 않습니다.

## 2026-11-10 일괄 생성 기록

2026-11-10 사용자 요청으로 저장 모델 10개의 누락 CSV를 생성했습니다. **test/sample은 최종 추론·ID 정렬에만 사용했습니다.** 모델 재학습·변수 선별·파라미터 조정·검증 점수 재계산은 하지 않았습니다. 대회에 자동 제출하지 않았고 새 Public 점수는 없습니다.

(2026-11-10 당시 안내) 오늘 v19를 제출하려면 **`submission/혜진_submission_v19_experimental.csv`**를 사용하세요. v18 후속 실험은 더 높은 원본 CV 평균에도 희귀 변이 조건 성능 저하가 있어 구분합니다. CSV를 만들었다는 사실은 모델 채택이나 대회 제출을 뜻하지 않습니다.

| 버전 | 새 제출 CSV | 상태 |
| --- | --- | --- |
| v2 | [혜진_submission_v2.csv](../../submission/혜진_submission_v2.csv) | 미채택 실험 |
| v7 | [혜진_submission_v7.csv](../../submission/혜진_submission_v7.csv) | 기준 모델 유지 |
| v8 | [혜진_submission_v8_reference.csv](../../submission/혜진_submission_v8_reference.csv) | 기준 모델; 기존 v8_experimental과 구분 |
| v9 | [혜진_submission_v9.csv](../../submission/혜진_submission_v9.csv) | 기준 모델 유지 |
| v10 | [혜진_submission_v10_reference.csv](../../submission/혜진_submission_v10_reference.csv) | 기준 모델; 기존 v10_clean_experimental과 구분 |
| v13 | [혜진_submission_v13_experimental.csv](../../submission/혜진_submission_v13_experimental.csv) | 미채택 실험 |
| v16 | [혜진_submission_v16_experimental.csv](../../submission/혜진_submission_v16_experimental.csv) | 전처리 대조용 실험 |
| v17 | [혜진_submission_v17_experimental.csv](../../submission/혜진_submission_v17_experimental.csv) | v17 실험 모델 |
| v18 | [혜진_submission_v18_followup_experimental.csv](../../submission/혜진_submission_v18_followup_experimental.csv) | 후속 실험; 희귀 변이 조건 성능 하락 |
| v19 | [혜진_submission_v19_experimental.csv](../../submission/혜진_submission_v19_experimental.csv) | 현재 우선 검토 후보; Public 미확인 |

기존 submission CSV는 덮어쓰지 않았습니다. v3·v4·v5·v6·v8 실험·v10 clean 실험·v12 실험 CSV는 그대로 유지했습니다. 공통 이름 `혜진_submission.csv`도 변경하지 않았습니다. v7·v8 기준·v9·v10 기준은 유지한 구성 때문에 기존 기준 제출과 같은 답이 나올 수 있으며 새 알고리즘으로 향상됐다는 뜻이 아닙니다.

## 별도 CSV를 만들지 않은 기록

- v1: 구분 가능한 원래 저장 피클/CSV가 현재 버전 아티팩트에 없어 충실하게 복원하지 않았습니다. v3 모델을 v1로 이름만 바꾸지 않았습니다.
- v11·v14·v15: 미채택 탐색·진단 버전이며 독립적인 최종 모델 피클이 없습니다. 유지한 모델의 답안을 새 버전의 별도 모델처럼 복제하거나 임의 재학습하지 않았습니다.
- 전처리기 피클은 분류 모델이 아니므로 별도 제출 답안을 생성하지 않았습니다.

## 검증과 재현

모든 새 CSV는 2,546행, `ID,SUBCLASS` 두 열, sample_submission과 같은 ID·행 순서이며 누락/중복 ID가 없습니다. 예측 확률의 유한성·비음수·행 합 1과 일부 배치 추론의 일치를 확인했습니다. 클래스 순서는 각 저장 모델 또는 해당 모델의 학습 OOF 클래스 메타데이터를 따릅니다. sample의 임시 정답으로 클래스 순서를 추측하지 않았습니다. 저장 모델 해시는 추론 전후 동일합니다.

버전별 모델/CSV/test/sample SHA256과 검증 증거는 Git 제외 `artifacts/submission_exports/*.csv.json`에 저장했습니다. v13은 기존 CatBoost Python 환경에서 추론했습니다. v13·v16~v19 노트북 끝에 저장 모델의 선택 실행 추론 셀을 추가했습니다. 이 셀은 학습 셀을 다시 실행하지 않고도 실행할 수 있으며 저장 모델이 필요합니다. 연구 단계의 open guard는 유지하고 새 추론 프로세스에서만 test/sample을 읽습니다. 추가 셀은 선택 실행 셀이므로 실행 횟수를 이전 연구 실행 결과처럼 꾸며 넣지 않았습니다.

이전 문서와 verification의 `test_opened=False`는 **당시 학습·선별·검증 실행**의 기록입니다. 이후 사용자가 승인한 이번 최종 추론과 구분하며 과거 실험 기록을 바꾸지 않았습니다. 이번 추론에 test를 썼다는 사실을 은폐하지 않습니다.

## v23 고정 후속 실험 추가

[혜진_submission_v23_followup_experimental.csv](../../submission/혜진_submission_v23_followup_experimental.csv)를 추가했습니다. 원래 1차 기준 미달과 별도 고정 후속 진단 통과를 구분합니다. 현재 새 실험 제출 후보이며 실제 대회 점수는 아직 없습니다. 기존 v19의 사용자 확인 Public은 0.3664759128입니다.


<!-- V26_EXPORT -->
## v26 실험용 제출

`submission/혜진_submission_v26_minjung_features_experimental.csv`: 고정한 combo ON 전체 train 모델에서 생성. 개선 기준 통과 `False`이며 Public은 미확인입니다. 모델·원본 CSV를 이름만 바꿔 복사하지 않았고 이전 버전은 보존했습니다. 정확한 예측 파일 검증은 `artifacts/v26/submission_verification.json`입니다.


<!-- V27_EXPORT -->
## v27 실험용 제출

`submission/혜진_submission_v27_geneformer_proxy_experimental.csv`: 고정 both 전체 train 모델로 생성. 단순 개선 기준 통과 `False`, Public 미확인. 저장 후 재로딩·표기 동치·2,546행·ID/순서·배치 일치 확인. provenance와 확률·체크섬 기록은 artifacts/v27에 있으며 기존 버전은 보존했습니다.


<!-- V28_EXPORT -->
## v28 고정 혼합 실험 제출

`submission/혜진_submission_v28_fixed_blend_experimental.csv`: v25/v26/v27=80/10/10. 5-fold 확인 기준 통과 `False`, Public 미확인. v25 실제 Public 0.390417094와 로컬 검증을 구분합니다. 형제 라벨 반전 없음. 최종 확률·ID·순서·배치·체크섬 기록은 artifacts/v28/submission_verification.json입니다.


<!-- V29_EXPORT -->
## v29 축소 모델 실험 제출

`submission/혜진_submission_v29_pruned_experimental.csv`: 선택된 9개 모델만 전체 train에서 새로 학습해 생성. 성능 유지 확인 기준 `True`, Public 미확인. 기존 v25 0.390417094와 구분합니다. 검증·비용·원래 비중·확률/ID/배치 기록은 artifacts/v29에 보존했습니다.


<!-- V30_EXPORT -->
## v30 최종 공유4개 D 실험

`submission/혜진_submission_v30_compact_experimental.csv`: rich_lr|rich_lgb|rare_cnb|aug_ova, 4개. A/B/C/D 개발 비교로 선택했으므로 독립 최종 평가 아님. 그룹5-fold 평균 F1 0.489216, v29 대비 +0.001564, 개선 기준 False. A/B/C 일부 결과와 과거4개 recipe를 참고한 적응적 후속이며 외부 독립 확인이 아닙니다. Public 미확인, 기존 제출을 덮어쓰지 않습니다. 최종 고정 후 추론만 test에 적용했습니다.


<!-- V31_EXPORT -->
## v31 반복nested 실험

`submission/혜진_submission_v31_compact_experimental.csv`: 고정4개, `baseline`. nested선택절차 평균 F1 0.492889, 같은fold v30기준 0.497543, 차이 -0.004654, 개선기준 False. 마지막구성은별도개발inner선택으로정했으며 이nested점수를고정구성독립성능으로붙이지않습니다. 최종설정변경 False, v30 CSV와hash일치 True. Public미확인, 기존모델/CSV보존.


<!-- PUBLIC_V29_20261112 -->
## 실제 제출 결과 — v29 (2026-11-12 사용자 보고)

- 제출 파일: `submission/혜진_submission_v29_pruned_experimental.csv`
- Public Macro F1: **0.3917888655**
- 이전 v25 Public **0.390417094** 대비 **+0.0013717715** (약 +0.13718 퍼센트포인트).
- 현재 사용자 보고로 확인된 **혜진 버전의 Public 최고 기록**을 갱신했습니다. 팀 전체 최고 기록이라는 뜻은 아닙니다.
- v29는 v25의 14개 분류기를 9개로 축소하고 기존 상대 가중치를 정규화한 뒤 전체 train에서 재학습한 후보입니다.
- 같은 그룹 5-fold의 평균 F1 차이 +0.001233과 이번 Public 차이는 별개의 결과입니다. 이번 제출 점수는 관측된 소폭 개선이며 일반화 성능의 통계적 우월성을 입증하지 않습니다.
- 점수 출처는 사용자 보고이며 대회 사이트 직접 조회 결과는 아닙니다. 기존 학습 시점 verification JSON의 Public 미확인 기록은 당시 상태로 보존합니다.
