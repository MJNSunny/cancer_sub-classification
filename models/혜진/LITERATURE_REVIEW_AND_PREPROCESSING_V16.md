# 논문 50편 검토와 암종 분류 EDA·전처리 재설계 — v16

작성·검색 기준일: **2026-11-10**. 기존 v6·v10을 보존한 별도 연구입니다. test/sample은 열지 않았고 기존 홀드아웃도 점수 계산에 사용하지 않았습니다. 외부 환자·정답 데이터는 추가하지 않았습니다.

## 먼저 확인할 결과

- 같은 새 그룹 분할에서 기존 raw 표현의 고정 LR 평균 F1은 **0.381589**입니다.
- inner CV가 전처리를 선택한 과정의 outer 평균 Macro F1은 **0.390505**입니다. 개별 outer 최고값을 이 값 대신 쓰지 않습니다.
- 이 실험은 단순 모델에 대한 전처리 대조입니다. 과거 v10 앙상블과 seed·모델이 달라 직접 우열을 비교할 수 없으며, 새 Public 성능이나 0.60 달성을 주장하지 않습니다.
- 새 파서·전처리기·실험용 LR 모델을 저장했지만 기존 주 모델과 제출 파일은 교체하지 않았습니다.

## 1. 문헌을 어떻게 찾고 어디까지 확인했는가

Europe PMC의 DOI/PMID/PMCID 검색과 출판사·PMC 원문을 사용했습니다. 키워드는 somatic mutation / tissue of origin / cancer type classification / rare variant meta-feature / network-based stratification / variant annotation / HGVS / feature-selection leakage / nested cross-validation입니다. 제목·연도·식별자를 대조한 **중복 없는 50편**을 선별했습니다. arXiv와 정식 출판본을 두 편으로 세거나 corrigendum을 독립 근거로 세지 않았습니다.

49편은 초록 또는 출판사 초록을 확인했고, 초록이 없는 P45는 공개 본문을 확인했습니다. 공개 XML 원문 캐시는 26편 확보했습니다. **원문 확보는 전체 정독을 뜻하지 않습니다.** 핵심 15편은 방법/중요 본문의 특정 절·발췌를 추가로 검토했습니다. 각 논문 아래의 검토 범위를 구분했습니다. 이는 선별형 근거 검토이며 정식 체계적 문헌고찰·메타분석은 아닙니다.

P34는 최초 DOI가 무관한 lncRNA 논문으로 연결되어 제목 대조 후 올바른 갑상선암 논문으로 교체했습니다. 최종 50편에는 수정된 논문만 포함합니다. `artifacts/v16/literature/excluded_identifier_match.json`에 제외 근거를 남겼습니다. 게재연도는 Europe PMC 기준이며 온라인 선행 게재연도와 다를 수 있습니다.

원문/초록 캐시는 연구용 `artifacts/v16/literature/`에만 두고 Git에 포함하지 않습니다. 이 문서에는 원문 복사 대신 직접 작성한 요약·적용·한계를 기록했습니다. 검색에 환자 ID나 환자별 변이 목록을 전송하지 않았습니다.

## 2. 논문의 입력과 이 CSV의 입력은 다르다

| 정보 | 현재 가용성 | 처리 |
| --- | --- | --- |
| gene별 WT/변이 문자열 | 있음 | 원문을 보존하고 보수적으로 구조화 |
| 단백질처럼 보이는 AA 변화·위치 | 다수 있음 | 표기 기반 속성; 실제 참조 단백질과의 일치 검증은 안 됨 |
| DNA ref/alt·염색체·유전체 좌표·assembly | 없음 | SBS96·genomic 1 Mb bin을 만들지 않음 |
| transcript/isoform·참조 서열 | 없음 | 위치 ±몇 칸 보정·3′ 정규화·isoform 매핑을 하지 않음 |
| CNV·fusion·methylation·RNA·임상 노출 | 없음 | 변이 유무로 가짜 상태를 추정하지 않음 |
| SIFT·PolyPhen·CADD 등 기능 점수 | 없음 | missense/fs 유형에 임의 점수를 대입하지 않음 |
| 분석 대상 exon 길이·시퀀싱 영역 | 없음 | 변이 수를 TMB/Mb라 부르지 않고 유전자 길이를 최대 관측 위치로 추정하지 않음 |

논문에서 높은 accuracy를 보고했더라도 WGS·CNV·RNA·암종 수·cohort·평가 지표가 다릅니다. 논문의 점수를 현재 26종 Macro F1의 기대값이나 이론적 상한으로 사용하지 않습니다. 특히 mutation-only와 multi-omics 결과의 차이는 [P01](https://doi.org/10.1038/s41467-019-13825-8), [P02](https://doi.org/10.1038/s41467-022-31666-w), [P06](https://doi.org/10.1038/s41598-019-53034-3), [P07](https://doi.org/10.1186/s13073-017-0493-2), [P09](https://doi.org/10.1186/s13073-023-01204-4)에서 확인했습니다.

## 3. 어떤 근거를 어떤 코드로 옮겼는가

| 변경 ID | 구현 또는 판단 | 근거 | 원문 재현과의 차이 |
| --- | --- | --- |
| M01 | `parse_token16`, `parse_rows16`: 원문 보존·표기 분리·미해석/불확실성 기록 | [P41](https://doi.org/10.1093/nar/gkq603), [P42](https://doi.org/10.1186/s13059-016-0974-4), [P43](https://doi.org/10.1002/humu.22981) | 완전한 HGVS validator/annotation tool 아님 |
| M02 | gene/type count·raw/unique event 수·변이량·동의 채널 유지 | [P04](https://doi.org/10.1016/j.bbadis.2020.165916), [P06](https://doi.org/10.1038/s41598-019-53034-3), [P17](https://doi.org/10.1038/nature12213), [P19](https://doi.org/10.1038/nature12634), [P20](https://doi.org/10.1016/j.cell.2017.09.042) | TMB·dN/dS·MutSigCV가 아닌 관측값 |
| M03 | exact residual + 공유 gene/type/AA metadata + train DF 기반 희귀 back-off | [P05](https://doi.org/10.1111/biom.13367), [P09](https://doi.org/10.1186/s13073-023-01204-4), [P10](https://doi.org/10.1016/j.jbi.2019.103247) | 계층 Bayesian/group-lasso·attention·NMF의 재현 아님; 제한된 입력에 대한 자체 적응 |
| M04 | 논문별 작은 gene panel 합계의 별도 ablation | [P11](https://doi.org/10.1038/nmeth.2651), [P13](https://doi.org/10.1186/1471-2164-16-s7-s7), [P14](https://doi.org/10.1016/j.cell.2018.03.035) 및 P25~P40 | 실제 구성원은 아래 명시한 TCGA 부분집합; PPI/network propagation이 아님 |
| M06 | ID 제외·test open 차단·그룹 분리·inner 선택/outer 평가 | [P47](https://doi.org/10.1073/pnas.102102699), [P48](https://doi.org/10.1186/1471-2105-7-91), [P49](https://www.jmlr.org/papers/v11/cawley10a.html), [P50](https://doi.org/10.1016/j.patter.2023.100804) | 3×2 nested group CV; 과거 관찰 편향까지 제거하지는 못함 |
| M07 | 고정 LR 및 ExtraTrees 대조 | [P03](https://doi.org/10.3389/fgene.2020.00674), [P07](https://doi.org/10.1186/s13073-017-0493-2) | 저자의 RF 선별이나 모델 전체를 복제한 것이 아님 |

M03의 exact 변이 감쇠는 `df/(df+5)`라는 명시적 휴리스틱입니다. **MaxAbs 이후** 해당 residual 열에 적용해 column scaling이 감쇠를 상쇄하지 않도록 확인했습니다. gene/type/AA 공유 특징은 남겨 희귀·미관측 exact 변이도 가능한 일반 정보에 기여하게 합니다. training 희귀 요약에는 자기 자신을 뺀 DF를 쓰고, 검증/추론에는 학습 DF만 씁니다. 이 값은 posterior나 병원성 점수가 아닙니다.

## 4. 새 파서의 범위와 검증 사례

| 입력 예 | 해석 | 지키는 경계 |
| --- | --- | --- |
| `R132H` / `R132R` | missense / synonymous | 기능적 유해성은 판정하지 않음 |
| `R213*` / `*363*` / `*213Q` | stop gained / retained / lost | 별표가 있다는 이유로 전부 stop gained로 묶지 않음 |
| `K16Rfs*23` | 영향 위치 16, 새 reading-frame 종료 거리 23 | 23을 변이 위치로 쓰지 않음 |
| `1_2FS>FS` | 길이가 일치하는 synonymous block | 대문자 AA `FS`를 소문자 frameshift `fs`로 읽지 않음 |
| `483_484MP>IA` | 두 AA 성분 속성, 원래 복합 event는 1개로 보존 | 독립 DNA 사건 두 개라고 단정하지 않음 |
| `10_12AAA>DD` | 길이 불일치 complex range | 임의 분해·위치 이동을 하지 않음 |
| `p.(Arg123His)` | 불확실성 표시 + 구조화 AA 변화 | 추정 표기 괄호를 확정 관측과 합치지 않음 |
| `R123X` | ambiguous residue/X 플래그 | X를 무조건 stop으로 바꾸지 않음 |
| `A391` / 미해석 토큰 | 불완전/원문 보존 | 버리거나 정답을 추정하지 않음 |
| WT / 결측 | 서로 다른 상태 | 결측을 WT로 대입하지 않음 |

15개 표기 fixture와 결측·중복 검사 사례를 통과했습니다. 이 파서는 데이터의 단백질형 문법을 해석하는 보수적 구현입니다. 참조 서열 검증을 한 정식 HGVS 변환기가 아니며, bare `490del` 같은 legacy 위치는 데이터의 단백질형 문맥을 가정한 인덱스입니다. protein bin 64/256은 공학적 구간이며 실제 단백질 domain·유전자 길이·유전체 구간이 아닙니다.

기존 표기 분류와의 변경 기록:

| legacy_kind   | kind             |   unique_tokens |   occurrences |
|:--------------|:-----------------|----------------:|--------------:|
| deletion      | deletion         |               2 |             2 |
| frameshift    | block_change     |               2 |             2 |
| frameshift    | frameshift       |            5519 |          7897 |
| other         | block_change     |              80 |            85 |
| other         | synonymous_block |              43 |            49 |
| stop          | block_change     |              46 |            47 |
| stop          | stop_gained      |            5487 |         10634 |
| stop          | stop_retained    |              67 |            83 |
| substitution  | missense         |           69584 |        132806 |
| synonymous    | synonymous       |           19489 |         53810 |

## 5. EDA 범위와 실제 관찰

공식 train은 6,201명·4,384개 gene 컬럼이며, 이전 홀드아웃 1,241명은 점수 계산에서 제외했습니다. EDA와 교차검증은 개발 4,960명만 사용했습니다. 새 canonical grouping 때문에 제외한 개발 환자는 0명입니다. 원본/새 정규화 동일 프로필을 union하여 같은 그룹이 양쪽 fold에 걸치지 않게 했습니다.

| SUBCLASS   |   patients |   mean_mutated_genes |   median_mutated_genes |   mean_unique_events |   mean_unparsed |   stop_retained |
|:-----------|-----------:|---------------------:|-----------------------:|---------------------:|----------------:|----------------:|
| ACC        |         58 |             36.1724  |                   24   |             39.1552  |               0 |               1 |
| BLCA       |         84 |             75.0119  |                   57.5 |             81       |               0 |               9 |
| BRCA       |        629 |             15.7631  |                    9   |             16.4833  |               0 |               4 |
| CESC       |        124 |             44.2581  |                   18.5 |             48.1855  |               0 |              12 |
| COAD       |        179 |             81.3575  |                   24   |             97.324   |               0 |               1 |
| DLBC       |         31 |             49.3548  |                   30   |             54.6774  |               0 |               1 |
| GBMLGG     |        369 |             12.6585  |                   11   |             13       |               0 |               1 |
| HNSC       |        179 |             40.9497  |                   32   |             43.0168  |               0 |               4 |
| KIPAN      |        412 |             16.3714  |                   15   |             16.8447  |               0 |               0 |
| KIRC       |        267 |             13.2584  |                   13   |             13.5655  |               0 |               0 |
| LAML       |        127 |              3.33071 |                    3   |              3.38583 |               0 |               0 |
| LGG        |        183 |              9.04372 |                    8   |              9.38251 |               0 |               0 |
| LIHC       |        127 |             31.3937  |                   24   |             32.2677  |               0 |               1 |
| LUAD       |        148 |             58.1284  |                   41.5 |             61.2838  |               0 |               4 |
| LUSC       |        143 |             71.0839  |                   59   |             75.2517  |               0 |               6 |
| OV         |        203 |             14.33    |                   12   |             14.4433  |               0 |               2 |
| PAAD       |         96 |             41.5625  |                   14.5 |             66.5     |               0 |               0 |
| PCPG       |        118 |              4.5     |                    4   |              4.61864 |               0 |               0 |
| PRAD       |        213 |              7.9061  |                    6   |              8.12207 |               0 |               0 |
| SARC       |        159 |             13.4403  |                    9   |             14.5723  |               0 |               1 |
| SKCM       |        221 |            133.851   |                   83   |            164.181   |               0 |              18 |
| STES       |        303 |             81.4389  |                   41   |             89.0363  |               0 |               4 |
| TGCT       |        100 |             17.24    |                   16   |             17.46    |               0 |               0 |
| THCA       |        260 |              4.45769 |                    4   |              4.46923 |               0 |               0 |
| THYM       |         68 |              6.30882 |                    3   |              6.55882 |               0 |               0 |
| UCEC       |        159 |            121.226   |                   18   |            160.069   |               0 |               4 |

![개발 환자의 관측 변이량](figures_v16/burden_development.png)

동일 변이 프로필에서 여러 라벨이 나타나는 경우를 곧바로 오표기 환자라고 단정하지 않았습니다. 서로 다른 암이 같은 관측 변이를 가질 수 있고 추가 임상 정보가 없을 수도 있습니다. 다수결 relabel이나 어려운 환자 제거로 점수를 올리지 않았습니다. 저변이 환자도 평가에 남겼습니다.

![문헌 마커의 데이터 내 관측 비율](figures_v16/marker_fractions_development.png)

heatmap은 현재 개발 데이터의 관측 빈도이며 논문의 유병률이나 확정 진단 기준이 아닙니다. 측정 컬럼이 없는 gene은 0/WT 대신 unmeasured로 구분했습니다. GBMLGG/LGG, KIPAN/KIRC 및 STES/STAD·COAD/COADREAD 등의 명칭 관계는 데이터 사전 확인 과제로 남기고 라벨을 바꾸지 않았습니다.

## 6. 논문 유전자 부분집합과 실제 측정 범위

| panel               | paper   | requested_genes                                                   | present_genes                               | unmeasured_genes           |
|:--------------------|:--------|:------------------------------------------------------------------|:--------------------------------------------|:---------------------------|
| P25_breast          | P25     | TP53 PIK3CA GATA3 MAP3K1                                          | TP53 PIK3CA GATA3 MAP3K1                    | nan                        |
| P26_colorectal      | P26     | APC TP53 SMAD4 PIK3CA KRAS ARID1A SOX9 FAM123B POLE MLH1          | APC TP53 PIK3CA SOX9 POLE MLH1              | SMAD4 KRAS ARID1A FAM123B  |
| P27_glioma          | P27     | IDH1 IDH2 TP53 ATRX CIC FUBP1 NOTCH1                              | IDH1 IDH2 TP53 ATRX NOTCH1                  | CIC FUBP1                  |
| P29_gbm             | P29     | EGFR PDGFRA                                                       | EGFR                                        | PDGFRA                     |
| P30_renal           | P30     | VHL PBRM1 SETD2 ARID1A SMARCA4                                    | VHL                                         | PBRM1 SETD2 ARID1A SMARCA4 |
| P31_papillary_renal | P31     | MET SETD2 FH                                                      | MET FH                                      | SETD2                      |
| P32_ovarian         | P32     | TP53 NF1 BRCA1 BRCA2 RB1 CDK12                                    | TP53 NF1 BRCA1 BRCA2 RB1                    | CDK12                      |
| P33_uterine         | P33     | TP53 PTEN CTNNB1 PIK3CA ARID1A KRAS ARID5B POLE                   | TP53 PTEN CTNNB1 PIK3CA ARID5B POLE         | ARID1A KRAS                |
| P34_thyroid         | P34     | BRAF EIF1AX PPM1D CHEK2                                           | BRAF EIF1AX PPM1D CHEK2                     | nan                        |
| P35_prostate        | P35     | SPOP FOXA1 IDH1                                                   | SPOP IDH1                                   | FOXA1                      |
| P36_lung_ad         | P36     | RIT1 MGA EGFR RBM10 NF1 MET ERBB2                                 | RIT1 EGFR NF1 MET ERBB2                     | MGA RBM10                  |
| P37_lung_scc        | P37     | TP53 HLA-A NFE2L2 KEAP1 CDKN2A RB1                                | TP53 HLA-A NFE2L2 CDKN2A RB1                | KEAP1                      |
| P38_melanoma        | P38     | BRAF NRAS HRAS KRAS NF1 KIT                                       | BRAF HRAS NF1 KIT                           | NRAS KRAS                  |
| P39_gastric         | P39     | PIK3CA RHOA                                                       | PIK3CA RHOA                                 | nan                        |
| P40_headneck        | P40     | PIK3CA TRAF3 TP53 CDKN2A HRAS CASP8 NOTCH1 NSD1 AJUBA FAT1 NFE2L2 | PIK3CA TP53 CDKN2A HRAS CASP8 NOTCH1 NFE2L2 | TRAF3 NSD1 AJUBA FAT1      |

이 목록은 각 논문에 명시된 일부 mutation gene을 고정한 수동 사전지식입니다. 저자의 전체 pathway·driver 목록을 복제하지 않았습니다. IDH/RAS 계열을 IDH1/IDH2 및 NRAS/HRAS/KRAS로 펼친 것은 명시적 구현 선택입니다. HGNC alias를 추측해 컬럼을 합치지 않았습니다. 입력은 관측 mutation count뿐이며 경로 활성·임상 아형·fusion/CNV·methylation을 의미하지 않습니다. `truncation_notation_genes`라는 기존 변수명은 실제로 stop/fs/deletion/delins 표기를 합한 값이라 in-frame 변경도 포함할 수 있으며 기능 상실의 확정 판정이 아닙니다.

외부에서 사용한 것은 방법과 고정 gene 사전지식이며 외부 환자 행이나 정답은 추가하지 않았습니다. 문헌의 TCGA cohort와 이 CSV 원천의 환자 중복 여부는 확인할 수 없어 독립 외부 코호트라고 주장하지 않습니다.

## 7. 전처리 선택과 검증

4개 view는 legacy_raw / hierarchical / rare_backoff / rare_backoff_panels입니다. 표기 구조화·이벤트 count를 먼저 비교하고, 희귀 back-off 및 고정 panel 추가를 순서대로 분리했습니다. 모든 DF·어휘·chi2 최대 4096개·MaxAbs는 해당 inner 또는 outer 학습 부분에서만 적합했습니다. 전처리 view 선택은 inner 2-fold의 고정 LR(C=0.1)로 하며 outer 3-fold(seed 16016)에서 선택 과정을 평가했습니다. ExtraTrees는 200개·depth20·leaf2의 고정 대조군입니다. outer 검증으로 조기 종료하거나 다시 선택하지 않았습니다.

각 고정 view의 outer 대조(탐색적 ablation):

| view                | algo   |   macro_f1 |   accuracy |   selected_features |
|:--------------------|:-------|-----------:|-----------:|--------------------:|
| rare_backoff        | lr     |   0.392376 |   0.39294  |                4096 |
| rare_backoff_panels | lr     |   0.391436 |   0.392335 |                4096 |
| hierarchical        | lr     |   0.389078 |   0.390722 |                4096 |
| rare_backoff_panels | extra  |   0.386964 |   0.379836 |                4096 |
| legacy_raw          | lr     |   0.381589 |   0.386084 |                4096 |
| rare_backoff        | extra  |   0.377146 |   0.371973 |                4096 |
| hierarchical        | extra  |   0.37277  |   0.368143 |                4096 |
| legacy_raw          | extra  |   0.352173 |   0.355642 |                4096 |

선택 과정을 평가한 nested LR 결과:

|   fold |   macro_f1 |
|-------:|-----------:|
|      0 |   0.405468 |
|      1 |   0.398309 |
|      2 |   0.36774  |

nested fold 평균은 **0.390505**, 전체 OOF를 합친 pooled F1은 **0.392844**입니다. 두 값은 평균 방식이 다릅니다. 최종 배포 실험용 view `rare_backoff_panels`는 inner 선택의 다수결/inner 평균으로 정했고 outer 최고 view로 바꾸지 않았습니다.

외부 panel이 모든 알고리즘을 개선하지는 않았습니다. LR에서는 panel 없는 back-off가 탐색 평균에서 조금 높고, 트리에서는 panel이 도움이 됐습니다. 논문상 타당성이 곧 이 데이터의 성능 개선을 보장하지 않습니다. 더구나 이미 개발 데이터를 여러 버전에서 관찰해 온 연구자 선택 편향은 nested CV만으로 소급 제거되지 않습니다.

## 8. 실제 입력 변수와 저장 상태

| view                | family           |   selected_features |
|:--------------------|:-----------------|--------------------:|
| legacy_raw          | aa               |                 739 |
| legacy_raw          | gene             |                1514 |
| legacy_raw          | module           |                   7 |
| legacy_raw          | numeric          |                   6 |
| legacy_raw          | position         |                 215 |
| legacy_raw          | type             |                1418 |
| legacy_raw          | variant          |                 197 |
| hierarchical        | aa_global        |                 178 |
| hierarchical        | aa_meta          |                 413 |
| hierarchical        | effect           |                 408 |
| hierarchical        | format           |                 732 |
| hierarchical        | gene             |                 887 |
| hierarchical        | gene_event_count |                 560 |
| hierarchical        | num              |                  10 |
| hierarchical        | protein_bin256   |                 484 |
| hierarchical        | protein_bin64    |                 278 |
| hierarchical        | variant          |                 146 |
| rare_backoff        | aa_global        |                 174 |
| rare_backoff        | aa_meta          |                 290 |
| rare_backoff        | effect           |                 311 |
| rare_backoff        | format           |                 514 |
| rare_backoff        | gene             |                 658 |
| rare_backoff        | gene_event_count |                 407 |
| rare_backoff        | num              |                  12 |
| rare_backoff        | protein_bin256   |                 308 |
| rare_backoff        | protein_bin64    |                 195 |
| rare_backoff        | rare_gene        |                1020 |
| rare_backoff        | supported_gene   |                  78 |
| rare_backoff        | variant          |                 129 |
| rare_backoff_panels | aa_global        |                 174 |
| rare_backoff_panels | aa_meta          |                 290 |
| rare_backoff_panels | effect           |                 307 |
| rare_backoff_panels | format           |                 508 |
| rare_backoff_panels | gene             |                 656 |
| rare_backoff_panels | gene_event_count |                 402 |
| rare_backoff_panels | num              |                  12 |
| rare_backoff_panels | panel            |                  23 |
| rare_backoff_panels | protein_bin256   |                 307 |
| rare_backoff_panels | protein_bin64    |                 194 |
| rare_backoff_panels | rare_gene        |                1016 |
| rare_backoff_panels | supported_gene   |                  78 |
| rare_backoff_panels | variant          |                 129 |

원본 raw와 새 해석 결과는 `parser_audit_dev.csv`로 대조할 수 있습니다. 정확한 최종 선택 목록은 `artifacts/v16/selected_features_<view>.csv`, 기본 선택은 `final_selected_features.csv`입니다.

- `preprocessor_v16_<view>.pkl`: 4개 전처리기를 공식 train 전체로 재적합한 보관본.
- `preprocessor_v16.pkl`, `cancer_model_v16_experimental.pkl`: inner 선택으로 정한 실험용 LR pipeline.
- `full_train_rare_backoff_matrix.npz`: 전체 train용 새 back-off 표현. 행 ID/라벨은 `full_train_matrix_rows.csv`, 열은 해당 view의 selected_features 파일.
- 전체-train 재적합본은 위 CV 점수를 계산하는 데 사용하지 않았습니다. training 행렬의 희귀 요약은 자기 자신 제외 규칙을 쓰므로 inference-role transform과 일부 값이 다릅니다.
- 신규 test 추론·제출 CSV·Public 점수는 없습니다. 기존 v6·v10 파일을 변경하지 않았습니다.

전체 train에 적합한 저장 행렬을 다시 분할해 CV를 계산하면 누수가 생깁니다. 이 행렬은 최종 학습 보관용이며, 새 검증에서는 반드시 각 fold의 학습 부분만으로 전처리기를 다시 적합해야 합니다. 점별 문자열 파싱과 동일 프로파일 그룹 형성은 고정 규칙이고, 빈도·어휘·스케일·변수 선택은 fold 안에서만 학습합니다.

## 9. 실행과 근거 파일

`cencer_v16.ipynb`에 파서·EDA·inner/outer 학습·전처리 저장·이 보고서 생성을 모두 포함했습니다. `requirements-v16.txt` 환경과 `data/train.csv`만 있으면 실행합니다. 문헌 메타데이터/직접 작성한 검토 요약은 노트북 안에도 고정해 재실행 시 네트워크가 필요하지 않습니다. 논문 원문은 코드 실행 의존성이 아닙니다.

아래의 논문별 기록은 **실제로 가져온 것과 가져오지 않은 것**을 구분합니다. 적용 태그 M01/M02/M03/M04/M06/M07는 3절, X01은 입력 부재, X02는 길이/영역 부재, X03은 기능 점수/참조 정보 부재, X04는 외부 네트워크 알고리즘 미재현을 뜻합니다.

## 10. 논문 50편별 분석·적용·한계

### P01. [A deep learning system accurately classifies primary and metastatic cancers using passenger mutation patterns](https://doi.org/10.1038/s41467-019-13825-8)

2020 · Jiao W · 검토 범위: 초록 + Somatic mutation feature sets / Neural Network 절

- 내용: WGS의 염기 치환 문맥과 유전체 구간별 passenger 분포를 결합한다. 단순 유전자 목록 분류기와 입력 정보가 다르다.
- 참고·적용: 변이 종류와 전체 관측 변이량을 분리해 EDA하고, 동의 변이를 근거 없이 제거하지 않는다.
- 미적용·한계: CSV에는 염기 문맥·염색체·1 Mb 구간이 없다. SBS96, 유전체 분포, 논문 신경망을 재현하지 않았으며 AA 변화는 DNA signature가 아니다.
- 연결: EDA-burden, M02, X01

### P02. [Machine learning-based tissue of origin classification for cancer of unknown primary diagnostics using genome-wide mutation features](https://doi.org/10.1038/s41467-022-31666-w)

2022 · Nguyen L · 검토 범위: 초록 + Extraction of genomic features / Classifier training 절

- 내용: CUPLR는 WGS 기반 driver/passenger·구조변이 특징과 암종별 선별, OOF 확률 보정을 사용한다.
- 참고·적용: 서로 다른 특징군의 기여를 분리하고 선별을 학습 부분 안에 둔다.
- 미적용·한계: 511개 특징과 구조변이·RMD·isotonic calibration은 구현하지 않았다. 동일한 정보가 없는 이 데이터에 논문 성능을 전용하지 않는다.
- 연결: M06, X01

### P03. [Predicting Cancer Tissue-of-Origin by a Machine Learning Method Using DNA Somatic Mutation Data](https://doi.org/10.3389/fgene.2020.00674)

2020 · Liu X · 검토 범위: 초록 + Feature Selection 절

- 내용: 유전자별 체세포 변이에서 RF 중요도 선별과 로지스틱 분류를 결합했다.
- 참고·적용: 복잡한 새 앙상블보다 로지스틱과 트리의 단순 대조 실험으로 전처리 효과를 먼저 비교한다.
- 미적용·한계: 논문의 300개 유전자나 보고 정확도를 그대로 가져오지 않는다. 본 실험은 chi2 선별을 매 fold 내부에서 수행한다.
- 연결: M06, M07

### P04. [A machine learning framework to trace tumor tissue-of-origin of 13 types of cancer based on DNA somatic mutation](https://doi.org/10.1016/j.bbadis.2020.165916)

2020 · He B · 검토 범위: 초록

- 내용: ICGC의 변이량을 유전자 길이로 정규화한 표현과 RF를 평가했다.
- 참고·적용: 유전자 존재 여부 외에 이벤트 수와 관측 변이량을 보존한다.
- 미적용·한계: 실제 유전자 길이·시퀀싱 영역이 없으므로 길이 정규화를 재현하지 않는다. 관측 최대 AA 위치를 유전자 길이로 쓰거나 변이 수를 TMB/Mb라고 부르지 않는다.
- 연결: M02, X02

### P05. [Using the "Hidden" genome to improve classification of cancer types](https://doi.org/10.1111/biom.13367)

2021 · Chakraborty S · 검토 범위: 초록 + PMC 검색 색인에 제공된 Model / Prediction / CV 본문

- 내용: 새 환자의 미관측 희귀 변이를 유전자·염기 문맥 메타특징으로 연결하고, 변이 고유 효과를 계층적으로 추정한다.
- 참고·적용: 정확한 변이 residual과 유전자·유형·AA 변화 메타특징을 함께 두어 희귀·미관측 변이도 공유 특징에 남게 한다.
- 미적용·한계: group-lasso 혼합효과 모델의 재현은 아니다. df/(df+5) 감쇠는 자체 휴리스틱이며 염기 문맥 대신 단백질 수준의 가능한 메타특징만 사용한다.
- 연결: M03, X01

### P06. [CPEM: Accurate cancer type classification based on somatic alterations using an ensemble of a random forest and a deep neural network](https://doi.org/10.1038/s41598-019-53034-3)

2019 · Lee K · 검토 범위: 초록 + Experimental setup / Feature Construction 절

- 내용: CPEM은 유전자별 변이 개수와 여러 genomic 특징을 비교하고 inner/outer CV를 분리했다.
- 참고·적용: 유전자별 다중 이벤트를 무조건 1로만 축약하지 않고, 전처리 선택은 inner 그룹 CV에 넣는다.
- 미적용·한계: CNV·SBS와 RF+DNN 전체를 재현하지 않는다. 본 실험의 주 평가치는 고정 LR의 nested 전처리 선택 과정이며 트리는 별도 대조다.
- 연결: M02, M06

### P07. [Predicting cancer type from tumour DNA signatures](https://doi.org/10.1186/s13073-017-0493-2)

2017 · Soh KP · 검토 범위: 초록 + Methods 절

- 내용: 돌연변이만 쓰는 경우와 copy-number를 함께 쓰는 경우의 성능 차이를 보고했다.
- 참고·적용: 정보 종류의 한계를 명시하고, 단순 로지스틱·트리 기준선을 남긴다.
- 미적용·한계: 다른 암종 수와 accuracy 결과를 현재 26종 Macro F1의 이론적 상한으로 해석하지 않는다. 없는 CNV를 WT 표기로부터 추정하지 않는다.
- 연결: M07, X01

### P08. [Development of Genome-Derived Tumor Type Prediction to Inform Clinical Cancer Care](https://doi.org/10.1001/jamaoncol.2019.3985)

2020 · Penson A · 검토 범위: 구조화 초록

- 내용: 임상 패널의 분자 변이와 유도 특징을 결합하고 별도 외부 코호트에서 평가했다.
- 참고·적용: 임상 확률과 모델 점수를 구분하고, 반복 재분할을 독립 외부 검증이라고 부르지 않는다.
- 미적용·한계: 외부 환자 데이터·임상 패널·signature·calibration을 가져오지 않았다. 본 데이터의 새로운 임상 성능을 주장하지 않는다.
- 연결: M06, X01

### P09. [Mutation-Attention (MuAt): deep representation learning of somatic mutations for tumour typing and subtyping](https://doi.org/10.1186/s13073-023-01204-4)

2023 · Sanjaya P · 검토 범위: 초록 + Preparing MuAt inputs / Evaluating MuAt in sparse data 절

- 내용: 개별 변이의 문맥·위치·주석을 attention 입력으로 사용하며 희소 변이 조건도 평가한다.
- 참고·적용: 원문 변이 토큰과 구조화 속성을 함께 보존하고 변이량에 따른 EDA를 한다.
- 미적용·한계: DNA 3-mer와 유전체 위치가 없어 MuAt attention 입력은 만들 수 없다. 단백질 위치 bin은 자체 특징이지 논문 1 Mb genomic bin이 아니다.
- 연결: M01, M03, X01

### P10. [Cancer classification and pathway discovery using non-negative matrix factorization](https://doi.org/10.1016/j.jbi.2019.103247)

2019 · Zeng Z · 검토 범위: 초록

- 내용: 유전자 수준으로 변이를 모으고 nsNMF와 SVM을 결합했다. 평가한 설정에서는 count 표현이 annotation score 표현보다 나았다.
- 참고·적용: 유전자별 event count를 별도 특징으로 남기고 annotation 점수를 가짜로 만들지 않는다.
- 미적용·한계: NMF/SVM 파이프라인과 SIFT·PolyPhen·CADD 점수는 구현하지 않았다. 4개 암종의 결과를 현재 과제와 직접 비교하지 않는다.
- 연결: M02, X03

### P11. [Network-based stratification of tumor mutations](https://doi.org/10.1038/nmeth.2651)

2013 · Hofree M · 검토 범위: 초록 + Processing of patient mutation profiles / Network smoothing 절

- 내용: 유전자 변이 신호를 외부 네트워크에 확산하고 NMF·consensus clustering으로 아형을 찾는다.
- 참고·적용: 희귀한 개별 유전자 신호를 묶는 관점을 참고하되, 본 구현은 명시적 문헌 유전자 패널 합계로만 제한한다.
- 미적용·한계: PPI·random-walk·NBS를 재현하지 않았다. 원문의 저변이 환자 제외를 따라하지 않고 모든 개발 환자를 평가한다.
- 연결: M04, EDA-burden, X04

### P12. [pyNBS: a Python implementation for network-based stratification of tumor mutations](https://doi.org/10.1093/bioinformatics/bty186)

2018 · Huang JK · 검토 범위: 초록

- 내용: pyNBS는 NBS 단계를 모듈화하고 네트워크·파라미터 재현성을 다룬다.
- 참고·적용: 파서·특징·학습·검증을 분리하고 고정 설정 및 출처를 노트북과 JSON에 기록한다.
- 미적용·한계: Python 2.7 소프트웨어나 외부 네트워크를 설치·재현한 것이 아니다.
- 연결: M06, X04

### P13. [Network-based stratification analysis of 13 major cancer types using mutations in panels of cancer genes](https://doi.org/10.1186/1471-2164-16-s7-s7)

2015 · Zhong X · 검토 범위: 초록

- 내용: 선별된 유전자 패널을 이용한 NBS가 조직 내 아형화에 유용할 수 있음을 비교했다.
- 참고·적용: 모든 exact 변이를 동일하게 쓰는 것과 작고 고정된 문헌 패널을 추가하는 것을 구분해 평가한다.
- 미적용·한계: FoundationOne 등 저자의 패널을 복제하지 않았고, 조직 내 군집화 결과가 26종 supervised 분류 향상을 보장하지 않는다.
- 연결: M04, X04

### P14. [Oncogenic Signaling Pathways in The Cancer Genome Atlas](https://doi.org/10.1016/j.cell.2018.03.035)

2018 · Sanchez-Vega F · 검토 범위: 초록 + PubMed 원문 도식 설명

- 내용: 10개 신호 경로의 변화를 mutation·CNV·발현·fusion·methylation으로 함께 조사했다.
- 참고·적용: 변이 유전자들을 묶는 생물학적 사전지식을 실험하되, 실제 구현 목록은 각 TCGA 논문에서 뽑은 작은 패널로 명시한다.
- 미적용·한계: 저자의 완전한 경로 유전자집합이나 경로 활성도를 구현하지 않았다. 변이 0개가 곧 경로 비활성이라는 뜻이 아니다.
- 연결: M04, X01

### P15. [The Cancer Genome Atlas Pan-Cancer analysis project](https://doi.org/10.1038/ng.2764)

2013 · Cancer Genome Atlas Research Network · 검토 범위: 초록

- 내용: Pan-Cancer는 여러 조직과 분자 층위의 공통점·차이를 함께 분석하는 틀을 제시한다.
- 참고·적용: 암종별 EDA와 암종 간 중첩을 함께 보고, 외부 코호트와 현재 라벨 정의를 구분한다.
- 미적용·한계: 본 CSV가 논문의 원본 코호트와 동일하다고 가정하지 않고 STES·GBMLGG·KIPAN 라벨을 임의 재매핑하지 않는다.
- 연결: EDA-taxonomy

### P16. [Comprehensive Characterization of Cancer Driver Genes and Mutations](https://doi.org/10.1016/j.cell.2018.02.060)

2018 · Bailey MH · 검토 범위: 초록

- 내용: 여러 driver 탐지 알고리즘과 구조·서열 근거를 통합해 cancer driver 후보를 정리했다.
- 참고·적용: 흔한 변이·gene support와 driver 판정을 혼동하지 않도록 EDA 해석을 제한한다.
- 미적용·한계: 299개 목록을 불러오지 않았으며, 특정 유전자에서 발생한 모든 변이를 driver 또는 병적 변이로 단정하지 않는다.
- 연결: EDA-driver, X03

### P17. [Mutational heterogeneity in cancer and the search for new cancer-associated genes](https://doi.org/10.1038/nature12213)

2013 · Lawrence MS · 검토 범위: 초록 + mutation heterogeneity / Methods Summary 발췌

- 내용: 유전자·암종별 배경 변이율의 이질성이 빈도 기반 driver 탐지의 거짓 양성을 만들 수 있다.
- 참고·적용: 변이량의 긴 꼬리와 암종별 차이를 점검하고, 행 정규화로 변이량을 지우지 않는다.
- 미적용·한계: MutSigCV의 발현·복제 시점·배경 공변량이 없어 그 알고리즘은 구현하지 않았다. TTN 같은 유전자를 자동 제거하거나 germline으로 단정하지 않는다.
- 연결: M02, EDA-driver

### P18. [Discovery and saturation analysis of cancer genes across 21 tumour types](https://doi.org/10.1038/nature12912)

2014 · Lawrence MS · 검토 범위: 초록

- 내용: 암종과 빈도에 따라 driver 탐지에 필요한 표본 수와 포화 양상이 다름을 분석했다.
- 참고·적용: 희귀 암종의 학습 환자 수와 불확실성을 명시하고 6천 환자에서 높은 점수를 보장하지 않는다.
- 미적용·한계: 논문의 표본 수 추정치를 이 과제의 절대 최소 요건이나 성능 상한으로 사용하지 않는다.
- 연결: EDA-sample, M06

### P19. [Mutational landscape and significance across 12 major cancer types](https://doi.org/10.1038/nature12634)

2013 · Kandoth C · 검토 범위: 초록

- 내용: 12개 암종에서 유전자·변이 종류·문맥과 조직 특이성 및 공유성을 조사했다.
- 참고·적용: 변이 종류와 유전자 공유 양상을 암종별로 비교하고 gene/type 특징군을 분리한다.
- 미적용·한계: 127개 유전자 목록을 전부 가져오지 않았고 조직 특이성을 단일 마커의 확정 진단 규칙으로 쓰지 않는다.
- 연결: M02, EDA-marker

### P20. [Universal Patterns of Selection in Cancer and Somatic Tissues](https://doi.org/10.1016/j.cell.2017.09.042)

2017 · Martincorena I · 검토 범위: 초록

- 내용: 선택압을 정량화하며 같은 유전자 안에서도 driver와 passenger 비중이 다를 수 있음을 보여준다.
- 참고·적용: 동의/비동의/stop 관련 표기 채널을 나누되 기능 판정과 분리한다.
- 미적용·한계: 기회 수와 염기 문맥이 없어 dN/dS를 계산하지 않는다. 단순 비동의/동의 개수 비율을 dN/dS나 selection coefficient라고 부르지 않는다.
- 연결: M02, X03

### P21. [Signatures of mutational processes in human cancer](https://doi.org/10.1038/nature12477)

2013 · Alexandrov LB · 검토 범위: 초록

- 내용: 대규모 염기 치환 문맥에서 여러 암에 공유되거나 특정 암에 치우친 mutational signature를 추정했다.
- 참고·적용: 관측 변이 종류의 분포는 보존하지만, 입력에 없는 DNA 문맥은 추정하지 않는다.
- 미적용·한계: AA 치환으로 SBS signature·흡연·자외선·APOBEC 노출을 만들지 않는다.
- 연결: X01, EDA-format

### P22. [The repertoire of mutational signatures in human cancer](https://doi.org/10.1038/s41586-020-1943-3)

2020 · Alexandrov LB · 검토 범위: 초록

- 내용: SBS·DBS·군집 치환·indel signature를 많은 WGS/WES에서 구분했다.
- 참고·적용: 같은 '변이 수'라도 정보 해상도가 다름을 문서화하고 표기 수준 특징이라고 명명한다.
- 미적용·한계: 단백질 표기만으로 COSMIC signature, MSI, DNA 복구 결함을 판정하지 않는다.
- 연결: X01, X03

### P23. [Pan-cancer analysis of whole genomes](https://doi.org/10.1038/s41586-020-1969-6)

2020 · ICGC/TCGA Pan-Cancer Analysis of Whole Genomes Consortium. · 검토 범위: 초록

- 내용: PCAWG는 matched-normal을 포함한 WGS로 coding 외 다양한 변이와 종양 진화를 분석했다.
- 참고·적용: 이미 가공된 CSV에서 확인할 수 없는 입력·실험 조건을 가용성 표에 명시한다.
- 미적용·한계: 정상 대조군·VCF·coverage가 없으므로 somatic/germline 재판정이나 구조변이 분석을 했다고 쓰지 않는다.
- 연결: EDA-availability, X01

### P24. [The COSMIC Cancer Gene Census: describing genetic dysfunction across all human cancers](https://doi.org/10.1038/s41568-018-0060-1)

2018 · Sondka Z · 검토 범위: 초록

- 내용: 2018 CGC는 근거 수준을 검토한 cancer gene 지식자원과 tier를 설명한다.
- 참고·적용: 일반적인 빈도와 전문가의 driver 근거가 다른 개념임을 구분한다.
- 미적용·한계: CGC 전체나 최신 목록을 다운로드하지 않았다. 논문의 2018년 유전자 수를 현재 자원 크기로 제시하지 않는다.
- 연결: EDA-driver, X03

### P25. [Comprehensive molecular portraits of human breast tumours](https://doi.org/10.1038/nature11412)

2012 · Cancer Genome Atlas Network. · 검토 범위: 초록

- 내용: 유방암의 분자적 이질성과 일부 난소암과의 공통점, TP53·PIK3CA·GATA3 등의 변이를 보고했다.
- 참고·적용: 명시된 유전자 부분집합으로 P25 패널을 만들고 BRCA/OV 공유 마커를 EDA한다.
- 미적용·한계: 발현 기반 유방 아형을 이 CSV에서 복원하거나 공유 변이를 라벨 오류로 단정하지 않는다.
- 연결: M04, EDA-taxonomy

### P26. [Comprehensive molecular characterization of human colon and rectal cancer](https://doi.org/10.1038/nature11252)

2012 · Cancer Genome Atlas Network. · 검토 범위: 초록

- 내용: 대장·직장암에서 hypermutation과 APC·TP53·SMAD4·PIK3CA·KRAS 등 여러 변이를 함께 분석했다.
- 참고·적용: P26 패널과 관측 변이량의 암종별 분포를 비교한다.
- 미적용·한계: 높은 변이량만으로 MSI를 확정하거나 논문의 hypermutation 비율·암종 비율을 예측에 강제로 적용하지 않는다.
- 연결: M02, M04

### P27. [Comprehensive, Integrative Genomic Analysis of Diffuse Lower-Grade Gliomas](https://doi.org/10.1056/nejmoa1402121)

2015 · Cancer Genome Atlas Research Network · 검토 범위: 구조화 초록

- 내용: IDH·TP53·ATRX와 1p/19q 등 다중 플랫폼 정보로 저등급 교종의 분자적 구분을 조사했다.
- 참고·적용: P27 패널로 gene-level 공유와 LGG/GBMLGG 혼동을 살펴본다. IDH는 IDH1/IDH2로 명시적으로 풀어 쓴다.
- 미적용·한계: 1p/19q codeletion을 변이 목록에서 추정하지 않는다. 현재 두 라벨의 임상 정의를 알 수 없어 합치거나 다시 붙이지 않는다.
- 연결: M04, EDA-taxonomy

### P28. [Molecular Profiling Reveals Biologically Discrete Subsets and Pathways of Progression in Diffuse Glioma](https://doi.org/10.1016/j.cell.2015.12.028)

2016 · Ceccarelli M · 검토 범위: 초록

- 내용: 등급을 가로지르는 diffuse glioma의 분자적 이질성과 진행 관련 집단을 분석했다.
- 참고·적용: LGG와 더 넓은 glioma 명칭의 관계를 데이터 사전 확인 항목으로 남긴다.
- 미적용·한계: 논문을 근거로 환자의 등급·예후를 생성하거나 제공된 암종을 교정하지 않는다.
- 연결: EDA-taxonomy, X01

### P29. [The somatic genomic landscape of glioblastoma](https://doi.org/10.1016/j.cell.2013.09.034)

2013 · Brennan CW · 검토 범위: 초록

- 내용: GBM에서 EGFR·PDGFRA 등의 변이 외에 rearrangement·promoter·methylation 등 다양한 정보를 다룬다.
- 참고·적용: 현재 관측 가능한 EGFR/PDGFRA의 작은 P29 패널만 추가한다.
- 미적용·한계: HGVSp로 EGFR 증폭·fusion·TERT promoter·MGMT methylation을 추정하지 않는다.
- 연결: M04, X01

### P30. [Comprehensive molecular characterization of clear cell renal cell carcinoma](https://doi.org/10.1038/nature12222)

2013 · Cancer Genome Atlas Research Network. · 검토 범위: 초록

- 내용: clear-cell RCC에서 VHL 및 chromatin 관련 유전자와 다른 분자 층위를 함께 분석했다.
- 참고·적용: VHL·PBRM1·SETD2·ARID1A·SMARCA4의 P30 패널을 EDA와 실험 특징으로 사용한다.
- 미적용·한계: KIPAN을 KIRC로 바꾸거나 유전자 하나로 조직형을 확정하지 않는다. 패널은 완전한 pathway annotation이 아니다.
- 연결: M04, EDA-taxonomy

### P31. [Comprehensive Molecular Characterization of Papillary Renal-Cell Carcinoma](https://doi.org/10.1056/nejmoa1505917)

2016 · Cancer Genome Atlas Research Network · 검토 범위: 구조화 초록

- 내용: papillary RCC에서 MET·SETD2·FH와 CNV·fusion·methylation 등 여러 차이를 보고했다.
- 참고·적용: 직접 변이로 관측 가능한 세 유전자만 P31 부분집합으로 사용한다.
- 미적용·한계: CDKN2A silencing·TFE3 fusion·CIMP·NRF2 발현을 mutation table로부터 생성하지 않는다.
- 연결: M04, X01

### P32. [Integrated genomic analyses of ovarian carcinoma](https://doi.org/10.1038/nature10166)

2011 · Cancer Genome Atlas Research Network. · 검토 범위: 초록

- 내용: 고등급 장액성 난소암의 TP53 및 소수 재발 변이와 copy-number·발현·methylation 이질성을 분석했다.
- 참고·적용: P32 변이 유전자 부분집합과 BRCA/OV 사이 공통점을 비교한다.
- 미적용·한계: 본 CSV의 OV가 같은 조직형이라고 단정하거나 논문의 TP53 빈도를 강제 정답 규칙으로 사용하지 않는다.
- 연결: M04, EDA-taxonomy

### P33. [Integrated genomic characterization of endometrial carcinoma](https://doi.org/10.1038/nature12113)

2013 · Cancer Genome Atlas Research Network · 검토 범위: 초록

- 내용: 자궁내막암의 POLE·MSI·copy-number 관련 다층적 분류와 다른 암과의 공유 특징을 제시했다.
- 참고·적용: P33 패널과 변이량·종결/frameshift 표기를 따로 본다.
- 미적용·한계: POLE 변이나 많은 변이 수를 곧바로 POLE subtype·MSI·copy-number high/low로 표시하지 않는다.
- 연결: M02, M04, X01

### P34. [Integrated genomic characterization of papillary thyroid carcinoma](https://doi.org/10.1016/j.cell.2014.09.050)

2014 · Cancer Genome Atlas Research Network. · 검토 범위: 초록; DOI와 제목을 별도 대조해 수정

- 내용: papillary thyroid carcinoma에서 낮은 변이 빈도와 BRAF·EIF1AX·PPM1D·CHEK2 및 다른 분자 정보를 조사했다.
- 참고·적용: 명시된 네 유전자의 P34 패널과 저변이 환자 분포를 비교한다.
- 미적용·한계: 처음 입력한 DOI가 다른 논문에 연결되어 제외·교체했다. 최종 DOI는 10.1016/j.cell.2014.09.050이며 잘못 연결된 논문은 50편에 세지 않는다.
- 연결: M04, EDA-burden

### P35. [The Molecular Taxonomy of Primary Prostate Cancer](https://doi.org/10.1016/j.cell.2015.10.025)

2015 · Cancer Genome Atlas Research Network. · 검토 범위: 초록

- 내용: 전립선암을 SPOP·FOXA1·IDH1 변이 또는 일부 fusion을 바탕으로 분자적으로 구분했다.
- 참고·적용: 현재 CSV가 관측할 수 있는 세 mutation gene만 P35 패널로 사용한다.
- 미적용·한계: ERG/ETV/FLI1의 gene 변이를 fusion 양성으로 간주하지 않는다. 저변이 환자를 자동 PRAD로 보내지 않는다.
- 연결: M04, EDA-burden, X01

### P36. [Comprehensive molecular profiling of lung adenocarcinoma](https://doi.org/10.1038/nature13385)

2014 · Cancer Genome Atlas Research Network. · 검토 범위: 초록

- 내용: 폐선암에서 EGFR·RBM10·RIT1·MGA 등과 다른 플랫폼의 특이성을 함께 보고했다.
- 참고·적용: 초록에서 명시한 mutation gene의 P36 부분집합을 비교한다.
- 미적용·한계: 성별·흡연·단백질 경로 활성을 gene 변이로 생성하거나 splice skipping을 확정하지 않는다.
- 연결: M04, X01

### P37. [Comprehensive genomic characterization of squamous cell lung cancers](https://doi.org/10.1038/nature11404)

2012 · Cancer Genome Atlas Research Network. · 검토 범위: 초록

- 내용: 폐 편평암에서 TP53과 NFE2L2/KEAP1·CDKN2A/RB1 등의 여러 변화가 관측됐다.
- 참고·적용: P37 패널로 공유 유전자들과 변이 종류를 함께 본다.
- 미적용·한계: 유전자 변이가 곧 모든 copy-number·pathway 활성 변화를 포괄하지 않으며 TP53 하나를 특정 암 확정자로 쓰지 않는다.
- 연결: M04, X01

### P38. [Genomic Classification of Cutaneous Melanoma](https://doi.org/10.1016/j.cell.2015.05.044)

2015 · Cancer Genome Atlas Network. · 검토 범위: 초록

- 내용: 피부 흑색종을 BRAF/RAS/NF1와 Triple-WT 등으로 구분하며 mutation 외 정보도 비교했다.
- 참고·적용: P38 패널을 사용한다. 본 구현에서 RAS를 NRAS/HRAS/KRAS로 명시적으로 펼친 것은 작은 수동 사전지식이다.
- 미적용·한계: CSV에서 세 유전자 변이가 없다는 이유로 임상 Triple-WT 아형을 확정하지 않는다.
- 연결: M04, EDA-marker

### P39. [Comprehensive molecular characterization of gastric adenocarcinoma](https://doi.org/10.1038/nature13480)

2014 · Cancer Genome Atlas Research Network. · 검토 범위: 초록

- 내용: 위선암의 EBV·MSI·genomic-stable·chromosomal-instability 집단과 관련 변화를 분석했다.
- 참고·적용: 현재 확인 가능한 PIK3CA/RHOA 변이만 P39 패널에 포함한다.
- 미적용·한계: EBV 상태·MSI·염색체 불안정성을 단백질 변이에서 추정하지 않는다. STES를 논문 STAD와 동일 라벨로 취급하지 않는다.
- 연결: M04, EDA-taxonomy, X01

### P40. [Comprehensive genomic characterization of head and neck squamous cell carcinomas](https://doi.org/10.1038/nature14129)

2015 · Cancer Genome Atlas Network. · 검토 범위: 초록

- 내용: 두경부암에서 HPV·흡연 관련 집단을 포함한 이질성과 여러 mutation gene을 보고했다.
- 참고·적용: 초록에 제시된 mutation gene들의 P40 부분집합을 비교한다.
- 미적용·한계: TP53/PIK3CA 등으로 HPV·흡연·인구학 정보를 확정하거나 가짜 임상 변수를 만들지 않는다.
- 연결: M04, X01

### P41. [ANNOVAR: functional annotation of genetic variants from high-throughput sequencing data](https://doi.org/10.1093/nar/gkq603)

2010 · Wang K · 검토 범위: 초록 + Gene-based annotation 절

- 내용: ANNOVAR는 유전체 참조·유전자/전사체 정의를 바탕으로 변이 기능을 주석화하고 여러 isoform을 구분한다.
- 참고·적용: 원문과 파싱 결과를 나눠 저장하고 해석 불가·불완전·참조 정보 누락을 표시한다.
- 미적용·한계: 유전체 좌표·assembly·transcript가 없으므로 ANNOVAR를 실제 실행하지 않았고, AA 위치를 임의로 이동해 같은 변이로 합치지 않는다.
- 연결: M01, X03

### P42. [The Ensembl Variant Effect Predictor](https://doi.org/10.1186/s13059-016-0974-4)

2016 · McLaren W · 검토 범위: 초록 + Transcript annotation / Protein annotation 절

- 내용: VEP는 전사체와 참조 assembly를 맞추고 여러 기능·단백질 주석 및 예측 도구를 연결한다.
- 참고·적용: 단백질 위치와 DNA 위치를 구분하고, 정보 가용성을 필드 단위로 기록한다.
- 미적용·한계: 동일 gene의 AA 위치만으로 단일 genomic variant·isoform을 정하지 않는다. VEP·domain·보존성 점수를 계산하지 않았다.
- 연결: M01, X03

### P43. [HGVS Recommendations for the Description of Sequence Variants: 2016 Update](https://doi.org/10.1002/humu.22981)

2016 · den Dunnen JT · 검토 범위: 초록 + 출판사 본문의 Reference Sequences / Existing Standards / Modifications 절

- 내용: 변이 기술의 참조·불확실성·표기 구분을 명확히 한다. X의 역사적 stop 용법과 현재 unknown-AA 의미, fs 뒤 종료 거리의 의미도 구분한다.
- 참고·적용: stop retained/gained/lost, 대문자 AA 서열과 fs, 불완전 표기·괄호 불확실성을 구분하고 원문을 유지한다.
- 미적용·한계: 완전한 HGVS validator나 reference-aware 3′ normalization이 아니다. legacy range는 길이가 맞을 때만 성분 속성을 추출하고 독립 사건 여러 개로 단정하지 않는다.
- 연결: M01

### P44. [A general framework for estimating the relative pathogenicity of human genetic variants](https://doi.org/10.1038/ng.2892)

2014 · Kircher M · 검토 범위: 초록

- 내용: CADD는 다수 기능 주석과 학습 대비군을 결합해 variant 단위 상대적 점수를 만든다.
- 참고·적용: 단순 유형 코드를 기능 점수로 오인하지 않도록 미가용 특징 표에 명시한다.
- 미적용·한계: ref/alt DNA·assembly와 필요한 주석이 없어 CADD를 계산하지 않는다. missense/fs에 임의 점수를 부여해 CADD라고 부르지 않는다.
- 연결: X03

### P45. [A method and server for predicting damaging missense mutations](https://doi.org/10.1038/nmeth0410-248)

2010 · Adzhubei IA · 검토 범위: 초록 없음; PMC에 공개된 편집자서신 본문 검토

- 내용: PolyPhen-2는 단백질 서열·구조와 상동서열 정렬 특징을 이용해 missense 영향 가능성을 추정한다.
- 참고·적용: AA 치환 기록과 생물학적 기능 영향 예측을 구분한다.
- 미적용·한계: 서열 정렬·구조·정확한 참조 단백질 정보가 없어 PolyPhen-2를 실행하지 않는다. AA 치환 종류를 damaging score로 바꾸지 않는다.
- 연결: X03

### P46. [SIFT: Predicting amino acid changes that affect protein function](https://doi.org/10.1093/nar/gkg509)

2003 · Ng PC · 검토 범위: 초록

- 내용: SIFT는 단백질 치환의 기능 영향 가능성을 구별하는 도구다.
- 참고·적용: 미지 변이도 AA 메타특징에는 남기되 기능적 해로움을 확정하지 않는다.
- 미적용·한계: 필요한 참조 서열과 상동성 정보를 준비하지 않았으므로 SIFT 점수를 만들지 않는다.
- 연결: M03, X03

### P47. [Selection bias in gene extraction on the basis of microarray gene-expression data](https://doi.org/10.1073/pnas.102102699)

2002 · Ambroise C · 검토 범위: 초록

- 내용: gene selection을 CV 밖에서 수행하면 오류 추정이 낙관적으로 바뀔 수 있음을 보여준다.
- 참고·적용: DF·어휘·chi2·스케일을 매 inner/outer 학습 부분에서 다시 적합한다.
- 미적용·한계: 개발 전체에서 한 번 선별한 목록을 모든 fold에 공통 적용하지 않는다. label-conflict 환자를 정답 오류라고 임의로 제거하지 않는다.
- 연결: M06

### P48. [Bias in error estimation when using cross-validation for model selection](https://doi.org/10.1186/1471-2105-7-91)

2006 · Varma S · 검토 범위: 초록 + Nested CV 절

- 내용: CV로 최적화한 설정의 같은 CV 점수를 최종 성능으로 쓰면 선택 편향이 생기며 nested CV가 이를 줄인다.
- 참고·적용: inner 그룹 CV가 전처리 view를 선택하고 outer 그룹 CV가 선택 과정을 평가하게 한다.
- 미적용·한계: 개별 outer view 중 최고 점수는 탐색적 결과로 표시한다. 이미 반복 관측한 데이터에서 모든 연구자 편향이 사라졌다고 주장하지 않는다.
- 연결: M06

### P49. [On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation](https://www.jmlr.org/papers/v11/cawley10a.html)

2010 · Gavin C. Cawley; Nicola L. C. Talbot · 검토 범위: JMLR 출판사 초록

- 내용: 유한한 검증 표본에서 모델 선택 기준 자체에 과적합할 수 있고 알고리즘 간 작은 차이가 선택 편향보다 작을 수 있다.
- 참고·적용: 적은 고정 비교군, 선택 과정과 탐색 최대값의 분리, 과거 반복 검증의 한계를 기록한다.
- 미적용·한계: 새 seed를 새로운 환자 코호트라 부르지 않고 최고점만 골라 성능 개선이라고 선언하지 않는다.
- 연결: M06

### P50. [Leakage and the reproducibility crisis in machine-learning-based science](https://doi.org/10.1016/j.patter.2023.100804)

2023 · Kapoor S · 검토 범위: 초록 + leakage taxonomy 중 L1/중복·전처리·선별 관련 본문

- 내용: 학습/평가 혼합, 전체 데이터 전처리·선별, 중복과 부적절한 proxy가 재현 불가능한 결과를 만들 수 있음을 정리한다.
- 참고·적용: test/sample open 차단, ID 제외, raw/canonical 그룹 검사, 전처리 fit 범위와 데이터 가용성·캐시 출처를 기록한다.
- 미적용·한계: 과거 test EDA와 반복된 홀드아웃 관찰의 영향을 이번 조치로 소급 제거했다고 주장하지 않는다.
- 연결: M06, EDA-availability


## 사용자 승인 후속 제출 추론 기록

2026-11-10 사용자 요청으로 저장 모델의 최종 test 추론을 수행해 제출 CSV를 생성했습니다. 앞의 test 미사용 기록은 학습·선별·검증 단계이며, 이번 추론에서 모델·파라미터를 변경하지 않았습니다. 상세 파일명과 검증은 [CSV 내보내기 기록](SUBMISSION_EXPORT_MANIFEST.md)을 따릅니다. 대회 자동 제출이나 Public 점수 확인은 하지 않았습니다.
