"""Compare frozen v19 with v4 core on same saved group holdout; never read test."""
from pathlib import Path
import json,hashlib,os,time
os.environ.setdefault('OMP_NUM_THREADS','4')
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import f1_score,classification_report
P=Path(__file__).resolve().parent
ROOT=P.parents[3]
original=ROOT/'models'/'혜진'/'claude'/'model_민정_v10_claude_v4.ipynb'
nb=json.loads(original.read_text())
ns={}
exec(''.join(nb['cells'][2]['source']),ns)
# Use v4 core settings; disable outer validation ES and all overrides.
ns['CFG'].update(USE_DUP_RULE=False,USE_CLASS_SCALE=False,USE_PAIR_BIAS=False,NOISE_EVAL=False,INNER_ES=True)
train=pd.read_csv(ROOT/'data'/'train.csv').fillna('WT')
genes=[g for g in train if g not in ['ID','SUBCLASS']]
le=LabelEncoder().fit(train.SUBCLASS);y=le.transform(train.SUBCLASS)
ns.update(train=train,gene_cols=genes,le=le,y=y,n_class=len(le.classes_))
exec(''.join(nb['cells'][11]['source']),ns)
exec(''.join(nb['cells'][12]['source']).split('ex_tr, ex_te =')[0],ns)
exec(''.join(nb['cells'][15]['source']).split('print(')[0],ns)
exec(''.join(nb['cells'][16]['source']).split('# 참고용')[0],ns)
# Import fit_tree and make_lr definitions without executing run_cv.
src=''.join(nb['cells'][22]['source']).split('_T_CV =')[0].replace('n_jobs=-1','n_jobs=4')
exec(src,ns)
ex=ns['extract'](train)
h=np.array([hashlib.sha256(json.dumps([(g,sorted(set(ns['cell_tokens'](v)))) for g,v in zip(genes,row) if v!='WT'],ensure_ascii=False).encode()).hexdigest() for row in train[genes].to_numpy()])
idx=np.load(P/'split_indices.npz');dev=idx['dev'];hold=idx['holdout']
assert not set(h[dev])&set(h[hold])
# Independent inner group split, never outer holdout for iteration selection.
i,j=next(StratifiedGroupKFold(7,shuffle=True,random_state=271828).split(y[dev],y[dev],h[dev]))
a,b=dev[i],dev[j]
assert not set(h[a])&set(h[b]) and not set(a)&set(hold) and not set(b)&set(hold)
vi=ns['fit_vocab'](ex,a);Xi,_=ns['compose'](ex,vi)
v=ns['fit_vocab'](ex,dev);X,_=ns['compose'](ex,v)
weights=compute_sample_weight('balanced',y[dev]); wi=compute_sample_weight('balanced',y[a])
probs={};iters={}
for kind in ['xgb','lgb']:
 probs[kind]=np.zeros((len(hold),len(le.classes_)))
 iters[kind]=[]
 for seed in [42,7]:
  _,bi=ns['fit_tree'](kind,Xi[a],y[a],wi,Xi[b],y[b],seed)
  # Same v4 INNER_ES=True multiplier; holdout labels never passed to fit.
  rounds=max(10,round(bi*ns['CFG']['REFIT_MULT']))
  m,_=ns['fit_tree'](kind,X[dev],y[dev],weights,None,None,seed,n_fixed=rounds)
  probs[kind]+=m.predict_proba(X[hold])/2
  iters[kind].append(dict(seed=seed,inner_best=bi,refit_rounds=rounds))
  print(kind,seed,iters[kind][-1],flush=True)
lr=ns['make_lr'](.1);lr.fit(X[dev],y[dev]);probs['lr']=lr.predict_proba(X[hold])
# Frozen weights from v4's existing manifest, never tuned on this holdout.
cp=.1*probs['xgb']+.5*probs['lgb']+.4*probs['lr']
cache=np.load(P/'holdout_predictions.npz');assert np.array_equal(cache['rows'],hold)
vp=cache['selected']; score=lambda q:float(f1_score(y[hold],q.argmax(1),average='macro'))
np.savez_compressed(P/'comparison_v19_claude_v4_predictions.npz',rows=hold,v19=vp,claude_v4_core=cp,**probs)
# Paired cluster bootstrap to express uncertainty, not select/refit models.
rng=np.random.default_rng(20261113);groups=np.unique(h[hold]); members=[np.where(h[hold]==g)[0] for g in groups]
deltas=[]
for _ in range(1000):
 rows=np.concatenate([members[k] for k in rng.integers(0,len(groups),len(groups))])
 def f(q):return f1_score(y[hold][rows],q[rows].argmax(1),labels=np.arange(len(le.classes_)),average='macro',zero_division=0)
 deltas.append(f(cp)-f(vp))
ci=np.quantile(deltas,[.025,.975]).tolist()
r=dict(n_train=len(dev),n_holdout=len(hold),v19_macro_f1=score(vp),claude_v4_core_macro_f1=score(cp),delta_claude_minus_v19=score(cp)-score(vp),paired_group_bootstrap_95pct_delta=ci,iterations=iters,claude_weights=dict(xgb=.1,lgb=.5,lr=.4),claude_lr_C=.1,claude_per_model={k:score(q) for k,q in probs.items()},winner='claude_v4_core' if score(cp)>score(vp) else 'v19',source_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),train_sha256=hashlib.sha256((ROOT/'data'/'train.csv').read_bytes()).hexdigest(),caveats=['Same group holdout as v19; v19 cached predictions reused.','v4 adapted to train-internal grouped early stopping; not exact original random 5-fold pipeline.','v4 existing hyperparameters/weights were selected using full train OOF; holdout therefore is not untouched for v4 model development.','Both pipelines previously saw team data during development; no new external test.','No duplicate override, test file, or leaderboard submission used in this comparison.'])
(P/'comparison_v19_claude_v4.json').write_text(json.dumps(r,indent=2))
(P/'comparison_claude_classification.txt').write_text(classification_report(y[hold],cp.argmax(1),target_names=le.classes_,zero_division=0))
lines=['# v19와 Claude v4 비교','',f"동일 그룹 분리 holdout {len(hold)}행에서 비교했습니다. test는 읽지 않았습니다.",'','| 모델 | Macro F1 |','|---|---:|',f"| Codex v19 | {score(vp):.5f} |",f"| Claude v4 core (내부 그룹 early stopping으로 변경) | {score(cp):.5f} |",'',f"점수 차이(Claude−v19): **{score(cp)-score(vp):+.5f}**. 그룹 단위 paired bootstrap 95% 구간: [{ci[0]:+.5f}, {ci[1]:+.5f}]. 구간은 기존 튜닝의 선택 편향을 보정하지 않습니다.",'','## 비교 조건과 한계','',*['- '+c for c in ['v19는 이전에 저장한 동일 holdout 예측을 재사용했습니다. 두 모델 모두 학습행 4,958개이며 같은 정규화 프로필은 학습/평가에 걸치지 않습니다.','v4는 원래 XGB+LightGBM(각 seed42/7)+LR, 콤보 ON, LR C=.1, 앙상블 .1/.5/.4입니다. v19는 콤보 OFF, XGB(seed42/137)+LR, 비중 .4/.6입니다.','v4 원본의 평가 fold early stopping을 그대로 적용하면 비교용 정답을 학습 회수 선택에 쓰게 되므로, 학습 4,958행 안의 그룹 7-fold 중 한 분할로 회수를 정하고 1.15배 하여 4,958행 전체를 재학습했습니다. 내부 특징 사전도 내부 학습 행에서만 정했습니다. 이는 원본 v4의 그대로 재현한 점수는 아닙니다.','원본 v4의 C/앙상블 비중 등은 전체 train OOF로 이미 정해졌으므로 이 holdout의 라벨도 과거 선택에 간접 관여했습니다. 따라서 새 독립 검증에서의 확정적 우열로 해석할 수 없습니다. 비교 결과를 보고 다시 튜닝하지 않았습니다.','중복 라벨 덮어쓰기는 양쪽에서 제외했습니다. 원본 v4의 0.54180은 행 단위 5-fold + 중복 규칙 점수로 이 표와 직접 비교할 수 없습니다. 기본 모델 원본 OOF는 0.47729입니다.','내부 점수로 리더보드 우열을 확정할 수 없습니다. 대회 제출은 하지 않았으며 기존 파일도 수정하지 않았습니다.']], '', '세부 결과: `comparison_v19_claude_v4.json`, 예측: `comparison_v19_claude_v4_predictions.npz`, 재현 코드: `compare_claude_v4.py`.']
(P/'COMPARISON_CLAUDE_V4.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(r,indent=2),flush=True)
