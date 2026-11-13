"""Create independently runnable version notebooks without executing expensive training."""
import ast,json
from pathlib import Path
out=Path(__file__).resolve().parent
source=(out/'run_experiments.py').read_text()
tree=ast.parse(source)
# Recover literal configs without importing runner (which would start the sweep).
ns={}
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='configs' for t in node.targets): exec(compile(ast.Module(body=[node],type_ignores=[]),'configs','exec'),ns)
 if isinstance(node,ast.AugAssign) and isinstance(node.target,ast.Name) and node.target.id=='configs': exec(compile(ast.Module(body=[node],type_ignores=[]),'configs','exec'),ns)
results={}
if (out/'development_results.csv').exists():
 import csv
 results={r['version']:r for r in csv.DictReader((out/'development_results.csv').open())}
for cfg in ns['configs']:
 version=cfg['version']
 intro=f'''# 민정 모델 개선 실험 — {version}\n\n원본: `../model_민정_v10_original.ipynb` (수정하지 않은 복사본).\n\n설정: `{json.dumps(cfg,ensure_ascii=False)}`\n\ntrain 내부 그룹 3-fold 개발 검증입니다. 분리된 확인용 holdout과 test는 이 노트북에서 평가하거나 읽지 않습니다. 특징 사전·빈도 필터·스케일·IDF·가중치는 각 학습 fold로만 적합합니다. 학습 180회 고정, 중복 라벨 덮어쓰기 없음. 아래 실행 셀은 해당 버전을 재학습합니다.\n\n개발 OOF에서 앙상블 비중을 선택하므로 이 점수에는 선택 편향이 있습니다. 최종 확인 점수는 `summary.json`을 보세요.\n'''
 if version in results: intro+='\n저장된 개발 결과:\n```json\n'+json.dumps(results[version],ensure_ascii=False,indent=2)+'\n```\n'
 code='''from pathlib import Path
import json
HERE=Path.cwd()
if not (HERE/'run_experiments.py').exists():
    HERE=HERE/'models'/'혜진'/'codex'/'minjung_experiments'
script=HERE/'run_experiments.py'
ns={'__file__':str(script.resolve())}
# Load train-only functions/setup; stop before the full sweep loop.
exec(compile(script.read_text().split('# Query transforms may see')[0],str(script),'exec'),ns)
'''+f"cfg={cfg!r}\n"+'''np=ns['np']; y=ns['y']; dev=ns['dev']
ox=np.zeros((len(y),ns['n_class'])); ol=ox.copy()
for f,(a,b) in enumerate(ns['folds']):
    px,pl=ns['fit_predict'](a,ns['ex'],ns['docs'],cfg,foldkey=f)
    ox[b]=px[b]; ol[b]=pl[b]
    print('fold completed',f)
from sklearn.metrics import f1_score
scores=[(float(f1_score(y[dev],(w*ox[dev]+(1-w)*ol[dev]).argmax(1),average='macro')),w) for w in [0.,.25,.4,.5,.6,.75,1.]]
score,w=max(scores,key=lambda t:t[0])
print({'version':cfg['version'],'development_macro_f1':score,'xgb_weight':w})
np.savez_compressed(HERE/(cfg['version']+'_oof.npz'),xgb=ox[dev],lr=ol[dev],rows=dev)
'''
 nb=dict(cells=[dict(cell_type='markdown',metadata={},source=intro.splitlines(True)),dict(cell_type='code',execution_count=None,metadata={},outputs=[],source=code.splitlines(True))],metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python')),nbformat=4,nbformat_minor=5)
 (out/(version+'.ipynb')).write_text(json.dumps(nb,ensure_ascii=False,indent=1))
print('Packaged',len(ns['configs']),'notebooks')
