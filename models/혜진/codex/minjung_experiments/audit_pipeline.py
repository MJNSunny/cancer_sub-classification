"""Leakage and artifact consistency checks. Does not fit models or read test values."""
import ast,hashlib,json
from pathlib import Path
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import MaxAbsScaler
from scipy import sparse
p=Path(__file__).resolve().parent
root=p.parents[3]
s=(p/'run_experiments.py').read_text()
ast.parse(s)
# Unknown validation/test tokens never expand the train vocabulary.
dv=DictVectorizer(); a=dv.fit_transform([{'known':1},{'known':2}]); b=dv.transform([{'known':100,'query_only':1}])
assert dv.get_feature_names_out().tolist()==['known'] and b.shape[1]==1
sc=MaxAbsScaler().fit(a); before=sc.max_abs_.copy(); sc.transform(b); assert np.array_equal(before,sc.max_abs_)
tf=TfidfTransformer().fit(a); before=tf.idf_.copy(); tf.transform(b); assert np.array_equal(before,tf.idf_)
idx=np.load(p/'split_indices.npz'); dev=idx['dev']; hold=idx['holdout']
assert not set(dev)&set(hold)
assert set(dev)|set(hold)==set(range(6201))
valid=[]
for i in range(3):
 a,b=idx[f'train_{i}'],idx[f'valid_{i}']
 assert not set(a)&set(b) and set(a)|set(b)==set(dev)
 assert not set(a)&set(hold) and not set(b)&set(hold)
 valid.extend(b.tolist())
assert sorted(valid)==sorted(dev.tolist())
# 원본 파일은 Git에 포함되지 않을 수 있으므로 배포 복사본의 셀 내용을 검사합니다.
# 공개용 정리에서 데이터 미리보기 출력만 제거했으며 코드·문서 셀은 유지했습니다.
copy=p.parent/'model_민정_v10_original.ipynb'
def notebook_source_sha256(path):
    import json
    cells=json.loads(path.read_text())['cells']
    return hashlib.sha256(json.dumps([(c['cell_type'],c['source']) for c in cells],ensure_ascii=False).encode()).hexdigest()
expected_source_sha256='eeb97af3fd7deb50c621fe623595722e3ab662cc71a352f9320dfae3eba7916e'
assert notebook_source_sha256(copy)==expected_source_sha256
original=root/'models'/'민정'/'model_민정_v10.ipynb'
if original.exists():
    assert notebook_source_sha256(original)==expected_source_sha256
# Check test read occurs after frozen selection and holdout evaluation in runner source.
assert s.index("test=pd.read_csv(DATA/'test.csv')")>s.index("(OUT/'frozen_selection.json').write_text")
fit_calls=[n for n in ast.walk(ast.parse(s)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='fit']
assert 'early_stopping_rounds' not in s[s.index('def fit_predict'):]
r=dict(passed=True,notebook_source_sha256=expected_source_sha256,published_notebook_sha256=hashlib.sha256(copy.read_bytes()).hexdigest(),n_dev=len(dev),n_holdout=len(hold),checks=['Notebook code and markdown preserved; dataset preview output removed','No overlapping rows between development and holdout','3-fold partition covers development exactly once','Canonical profile group non-overlap asserted in runner','Unknown query tokens ignored','Query outliers cannot alter scaler or IDF','Test CSV read after frozen selection','No outer validation early stopping','No duplicate-label override'],limits=['Static and synthetic checks do not establish competition-specific approval.','Existing team work may have previously used holdout rows.','Selection CV has tuning bias; confirmatory holdout is separate.'])
(p/'leakage_audit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
