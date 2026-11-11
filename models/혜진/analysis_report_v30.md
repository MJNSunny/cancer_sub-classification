# v30 최종 활성 후보 — 공유 전처리1개 + 분류기4개

## 결과와 한계

| 이번 동일 그룹5-fold 비교 | 분류기 수 | 평균 Macro F1 | 평균 accuracy |
|---|---:|---:|---:|
| v29 기존 구성 | 9 | 0.487652 | 48.6694% |
| A: 새 단순 표현·nested 소형 조합 선택 | 2~4 | 0.433061 | 43.7298% |
| B: 새 희귀 표현·고정3개 | 3 | 0.440548 | 45.0403% |
| C: B + 보조 CNB 고정15% | 4 | 0.446553 | 45.3427% |
| **D: 검증된 문헌 전처리 차용·공유4개** | **4** | **0.489216** | **49.0323%** |

D−v29 평균 차이는 **+0.001564**, pooled F1 **0.492652**입니다. 평균+0.003/최악fold-0.003의 기존 공학적 개선 기준 통과 **False**. 작은 평균 상승을 확실한 성능 개선이라고 주장하지 않습니다. 고정 OOF의 조건부 그룹 bootstrap95% pooled 차이 구간은 `[-0.004164516789497824, 0.01039518248903616]`입니다. 이는 학습·선택·적응적 설계 불확실성을 포함하지 않고 fold 평균 차이의 CI도 아닙니다.

A/B/C가 기대보다 낮아 기존 전처리의 좋은 부분까지 버리지 않고 차용했습니다. D의4개 recipe/기존 비중은 과거 v29의4개 후보에서도 연구했던 이력이 있습니다. 그 과거 후보는 다른 split에서14개 baseline 대비 기준을 통과하지 못했습니다. 이번 결과가 과거 실패를 취소하거나 독립 재발견을 뜻하지 않습니다. 새로운 클래스에서 하나의 전처리를 공유하고4개를 **새로 fit**했으며, v25/v29 학습 피클이나14개 전체 모델을 감싸지 않습니다. D와 앞선 후보를 같은 개발 결과로 비교해 선택했으므로 최고 관측값에는 선택 편향이 남습니다.

|   fold | selected                             |       f1 |   accuracy |   features |   fit_predict_seconds |   v29_f1 |   delta_vs_v29 |
|-------:|:-------------------------------------|---------:|-----------:|-----------:|----------------------:|---------:|---------------:|
|      0 | rich_lr\|rich_lgb\|rare_cnb\|aug_ova | 0.527756 |   0.512097 |       8192 |               57.3598 | 0.522736 |     0.00502011 |
|      1 | rich_lr\|rich_lgb\|rare_cnb\|aug_ova | 0.461104 |   0.477823 |       8192 |               58.4278 | 0.464869 |    -0.00376456 |
|      2 | rich_lr\|rich_lgb\|rare_cnb\|aug_ova | 0.468022 |   0.46875  |       8192 |               59.8749 | 0.469139 |    -0.00111708 |
|      3 | rich_lr\|rich_lgb\|rare_cnb\|aug_ova | 0.507956 |   0.514113 |       8192 |               58.7323 | 0.496357 |     0.011599   |
|      4 | rich_lr\|rich_lgb\|rare_cnb\|aug_ova | 0.481243 |   0.478831 |       8192 |               54.9731 | 0.485161 |    -0.00391807 |

Public는 미확인입니다. v25 실제 **0.390417094**를 넘었다거나 리더보드0.50을 달성했다고 말하지 않습니다. 실험용 후보로 저장하며 기존 파일/모델은 보존합니다. 같은 과거 개발4960명 재평가이고 보류1241명은 평가하지 않았으며, 최종 배포 fit에서만 전체6201명을 합칩니다.

## 최종 구조

`원본 gene 문자열 → 고정 X/* canonicalization → 문헌 기반 보수적 파서 → 공유 rare_backoff 전처리/8192개 선택 변수 → LR·LightGBM(multiclass)·ComplementNB·LightGBM(OVA) → 고정 가중 확률 평균 → SUBCLASS`

| 분류기 | 설정 | 비중 |
|---|---|---:|
| rich_lr | LR C1/balanced/max_iter1600 | 22.689076% |
| rich_lgb | LightGBM300trees/leaves15/depth5/lr.04/lambda10/min_child20/colsample.85/balanced/seed17017 | 22.689076% |
| rare_cnb | ComplementNB alpha1/normFalse/temperature2 | 12.605042% |
| aug_ova | LightGBM OVA500trees/leaves15/depth5/lr.04/lambda10/min_child20/colsample.85/is_unbalance/seed23023 | 42.016807% |

비중은 v25의 해당4개 leaf 비중 .108/.108/.06/.2를 합 .476으로 나눈 고정값입니다. 이번 결과로 비중을 탐색하지 않았습니다. 최종4개 객체지만 OVA는 내부적으로26개 이진 목표, LightGBM에는 많은 트리가 존재합니다. 학습기 종류는3종(LR/LGB/CNB), 전처리는1개이며 NN/Geneformer/XGBoost는 최종 D 추론에 포함하지 않습니다. 전체 notebook의 A/B 연구 재현에는 관련 패키지가 필요합니다.

이 구성은 기존 분류기의 일부를 불러와 추론 때만 숨긴 축소가 아닙니다. 공유 표현을 원래 train에서 새로 적합하고4개 estimator만 train6201명에서 새로 학습했습니다. OVA를 제외한3개는 원래 행만, OVA는 아래 train-only 증강도 사용합니다. 모델 수4개 상한을 지켰으며5개는 추가하지 않았습니다.

## 차용한 전처리와 새 표현의 차이

v16의 `parse_token16/parse_rows16`, `Preprocess16('rare_backoff',min_df=3,k=8192)` 정의를 notebook에 직접 넣었습니다. 외부 프로젝트 py를 import하지 않습니다. 과거의 **unfitted 정의/원리** 차용이며 기존 fitted state 차용은 아닙니다. 문헌 gene panel branch는 사용하지 않고 빈 panel dict로 둡니다. 외부 환자·사전학습·외부 gene 목록을 새로 불러오지 않습니다.

- p./3-letter AA/불확실성 괄호, 동일 길이 block, stop gained/lost/retained, fs 종료거리, del/ins/delins, 불완전/미해석 표기를 구분합니다. 같은 길이 block을 성분 속성으로 풀어도 원래 event는1개입니다. 복합표기를 무조건 지우거나 DNA 사건 수로 재해석하지 않습니다.
- `R1450X/p.R1450X`형 단일-AA 치환은 원래 v25의 dataset legacy-stop 가정을 유지해 *로 통일합니다. 모든 X의 보편적 HGVS 의미가 stop이라는 뜻은 아닙니다.
- gene 유무/log event count, effect별 log count, 원래 format, AA gene/global count, protein bin64/256, fs stop distance, rare/supported gene count, 관측/원문/중복/불확실/미해석/유형 분율/rare/unseen 요약을 공유합니다.
- 학습 DF는 gene×canonical event로 계산합니다. training rarity/unseen은 자기 자신1을 제외, validation/inference는 학습 DF만 사용합니다.
- 각 학습 fold의 원래 행에서 어휘·DF≥3(일부 numeric 예외)·chi2상위8192·MaxAbs를 fit하고 exact residual만 MaxAbs 후 df/(df+5)로 완화합니다. 이 값은 병원성/driver/기능 점수가 아닙니다.
- OVA에만 기존 corrupt23를 차용: 해당 train 내 DF2 이하 missense/synonymous/synonymous_block pool, gene mask0.1, Poisson20 nuisance. 원본1/증강0.5, 전처리 fit은 원래 train만, 증강에는 transform만 수행. 이 증강은 label-preserving 모델링 가정이지 실제 정상/암 변이 구분이 아닙니다.
- raw_tokens/duplicate_tokens를 별도 기록하므로 중복 토큰 수까지 무조건 불변이라고 주장하지 않습니다. X/* canonicalization과 배치 독립성은 저장 모델에서 실제 검사했습니다.

공유 변수군:

| family           |   features |
|:-----------------|-----------:|
| aa_global        |        181 |
| aa_meta          |        690 |
| effect           |        625 |
| format           |       1164 |
| gene             |       1331 |
| gene_event_count |        826 |
| num              |         13 |
| protein_bin256   |        904 |
| protein_bin64    |        463 |
| rare_gene        |       1711 |
| supported_gene   |         99 |
| variant          |        185 |

정확한 변수8192개·학습지원도·원래 unscaled chi2·exact DF·감쇠비중은 `d_selected_variables.csv`와 `selected_variables_v30.md`에 기록했습니다. exact DF 칸의 비-event NaN은 해당 없음이며 환자 데이터의 결측 처리와 다릅니다.

## D의 오류 진단

|              |   precision |   recall |   f1-score |     support |
|:-------------|------------:|---------:|-----------:|------------:|
| ACC          |    1        | 0.844828 |   0.915888 |   58        |
| BLCA         |    0.553571 | 0.369048 |   0.442857 |   84        |
| BRCA         |    0.64375  | 0.491256 |   0.557259 |  629        |
| CESC         |    0.375    | 0.387097 |   0.380952 |  124        |
| COAD         |    0.796296 | 0.72067  |   0.756598 |  179        |
| DLBC         |    0.8      | 0.258065 |   0.390244 |   31        |
| GBMLGG       |    0.539735 | 0.441734 |   0.485842 |  369        |
| HNSC         |    0.348315 | 0.346369 |   0.347339 |  179        |
| KIPAN        |    0.442197 | 0.371359 |   0.403694 |  412        |
| KIRC         |    0.465753 | 0.254682 |   0.329298 |  267        |
| LAML         |    0.62037  | 0.527559 |   0.570213 |  127        |
| LGG          |    0.471503 | 0.497268 |   0.484043 |  183        |
| LIHC         |    0.384615 | 0.354331 |   0.368852 |  127        |
| LUAD         |    0.542373 | 0.432432 |   0.481203 |  148        |
| LUSC         |    0.577778 | 0.545455 |   0.561151 |  143        |
| OV           |    0.33033  | 0.541872 |   0.410448 |  203        |
| PAAD         |    0.438202 | 0.40625  |   0.421622 |   96        |
| PCPG         |    0.22807  | 0.440678 |   0.300578 |  118        |
| PRAD         |    0.279255 | 0.492958 |   0.356537 |  213        |
| SARC         |    0.177778 | 0.251572 |   0.208333 |  159        |
| SKCM         |    0.947644 | 0.819005 |   0.878641 |  221        |
| STES         |    0.530547 | 0.544554 |   0.537459 |  303        |
| TGCT         |    0.469388 | 0.69     |   0.558704 |  100        |
| THCA         |    0.840796 | 0.65     |   0.733189 |  260        |
| THYM         |    0.184971 | 0.470588 |   0.26556  |   68        |
| UCEC         |    0.664557 | 0.660377 |   0.662461 |  159        |
| accuracy     |    0.490323 | 0.490323 |   0.490323 |    0.490323 |
| macro avg    |    0.525107 | 0.492693 |   0.492652 | 4960        |
| weighted avg |    0.533443 | 0.490323 |   0.50118  | 4960        |

동일 profile의 라벨 충돌·공유 분자 특징·미관측 임상 정보는 가능한 한계지만, 이 표로 정답 오류/진짜 환자 중복을 단정하거나 형제 라벨을 뒤집지 않습니다. 임상적 안전성/외부 코호트 일반화/개별 환자 진단 성능을 입증한 모델이 아닙니다.

## 재현·저장·최종 추론

- 활성 피클 `artifacts/v30/cancer_model_v30_compact_experimental.pkl`, **48,974,128 bytes**, model SHA `176769082696bd4c95b1f3645c15bffb30dfc01842cd57ab84f7383defd8770d`.
- full train 선택4개 fit 71.66초, 분류기별 `{'rich_lr': 2.1224497919902205, 'rich_lgb': 16.501886124984594, 'rare_cnb': 0.009662666998337954, 'aug_ova': 41.19990233401768}`. 탐색/로딩/파싱 제외이며 다른 CPU 부하의 과거 시간과 직접 배수 비교 안 함.
- A/B/C/D source·선별·학습·진짜 OOF·실패 및 cache 출처 모두 notebook/artifacts에 보존. D 완료 CV cache는 train/source/protocol/parsed-cache SHA 및 정확한 fold 인덱스를 확인해 재사용하며, 전체 train 모델로 CV하지 않습니다. cache가 없으면 notebook에서 새로 학습합니다.
- 최종 CSV `submission/혜진_submission_v30_compact_experimental.csv`,2546행. 선택 고정 뒤 **test에 추론만** 적용했습니다. test/sample은 연구 open 차단, 추론 child는 train open 차단. fit/선별/비중/암종 비율 정렬에 test 미사용.
- 독립 child 재로딩, ID/순서/클래스/확률합, batch invariance, X/* 동등 예측, model/CSV hash 확인. 기존 원본·모델·제출 보존, commit/push하지 않음.
- 최종 후보는 적은 모델로 대등한 평균 성능을 보인 실험용이며, 사전 개선 기준 미통과라면 기존 모델 교체나 확실한 성능 향상을 주장하지 않습니다.

---

## A/B/C 상세 실패·문헌 연결 기록

## C: 선택적 네 번째 CNB를 넣을 가치가 있는가

B3의 확률에0.85, RareFeatures 기반 ComplementNB(alpha1,normFalse,temperature2)에0.15를 고정했습니다. 이 네 번째 후보는 raw-TFIDF CNB와 다른 공유 희귀 표현입니다. 비중 grid 탐색은 하지 않았습니다. C의 CNB 전처리는 각 fold 학습 행에서 다시 fit하고, 전체train B 전처리를 CV에 사용하지 않습니다. B 대비 평균+0.003 이상/최악fold-0.003 이상일 때만 추가하는 개발 판단이며, 같은 결과로 선택한 편향이 남습니다. protocol은 C 점수 전에 저장했고 A/B의 일부 약한 결과를 본 뒤 설계한 적응적 후속입니다.

C 평균 F1 **0.446553**, B 대비 **+0.006005**, 최악 차이 **-0.003634**. 네 번째 추가 **False**. 5개는 미사용입니다.

|   fold |     b_f1 |     c_f1 |   c_accuracy |   delta_c_minus_b |
|-------:|---------:|---------:|-------------:|------------------:|
|      0 | 0.46263  | 0.463411 |     0.46875  |       0.000781302 |
|      1 | 0.41962  | 0.441742 |     0.445565 |       0.0221223   |
|      2 | 0.416605 | 0.422373 |     0.434476 |       0.00576813  |
|      3 | 0.449435 | 0.445801 |     0.464718 |      -0.0036336   |
|      4 | 0.45445  | 0.459436 |     0.453629 |       0.00498604  |

---

# v30 — 처음부터 다시 구성한 소형 앙상블과 실패/후속 기록

## B 후보 결과와 판단

B 후보 모델은 **3개**: `rare_lr + rare_ova + rare_mlp`, **1/3씩 균등 확률 평균**입니다. 하나의 parser·희귀 변이 전처리·선택 변수 행렬을 공유합니다. 기존 v25/v29 학습 분류기나 피클을 가져와 감싼 모델이 아닙니다.

| 비교 | 평균 Macro F1 | 평균 accuracy | 평가 의미 |
|---|---:|---:|---|
| v29 9개 | 0.487652 | 기존 v29 보고서 참조 | 동일 train/validation의 실제 OOF |
| v30 A: 35개 소형 조합 선택 과정 | 0.433061 | 43.7298% | inner2/outer5 nested, 조합 선택 과정의 성능 |
| v30 B: 고정3개 희귀 변이 후속 | **0.440548** | **45.0403%** | A 일부 결과를 보고 설계한 적응적 후속의 그룹5fold |

- B−v29 평균 **-0.047104**, fold 차이 `[-0.06010588250572263, -0.04524883309750355, -0.052533610907847306, -0.04692264257389556, -0.030711216659891738]`, 짝지은 참조 확인 **True**.
- 공학적 개선 기준: 평균 +0.003 이상·모든 fold -0.003 이상. 통과 **False**. 실패하면 기존 성능 모델의 교체/개선을 주장하지 않습니다.
- B pooled OOF Macro F1 **0.444090**. B는 고정3개 구성이지만 adaptive history가 있어 외부 독립 확인이나 선택 편향 없는 최고점으로 표현하지 않습니다.
- Public 미제출/미확인. v25 실제 **0.390417094**, v19 실제 **0.3664759128**과 로컬 점수를 구분합니다.
- 모델 50,169,322 bytes, 공유 선택 변수 8192개. 최종 train6201명 학습·피클 저장·재로딩·제출 CSV까지 완료했습니다.

## 요구사항과 범위 변경을 숨기지 않기

사용자는 '처음부터 단순하게, 단일 모델일 필요는 없고 최대4개까지, 5개는 먼저 문의'라고 정했습니다. 최종은3개이며5개를 추가하지 않았습니다. 기존 모델은 보존합니다.

초기에는 단일 모델 제한으로 시작했다가 사용자 설명에 따라 outer 점수 전 중단했습니다. 일부 inner 결과는 확인했고 로그를 `aborted_single_only/`에 보관했습니다. 그 다음 문자열 group-ID pilot은 SGKF 정렬이 달라져 기존 v29와 분할이 일치하지 않았습니다. 일부 pilot outer 점수를 확인한 뒤 중단하고, group ID의 원래 숫자 정렬을 복구했습니다. 해당 partial 결과는 `pilot_string_group_ids/`에 남기며 최종 대조에 섞지 않습니다.

수정한 A는 공유 AA/bin과 일부 train-only 증강을 추가한 후 nested5fold로 평가했습니다. B는 A 일부 outer 결과가 약한 것을 본 뒤, 과거 v16 문헌 설계와 v23~25의 희귀 변이 처리에서 배운 점을 새 코드로 구현한 후속입니다. B의3개 구성·파라미터·동일 가중치는 **B 점수를 보기 전에 고정**했습니다. 같은 과거 환자의 반복 평가와 적응적 설계 이력을 감추지 않습니다. 새 seed만으로 연구자 편향을 없앨 수 없습니다.

## 실패 기록에서 무엇을 배웠나

| 과거/이번 관찰 | 반영 |
|---|---|
| v19 로컬 개선이 Public에서 그대로 유지되지 않음 | 실제 Public와 로컬 점수 분리, 리더보드 향상 보장 안 함 |
| v25 표기 정합성 | 단일 치환 A123X만 A123*로 통일하는 기존 legacy 가정 유지. 모든 X를 stop으로 변환하지 않음 |
| v29 4개 pruning 후보가 추가 검증에서 탈락 | 소수 모델이라는 이유만으로 성능 유지 선언 안 함. 새 표현과 모델을 다시 학습 |
| v30 A의 단순 특징만으로 기존 앙상블을 넘지 못할 수 있음 | B에 학습 DF 기반 희귀/지원 표현·미관측 요약 보강. 기존 좋은 전처리 관점은 살리되 학습 모델은 재사용 안 함 |
| 무조건 행 정규화는 부담량 신호를 없앨 수 있음 | L1/L2 행 정규화 없이 burden와 유형 분율 모두 유지 |
| rare exact는 미래 환자에서 안 나올 수 있음 | gene/type/AA/bin back-off + residual attenuation. df/(df+5)는 자체 휴리스틱이지 병원성 점수 아님 |
| 많은 모델/비중 최적화는 운영 부담·선택 편향 | B3개 고정·동일 비중·shared preprocessor·메타 모델 없음 |
| 형제 라벨/쌍둥이 규칙의 일반화 위험 | 그룹 분리만 사용, 라벨 반전·정답 복사·강제 암종 비율 보정 미사용 |

## 논문 50편 기록을 다시 참고한 범위

`LITERATURE_REVIEW_AND_PREPROCESSING_V16.md`의50편별 요약·검토 범위·구현/미구현 경계를 재검토했습니다. 이번에50편 원문을 전부 새로 정독한 것은 아닙니다. 실제 v30 구현 연결은 아래와 같습니다.

| 문헌 검토 ID/출처 | 참고한 내용 | 실제 적용·한계 |
|---|---|---|
| [P03](https://doi.org/10.3389/fgene.2020.00674) | mutation 선별·단순 LR 기준선 | LR 비교/고정3개 구성. 저자의 gene 목록/성능 차용 아님 |
| [P05](https://doi.org/10.1111/biom.13367) | 미관측 희귀 변이를 공유 meta-feature에 연결 | gene/type/AA/bin + exact residual + train DF 희귀 back-off. Bayesian/group-lasso 재현 아님 |
| [P06](https://doi.org/10.1038/s41598-019-53034-3), [P10](https://doi.org/10.1016/j.jbi.2019.103247) | 관측 event count·mutation 기반 분류 | gene binary/log unique count와 burden 보존. CNV·NMF·기능 점수 미사용 |
| [P17](https://doi.org/10.1038/nature12213), [P19](https://doi.org/10.1038/nature12634), [P20](https://doi.org/10.1016/j.cell.2017.09.042) | 변이량 이질성·유형·동의 변이 구분 | 부담량/유형 수·분율 별도 유지. synonymous 미삭제. driver·병원성 판정 아님 |
| [P41](https://doi.org/10.1093/nar/gkq603), [P42](https://doi.org/10.1186/s13059-016-0974-4), [P43](https://doi.org/10.1002/humu.22981) | 참조정보·표기와 불확실성 구별 | stop gained/lost/retained, unparsed 보존. 정식 HGVS validator가 아니며 위치 이동 금지 |
| [P47](https://doi.org/10.1073/pnas.102102699), [P48](https://doi.org/10.1186/1471-2105-7-91), [P49](https://www.jmlr.org/papers/v11/cawley10a.html), [P50](https://doi.org/10.1016/j.patter.2023.100804) | 선별 누수·선택 편향·재현성 | 어휘/DF/chi2/스케일을 학습부에서만 fit. A nested 선택 평가와 B 고정 조합 평가를 구분. 적응적 후속 편향은 남음 |


외부 환자·정답·pretrained weights·PPI·CGC 테이블을 새로 추가하지 않았습니다. Geneformer를 사용하지 않습니다. 논문 방법을 참고하는 것과 외부 데이터 사용 규정은 구분합니다. DNA ref/alt·assembly·transcript·coverage가 없으므로 SBS96·CNV·MSI·TMB/Mb·SIFT/PolyPhen/CADD·단백질 위치 보정을 만들지 않습니다. 문헌상의 다른 cohort/accuracy를 본26종 MacroF1 기대치로 쓰지 않습니다.

## 입력·EDA·중복 그룹

원본 train6201행,4384개 gene,26개 SUBCLASS입니다. ID는 입력에서 제외하며 SUBCLASS는 정답으로만 사용합니다. 개발4960명에서 EDA/CV, 기존 보류1241명은 평가하지 않습니다. 최종 배포 학습에만 전체6201명을 사용합니다. 원본 CSV 수정 없음.

기존 보수적 그룹과 새 canonical profile을 union해 같은 프로필의 fold 간 중복을 방지했습니다. 추가 합쳐진 그룹/개발 제외는 없었고 v29의5개 train/validation 인덱스와 전부 일치하는 것을 확인했습니다. train checksum `92418b8441d058cfc68e939dd88725610750be4bc8edc51253cffc72fc4fc0ab`. 그룹은 정답/test 없이 원본 프로필에서만 구성했습니다. 프로필 일치가 같은 환자임을 증명하는 것은 아닙니다.

| SUBCLASS   |   ('mutated_genes', 'count') |   ('mutated_genes', 'median') |   ('mutated_genes', 'mean') |   ('unique_events', 'count') |   ('unique_events', 'median') |   ('unique_events', 'mean') |
|:-----------|-----------------------------:|------------------------------:|----------------------------:|-----------------------------:|------------------------------:|----------------------------:|
| ACC        |                           58 |                          24   |                    36.1724  |                           58 |                          26   |                    39.1552  |
| BLCA       |                           84 |                          57.5 |                    75.0119  |                           84 |                          60   |                    81       |
| BRCA       |                          629 |                           9   |                    15.7631  |                          629 |                          10   |                    16.4833  |
| CESC       |                          124 |                          18.5 |                    44.2581  |                          124 |                          19   |                    48.1855  |
| COAD       |                          179 |                          24   |                    81.3575  |                          179 |                          24   |                    97.324   |
| DLBC       |                           31 |                          30   |                    49.3548  |                           31 |                          32   |                    54.6774  |
| GBMLGG     |                          369 |                          11   |                    12.6585  |                          369 |                          12   |                    13       |
| HNSC       |                          179 |                          32   |                    40.9497  |                          179 |                          33   |                    43.0168  |
| KIPAN      |                          412 |                          15   |                    16.3714  |                          412 |                          15   |                    16.8447  |
| KIRC       |                          267 |                          13   |                    13.2584  |                          267 |                          13   |                    13.5655  |
| LAML       |                          127 |                           3   |                     3.33071 |                          127 |                           3   |                     3.38583 |
| LGG        |                          183 |                           8   |                     9.04372 |                          183 |                           8   |                     9.38251 |
| LIHC       |                          127 |                          24   |                    31.3937  |                          127 |                          25   |                    32.2677  |
| LUAD       |                          148 |                          41.5 |                    58.1284  |                          148 |                          42   |                    61.2838  |
| LUSC       |                          143 |                          59   |                    71.0839  |                          143 |                          60   |                    75.2517  |
| OV         |                          203 |                          12   |                    14.33    |                          203 |                          12   |                    14.4433  |
| PAAD       |                           96 |                          14.5 |                    41.5625  |                           96 |                          14.5 |                    66.5     |
| PCPG       |                          118 |                           4   |                     4.5     |                          118 |                           4   |                     4.61864 |
| PRAD       |                          213 |                           6   |                     7.9061  |                          213 |                           6   |                     8.12207 |
| SARC       |                          159 |                           9   |                    13.4403  |                          159 |                           9   |                    14.5723  |
| SKCM       |                          221 |                          83   |                   133.851   |                          221 |                          87   |                   164.181   |
| STES       |                          303 |                          41   |                    81.4389  |                          303 |                          42   |                    89.0363  |
| TGCT       |                          100 |                          16   |                    17.24    |                          100 |                          16   |                    17.46    |
| THCA       |                          260 |                           4   |                     4.45769 |                          260 |                           4   |                     4.46923 |
| THYM       |                           68 |                           3   |                     6.30882 |                           68 |                           3   |                     6.55882 |
| UCEC       |                          159 |                          18   |                   121.226   |                          159 |                          19   |                   160.069   |

## 파서와 변수군의 의미

공백/세미콜론/쉼표로 cell 토큰을 분리하고 pointwise canonicalization 후 환자·gene 내 같은 토큰을1개로 셉니다. 단일 AA substitution·stop gained/lost/retained·fs/delins/del/ins를 구분합니다. 복합/불완전 표기는 unparsed/exact로 보존하며 임의 위치 이동·서열 추정·분해를 하지 않습니다. 이 파서는 정식 HGVS validator가 아니고 새로운 표기에서는 미해석률을 확인해야 합니다.

| 특징군 | 정의/의미 |
|---|---|
| gene/count | gene별 변이 있음 binary·서로 다른 canonical 토큰 수 log1p |
| type/effectcount | gene별 표기유형 binary 및 유형별 event 수 log1p |
| event | gene×canonical exact 표기. 학습 DF3 이상만 어휘 후보 |
| meta | gene×AA 치환, 단백질 표기 위치 bin64/256. 실제 domain·genomic bin 아님 |
| aa_global | gene을 공유한 AA 치환 수. DNA mutation signature 아님 |
| rare/supported | 해당 gene의 사건 중 학습 참조 DF<3/≥3 개수. 병적/양성 분류 아님 |
| summary | gene/event/미해석/결측/유형별 log 수·유형 분율·rare/unseen 요약 |
| missing | 결측 gene binary. WT와 구별 |

rare/unseen training 특징은 각 event DF에서 자기 자신1을 빼서 계산하고, validation/inference는 학습 DF만 사용합니다. labels로 rare pool/DF를 정하지 않습니다. 원본 학습부에서 DictVectorizer→DF≥3(summary 예외)→global chi2 상위 최대8192→MaxAbs를 fit합니다. exact event 열은 **MaxAbs 후** df/(df+5)를 곱합니다. 이는 임의 조합별 분류기를 더 넣는 것이 아니라 하나의 공유 전처리입니다.

| family      |   features |
|:------------|-----------:|
| aa_global   |        182 |
| count       |        840 |
| effectcount |        630 |
| event       |        187 |
| gene        |       1345 |
| meta        |       1996 |
| rare        |       1720 |
| summary     |         12 |
| supported   |         99 |
| type        |       1181 |

최종 전체 변수·원래 학습 DF·chi2·residual weight는 `b_selected_variables.csv`와 `selected_variables_v30.md`에 기록했습니다. chi2는 표본 내 라벨 연관성이지 병원성·인과성이나 임상 진단 근거가 아닙니다.

## 학습부 내부 증강

OVA/MLP만 원본 행 + 증강 행으로 fit합니다. 원본 학습 fold에서 DF2 이하 missense/synonymous event를 nuisance pool로 정하고, gene mask0.1 및 Poisson20 nuisance를 사용합니다. 원래 gene이 있으면 최소1개를 남기고, missing gene에는 nuisance를 넣지 않습니다. 변형된 event에서 gene/type/AA/bin/count/summary를 다시 계산해 채널이 서로 모순되지 않게 합니다.

어휘/DF/chi2/MaxAbs는 원래 학습 행에서만 fit하고, 증강에는 transform만 수행합니다. 원본1/증강0.5 가중치이며 MLP는 원본 train class-balanced weight를 적용합니다. OVA는 is_unbalance를 사용합니다. LR는 증강 없이 원본 class-balanced fit입니다. 증강이 실제 질병 생물학을 재현하거나 nuisance가 germline임을 뜻하지 않으며, label-preserving augmentation은 모델링 가정입니다. test/validation 원본은 증강하지 않습니다.

## 최종 B 모델 설정과 구조

1. LR: C1, balanced, max_iter1600.
2. LightGBM: multiclassova/is_unbalance,500trees,leaves15,depth5,min_child20,lambda10,learning_rate.04,colsample.85.
3. MLP: hidden128,alpha1,batch128,learning_rate.001,max_iter180,early_stoppingFalse,balanced sample weight.

세 확률을 각각 행합1로 맞춘 뒤 동일 비중으로 평균하고 argmax합니다. OVA는 API 객체1개 안에서26개 one-vs-all 문제를 학습하며 트리·파라미터 자체가3개뿐이라는 뜻은 아닙니다. MLP180epoch 상한은 수렴 보증이 아니며, 예측 확률은 임상적 확률로 calibration한 결과가 아닙니다. 모든 model seed는30031이며 MaxAbs/DF/어휘/선택 변수는 공유합니다.

v25/v29의 classifier나 pretrained 모델을 불러와 학습/추론하는 구조가 아닙니다. 일반 알고리즘과 과거 전처리의 좋은 원리를 차용해 새 코드로 전체 학습했습니다. 유지보수 대상은 parser1개·전처리1개·학습기3종·균등 평균이며 이전9개보다 개념 수를 줄였습니다. 라이브러리/표기 스키마 관리는 여전히 필요합니다.

## A의 nested 결과와 B 결과를 섞지 않기

A는 기본 설정6개와 family-distinct1~4개 조합35개를 균등 평균으로 비교했습니다. 매 outer 학습부 inner2-fold에서 최고점0.002 이내의 최소 모델 수를 선택했습니다. 아래 A 점수는 조합 선택 과정의 성능이며 마지막 배포 조합의 독립 점수가 아닙니다.

|   fold | selected                           |       f1 |   accuracy |   features |   fit_seconds |   prediction_seconds |   v29_f1 |   delta_vs_v29 |
|-------:|:-----------------------------------|---------:|-----------:|-----------:|--------------:|---------------------:|---------:|---------------:|
|      0 | lr_light\|lgb31_ova\|xgb4          | 0.450555 |   0.460685 |      27432 |       73.2049 |             2.65861  | 0.522736 |     -0.0721803 |
|      1 | lr_light\|xgb4                     | 0.381561 |   0.397177 |      18474 |       24.5585 |             0.437742 | 0.464869 |     -0.0833075 |
|      2 | lgb31_ova\|xgb4\|mlp128            | 0.432675 |   0.428427 |      27633 |      125.061  |             2.18894  | 0.469139 |     -0.036464  |
|      3 | lr_strong\|lgb31_ova\|xgb4\|mlp128 | 0.439456 |   0.447581 |      36552 |      118.817  |             2.69519  | 0.496357 |     -0.0569009 |
|      4 | lgb31_ova\|xgb4\|mlp128            | 0.461057 |   0.452621 |      27567 |      111.007  |             2.10567  | 0.485161 |     -0.0241035 |

A 마지막 구성 `lr_strong|lgb31_ova|xgb4|mlp128`, 모델 수 4. 피클과 모든 결과는 `artifacts/v30/primary_a/`에 보존했습니다. B 결과로 A를 성공으로 고치지 않습니다.

B는 고정3개를 동일한 그룹5fold에서 새로 fit했습니다. v29 참조는 전체 train 모델 예측이 아니라 당시의 실제 OOF만 읽고 인덱스·class 순서·train SHA를 확인합니다. 참조 캐시가 없어도 B 학습은 가능하며 대조만 생략합니다.

|   fold | selected                    |       f1 |   accuracy |   features |   fit_seconds |   v29_f1 |   delta_vs_v29 |
|-------:|:----------------------------|---------:|-----------:|-----------:|--------------:|---------:|---------------:|
|      0 | rare_lr\|rare_ova\|rare_mlp | 0.46263  |   0.467742 |       8192 |       81.8486 | 0.522736 |     -0.0601059 |
|      1 | rare_lr\|rare_ova\|rare_mlp | 0.41962  |   0.4375   |       8192 |       72.6642 | 0.464869 |     -0.0452488 |
|      2 | rare_lr\|rare_ova\|rare_mlp | 0.416605 |   0.431452 |       8192 |       84.4071 | 0.469139 |     -0.0525336 |
|      3 | rare_lr\|rare_ova\|rare_mlp | 0.449435 |   0.465726 |       8192 |       79.7806 | 0.496357 |     -0.0469226 |
|      4 | rare_lr\|rare_ova\|rare_mlp | 0.45445  |   0.449597 |       8192 |       70.893  | 0.485161 |     -0.0307112 |

## 오류 진단

|              |   precision |   recall |   f1-score |     support |
|:-------------|------------:|---------:|-----------:|------------:|
| ACC          |    1        | 0.793103 |   0.884615 |   58        |
| BLCA         |    0.585366 | 0.285714 |   0.384    |   84        |
| BRCA         |    0.549729 | 0.483307 |   0.514382 |  629        |
| CESC         |    0.223301 | 0.185484 |   0.202643 |  124        |
| COAD         |    0.742331 | 0.675978 |   0.707602 |  179        |
| DLBC         |    0.714286 | 0.16129  |   0.263158 |   31        |
| GBMLGG       |    0.540773 | 0.341463 |   0.418605 |  369        |
| HNSC         |    0.312139 | 0.301676 |   0.306818 |  179        |
| KIPAN        |    0.425316 | 0.407767 |   0.416357 |  412        |
| KIRC         |    0.448276 | 0.243446 |   0.315534 |  267        |
| LAML         |    0.603774 | 0.503937 |   0.549356 |  127        |
| LGG          |    0.462451 | 0.639344 |   0.536697 |  183        |
| LIHC         |    0.348624 | 0.299213 |   0.322034 |  127        |
| LUAD         |    0.485981 | 0.351351 |   0.407843 |  148        |
| LUSC         |    0.482143 | 0.377622 |   0.423529 |  143        |
| OV           |    0.302139 | 0.55665  |   0.391681 |  203        |
| PAAD         |    0.369231 | 0.25     |   0.298137 |   96        |
| PCPG         |    0.208333 | 0.423729 |   0.27933  |  118        |
| PRAD         |    0.232673 | 0.441315 |   0.3047   |  213        |
| SARC         |    0.169154 | 0.213836 |   0.188889 |  159        |
| SKCM         |    0.931818 | 0.742081 |   0.826196 |  221        |
| STES         |    0.482877 | 0.465347 |   0.47395  |  303        |
| TGCT         |    0.6      | 0.57     |   0.584615 |  100        |
| THCA         |    0.806604 | 0.657692 |   0.724576 |  260        |
| THYM         |    0.14359  | 0.411765 |   0.212928 |   68        |
| UCEC         |    0.60625  | 0.610063 |   0.60815  |  159        |
| accuracy     |    0.450403 | 0.450403 |   0.450403 |    0.450403 |
| macro avg    |    0.491429 | 0.438199 |   0.44409  | 4960        |
| weighted avg |    0.495643 | 0.450403 |   0.460138 | 4960        |

큰 혼동 흐름:

| true   | predicted   |   patients |   fraction_within_true_class |
|:-------|:------------|-----------:|-----------------------------:|
| GBMLGG | LGG         |        126 |                    0.341463  |
| KIRC   | KIPAN       |         98 |                    0.367041  |
| BRCA   | OV          |         75 |                    0.119237  |
| KIPAN  | KIRC        |         65 |                    0.157767  |
| BRCA   | PRAD        |         52 |                    0.0826709 |
| KIPAN  | PRAD        |         43 |                    0.104369  |
| LGG    | GBMLGG      |         42 |                    0.229508  |
| KIRC   | PRAD        |         36 |                    0.134831  |
| BRCA   | PCPG        |         34 |                    0.0540541 |
| THCA   | PCPG        |         32 |                    0.123077  |
| SARC   | OV          |         31 |                    0.194969  |
| SARC   | PRAD        |         31 |                    0.194969  |
| PRAD   | THYM        |         29 |                    0.13615   |
| KIPAN  | BRCA        |         28 |                    0.0679612 |
| PCPG   | THYM        |         26 |                    0.220339  |

같은 입력의 다른 라벨·암종 간 공유 변이·관측 정보 부족이 가능한 한계지만, 이 표만으로 원인을 확정하거나 진짜 오진이라고 부르지 않습니다. 결과를 보고 라벨 반전/쌍별 추가 전문가를 붙이지 않았습니다. adaptive 같은 환자 반복 평가라 외부 코호트 일반화·임상적 안전성·리더보드 향상을 보증하지 않습니다.

## 실행·저장·추론

`cencer_v30.ipynb`에 A와 B의 source·EDA·선별·검증·학습·모델 저장·최종 추론·문서 생성이 모두 있습니다. 외부 프로젝트 py를 요구하지 않으며 worker는 artifacts 아래 자동 생성합니다. 원본 data와 requirements 환경이 필요합니다. 참조 v29 캐시는 대조용 선택 사항입니다.

- Python 3.15.0, requirements-v30.txt.
- 피클 `artifacts/v30/before_d/cancer_model_v30_before_d.pkl`, 50,169,322 bytes, checksum `47116a2e0af880c36a0baf5e57237e3102a9c8ef807381c4dcacca4d87e7bdbf`.
- 전체 train6201명에서 고정3개만 새로 fit. fit시간 133.76초(파싱·nested 탐색 제외), 개별 `{'rare_lr': 1.8553527090116404, 'rare_ova': 43.47619908300112, 'rare_mlp': 78.64734812499955}`.
- 독립 추론 프로세스에서 모델만 로드해 test2546명을 예측. 해당 프로세스는 train open을 차단하고 fit하지 않음. 연구 프로세스는 test/sample open을 차단.
- 최종 `submission/혜진_submission_v30_compact_experimental.csv`, 2546행. ID·순서·클래스·확률합·배치 불변성·X/* 예측 일치·재로딩·모델/CSV hash 검사.
- test 빈도/분포·정답·형제 label 규칙 미사용. raw CSV와 이전 모델/제출 파일 보존. Public 미확인으로 실험용 파일을 기존 최고 Public 모델로 덮어쓰지 않음.
- 공유 표기 parser와 train DF back-off 외에 Geneformer/외부 환자/정답 사전/COAD prior를 넣지 않음. 기존 가정의 규정 적합성과 임상 안전성은 별도 확인 대상.
