# 🧬 암 유전체 기반 머신러닝 모델의 특징 추출(Feature Engineering) 가이드

본 문서는 암 유전체 분석 및 암종 분류 머신러닝 모델링 과정에서 사용되는 **종양 돌연변이 부담(TMB)**, **변이 유형별 정량화**, **드라이버 변이의 위치적 특성(핫스팟/인프레임)**, 그리고 **유전자 동반 변이 조합(Co-mutation Pattern)** 등의 전처리 및 특징 추출 기법을 정리한 자료입니다.

---

## 1. 종양 돌연변이 부담 (TMB, Tumor Mutational Burden)

### 개념
- **정의**: 암 환자의 유전체 **1메가베이스(Mb) 당 발생하는 돌연변이의 총 개수**를 의미합니다.
- **분석 내용**:
  - **총 변이 유전자 수 및 로그 변환**: 환자 간 변이 개수의 편차가 극심함(최소 수개 ~ 최대 수천 개)에 따라, 모델이 데이터의 스케일에 편향되지 않고 안정적으로 학습할 수 있도록 로그 변환(Log Transformation) 수치를 함께 산출하여 스케일을 조절합니다.
  - **전체 이벤트 수**: 해당 환자 샘플에서 발생한 전체 변이 건수의 총합입니다.

---

## 2. 변이 유형별 개수 및 비율 (Variant Types & Ratios)

유전자에 발생한 돌연변이가 단백질 구조 및 염기서열 변화에 미치는 영향을 분류하고, 각 유형별 **발생 건수** 및 **전체 이벤트 대비 비율(%)**을 정량 피처로 생성합니다.

| 변이 유형 (Variant Type) | 성격 및 생물학적 특징 |
| :--- | :--- |
| **Missense (미스센스 변이)** | 단일 염기 변화로 인해 단백질을 구성하는 **아미노산 종류가 변경**되는 변이입니다. |
| **Silent (침묵 변이)** | 염기는 변했으나 **최종 아미노산은 변하지 않아** 단백질 기능에 영향을 주지 않는 변이입니다. |
| **Nonsense (널센스/종결 변이)** | 중간에 **조기 종결 코돈(Stop Codon)**이 형성되어 단백질 합성이 중간에 끊어지는 변이입니다. |
| **Frameshift (프레임시프트 변이)** | 염기의 삽입/결실로 **읽기 프레임(Reading Frame)이 밀려** 전혀 다른 아미노산 서열이 생성되는 변이입니다. |
| **Inframe (인프레임 변이)** | 염기가 3의 배수 단위로 삽입/결실되어 **프레임은 유지된 채** 일부 아미노산만 증감하는 변이입니다. |

---

## 3. 핫스팟 (Hotspot) 및 위치 기반 변이 특징

드라이버 변이의 핵심 위치 정보와 돌연변이의 세부 성격을 인공지능이 직관적으로 인식하도록 **이진 피처(Binary Feature: 0 또는 1)**로 변환하는 단계입니다.

### 1) 핫스팟 및 절단형 변이 (`hs_*`)
* **핫스팟 (Hotspot)**
  * 특정 발암 유전자(Oncogene) 내에서 돌연변이가 유독 빈번하게 발생하는 결정적인 아미노산 위치입니다.
  * *예시:* 흑색종/대장암의 대표 드라이버 변이인 `BRAF|V600` (BRAF 유전자의 600번째 아미노산 변이)
  * *목적:* 해당 위치 변이 발생 여부를 이진 피처(0/1)로 생성하여 강한 발암 신호를 모델에 직접 주입합니다.
* **절단형 (Truncating) 변이**
  * Nonsense, Frameshift 등 단백질 중간을 불완전하게 끝맺어 기능을 무력화하는 변이입니다. 주요 종양억제유전자(TSG)의 기능 상실 패턴을 포착합니다.

### 2) 인프레임 변이의 위치 세분화 (`gene|위치_inframe`)
* 단순 "어느 유전자에 인프레임 변이가 발생했다"는 추상적 정보에 그치지 않고, **"어느 유전자의 정확히 몇 번째 아미노산 위치에서 일어났는지"** 구조화(`gene|위치_inframe`)하는 기법입니다.
* 인프레임 변이는 단백질의 특정 구조적 도메인(Functional Domain)에 집중되는 경향이 강하므로, 위치 단위로 정밀 분할할 때 암종별 특이적 구조 변형 패턴 식별 정확도가 크게 상승합니다.

---

## 4. 유전자 동반 변이 조합 (Co-mutation Pattern)

특정 암종 진단의 결정적 기준이 되는 **유전자 간의 동반 변이 조합 패턴**을 족집게 형태의 맞춤형 이진 피처로 주입하는 고급 엔지니어링 기법입니다.

### 1) 동반변이 콤보 피처 (`cb_*`)
* **개념**: 암 조직 발생/진화 시 두 개 이상의 유전자가 동시에 변이되는 현상은 특정 암종만의 고유한 발암 시그니처(Signature)가 됩니다.
* **의도**: 각 유전자 변이를 독립적으로 보지 않고 `"유전자 A와 유전자 B가 동시에 변이되었는가?"`를 묶어 콤보 변수(`cb_*`)로 제공함으로써 암종 분류 성능을 극대화합니다.

### 2) 대표적인 생물학적 예시
* **대장암 (Colorectal Cancer)**: `APC` 유전자의 절단형 변이와 `TP53` 변이가 동시에 출현하는 조합 (전형적인 Adenoma-Carcinoma Sequence 경로 대변)
* **신장암 (Renal Cell Carcinoma)**: 투명세포신장암(ccRCC)에서 관찰되는 `VHL` 유전자 불활성화와 염색체 3p 구역 내 `PBRM1` 유전자의 동반 변이 조합

---

## 💡 요약 및 종합 정리

> **핵심 요약**
> 1. **TMB 및 정량 비율 분석**: 환자별 전체 변이 규모(TMB)와 변이가 단백질 기능에 미친 영향(Missense, Nonsense 등 비율)을 계산해 전체적인 유전체 불안정성 스케일을 조절·입력합니다.
> 2. **위치 및 구조적 정밀화**: 발암 핫스팟(`hs_*`)과 인프레임 위치(`gene|위치_inframe`)를 세부 이진 피처화하여 미세한 암종별 도메인 구조 변형을 모델이 학습하도록 돕습니다.
> 3. **의학 가이드 기반 콤보 변수**: 문헌적 근거(도메인 지식)를 기반으로 유전자 동반 변이 패턴(`cb_*`)을 정의해 명확한 암종 구분 신호를 직접 주입합니다.

---

## 📚 참고 문헌 및 출처 (References)

### TMB & 변이 유형 분석
* [JAMA Oncology - TMB Clinical Utility](https://jamanetwork.com/journals/jamaoncology/fullarticle/2755639)
* [Nature Communications - Mutational Signatures](https://www.nature.com/articles/s41467-019-13825-8)
* [PubMed - Martincorena et al. (2017) Universal patterns of selection in cancer genomes](https://pubmed.ncbi.nlm.nih.gov/28420421/)
* [PubMed - TMB & Immunotherapy Response](https://pubmed.ncbi.nlm.nih.gov/32217756/)
* [ScienceON - 암 유전체 변이 분석 기술](https://scienceon.kisti.re.kr/srch/selectPORSrchArticle.do?cn=NART115719302)

### 핫스팟, 인프레임 및 주요 암종별 연구
* **대장암 (APC, TP53)**
  * [PMC5720395 - Adenoma to Carcinoma Transition](https://pmc.ncbi.nlm.nih.gov/articles/PMC5720395/)
  * [PubMed 26336987 - Genomic Landscapes of Colorectal Cancer](https://pubmed.ncbi.nlm.nih.gov/26336987/)
  * [Nature 2024 - Colorectal Cancer Driver Mutations](https://www.nature.com/articles/s41586-024-07747-9)
* **신장암 (VHL, PBRM1)**
  * [PMC6299341 - VHL and PBRM1 Loss in ccRCC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6299341/)
  * [AACR Cancer Research - Cooperation among Cancer Genes](https://aacrjournals.org/cancerres/article/73/14/4173/584186/Cooperation-and-Antagonism-among-Cancer-Genes-The)
  * [Nature 2013 - Clear Cell Renal Cell Carcinoma Genomics](https://www.nature.com/articles/nature12222)

### 유전자 동반 변이 (Co-mutation) 및 아미노산/경로 분석
* **동반 변이 근거**
  * [PMC8490399 - Co-mutation Profiles in Cancer](https://pmc.ncbi.nlm.nih.gov/articles/PMC8490399/)
  * [JITC - Co-mutational Landscape & Clinical Outcomes](https://jitc.bmj.com/content/8/1/e000319)
* **아미노산 치환쌍 (`aa_*`)**
  * [PubMed 28837668](https://pubmed.ncbi.nlm.nih.gov/28837668/) | [PubMed 26581171](https://pubmed.ncbi.nlm.nih.gov/26581171/) | [PubMed 28671612](https://pubmed.ncbi.nlm.nih.gov/28671612/)
  * [eLife - Amino Acid Substitution Effects](https://elifesciences.org/articles/99341)
* **경로(Pathway)별 집계**
  * [NCI GDC - Oncogenic Signaling Pathways in Cancer](https://gdc.cancer.gov/about-data/publications/Pathways-2018)
  * [Cell 2018 - Pathway alterations across 33 cancer types](https://www.cell.com/cell/fulltext/S0092-8674(18)30229-0)
  * [cBioPortal for Cancer Genomics](https://www.cbioportal.org/)