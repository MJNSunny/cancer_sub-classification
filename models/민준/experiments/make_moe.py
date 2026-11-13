"""담당 나누기 앙상블(MoE): X 표기가 있는 환자는 민정 v6, 없는 환자는 v11 답을 쓴다.

사용법 (oz-final 폴더에서):
    python tools/make_moe.py out/norm_twin/submission.csv 민정_1110/submission_v5.csv out/moe_v11_mj
    python tools/make_moe.py out/norm_twin/submission.csv 민정_1110/submission_v5.csv out/moe2_v11_mj --wide
      (--wide: X 표기에 더해 '한 칸 완전중복'·'위치만 다른 중복 표기' 행도 민정 v6에게)

- 담당 기준은 그 환자 한 줄만 본다: 유전자 칸 중 하나라도 `R1450X`처럼 "글자+숫자+X" 토큰이 있으면 X 표기 환자.
  test 통계(비율·개수)는 쓰지 않는다.
- 두 입력 모두 쌍둥이 규칙이 이미 적용된 제출 파일이다 (둘의 쌍둥이 행과 답은 같다).
"""
import re
import sys

import numpy as np
import pandas as pd

RE_X = re.compile(r"^[A-Z]\d+X$")


def has_x(row_cells):
    """한 환자의 셀 목록 → X 표기 토큰이 하나라도 있으면 True"""
    return any(RE_X.match(t) for cell in row_cells for t in str(cell).split())


assert has_x(["WT", "R1450X"]) and has_x(["A1B R12X"]) and not has_x(["R1450*", "WT", "X12A", "S221Kfs"])

RE_TOK = re.compile(r"^([A-Z])(\d+)(.*)$")


def has_dup_or_iso(row_cells):
    """한 칸에 같은 표기가 두 번(V39V V39V) 있거나, 위치만 다른 같은 변화(Q644Sfs Q580Sfs)가 있으면 True"""
    for cell in row_cells:
        t = str(cell).split()
        if len(t) < 2:
            continue
        if len(set(t)) < len(t):
            return True
        pos = {}
        for x in set(t):
            m = RE_TOK.match(x)
            if m:
                pos.setdefault((m.group(1), m.group(3)), set()).add(m.group(2))
        if any(len(v) > 1 for v in pos.values()):
            return True
    return False


assert has_dup_or_iso(["V39V V39V"]) and has_dup_or_iso(["Q644Sfs Q580Sfs"]) and not has_dup_or_iso(["Q369* I368N", "WT"])


def main(clean_sub, x_sub, out_dir, wide=False):
    test = pd.read_csv("test.csv").fillna("WT")
    sample = pd.read_csv("sample_submission.csv")
    a, b = pd.read_csv(clean_sub), pd.read_csv(x_sub)
    assert (a.ID.values == sample.ID.values).all() and (b.ID.values == sample.ID.values).all()
    cells = test.drop(columns="ID").to_numpy(dtype=object)
    flag = np.array([has_x(r) or (wide and has_dup_or_iso(r)) for r in cells])   # 행마다 따로 계산 (행 독립)
    sub = a.copy()
    sub.loc[flag, "SUBCLASS"] = b.loc[flag, "SUBCLASS"].values
    sub.to_csv(f"{out_dir}/submission.csv", index=False, encoding="utf-8-sig")
    print(f"X 표기 환자 {flag.sum()}명 → {x_sub} / 나머지 {(~flag).sum()}명 → {clean_sub}")
    print(f"저장: {out_dir}/submission.csv")


if __name__ == "__main__":
    main(*sys.argv[1:4], wide="--wide" in sys.argv)
