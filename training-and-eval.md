# Skill: training-and-eval
Use when: models, training, metrics, experiments, Colab runs.

## Smoke test BEFORE every real run (saves tokens and time)
64 objects, 1 epoch, CPU, must finish in about a minute and produce a metric. Only then run for real.

## Config (one YAML per experiment, in configs/)
```yaml
exp: C_pretrained
model: resnet18            # smallcnn | resnet18
pretrained: true
bands: [g, r, i, z, y]     # always this order (H16)
train_pipelines: [D1, D2]
eval_pipelines: [D1, D2]
data_source: small         # small | main | band-g ... (H3: never mix)
seed: 0
epochs: 20
batch_size: 128
lr: 1.0e-4
weight_decay: 1.0e-4
```
train.py --config <file>. Seed Python, NumPy, torch. Log the config + git commit with each run.

## Models
- SmallCNN: 3-4 blocks of Conv-BN-ReLU (+pool), global average pool, Linear -> 1 logit.
- ResNet-18 for N channels:
```python
import torch.nn as nn, torchvision
def make_resnet18(in_ch, pretrained):
    w = torchvision.models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
    m = torchvision.models.resnet18(weights=w)
    old = m.conv1
    m.conv1 = nn.Conv2d(in_ch, 64, 7, 2, 3, bias=False)
    if pretrained:   # reuse RGB filters: average them and repeat across channels
        m.conv1.weight.data = old.weight.data.mean(1, keepdim=True).repeat(1, in_ch, 1, 1) * (3.0 / in_ch)
    m.maxpool = nn.Identity()     # cutouts are tiny: do not shrink them early (log H,W in STATE.md)
    m.fc = nn.Linear(512, 1)
    return m
```
Loss BCEWithLogitsLoss. AdamW. Early stopping on val loss (patience 5). AMP only if CUDA.
Save best checkpoint to models/ (gitignored). Fair comparison = change ONE thing only (H9).

## Metrics (src/evaluate.py), per pipeline AND overall (H8)
```python
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve
def tpr_at_fpr(y, s, target):
    fpr, tpr, _ = roc_curve(y, s)
    return float(np.interp(target, fpr, tpr))
def all_metrics(y, s):
    return dict(auc=roc_auc_score(y, s), ap=average_precision_score(y, s),
                tpr_fpr1e2=tpr_at_fpr(y, s, 1e-2), tpr_fpr1e3=tpr_at_fpr(y, s, 1e-3))
```
Small val sets make TPR@FPR=1e-3 noisy: report it, but say how many negatives it rests on.

## results/runs.csv header
run_id,phase,exp,model,pretrained,bands,train_pipelines,eval_pipeline,data_source,seed,auc,ap,tpr_fpr1e2,tpr_fpr1e3,commit,notes
One row per (run, eval_pipeline). Aggregate mean +/- std over seeds in scripts, never by hand.

## Long runs / Colab
The agent usually has no GPU. If a run is slow, write docs/COLAB_RUN.md: ready-to-paste cells
(clone repo, pip install -r requirements.txt, set LENS_DATA_ROOT, run train.py with a config).
The owner runs it, then copies results/ and figures/ back into the repo.
