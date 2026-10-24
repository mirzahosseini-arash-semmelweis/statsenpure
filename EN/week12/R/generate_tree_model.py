"""Regenerate the seven-leaf, three-predictor teaching tree.

Standalone synthetic teaching model, deliberately distinct from the earlier
five-biomarker figure. Not patient data or a clinical risk model.
Dependencies for offline regeneration only: numpy, scikit-learn.
"""
import json
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from pathlib import Path

r = np.random.default_rng(12)
x = r.normal(size=(900, 3))
logit = 1.2*x[:, 0] - 0.85*x[:, 1] + 1.45*(x[:, 2] > 0.55) - 0.35
p = 1/(1 + np.exp(-logit))
y = (r.random(len(x)) < p).astype(int)
model = DecisionTreeClassifier(max_depth=4, max_leaf_nodes=7,
                               min_samples_leaf=30, random_state=4).fit(x,y)
t = model.tree_
assert model.get_n_leaves() == 7 and model.get_depth() == 4
assert set(t.feature[t.feature >= 0]) == {0, 1, 2}
out = {
  "features": ["Amino acid A", "Lipid B", "Metabolite C"],
  "children_left": t.children_left.tolist(),
  "children_right": t.children_right.tolist(),
  "feature": t.feature.tolist(),
  "threshold": np.round(t.threshold, 4).tolist(),
  "value": np.round(t.value[:, 0, :], 6).tolist(),
  "samples": t.n_node_samples.tolist()
}
Path(__file__).with_name('tree_model.json').write_text(json.dumps(out,indent=2)+'\n')
print('nodes:',t.node_count,'leaves:',model.get_n_leaves(),'depth:',model.get_depth())
print('features used:',sorted(set(t.feature[t.feature>=0])))
