# 보관용 사본 (11/11 잡음 내성 시험, 민정 v6 피처·파라미터를 팀 folds.csv로 재학습). 프로젝트 루트에서 DATA_DIR=. 로 실행 → 로그 out/noise_mj.log
# ---- 민정 v6 cell [1] ----
import os, re, warnings
import numpy as np
import pandas as pd
from collections import Counter
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder, MaxAbsScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, accuracy_score, classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_sample_weight
import xgboost as xgb
warnings.filterwarnings("ignore")

CFG = dict(
    DATA_DIR=os.environ.get("DATA_DIR", "../../data"),
    SEED=42,
    N_FOLDS=int(os.environ.get("N_FOLDS", 5)),
    MIN_GENE_FREQ=5,        # train에서 변이 샘플이 이 값 미만인 유전자는 제외
    MIN_HOTSPOT_FREQ=5,     # gene|position 토큰 최소 빈도
    MIN_AA_FREQ=20,         # 아미노산 치환쌍 최소 빈도
    USE_AA_SUBS=True,       # 아미노산 치환 패턴 피처 on/off (CV로 효과 확인)
    USE_PATHWAYS=True,      # 경로 집계 피처 on/off
    USE_HOTSPOTS=True,      # gene|position, gene|trunc 토큰 on/off
    BALANCE=True,           # 클래스 불균형 보정 (sample weight / class_weight)
    XGB_N_EST=int(os.environ.get("XGB_N_EST", 2000)),
    LR_C=0.1,
    USE_COMBOS=True,        # 동반 변이 콤보 피처 on/off
    TMB_LOW=5,              # 극저변이 기준 (THCA/LAML 등)
    TMB_HIGH=30,            # 고변이 기준 (SKCM/UCEC/STES 등)
    COAD_TEST_PRIOR=0.22,   # 가이드가 말하는 test COAD 비율 (검증 시뮬레이션용)
    BOOST_MIN_GAIN=0.003,   # COAD 가중으로 시뮬 macroF1이 이만큼 안 오르면 적용 안 함
    NORMALIZE_TOKENS=True,  # 변이 표기 통일(p./3글자 코드/X->*) + 한 칸 안 중복 표기 제거 (test 표기 차이 대응)
    USE_TWIN=True,          # 쌍둥이(형제 라벨) 규칙: train에 짝 암종 프로필이 있으면 test를 짝 암종으로 교정
    RUN_ABLATION=False,     # True면 콤보 ON/OFF CV 비교 (시간 2배)
)


# ---- 민정 v6 cell [3] ----
D = CFG["DATA_DIR"]
train = pd.read_csv(f"{D}/train.csv").fillna("WT")
test = pd.read_csv(f"{D}/test.csv").fillna("WT")
sub = pd.read_csv(f"{D}/sample_submission.csv")

assert (test["ID"].values == sub["ID"].values).all(), "test와 sample_submission의 ID 순서가 다릅니다"
gene_cols = [c for c in train.columns if c not in ("ID", "SUBCLASS")]
assert gene_cols == [c for c in test.columns if c != "ID"], "train/test 유전자 컬럼이 다릅니다"

le = LabelEncoder()
y = le.fit_transform(train["SUBCLASS"])
n_class = len(le.classes_)
print("train", train.shape, "test", test.shape, "classes", n_class)
print(train["SUBCLASS"].value_counts())

# ---- 민정 v6 cell [6] ----
import pandas as pd
import numpy as np
import re

# 1. 데이터 로드
train = pd.read_csv(f"{D}/train.csv").fillna("WT")
test = pd.read_csv(f"{D}/test.csv").fillna("WT")

print("="*50)
print("1. 기본 데이터 크기 및 암종(SUBCLASS) 개수 확인")
print("="*50)
print(f"Train 크기: {train.shape}")
print(f"Test 크기: {test.shape}")

# 암종(SUBCLASS) 개수 및 분포 확인
subclass_counts = train["SUBCLASS"].value_counts()
print(f"총 암종(Subclass) 개수: {len(subclass_counts)}개")
print("\n[상위 5개 암종 분포]")
print(subclass_counts.head())

# 유전자 컬럼 분리
gene_cols = [c for c in train.columns if c not in ("ID", "SUBCLASS")]
print(f"\n유전자(Feature) 컬럼 총 개수: {len(gene_cols)}개")


print("\n" + "="*50)
print("2. 샘플당 변이 유전자 수 분포 (TMB)")
print("="*50)
# WT가 아닌 유전자의 개수를 행별로 카운트
mut_matrix = (train[gene_cols] != "WT")
mut_counts_per_sample = mut_matrix.sum(axis=1)
print(mut_counts_per_sample.describe().round(2))


print("\n" + "="*50)
print("3. 한 셀에 변이가 여러 개 들어있는지 확인 (구분자 체크)")
print("="*50)
# WT가 아닌 셀들만 추출
all_vals = train[gene_cols].values.ravel()
non_wt_vals = all_vals[all_vals != "WT"]

non_wt_series = pd.Series(non_wt_vals)
# 쉼표(,), 콜론(:), 세미콜론(;), 파이프(|), 공백 등이 포함된 비율 확인
sep_pattern = r"[,:;|\s]"
has_sep = non_wt_series.str.contains(sep_pattern, regex=True).mean()
print(f"Non-WT 값 중 구분자(, : ; | 공백)가 포함된 비율: {has_sep:.4%}")


print("\n" + "="*50)
print("4. 변이 표기 패턴 종류 확인 (정규식 기반 상위 패턴)")
print("="*50)
# 숫자를 'N'으로 치환하여 대표적인 변이 표기 패턴 분석
pattern_samples = non_wt_series.str.replace(r"\d+", "N", regex=True)
print(pattern_samples.value_counts().head(15))


print("\n" + "="*50)
print("5. 유전자별 변이 빈도 (희소성 확인)")
print("="*50)
gene_mut_freq = mut_matrix.sum(axis=0)
print(f"변이가 단 1개라도 발생한 유전자 수: {(gene_mut_freq > 0).sum()} / {len(gene_cols)}")
print(f"대다수 유전자의 변이 빈도 요약 (상위/하위):")
print(gene_mut_freq.describe().round(2))

# ---- 민정 v6 cell [8] ----
sample = pd.Series(train[gene_cols].iloc[:1000].to_numpy(dtype=object).ravel())
nonwt = sample[sample != "WT"]
print(f"non-WT 비율: {len(nonwt)/len(sample):.4%}")
print("한 셀에 구분자(, : ; | 공백)가 있는 비율:", nonwt.str.contains(r"[,:;|\s]").mean().round(4))
print(nonwt.str.replace(r"\d+", "N", regex=True).value_counts().head(25))

# ---- 민정 v6 cell [10] ----
def combo_features(ex):
    mut = ex["mut"]; n = mut.shape[0]
    n_genes = mut.sum(1)
    low, high = n_genes <= CFG["TMB_LOW"], n_genes >= CFG["TMB_HIGH"]

    def G(name):   # 유전자 변이 여부 (없는 유전자는 0 벡터 — 엉뚱한 컬럼 안 가져옴)
        j = gene_pos.get(name)
        return mut[:, j].copy() if j is not None else np.zeros(n, bool)

    tok_rows = {}
    for r, nm in zip(ex["tok_rows"], ex["tok_names"]):
        tok_rows.setdefault(nm, []).append(r)
    def T(name):   # 핫스팟/절단형 토큰 보유 여부 (MIN_HOTSPOT_FREQ와 무관하게 직접 계산)
        v = np.zeros(n, bool)
        if name in tok_rows: v[tok_rows[name]] = True
        return v

    f = {}
    # COAD
    f["COAD_APCtr_TP53"]  = T("APC|trunc") & G("TP53")
    f["COAD_APCtr_KRAS"]  = T("APC|trunc") & (G("KRAS") | G("FBXW7"))
    f["COAD_score"]       = T("APC|trunc").astype(int) + G("TP53") + G("KRAS") + G("FBXW7") + G("PIK3CA")
    # KIRC / KIPAN
    f["KIRC_VHL_PBRM1"]   = G("VHL") & G("PBRM1")
    f["KIRC_3p_score"]    = G("VHL").astype(int) + G("PBRM1") + G("SETD2") + G("BAP1")
    # UCEC
    f["UCEC_PTEN_CTNNB1"] = G("PTEN") & G("CTNNB1")
    f["UCEC_PTEN_PIK3CA"] = G("PTEN") & G("PIK3CA")
    f["UCEC_highTMB_PTEN"]= high & G("PTEN")
    # PAAD
    f["PAAD_score"]       = T("KRAS|G12").astype(int) + G("TP53") + T("CDKN2A|trunc") + G("SMAD4")
    # LGG vs GBMLGG
    f["LGG_IDH1_TP53_ATRX"] = T("IDH1|R132") & G("TP53") & G("ATRX")
    f["LGG_IDH1_clean"]   = T("IDH1|R132") & ~(G("PTEN") | G("EGFR"))
    f["GBM_PTEN_EGFR"]    = G("PTEN") & G("EGFR")
    f["GBM_noIDH1_signal"]= (G("PTEN") | G("EGFR")) & ~G("IDH1")
    # BRAF V600 + TMB (THCA vs SKCM vs COAD)
    f["THCA_BRAF_lowTMB"] = T("BRAF|V600") & low
    f["SKCM_BRAF_highTMB"]= T("BRAF|V600") & high
    f["SKCM_NRAS_highTMB"]= T("NRAS|Q61") & high
    f["COAD_BRAF_APC"]    = T("BRAF|V600") & T("APC|trunc")
    # 폐암 / 위식도 / 간 / 난소 / 백혈병
    f["LUAD_EGFR_noTP53"] = G("EGFR") & ~G("TP53")
    f["LUSC_TP53_noEGFR_highTMB"] = G("TP53") & ~G("EGFR") & high
    f["STES_highTMB_TP53_noAPC"]  = high & G("TP53") & ~T("APC|trunc")
    f["LIHC_CTNNB1_noAPC"]= G("CTNNB1") & ~G("APC")
    f["OV_TP53_lowTMB"]   = G("TP53") & (n_genes <= 20)
    f["LAML_NPM1_lowTMB"] = G("NPM1") & low

    names = list(f.keys())
    return np.c_[[np.asarray(f[k], np.float32) for k in names]].T, names

# ---- 민정 v6 cell [11] ----
AA = "ACDEFGHIKLMNPQRSTVWY"
AA_IDX = {a: i for i, a in enumerate(AA)}
TYPES = ["missense", "silent", "nonsense", "frameshift", "splice", "inframe", "other"]
TYPE_IDX = {t: i for i, t in enumerate(TYPES)}
SEP = re.compile(r"[,:;|\s]+")
AA3 = {"Ala":"A","Arg":"R","Asn":"N","Asp":"D","Cys":"C","Gln":"Q","Glu":"E","Gly":"G","His":"H","Ile":"I",
       "Leu":"L","Lys":"K","Met":"M","Phe":"F","Pro":"P","Ser":"S","Thr":"T","Trp":"W","Tyr":"Y","Val":"V","Ter":"*"}

def canon(tok):
    """변이 표기 1개를 한 가지 모양으로 통일한다 (그 토큰만 보고 바꿈 = 행 독립, train/test 동일 적용).
    p.Arg1450Ter / R1450X / R1450* -> R1450*   (옛 HGVS의 X도 종결 코돈으로 읽는 기존 동작 유지)"""
    t = tok.strip()
    if t.startswith("p."):
        t = t[2:]
    t = re.sub(r"[A-Z][a-z]{2}", lambda m: AA3.get(m.group(), m.group()), t)   # 3글자 아미노산 -> 1글자
    t = re.sub(r"^([A-Z])(\d+)X$", r"\1\2*", t)                                  # R1450X -> R1450*
    return t

def cell_tokens(cell):
    """셀 하나 -> 변이 토큰 목록. NORMALIZE_TOKENS면 표기를 통일하고 같은 변이의 중복 표기를 하나로 합친다."""
    toks = [t for t in SEP.split(str(cell)) if t and t != "WT"]
    if CFG["NORMALIZE_TOKENS"]:
        toks = list(dict.fromkeys(canon(t) for t in toks))
    return toks
RE_MIS = re.compile(r"^(?:p\.)?([A-Z])(\d+)([A-Z])$")
RE_NON = re.compile(r"^(?:p\.)?[A-Z]\d+(\*|X|Ter)$")

def parse_token(tok):
    """변이 표기 1개 -> (유형, 원래aa, 위치, 바뀐aa). 표기가 다르면 여기 규칙을 수정하세요."""
    low = tok.lower()
    m = re.search(r"\d+", tok)
    pos = m.group() if m else ""
    if "fs" in low or "frameshift" in low:
        return "frameshift", "", pos, ""
    if "splice" in low:
        return "splice", "", pos, ""
    if "del" in low or "ins" in low or "dup" in low:
        return "inframe", "", pos, ""
    if RE_NON.match(tok):
        return "nonsense", "", pos, ""
    m = RE_MIS.match(tok)
    if m:
        fa, p, ta = m.groups()
        return ("silent" if fa == ta else "missense"), fa, p, ta
    return "other", "", pos, ""

def extract(df):
    arr = df[gene_cols].to_numpy(dtype=object)
    mut = arr != "WT"
    n = len(df)
    type_cnt = np.zeros((n, len(TYPES)), np.float32)
    aa_cnt = np.zeros((n, 400), np.float32)
    tok_rows, tok_names = [], []
    rr, cc = np.nonzero(mut)
    for r, c in zip(rr, cc):
        gene = gene_cols[c]
        for tok in cell_tokens(arr[r, c]):
            typ, fa, pos, ta = parse_token(tok)
            type_cnt[r, TYPE_IDX[typ]] += 1
            if typ == "missense":
                tok_rows.append(r); tok_names.append(f"{gene}|{fa}{pos}")
                if fa in AA_IDX and ta in AA_IDX:
                    aa_cnt[r, AA_IDX[fa] * 20 + AA_IDX[ta]] += 1
            elif typ in ("nonsense", "frameshift", "splice"):
                tok_rows.append(r); tok_names.append(f"{gene}|trunc")
            elif typ == "inframe":                       # ← 추가
                tok_rows.append(r); tok_names.append(f"{gene}|inframe")        # 유전자 단위
                tok_rows.append(r); tok_names.append(f"{gene}|{pos}_inframe")  # 위치 단위 (EGFR 746_inframe 등)
    return dict(mut=mut, type_cnt=type_cnt, aa_cnt=aa_cnt,
                tok_rows=np.array(tok_rows, dtype=np.int64), tok_names=tok_names)

ex_tr, ex_te = extract(train), extract(test)
print("파싱 완료. 유형별 총 개수(train):", dict(zip(TYPES, ex_tr["type_cnt"].sum(0).astype(int))))
# ---- 표기 통일 동작 확인 ----
assert canon("R1450X") == "R1450*" == canon("p.Arg1450Ter") == canon("p.R1450*")
assert canon("E746_A750del") == "E746_A750del" and canon("S221Kfs") == "S221Kfs"
assert parse_token(canon("R1450X"))[0] == "nonsense"
_save = CFG["NORMALIZE_TOKENS"]; CFG["NORMALIZE_TOKENS"] = True
assert cell_tokens("R1450X R1450* p.Arg1450Ter") == ["R1450*"]          # 같은 변이의 여러 표기 -> 1개
assert cell_tokens("R175H, V600E") == ["R175H", "V600E"] and cell_tokens("WT") == []
CFG["NORMALIZE_TOKENS"] = _save


# ---- 민정 v6 cell [13] ----
def tokens_per_cell(df, normalize):
    vals = df[gene_cols].to_numpy(dtype=object).ravel()
    vals = vals[vals != "WT"]
    n = [len([t for t in SEP.split(str(v)) if t and t != "WT"]) if not normalize else
         len(dict.fromkeys(canon(t) for t in SEP.split(str(v)) if t and t != "WT")) for v in vals]
    return float(np.mean(n)) if n else 0.0

for nm, df in (("train", train), ("test", test)):
    print(f"{nm}: 칸당 변이 수 {tokens_per_cell(df, False):.2f} -> (표기 통일·중복 제거 후) {tokens_per_cell(df, True):.2f}")


# ---- 민정 v6 cell [14] ----
# ---- 경로/유전자군 사전 (초안: 필요에 맞게 수정/추가) ----
PATHWAYS = {
    "p53": ["TP53","MDM2","MDM4","CDKN2A","ATM","CHEK1","CHEK2"],
    "RTK_RAS": ["EGFR","ERBB2","ERBB3","ERBB4","FGFR1","FGFR2","FGFR3","FGFR4","MET","ALK","RET","KIT",
                "PDGFRA","KRAS","NRAS","HRAS","BRAF","RAF1","NF1","MAP2K1","MAP2K2","SOS1","PTPN11"],
    "PI3K": ["PIK3CA","PIK3CB","PIK3R1","PTEN","AKT1","AKT2","AKT3","MTOR","TSC1","TSC2","STK11","RICTOR","INPP4B"],
    "Wnt": ["APC","CTNNB1","AXIN1","AXIN2","RNF43","ZNRF3","TCF7L2","GSK3B","AMER1"],
    "CellCycle": ["RB1","CDK4","CDK6","CCND1","CCND2","CCND3","CCNE1","CDKN1A","CDKN1B","CDKN2B","E2F1","FBXW7"],
    "Notch": ["NOTCH1","NOTCH2","NOTCH3","NOTCH4","FBXW7","SPEN"],
    "Hippo": ["NF2","LATS1","LATS2","SAV1","YAP1","WWTR1","TEAD1"],
    "TGFb": ["TGFBR1","TGFBR2","SMAD2","SMAD3","SMAD4","ACVR1B","ACVR2A"],
    "NRF2": ["NFE2L2","KEAP1","CUL3"],
    "SWI_SNF": ["ARID1A","ARID1B","ARID2","SMARCA4","SMARCB1","PBRM1","SMARCA2"],
    "Chromatin": ["KMT2A","KMT2B","KMT2C","KMT2D","EZH2","SETD2","KDM6A","KDM5C","CREBBP","EP300",
                  "BAP1","ASXL1","DNMT3A","IDH1","IDH2","ATRX"],
    "DDR_MMR": ["BRCA1","BRCA2","PALB2","ATR","POLE","POLD1","MLH1","MSH2","MSH6","PMS2",
                "RAD51","RAD50","MRE11","FANCA","FANCD2","ERCC2"],
    "Splicing": ["SF3B1","SRSF2","U2AF1","RBM10"],
    "LongGenes": ["TTN","MUC16","MUC4","SYNE1","OBSCN","RYR2","RYR1","CSMD1","CSMD3","LRP1B","USH2A","FLG","PCLO"],
}
gene_pos = {g: i for i, g in enumerate(gene_cols)}
PW_IDX = {k: [gene_pos[g] for g in v if g in gene_pos] for k, v in PATHWAYS.items()}
print({k: f"{len(v)}/{len(PATHWAYS[k])}" for k, v in PW_IDX.items()})   # 데이터에 존재하는 유전자 수/사전 크기

# ---- 민정 v6 cell [15] ----
# ---- train 기준으로만 사용할 유전자/토큰/아미노산쌍 결정 (test는 보지 않음: Data Leakage 방지) ----
# test는 아래 compose()에서 이 기준에 맞춰 변환만 한다. test에만 있는 토큰은 tok_idx.get()이 None이라 무시됨.
freq = ex_tr["mut"].sum(0)
keep_idx = np.where(freq >= CFG["MIN_GENE_FREQ"])[0]

def uniq_pairs(ex):
    return set(zip(ex["tok_rows"].tolist(), ex["tok_names"]))

tok_cnt = Counter(nm for _, nm in uniq_pairs(ex_tr))
keep_tokens = sorted(t for t, c in tok_cnt.items() if c >= CFG["MIN_HOTSPOT_FREQ"])
tok_idx = {t: i for i, t in enumerate(keep_tokens)}

aa_tot = ex_tr["aa_cnt"].sum(0)
aa_keep = np.where(aa_tot >= CFG["MIN_AA_FREQ"])[0]
print(f"유전자 {len(keep_idx)}/{len(gene_cols)}, 핫스팟 토큰 {len(keep_tokens)}, 아미노산쌍 {len(aa_keep)}")

def compose(ex):
    mut = ex["mut"]; n = mut.shape[0]
    blocks, names = [], []
    def add(a, nm):
        blocks.append(np.asarray(a, np.float32).reshape(n, -1)); names.extend(nm)

    add(mut[:, keep_idx], [f"g_{gene_cols[i]}" for i in keep_idx])

    n_genes = mut.sum(1)
    tc = ex["type_cnt"]; n_ev = tc.sum(1)
    add(np.c_[n_genes, np.log1p(n_genes), n_ev], ["n_mut_genes", "log_n_mut_genes", "n_events"])
    add(tc, [f"cnt_{t}" for t in TYPES])
    trunc = tc[:, [TYPE_IDX[t] for t in ("nonsense", "frameshift", "splice")]].sum(1)
    add(np.c_[tc[:, TYPE_IDX["silent"]] / (n_ev + 1),
              tc[:, TYPE_IDX["missense"]] / (n_ev + 1),
              trunc / (n_ev + 1)], ["ratio_silent", "ratio_missense", "ratio_trunc"])

    if CFG["USE_HOTSPOTS"] and keep_tokens:
        H = np.zeros((n, len(keep_tokens)), np.float32)
        for r, nm in zip(ex["tok_rows"], ex["tok_names"]):
            j = tok_idx.get(nm)
            if j is not None:
                H[r, j] = 1
        add(H, [f"hs_{t}" for t in keep_tokens])
    if CFG["USE_COMBOS"]:
        C, cn = combo_features(ex)
        add(C, [f"cb_{k}" for k in cn])
    if CFG["USE_AA_SUBS"] and len(aa_keep):
        A = ex["aa_cnt"][:, aa_keep] / (tc[:, TYPE_IDX["missense"]] + 1)[:, None]
        add(A, [f"aa_{AA[k // 20]}>{AA[k % 20]}" for k in aa_keep])

    if CFG["USE_PATHWAYS"]:
        P = np.c_[[mut[:, idx].sum(1) if idx else np.zeros(n) for idx in PW_IDX.values()]].T
        add(P, [f"pw_{k}" for k in PW_IDX])

    return np.hstack(blocks), names

X, feat_names = compose(ex_tr)
X_te, _ = compose(ex_te)
print("X", X.shape, "X_te", X_te.shape)
# ==== 잡음 내성 시험: 민정 v6 피처 + XGB/LR (민정 설정), fold는 팀 folds.csv (우리와 같은 조건) ====
import json as _json
from pathlib import Path as _P
folds = pd.read_csv("folds.csv").set_index("ID").loc[train.ID].reset_index(); fold_arr = folds.fold.values
genes = gene_cols; VALS = train[genes].to_numpy(dtype=object)
import re as _re
RE_MIS_N = _re.compile(r"^([A-Z])(\d+)([A-Z])$")
VALS = train[genes].to_numpy(dtype=object)


def add_genes(v, mult, pool_c, pool_t, rng):
    """행마다 '원래 고장 유전자 수 × mult'개의 WT 칸에 학습 부분의 실제 고장 표기를 무작위로 심는다 (빈도 비례)."""
    v = v.copy()
    for i in range(len(v)):
        k = int(round(mult * max((v[i] != "WT").sum(), 1))); added = 0
        for j in rng.integers(0, len(pool_c), size=4 * k + 10):
            if v[i, pool_c[j]] == "WT":
                v[i, pool_c[j]] = pool_t[j]; added += 1
                if added == k: break
    return v


def add_isoform(v, rng):
    """고장 칸의 missense 토큰마다 '위치만 다른 같은 변화'를 하나 더 적는다 (예: M267I → M267I M206I)."""
    v = v.copy()
    for r, c in zip(*np.nonzero(v != "WT")):
        toks = str(v[r, c]).split(); extra = []
        for t in toks:
            m = RE_MIS_N.match(t)
            if m:
                p = int(m.group(2)) + int(rng.choice([-1, 1]) * rng.integers(20, 80))
                if p > 0: extra.append(f"{m.group(1)}{p}{m.group(3)}")
        v[r, c] = " ".join(toks + extra)
    return v



CONDS = {"원본": None, "고장 +1배": ("g", 1), "고장 +3배": ("g", 3), "표기 중복": ("iso", 0)}
P = {n: [np.zeros((len(y), n_class)), np.zeros((len(y), n_class))] for n in CONDS}
for k in range(5):
    tr, va = np.where(fold_arr != k)[0], np.where(fold_arr == k)[0]
    sw = compute_sample_weight("balanced", y[tr])
    m = xgb.XGBClassifier(objective="multi:softprob", n_estimators=CFG["XGB_N_EST"], learning_rate=0.08,
            max_depth=5, subsample=0.8, colsample_bytree=0.3, tree_method="hist",
            eval_metric="mlogloss", early_stopping_rounds=50, random_state=CFG["SEED"], n_jobs=-1)
    m.fit(X[tr], y[tr], sample_weight=sw, eval_set=[(X[va], y[va])], verbose=False)
    lr = make_pipeline(MaxAbsScaler(), LogisticRegression(C=CFG["LR_C"], max_iter=500, class_weight="balanced")).fit(X[tr], y[tr])
    rr, cc = np.nonzero(VALS[tr] != "WT"); pool_c, pool_t = cc, VALS[tr][rr, cc]
    for name, cond in CONDS.items():
        rng = np.random.default_rng(100 + k); v = VALS[va]
        if cond and cond[0] == "g": v = add_genes(v, cond[1], pool_c, pool_t, rng)
        if cond and cond[0] == "iso": v = add_isoform(v, rng)
        df_v = train.iloc[va].copy(); df_v[genes] = v
        Xv, _ = compose(extract(df_v))
        P[name][0][va] = m.predict_proba(Xv); P[name][1][va] = lr.predict_proba(Xv)
    print("fold", k, "done", flush=True)
mf = lambda p: f1_score(y, p.argmax(1), average="macro")
out = {}
for name in CONDS:
    b = 0.5 * P[name][0] + 0.5 * P[name][1]
    top = pd.Series(le.classes_[b.argmax(1)]).value_counts(normalize=True).head(3).round(2).to_dict()
    out[name] = dict(blend=mf(b), xgb=mf(P[name][0]), lr=mf(P[name][1]), top=top)
    print(f"[잡음] {name:8s} | 섞음 {out[name]['blend']:.4f} | XGB {out[name]['xgb']:.4f} | LR {out[name]['lr']:.4f} | 예측 상위 {top}")
_P("out/noise_mj").mkdir(parents=True, exist_ok=True)
_json.dump(out, open("out/noise_mj/noise.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
