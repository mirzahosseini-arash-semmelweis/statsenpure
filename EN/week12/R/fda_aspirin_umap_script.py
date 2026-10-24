import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, Lipinski, Crippen, Draw
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors

# -----------------------------
# User-configurable settings
# -----------------------------
INPUT_CSV = 'fda_drugs.csv'
OUTPUT_SVG = 'fda_aspirin_umap.svg'
TARGET_NAME = 'Acetylsalicylic acid'
N_NEIGHBORS = 3
RANDOM_STATE = 42
ALLOW_PCA_FALLBACK = True

# -----------------------------
# Try to import UMAP
# -----------------------------
UMAP_AVAILABLE = False
umap = None
try:
    import umap.umap_ as umap  # type: ignore
    UMAP_AVAILABLE = True
except Exception:
    if not ALLOW_PCA_FALLBACK:
        raise ImportError(
            "umap-learn is required. Install with: pip install umap-learn"
        )

# -----------------------------
# Descriptor functions
# -----------------------------
DESCRIPTOR_FUNCS = {
    'MolWt': Descriptors.MolWt,
    'ExactMolWt': Descriptors.ExactMolWt,
    'MolLogP': Crippen.MolLogP,
    'TPSA': rdMolDescriptors.CalcTPSA,
    'HeavyAtomCount': Lipinski.HeavyAtomCount,
    'NumHAcceptors': Lipinski.NumHAcceptors,
    'NumHDonors': Lipinski.NumHDonors,
    'NumRotatableBonds': Lipinski.NumRotatableBonds,
    'RingCount': Lipinski.RingCount,
    'NumAromaticRings': rdMolDescriptors.CalcNumAromaticRings,
    'FractionCSP3': rdMolDescriptors.CalcFractionCSP3,
    'NumHeteroatoms': Lipinski.NumHeteroatoms,
}

DESCRIPTOR_NAMES = list(DESCRIPTOR_FUNCS.keys())

# -----------------------------
# Data loading and descriptor calculation
# -----------------------------
def load_and_featurize(csv_path: str):
    df = pd.read_csv(csv_path)
    rows = []
    bad = []
    for idx, row in df.iterrows():
        mol = Chem.MolFromSmiles(str(row['smiles']))
        if mol is None:
            bad.append(idx)
            continue
        values = {name: func(mol) for name, func in DESCRIPTOR_FUNCS.items()}
        rows.append({
            'orig_index': idx,
            'name': row['name'],
            'smiles': row['smiles'],
            'mol': mol,
            **values,
        })
    feat = pd.DataFrame(rows)
    return feat, bad


def compute_embedding(X_scaled: np.ndarray):
    if UMAP_AVAILABLE:
        reducer = umap.UMAP(
            n_components=2,
            n_neighbors=20,
            min_dist=0.15,
            metric='euclidean',
            random_state=RANDOM_STATE,
        )
        coords = reducer.fit_transform(X_scaled)
        method_name = 'UMAP'
    else:
        warnings.warn('umap-learn not available; using PCA fallback for preview.')
        reducer = PCA(n_components=2, random_state=RANDOM_STATE)
        coords = reducer.fit_transform(X_scaled)
        method_name = 'PCA fallback'
    return coords, method_name


def molecule_image(mol, size=(500, 350)):
    img = Draw.MolToImage(mol, size=size)
    return np.asarray(img)


def draw_structure_tile(ax, mol, title, subtitle='', border='#cbd5e1', title_color='#111827'):
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(True)

    for spine in ax.spines.values():
        spine.set_edgecolor(border)
        spine.set_linewidth(1.5)

    ax.imshow(molecule_image(mol), interpolation='antialiased')
    ax.set_aspect('equal')
    ax.set_anchor('C')

    ax.set_title(
        title,
        fontsize=10.3,
        fontweight='bold',
        color=title_color,
        loc='left',
        pad=5
    )

    if subtitle:
        ax.text(
            0.01, -0.06,
            subtitle,
            transform=ax.transAxes,
            ha='left', va='top',
            fontsize=8.4,
            color='#475569'
        )

def main(input_csv=INPUT_CSV, output_svg=OUTPUT_SVG):
    feat, bad = load_and_featurize(input_csv)
    if feat.empty:
        raise RuntimeError('No valid molecules parsed from input file.')

    target_mask = feat['name'].str.lower() == TARGET_NAME.lower()
    if not target_mask.any():
        raise ValueError(f"Target '{TARGET_NAME}' not found in input data.")

    X = feat[DESCRIPTOR_NAMES].astype(float)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    coords, method_name = compute_embedding(X_scaled)
    feat['x'] = coords[:, 0]
    feat['y'] = coords[:, 1]

    target_idx = feat.index[target_mask][0]

    nn = NearestNeighbors(n_neighbors=N_NEIGHBORS + 1, metric='euclidean')
    nn.fit(coords)
    distances, indices = nn.kneighbors(coords[[target_idx]])
    neighbor_idx = indices[0][1:]
    neighbor_dist = distances[0][1:]

    # -----------------------------
    # Figure layout
    # -----------------------------
    plt.rcParams.update({
        'font.size': 10,
        'font.family': 'DejaVu Sans',
    })

    fig = plt.figure(figsize=(13.4, 7.2))
    fig.subplots_adjust(
        left=0.035,
        right=0.985,
        bottom=0.075,
        top=0.84
    )

    gs = GridSpec(
        1, 3,
        figure=fig,
        width_ratios=[0.75, 2.35, 1.55],
        wspace=0.28
    )

    # Left: descriptor list
    ax_left = fig.add_subplot(gs[0, 0])
    ax_left.axis('off')

    ax_left.set_title(
        'RDKit molecular\ndescriptors',
        fontsize=13.8,
        fontweight='bold',
        loc='left',
        pad=10
    )

    ax_left.text(
        0.0, 0.965,
        'Each drug is mapped from a\nnumeric descriptor vector:',
        transform=ax_left.transAxes,
        ha='left', va='top',
        fontsize=11.8,
        color='#334155'
    )

    descriptor_text = '\n'.join([f'• {name}' for name in DESCRIPTOR_NAMES])

    ax_left.text(
        0.02, 0.81,
        descriptor_text,
        transform=ax_left.transAxes,
        ha='left', va='top',
        fontsize=12.0,
        color='#0f172a',
        linespacing=1.38
    )

    # Center: embedding
    ax_mid = fig.add_subplot(gs[0, 1])

    ax_mid.scatter(
        feat['x'], feat['y'],
        s=24,
        c='#94a3b8',
        alpha=0.78,
        edgecolors='white',
        linewidths=0.2
    )

    # highlight neighbors
    ax_mid.scatter(feat.loc[neighbor_idx, 'x'], feat.loc[neighbor_idx, 'y'],
                   s=54, c='#2563eb', edgecolors='white', linewidths=0.8, zorder=3)

    # highlight aspirin
    ax_mid.scatter(feat.loc[target_idx, 'x'], feat.loc[target_idx, 'y'],
                   s=110, c='#dc2626', edgecolors='white', linewidths=1.3, zorder=4)

    # Labels
    ax_mid.annotate(
        'Acetylsalicylic acid',
        (feat.loc[target_idx, 'x'], feat.loc[target_idx, 'y']),
        xytext=(10, 10),
        textcoords='offset points',
        fontsize=12.3,
        color='#dc2626',
        fontweight='bold',
        bbox=dict(
            boxstyle='round,pad=0.20',
            fc='white',
            ec='#fecaca',
            lw=0.8
        )
    )

    ax_mid.set_title(
        f'{method_name} embedding of descriptor space',
        fontsize=14.0,
        fontweight='bold',
        pad=10
    )

    ax_mid.set_xlabel(f'{method_name} 1', fontsize=12.4)
    ax_mid.set_ylabel(f'{method_name} 2', fontsize=12.4)

    ax_mid.tick_params(axis='both', labelsize=11.2)
    ax_mid.grid(True, alpha=0.28, color='#cbd5e1')
    for spine in ax_mid.spines.values():
        spine.set_color('#94a3b8')

    """
    # Right: target + neighbors structures
    ax_right_bg = fig.add_subplot(gs[0, 2])
    ax_right_bg.axis('off')

    ax_right_bg.set_title(
        'Structures: aspirin and 3 nearest neighbors',
        fontsize=12.8,
        fontweight='bold',
        loc='left',
        pad=8
    )

    ax_right_bg.text(
        0.0, 0.988,
        f'Nearest neighbors computed in {method_name} 2D space.',
        transform=ax_right_bg.transAxes,
        ha='left', va='top',
        fontsize=9.5,
        color='#475569'
    )

    # Add a small blank spacer row at the top
    gs_right = GridSpecFromSubplotSpec(
        5, 1,
        subplot_spec=gs[0, 2],
        height_ratios=[0.22, 1, 1, 1, 1],
        hspace=0.58
    )

    # invisible spacer
    ax_spacer = fig.add_subplot(gs_right[0, 0])
    ax_spacer.axis('off')

    # target tile
    ax0 = fig.add_subplot(gs_right[1, 0])
    draw_structure_tile(
        ax0,
        feat.loc[target_idx, 'mol'],
        'Acetylsalicylic acid',
        border='#dc2626',
        title_color='#991b1b'
    )

    # neighbor tiles
    for row_i, (idx, dist) in enumerate(zip(neighbor_idx, neighbor_dist), start=2):
        axn = fig.add_subplot(gs_right[row_i, 0])
        draw_structure_tile(
            axn,
            feat.loc[idx, 'mol'],
            f'{row_i - 1}. {feat.loc[idx, "name"]}',
            subtitle=f'{method_name} distance = {dist:.3f}',
            border='#93c5fd',
            title_color='#1d4ed8'
        )
"""

    # ------------------------------------------------------------
    # Right panel: molecular structures in a 1–2–1 layout
    # ------------------------------------------------------------

    ax_right_bg = fig.add_subplot(gs[0, 2])
    ax_right_bg.axis('off')

    ax_right_bg.set_title(
        'Molecular structures',
        fontsize=13.5,
        fontweight='bold',
        loc='left',
        pad=2
    )

    # 4 rows: spacer + aspirin + two neighbors + last neighbor
    gs_right = GridSpecFromSubplotSpec(
        4, 2,
        subplot_spec=gs[0, 2],
        height_ratios=[0.08, 1.1, 1.15, 1.1],
        width_ratios=[1, 1],
        hspace=0.75,
        wspace=0.22
    )

    # Spacer for panel header
    ax_spacer = fig.add_subplot(gs_right[0, :])
    ax_spacer.axis('off')


    # Row 1: aspirin across both columns
    ax0 = fig.add_subplot(gs_right[1, :])

    draw_structure_tile(
        ax0,
        feat.loc[target_idx, 'mol'],
        'Acetylsalicylic acid',
        border='#dc2626',
        title_color='#991b1b'
    )


    # Row 2: neighbors 1 and 2 side by side
    for rank in [1, 2]:

        idx = neighbor_idx[rank - 1]

        axn = fig.add_subplot(
            gs_right[2, rank - 1]
        )

        draw_structure_tile(
            axn,
            feat.loc[idx, 'mol'],
            f'{rank}. {feat.loc[idx, "name"]}',
            subtitle=f'Distance = {neighbor_dist[rank - 1]:.3f}',
            border='#93c5fd',
            title_color='#1d4ed8'
        )


    # Row 3: neighbor 3 across both columns
    idx = neighbor_idx[2]

    ax3 = fig.add_subplot(gs_right[3, :])

    draw_structure_tile(
        ax3,
        feat.loc[idx, 'mol'],
        f'3. {feat.loc[idx, "name"]}',
        subtitle=f'Distance = {neighbor_dist[2]:.3f}',
        border='#93c5fd',
        title_color='#1d4ed8'
    )

    fig.text(
        0.012, 0.968,
        'FDA drugs: descriptor-space embedding and aspirin neighborhood',
        ha='left', va='top',
        fontsize=16,
        fontweight='bold',
        color='#111827'
    )

    out_path = Path(output_svg)
    fig.savefig(out_path, format='svg', bbox_inches='tight')
    fig.savefig(out_path.with_suffix('.png'), dpi=200, bbox_inches='tight')

    # Also save a compact CSV of the nearest neighbors
    nn_table = feat.loc[[target_idx] + list(neighbor_idx), ['name', 'smiles', 'x', 'y']].copy()
    nn_table.insert(0, 'rank', ['target'] + list(range(1, len(neighbor_idx) + 1)))
    nn_table.to_csv(out_path.with_suffix('.neighbors.csv'), index=False)

    print(f'Saved figure to {out_path}')
    print(f'Projection method used: {method_name}')
    print('Nearest neighbors:')
    for rank, (idx, dist) in enumerate(zip(neighbor_idx, neighbor_dist), start=1):
        print(f'  {rank}. {feat.loc[idx, "name"]} (distance {dist:.3f})')


if __name__ == '__main__':
    main()
