# v26 — 민정 v6의 좋은 부분을 분리 차용한 그룹 검증

## 출처와 차용 범위

사용자 제공 `/Users/mac/Downloads/model_민정_v6.ipynb`의 combo_features, PATHWAYS, 유전자/핫스팟/아미노산 빈도 선별 및 XGB+LR 구성을 참고했습니다. 사용자 전달 OOF 0.5416·Public 0.47874911은 팀원 결과로만 기록하며 본 코드에서 재현했다고 주장하지 않습니다. 팀원 노트북은 학습·데이터 접근을 실행하지 않고 코드만 읽었습니다.

차용한 변수: 유전자 변이 여부, 변이 유전자·이벤트 수, 종류별 개수·비율, gene|refAA+position 핫스팟, gene|trunc, 삽입·삭제의 gene|indel 및 gene|position_indel, 아미노산 치환쌍 비율, 경로 집계, 생물학적 지식 기반 동반 변이 조합입니다. 예로 APC 절단+TP53/KRAS, VHL+PBRM1, IDH1+TP53+ATRX, BRAF V600+변이량 등이 있습니다. 이들은 진단 규칙이나 인과관계가 아니라 고정된 파생변수입니다. 변이 유전자 수는 측정 염기 수로 나눈 TMB가 아닌 burden proxy입니다.

삽입·삭제 문자열만으로 in-frame인지 확정할 수 없어 팀원의 inframe 변수를 중립적인 indel로 명명했습니다. 대문자 FS를 무조건 frameshift로 읽거나 X를 모든 위치에서 치환하는 방식은 사용하지 않습니다. X/* 정규화는 v25 가정을 이어받으며 실제 생성 규약은 미확인입니다. 기존 v25 파서에서 3글자 아미노산을 1글자로 바꾼 뒤에도 legacy-X 정규화를 다시 적용해 p.Arg123X와 R123*가 같도록 보완했습니다.

## 그대로 가져오지 않은 부분

- 일반 StratifiedKFold 대신 동일 raw/정규화 프로필을 묶은 그룹 분할.
- 전체 train에서 빈도 선별 후 CV를 하지 않고 매 학습 fold 안에서 DF/어휘 선별.
- outer 검증으로 early stopping하지 않음. outer 학습 부분을 다시 그룹 5-fold로 나눠 한 inner fold에서 회수를 정하고, outer 학습 전체로 변수와 모델을 다시 fit.
- XGB+LR 비중 0.5/0.5 고정. 보고하는 OOF에서 비중 탐색하지 않음.
- 형제 라벨 반전 및 COAD 22% 가정·확률 보정 제외.
- 주 후보는 combo ON으로 결과 전에 지정. combo OFF는 효과 분리용 비교이며 결과를 보고 주 후보를 교체하지 않음.

## 학습 설정과 검증

기존 개발 환자 4,960명, seed23033 그룹 3-fold를 사용했습니다. 과거 홀드아웃은 평가하지 않았습니다. 유전자·핫스팟 DF>=5, 아미노산 치환 이벤트 count>=20, LR C=0.1 balanced+MaxAbsScaler. XGB depth5·lr0.08·subsample0.8·colsample0.3, inner 최대1200/early stop50, n_jobs2. 각 fold에서 inner training만으로 inner 피처를 선별하고 종료 회수를 정한 뒤 outer train 전체로 새 피처/모델을 fit했습니다. 최종 전체 학습 회수는 세 outer training의 inner 종료 회수 중앙값입니다.

v25와는 train SHA256과 학습·검증 인덱스가 정확히 일치하는 OOF만 비교했습니다. 캐시가 없을 경우 노트북에는 같은 train SHA와 분할 fingerprint로 제한한 기존 v25 문서 점수가 포함되어 있어 프로젝트 Python 파일이나 이전 피클 없이 새 모델 연구를 재현할 수 있습니다. 문서 기준값 사용은 v25 재실행으로 표시하지 않습니다.

## 결과

|   fold | candidate   |   features |   rounds |   macro_f1 |   accuracy |   v25_macro_f1 |   delta_vs_v25 | notation_probe_passed   |
|-------:|:------------|-----------:|---------:|-----------:|-----------:|---------------:|---------------:|:------------------------|
|      0 | combos_off  |       4966 |      205 |   0.470413 |   0.474002 |       0.481303 |     -0.0108902 | True                    |
|      0 | combos_on   |       4989 |      170 |   0.46981  |   0.477025 |       0.481303 |     -0.0114929 | True                    |
|      1 | combos_off  |       5060 |      179 |   0.474639 |   0.490018 |       0.497347 |     -0.0227079 | True                    |
|      1 | combos_on   |       5083 |      156 |   0.468466 |   0.488203 |       0.497347 |     -0.0288811 | True                    |
|      2 | combos_off  |       4980 |      162 |   0.478306 |   0.471264 |       0.500601 |     -0.0222947 | True                    |
|      2 | combos_on   |       5003 |      165 |   0.467913 |   0.468845 |       0.500601 |     -0.0326875 | True                    |

평균:

| candidate   |   macro_f1 |   accuracy |   delta_vs_v25 |
|:------------|-----------:|-----------:|---------------:|
| combos_off  |   0.474453 |   0.478428 |     -0.0186309 |
| combos_on   |   0.46873  |   0.478024 |     -0.0243538 |

동반 변이 조합 추가에 따른 평균 F1 차이: **-0.005723**. 이는 추가한 조합 전체의 영향이며 개별 조합이나 생물학적 인과 효과를 입증하지 않습니다.

v25 대비 사전 단순 개선 기준(평균 +0.003, 각 fold -0.001 이상) 통과: **False**. 이 기준 통과 자체도 외부 검증이나 Public 향상을 의미하지 않습니다. v25와 같은 개발 환자를 반복 관찰했으므로 탐색 편향이 있습니다. 본 실험 결과를 v25 대신 자동 채택하지 않습니다. 낮은 결과가 나왔다면 전체 파이프라인에서 충분한 개선이 없었다는 뜻이며, 팀원 Public 상승을 특정 후처리 하나로 단정하지 않습니다.

## 최종 저장

개선 여부와 별개로 사용자가 요청한 버전의 재현을 위해 사전 지정한 combo ON 모델을 **실험용**으로 전체 train 6,201명에 학습했습니다. 선택 변수 수 6173, XGB 회수 165. 기존 모델을 이름만 바꿔 저장하지 않았습니다. 저장·재로딩, 3-fold 각 16명 X/* 예측 동치, 최종 추론의 배치 순서 독립성을 확인했습니다. X/* 호환성은 가정한 표준 토큰 형식에 한정됩니다.

- `cencer_v26.ipynb`: 모든 전처리·선별·inner/outer 학습·검증·저장·추론 코드 포함.
- `artifacts/v26/cancer_model_v26_minjung_features_experimental.pkl`: 전체 모델, predict_frame 반환 열 순서는 classes_.
- `artifacts/v26/selected_variables.csv`: 전체 최종 변수 목록.
- `submission/혜진_submission_v26_minjung_features_experimental.csv`: 고정 실험 모델의 최종 추론 결과.
- `requirements-v26.txt`: 실행 환경.

모델 피클/확률/캐시 등 artifacts는 Git 제외입니다. test/sample은 연구 단계 audit hook으로 차단하고 마지막 별도 프로세스의 고정 모델 추론에서만 읽었습니다. v25에서 이어받은 표기 가정은 과거 test 관찰에 영향을 받은 설계임을 명시합니다. 원본 데이터와 이전 모델·CSV는 보존합니다. v26 Public은 미확인입니다.
