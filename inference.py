from pathlib import Path
import re
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from rdkit import Chem
from torch_geometric.data import Data, Batch
ATOM_TYPES = [
    1, 5, 6, 7, 8, 9, 14, 15, 16, 17,
    35, 53
]

HYBRIDIZATIONS = [
    Chem.rdchem.HybridizationType.SP,
    Chem.rdchem.HybridizationType.SP2,
    Chem.rdchem.HybridizationType.SP3,
    Chem.rdchem.HybridizationType.SP3D,
    Chem.rdchem.HybridizationType.SP3D2
]

BOND_TYPES = [
    Chem.rdchem.BondType.SINGLE,
    Chem.rdchem.BondType.DOUBLE,
    Chem.rdchem.BondType.TRIPLE,
    Chem.rdchem.BondType.AROMATIC
]

def one_hot_unknown(value, choices):
    return [float(value == c) for c in choices] + [
        float(value not in choices)
    ]

def atom_features(atom):
    features = []
    features += one_hot_unknown(
        atom.GetAtomicNum(), ATOM_TYPES
    )
    features += one_hot_unknown(
        atom.GetHybridization(), HYBRIDIZATIONS
    )
    features += [
        atom.GetDegree() / 6.0,
        atom.GetFormalCharge() / 4.0,
        atom.GetTotalNumHs() / 4.0,
        float(atom.GetIsAromatic()),
        float(atom.IsInRing()),
        atom.GetMass() / 200.0
    ]
    return features

def bond_features(bond):
    return (
        one_hot_unknown(bond.GetBondType(), BOND_TYPES)
        + [
            float(bond.GetIsConjugated()),
            float(bond.IsInRing())
        ]
    )

ATOM_DIM = len(atom_features(Chem.MolFromSmiles("C").GetAtomWithIdx(0)))
BOND_DIM = len(bond_features(Chem.MolFromSmiles("CC").GetBondWithIdx(0)))

def smiles_to_graph(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")

    x = torch.tensor(
        [atom_features(atom) for atom in mol.GetAtoms()],
        dtype=torch.float32
    )

    edges = []
    edge_attrs = []

    for bond in mol.GetBonds():
        i = bond.GetBeginAtomIdx()
        j = bond.GetEndAtomIdx()
        feat = bond_features(bond)

        edges.extend([[i, j], [j, i]])
        edge_attrs.extend([feat, feat])

    if edges:
        edge_index = torch.tensor(
            edges, dtype=torch.long
        ).t().contiguous()

        edge_attr = torch.tensor(
            edge_attrs, dtype=torch.float32
        )
    else:
        edge_index = torch.empty(
            (2, 0), dtype=torch.long
        )
        edge_attr = torch.empty(
            (0, BOND_DIM), dtype=torch.float32
        )

    return Data(
        x=x,
        edge_index=edge_index,
        edge_attr=edge_attr
    )

# AttentiveFP
from torch_geometric.nn import AttentiveFP

class HybridAttentiveFP(nn.Module):
    def __init__(
        self,
        atom_dim,
        bond_dim,
        solvent_dim,
        hidden_dim=512,
        num_layers=3,
        num_timesteps=3,
        dropout=0.2
    ):
        super().__init__()

        # Molecular graph encoder
        self.graph_encoder = AttentiveFP(
            in_channels=atom_dim,
            hidden_channels=hidden_dim,
            out_channels=hidden_dim,
            edge_dim=bond_dim,
            num_layers=num_layers,
            num_timesteps=num_timesteps,
            dropout=dropout
        )

        # Solvent composition encoder
        self.solvent_encoder = nn.Sequential(
            nn.Linear(solvent_dim, 128),
            nn.ReLU(),
            nn.LayerNorm(128),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU()
        )

        # Combined regression head
        self.regressor = nn.Sequential(
            nn.Linear(hidden_dim + 64, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

    def forward(self, data):

        # Graph-level molecular representation
        graph_embedding = self.graph_encoder(
            data.x,
            data.edge_index,
            data.edge_attr,
            data.batch
        )

        # Solvent representation
        solvent_embedding = self.solvent_encoder(
            data.solvent
        )

        # Combine molecular and solvent features
        combined = torch.cat(
            [graph_embedding, solvent_embedding],
            dim=1
        )

        return self.regressor(combined)




# MPNN
from torch_geometric.nn import NNConv, Set2Set
class HybridMPNN(nn.Module):
    def __init__(
        self,
        atom_dim,
        bond_dim,
        solvent_dim,
        hidden_dim=128,
        num_steps=3,
        set2set_steps=3,
        dropout=0.2
    ):
        super().__init__()

        self.num_steps = num_steps

        self.atom_encoder = nn.Linear(
            atom_dim, hidden_dim
        )

        # Bond-conditioned message function
        edge_network = nn.Sequential(
            nn.Linear(bond_dim, 128),
            nn.ReLU(),
            nn.Linear(128, hidden_dim * hidden_dim)
        )

        self.conv = NNConv(
            in_channels=hidden_dim,
            out_channels=hidden_dim,
            nn=edge_network,
            aggr="mean"
        )

        self.gru = nn.GRU(
            hidden_dim, hidden_dim
        )

        self.pool = Set2Set(
            hidden_dim,
            processing_steps=set2set_steps
        )

        self.solvent_encoder = nn.Sequential(
            nn.Linear(solvent_dim, 128),
            nn.ReLU(),
            nn.LayerNorm(128),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU()
        )

        self.regressor = nn.Sequential(
            nn.Linear(hidden_dim * 2 + 64, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

    def forward(self, data):
        x = F.relu(self.atom_encoder(data.x))

        h = x.unsqueeze(0)

        for _ in range(self.num_steps):
            m = F.relu(
                self.conv(x, data.edge_index, data.edge_attr)
            )

            x, h = self.gru(m.unsqueeze(0), h)
            x = x.squeeze(0)

        graph_embedding = self.pool(
            x, data.batch
        )

        solvent_embedding = self.solvent_encoder(
            data.solvent
        )

        combined = torch.cat(
            [graph_embedding, solvent_embedding],
            dim=1
        )

        return self.regressor(combined)




def canonicalize_smiles(smiles):
    mol = Chem.MolFromSmiles(str(smiles).strip())
    if mol is None or mol.GetNumAtoms() == 0:
        raise ValueError('SMILES is empty or invalid')
    return Chem.MolToSmiles(mol, canonical=True)

def normalize_ratios(names, text, allowed):
    if not names or len(names) != len(set(names)):
        raise ValueError('Select at least one solvent without duplicates')
    if set(names) - set(allowed):
        raise ValueError('The selected solvent is not supported by this model')
    parts = re.split(r'[:;\s]+', str(text).strip())
    try:
        values = np.array([float(x) for x in parts], dtype=np.float64)
    except ValueError:
        raise ValueError('Enter ratios such as 6:1 or 0.857:0.143')
    if len(values) != len(names):
        raise ValueError('Provide one ratio for each selected solvent')
    if not np.isfinite(values).all() or (values < 0).any() or not np.isfinite(values.sum()) or values.sum() <= 0:
        raise ValueError('Ratios must be finite, nonnegative, and have a positive total')
    return dict(zip(names, values / values.sum()))

class Predictor:
    def __init__(self, checkpoint_path, expected=None):
        # Accept either a configured file path or an uploaded binary stream.
        self.path = Path(checkpoint_path) if isinstance(checkpoint_path, (str, Path)) else None
        if self.path is not None and not self.path.is_file():
            raise FileNotFoundError(f'Checkpoint not found: {self.path}')
        saved = torch.load(self.path if self.path is not None else checkpoint_path,
                           map_location='cpu', weights_only=True)
        self.name = saved['model_name']
        if expected is not None and self.name != expected:
            raise ValueError(f'Expected a {expected} checkpoint, received {self.name}')
        classes = {'AttentiveFP': HybridAttentiveFP, 'MPNN': HybridMPNN}
        self.solvents = list(saved['solvent_cols'])
        self.inputs = list(saved['input_solvent_cols'])
        if self.inputs != self.solvents + ['missing_mobile_phase']:
            raise ValueError('Unsupported checkpoint schema')
        config = saved['model_config']
        if (config['atom_dim'],config['bond_dim'],config['solvent_dim']) != (ATOM_DIM,BOND_DIM,len(self.inputs)):
            raise ValueError('Feature dimensions do not match the checkpoint')
        self.model = classes[self.name](**config).cpu().eval()
        self.model.load_state_dict(saved['model_state_dict'], strict=True)

    @torch.inference_mode()
    def predict(self, smiles, names, ratio_text):
        canonical = canonicalize_smiles(smiles)
        mixture = normalize_ratios(names, ratio_text, self.solvents)
        graph = smiles_to_graph(canonical)
        graph.solvent = torch.tensor([[mixture.get(s,0.) for s in self.solvents]+[0.]], dtype=torch.float32)
        value = float(self.model(Batch.from_data_list([graph])).item())
        return {'SMILES': canonical, 'Rf': value, 'mixture': mixture}

