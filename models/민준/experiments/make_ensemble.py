"""두 모델의 test 확률을 반반 섞고 쌍둥이 규칙을 적용해 제출 파일을 만든다.

사용법 (oz-final 폴더에서):
    python tools/make_ensemble.py out/norm_twin/test.npy out/ens_v10_mj/inputs/test_minjung_v6.npy out/ens_v10_mj

- 입력: test 확률 (2546×26, 행 = test.csv 순서, 열 = 암종 알파벳순). 쌍둥이 규칙·COAD 보정을 넣기 **전** 확률이어야 한다.
- 섞는 비율은 0.5 : 0.5 고정. 두 모델의 fold 방식이 달라 OOF로 비율을 고를 수 없고, LB를 보며 비율을 맞추지 않는다.
- 쌍둥이 규칙은 v10_clean.py 8-1절과 같다: train만으로 만든 "프로필 → 암종" 사전을 test 행마다 찾아본다.
"""
import hashlib
import sys

import numpy as np
import pandas as pd

SWAP = {"KIPAN": "KIRC", "KIRC": "KIPAN", "GBMLGG": "LGG", "LGG": "GBMLGG"}


def profile_hashes(df, genes):
    return np.array([hashlib.md5("|".join(r).encode()).hexdigest()[:12] for r in df[genes].to_numpy(dtype=object)])


def main(a_path, b_path, out_dir):
    train = pd.read_csv("train.csv").fillna("WT")
    test = pd.read_csv("test.csv").fillna("WT")
    sample = pd.read_csv("sample_submission.csv")
    genes = list(train.columns[2:])
    classes = np.array(sorted(train.SUBCLASS.unique()))

    a, b = np.load(a_path), np.load(b_path)
    for p in (a, b):
        assert p.shape == (len(test), len(classes)) and np.isfinite(p).all()
        assert np.allclose(p.sum(1), 1, atol=1e-3), "행 합이 1이 아님 (쌍둥이 규칙·보정 전 확률인지 확인)"
    P = 0.5 * a + 0.5 * b

    lab = pd.Series(train.SUBCLASS.values).groupby(profile_hashes(train, genes)).agg(set).to_dict()
    n = 0
    for i, h in enumerate(profile_hashes(test, genes)):
        s = lab.get(h, set())
        if len(s) == 1 and next(iter(s)) in SWAP:
            P[i] = 0.0
            P[i, list(classes).index(SWAP[next(iter(s))])] = 1.0
            n += 1

    sub = sample[["ID"]].copy()
    sub["SUBCLASS"] = classes[P.argmax(1)]
    assert len(sub) == len(sample) and (sub.ID.values == sample.ID.values).all()
    sub.to_csv(f"{out_dir}/submission.csv", index=False, encoding="utf-8-sig")
    np.save(f"{out_dir}/test.npy", P)
    print(f"저장: {out_dir}/submission.csv (쌍둥이 규칙 {n}행)")


if __name__ == "__main__":
    main(*sys.argv[1:4])
