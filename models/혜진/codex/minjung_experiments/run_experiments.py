"""Train-only, grouped development CV; frozen holdout used after selection only."""
import os
os.environ.setdefault('OMP_NUM_THREADS','4')
import json, hashlib, sys, platform, time, re, warnings
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import LabelEncoder, MaxAbsScaler
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, accuracy_score, classification_report
import xgboost as xgb
warnings.filterwarnings('ignore', category=FutureWarning)
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
DATA=ROOT/'data'
nb=json.loads((OUT.parent/'model_민정_v10_original.ipynb').read_text())
exec(''.join(nb['cells'][1]['source']).split('CFG = dict(')[0])
# Copy original configuration without executing notebook training or test reads.
exec('CFG = dict('+''.join(nb['cells'][1]['source']).split('CFG = dict(',1)[1])
CFG.update(USE_DUP_RULE=False,USE_CLASS_SCALE=False,USE_KNN=False,PROFILE_WEIGHT=False,NORMALIZE_TOKENS=True)
train=pd.read_csv(DATA/'train.csv').fillna('WT')
gene_cols=[c for c in train if c not in ['ID','SUBCLASS']]
le=LabelEncoder().fit(train.SUBCLASS); y=le.transform(train.SUBCLASS); n_class=len(le.classes_)
exec(''.join(nb['cells'][10]['source']))
exec(''.join(nb['cells'][11]['source']).split('ex_tr, ex_te =')[0])
exec(''.join(nb['cells'][14]['source']).split('print(')[0])
exec(''.join(nb['cells'][15]['source']).split('# 참고용')[0])
# Canonical, order-insensitive profiles prevent equivalent representations crossing folds.
def profile(row):
 return hashlib.sha256(json.dumps([(g,sorted(set(cell_tokens(v)))) for g,v in zip(gene_cols,row) if v!='WT'],ensure_ascii=False).encode()).hexdigest()
h=np.array([profile(r) for r in train[gene_cols].to_numpy()])
ex=extract(train)
outer=list(StratifiedGroupKFold(5,shuffle=True,random_state=20261113).split(y,y,h))
dev,hold=outer[0]
folds=[(dev[a],dev[b]) for a,b in StratifiedGroupKFold(3,shuffle=True,random_state=314159).split(y[dev],y[dev],h[dev])]
assert not set(h[dev])&set(h[hold])
for a,b in folds: assert not set(h[a])&set(h[b]) and not set(a)&set(hold)
np.savez(OUT/'split_indices.npz',dev=dev,holdout=hold,**{f'train_{i}':a for i,(a,b) in enumerate(folds)},**{f'valid_{i}':b for i,(a,b) in enumerate(folds)})
# Exact and gene-type tokens; dictionaries are fitted separately in each training fold.
def token_docs(df):
 docs=[]
 for row in df[gene_cols].to_numpy():
  d={}
  for g,v in zip(gene_cols,row):
   if v=='WT': continue
   for t in cell_tokens(v):
    typ,_,_,_=parse_token(t)
    d[g+'|exact|'+t]=1; d[g+'|type|'+typ]=1
  docs.append(d)
 return docs
docs=token_docs(train)
configs=[
 dict(version='v11_baseline',alpha=1.,C=.1,mode='base',ablate=None),
 dict(version='v12_weight_half',alpha=.5,C=.1,mode='base',ablate=None),
 dict(version='v13_weight_none',alpha=0.,C=.1,mode='base',ablate=None),
 *[dict(version=f'v14_lr_C{c}',alpha=1.,C=c,mode='base',ablate=None) for c in [.03,.3,1.]],
 dict(version='v15_exact_binary',alpha=1.,C=.1,mode='binary',ablate=None),
 dict(version='v16_exact_tfidf',alpha=1.,C=.1,mode='tfidf',ablate=None),
 *[dict(version='v17_without_'+name,alpha=1.,C=.1,mode='base',ablate=key) for name,key in [('combos','USE_COMBOS'),('pathways','USE_PATHWAYS'),('aa','USE_AA_SUBS')]],
]
configs += [dict(version=f'v18_xgb_a{a}_lr_a{b}',alpha=a,lr_alpha=b,C=.1,mode='base',ablate=None) for a in [0.,.5,1.] for b in [0.,.5,1.] if a!=b]
results=[]; xcache={}; lcache={}; features={}
def matrices(rows,query_ex,query_docs,cfg):
 old=CFG.copy()
 if cfg['ablate']: CFG[cfg['ablate']]=False
 voc=fit_vocab(ex,rows)
 A,names=compose(ex,voc); B,_=compose(query_ex,voc)
 CFG.update(old)
 A=sparse.csr_matrix(A[rows]); B=sparse.csr_matrix(B)
 if cfg['mode']!='base':
  dv=DictVectorizer(dtype=np.float32)
  T=dv.fit_transform([docs[i] for i in rows]); U=dv.transform(query_docs)
  keep=np.asarray((T>0).sum(0)).ravel()>=3; T=T[:,keep]; U=U[:,keep]
  if cfg['mode']=='tfidf':
   tf=TfidfTransformer(); T=tf.fit_transform(T); U=tf.transform(U)
  A=sparse.hstack([A,T],format='csr'); B=sparse.hstack([B,U],format='csr')
 return A,B

def weights(rows,alpha):
 counts=np.bincount(y[rows],minlength=n_class)
 w=(len(rows)/(n_class*counts[y[rows]]))**alpha
 return w/w.mean()
def fit_predict(rows,Q,qd,cfg,seed=42,foldkey=None):
 fk=(foldkey,cfg['ablate'],cfg['mode'])
 if foldkey is not None and fk in features: A,B=features[fk]
 else:
  A,B=matrices(rows,Q,qd,cfg)
  if foldkey is not None: features[fk]=(A,B)
 sw=weights(rows,cfg['alpha'])
 # XGB uses original base representation for token LR variants.
 if cfg['mode']!='base':
  base=dict(cfg,mode='base'); XA,XB=matrices(rows,Q,qd,base)
 else: XA,XB=A,B
 xkey=(foldkey,cfg['alpha'],cfg['ablate'],seed)
 if foldkey is not None and xkey in xcache: px=xcache[xkey]
 else:
  model=xgb.XGBClassifier(n_estimators=180,learning_rate=.08,max_depth=5,subsample=.8,colsample_bytree=.3,tree_method='hist',objective='multi:softprob',eval_metric='mlogloss',random_state=seed,n_jobs=4)
  # No validation labels, early stopping, or test statistics enter fitting.
  model.fit(XA,y[rows],sample_weight=sw); px=model.predict_proba(XB)
  if foldkey is not None: xcache[xkey]=px
 lkey=(foldkey,cfg.get('lr_alpha',cfg['alpha']),cfg['ablate'],cfg['mode'],cfg['C'])
 if foldkey is not None and lkey in lcache: pl=lcache[lkey]
 else:
  model=make_pipeline(MaxAbsScaler(),LogisticRegression(C=cfg['C'],max_iter=1500))
  model.fit(A,y[rows],logisticregression__sample_weight=weights(rows,cfg.get('lr_alpha',cfg['alpha']))); pl=model.predict_proba(B)
  if foldkey is not None: lcache[lkey]=pl
 return px,pl
# Query transforms may see heldout feature values but never fit on them.
for cfg in configs:
 start=time.time(); ox=np.zeros((len(y),n_class)); ol=ox.copy()
 for f,(a,b) in enumerate(folds):
  # Compose all train for convenience; no statistics are fitted outside a.
  px,pl=fit_predict(a,ex,docs,cfg,foldkey=f)
  ox[b]=px[b]; ol[b]=pl[b]
 best=None
 for w in [0.,.25,.4,.5,.6,.75,1.]:
  p=w*ox[dev]+(1-w)*ol[dev]; s=f1_score(y[dev],p.argmax(1),average='macro')
  if best is None or s>best['cv_macro_f1']: best=dict(cfg,xgb_weight=w,cv_macro_f1=float(s))
 np.savez_compressed(OUT/(cfg['version']+'_oof.npz'),xgb=ox[dev],lr=ol[dev],rows=dev)
 best['seconds']=round(time.time()-start,1); results.append(best)
 pd.DataFrame(results).to_csv(OUT/'development_results.csv',index=False)
 print(json.dumps(best),flush=True)
# Freeze candidate before looking at holdout labels. Repeat alternate seed CV as a predeclared ensemble candidate.
best=max(results,key=lambda r:r['cv_macro_f1']).copy()
pred=np.zeros((len(y),n_class))
for f,(a,b) in enumerate(folds):
 px,pl=fit_predict(a,ex,docs,best,seed=137,foldkey=f)
 pred[b]=best['xgb_weight']*px[b]+(1-best['xgb_weight'])*pl[b]
base=np.load(OUT/(best['version']+'_oof.npz'))
basep=best['xgb_weight']*base['xgb']+(1-best['xgb_weight'])*base['lr']
seedscore=float(f1_score(y[dev],(.5*basep+.5*pred[dev]).argmax(1),average='macro'))
seed_ensemble=seedscore>best['cv_macro_f1']
selection=dict(best=best,seed_ensemble=seed_ensemble,seed_ensemble_cv=seedscore,selection_uses='development CV only; holdout not evaluated yet')
(OUT/'frozen_selection.json').write_text(json.dumps(selection,indent=2))
features.clear(); xcache.clear(); lcache.clear()
# Holdout evaluated once for baseline and frozen winner; never used to retune.
ha,hb=fit_predict(dev,ex,docs,best); hp=best['xgb_weight']*ha[hold]+(1-best['xgb_weight'])*hb[hold]
if seed_ensemble:
 sa,sb=fit_predict(dev,ex,docs,best,seed=137); hp=.5*hp+.5*(best['xgb_weight']*sa[hold]+(1-best['xgb_weight'])*sb[hold])
ba,bb=fit_predict(dev,ex,docs,configs[0]); bp=.4*ba[hold]+.6*bb[hold]
summary=dict(selection=selection,holdout=dict(n=len(hold),baseline_macro_f1=float(f1_score(y[hold],bp.argmax(1),average='macro')),selected_macro_f1=float(f1_score(y[hold],hp.argmax(1),average='macro')),selected_accuracy=float(accuracy_score(y[hold],hp.argmax(1)))),external_score_reference=.47959,notes=['Internal scores are not leaderboard scores.','Holdout previously may have been seen in team experiments.','No duplicate-label override; no test fit; no validation early stopping.'])
np.savez_compressed(OUT/'holdout_predictions.npz',rows=hold,baseline=bp,selected=hp)
(OUT/'holdout_classification.txt').write_text(classification_report(y[hold],hp.argmax(1),labels=np.arange(n_class),target_names=le.classes_,zero_division=0))
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)); print('HOLDOUT',json.dumps(summary),flush=True)
# Test file is read only AFTER all model and ensemble selection has been frozen.
test=pd.read_csv(DATA/'test.csv').fillna('WT'); sub=pd.read_csv(DATA/'sample_submission.csv')
assert list(test.columns)==['ID']+gene_cols and np.array_equal(test.ID,sub.ID)
te=extract(test); td=token_docs(test)
allrows=np.arange(len(y)); xa,la=fit_predict(allrows,te,td,best); tp=best['xgb_weight']*xa+(1-best['xgb_weight'])*la
if seed_ensemble:
 xa,la=fit_predict(allrows,te,td,best,seed=137); tp=.5*tp+.5*(best['xgb_weight']*xa+(1-best['xgb_weight'])*la)
sub['SUBCLASS']=le.inverse_transform(tp.argmax(1)); sub.to_csv(OUT/'submission_selected_core.csv',index=False)
np.save(OUT/'test_selected_probabilities.npy',tp)
manifest=dict(data_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [DATA/'train.csv',DATA/'test.csv']},python=sys.version,versions={m:__import__(m).__version__ for m in ['numpy','pandas','sklearn','scipy','xgboost']},selection=selection,test_used_only_for='transform and prediction after frozen selection',submissions_to_dacon=0)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('DONE',flush=True)
