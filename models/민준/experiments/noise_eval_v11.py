# 보관용 사본 (11/11 잡음 내성 시험). v11_clean.py 실행 끝에 붙여 EXP=noise_v11 등으로 실행 → 로그 out/noise_v11.log, out/noise_nogf.log, out/noise_nosig.log


# %% ==== 잡음 내성 시험 (v11 노트북 끝에 붙여 실행하는 실험용 블록, 공유 노트북에는 넣지 않음) ====
# fold k 모델로 검증 행을 예측하되, 검증 행에 가짜 고장을 섞는다. 가짜 고장은 그 fold의 '학습 부분'에 있던 고장에서만 뽑는다.
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


_v = np.array([["WT", "R175H", "WT"], ["V600E", "WT", "WT"]], dtype=object)
_o = add_genes(_v, 1, np.array([0, 2]), np.array(["A1B", "C2D"], dtype=object), np.random.default_rng(0))
assert ((_o != "WT").sum(1) == [2, 2]).all() and _o[0, 1] == "R175H"
assert add_isoform(np.array([["R175H"]], dtype=object), np.random.default_rng(0))[0, 0].startswith("R175H R")

CONDS = {"원본": None, "고장 +1배": ("g", 1), "고장 +3배": ("g", 3), "표기 중복": ("iso", 0)}
noise_res = {}
for name, cond in CONDS.items():
    P_lgb = np.zeros_like(res["oof"]); P_lr = np.zeros_like(res["oof"])
    for k in range(CFG["N_FOLDS"]):
        rng = np.random.default_rng(100 + k)
        trn, val = np.where(fold_arr != k)[0], np.where(fold_arr == k)[0]
        rr, cc = np.nonzero(VALS[trn] != "WT"); pool_c, pool_t = cc, VALS[trn][rr, cc]
        v = VALS[val]
        if cond and cond[0] == "g": v = add_genes(v, cond[1], pool_c, pool_t, rng)
        if cond and cond[0] == "iso": v = add_isoform(v, rng)
        df_v = train.iloc[val].copy(); df_v[genes] = v
        P_lgb[val], P_lr[val] = predict_parts(res["models"][k], parse_rows(df_v, genes, CFG["HGVS_LEGACY"], CFG["NORMALIZE"]))
    blend = 0.5 * P_lgb + 0.5 * P_lr; pred = CLASSES[blend.argmax(1)]
    top = pd.Series(pred).value_counts(normalize=True).head(3).round(2).to_dict()
    noise_res[name] = dict(blend=macro_f1(y, blend), lgb=macro_f1(y, P_lgb), lr=macro_f1(y, P_lr), top=top)
    print(f"[잡음] {name:8s} | 섞음 {noise_res[name]['blend']:.4f} | LGB {noise_res[name]['lgb']:.4f} | LR {noise_res[name]['lr']:.4f} | 예측 상위 {top}")
json.dump(noise_res, open(OUT / "noise.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
