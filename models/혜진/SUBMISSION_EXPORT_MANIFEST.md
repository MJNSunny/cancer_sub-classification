# 버전별 제출 CSV 내보내기 기록

2026-11-10 사용자 요청으로 저장 모델 10개의 누락 CSV를 생성했습니다. **test/sample은 최종 추론·ID 정렬에만 사용했습니다.** 모델 재학습·변수 선별·파라미터 조정·검증 점수 재계산은 하지 않았습니다. 대회에 자동 제출하지 않았고 새 Public 점수는 없습니다.

오늘 v19를 제출하려면 **`submission/혜진_submission_v19_experimental.csv`**를 사용하세요. v18 후속 실험은 더 높은 원본 CV 평균에도 희귀 변이 조건 성능 저하가 있어 구분합니다. CSV를 만들었다는 사실은 모델 채택이나 대회 제출을 뜻하지 않습니다.

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
