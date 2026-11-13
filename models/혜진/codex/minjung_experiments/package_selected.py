import json
from pathlib import Path
p=Path(__file__).resolve().parent
sel=json.loads((p/'frozen_selection.json').read_text())
code='''from pathlib import Path
import json
HERE=Path.cwd()
if not (HERE/'run_experiments.py').exists():
    HERE=HERE/'models'/'혜진'/'codex'/'minjung_experiments'
script=HERE/'run_experiments.py'
selection=json.loads((HERE/'frozen_selection.json').read_text())
# Freeze model settings before reading test.
cfg=selection['best']
ns={'__file__':str(script.resolve())}
exec(compile(script.read_text().split('# Query transforms may see')[0],str(script),'exec'),ns)
np=ns['np']; pd=ns['pd']; DATA=ns['DATA']
test=pd.read_csv(DATA/'test.csv').fillna('WT')
sub=pd.read_csv(DATA/'sample_submission.csv')
assert list(test.columns)==['ID']+ns['gene_cols'] and np.array_equal(test.ID,sub.ID)
query=ns['extract'](test); query_docs=ns['token_docs'](test)
rows=np.arange(len(ns['y'])); w=cfg['xgb_weight']
px,pl=ns['fit_predict'](rows,query,query_docs,cfg,seed=42)
P=w*px+(1-w)*pl
if selection['seed_ensemble']:
    px,pl=ns['fit_predict'](rows,query,query_docs,cfg,seed=137)
    P=.5*P+.5*(w*px+(1-w)*pl)
sub['SUBCLASS']=ns['le'].inverse_transform(P.argmax(1))
sub.to_csv(HERE/'submission_selected_core_reproduced.csv',index=False)
print('Saved',len(sub),'predictions; no competition submission performed.')
'''
text='# v19 최종 선택 모델 — 전체 train 재학습 및 제출 후보 생성\n\n개발 검증으로 고정한 설정입니다. test는 transform/predict에만 사용합니다. 모델 또는 앙상블 선택에 test/holdout 정답을 사용하지 않습니다. 학습 코드와 원본 복사 노트북을 함께 보존하세요.\n\n```json\n'+json.dumps(sel,ensure_ascii=False,indent=2)+'\n```\n\nPublic 0.47959 초과 여부는 아직 알 수 없습니다. 확인용 점수는 RESULTS.md에 기록합니다.\n'
nb=dict(cells=[dict(cell_type='markdown',metadata={},source=text.splitlines(True)),dict(cell_type='code',execution_count=None,metadata={},outputs=[],source=code.splitlines(True))],metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python')),nbformat=4,nbformat_minor=5)
(p/'v19_selected_seed_ensemble.ipynb').write_text(json.dumps(nb,ensure_ascii=False,indent=1))
