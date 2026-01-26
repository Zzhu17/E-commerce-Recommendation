from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import numpy as np
import torch
from torch import nn

from src.evaluation.metrics import ndcg_at_k


@dataclass
class LightGCNConfig:
    embedding_dim: int = 64
    num_layers: int = 3
    lr: float = 1e-3
    batch_size: int = 2048
    num_neg: int = 1
    epochs: int = 50
    reg: float = 1e-4
    seed: int = 42
    device: Optional[str] = None
    eval_k: int = 10
    eval_every: int = 5
    patience: int = 5
    score_batch: int = 512


class LightGCN(nn.Module):
    def __init__(self, num_users: int, num_items: int, embedding_dim: int, num_layers: int, norm_adj):
        super().__init__()
        self.num_users = num_users
        self.num_items = num_items
        self.num_layers = num_layers
        self.user_emb = nn.Embedding(num_users, embedding_dim)
        self.item_emb = nn.Embedding(num_items, embedding_dim)
        nn.init.xavier_uniform_(self.user_emb.weight)
        nn.init.xavier_uniform_(self.item_emb.weight)
        self.norm_adj = norm_adj

    def forward(self):
        all_emb = torch.cat([self.user_emb.weight, self.item_emb.weight], dim=0)
        embs = [all_emb]
        for _ in range(self.num_layers):
            all_emb = torch.sparse.mm(self.norm_adj, all_emb)
            embs.append(all_emb)
        out = torch.stack(embs, dim=0).mean(dim=0)
        user_out, item_out = torch.split(out, [self.num_users, self.num_items], dim=0)
        return user_out, item_out


def build_norm_adj(edges: np.ndarray, num_users: int, num_items: int, device: torch.device):
    if edges.size == 0:
        raise ValueError("No edges provided for LightGCN.")
    users = torch.tensor(edges[:, 0], dtype=torch.long, device=device)
    items = torch.tensor(edges[:, 1], dtype=torch.long, device=device) + num_users
    weights = None
    if edges.shape[1] >= 3:
        weights = torch.tensor(edges[:, 2], dtype=torch.float32, device=device)
    row = torch.cat([users, items])
    col = torch.cat([items, users])
    indices = torch.stack([row, col], dim=0)
    if weights is None:
        values = torch.ones(indices.size(1), dtype=torch.float32, device=device)
    else:
        values = torch.cat([weights, weights])
    n_nodes = num_users + num_items
    adj = torch.sparse_coo_tensor(indices, values, (n_nodes, n_nodes))
    deg = torch.sparse.sum(adj, dim=1).to_dense()
    deg_inv_sqrt = torch.pow(deg, -0.5)
    deg_inv_sqrt[torch.isinf(deg_inv_sqrt)] = 0.0
    d_mat = deg_inv_sqrt
    norm_values = d_mat[row] * values * d_mat[col]
    norm_adj = torch.sparse_coo_tensor(indices, norm_values, (n_nodes, n_nodes))
    return norm_adj


class NegativeSampler:
    def __init__(self, user_pos: Dict[int, set], num_items: int, seed: int = 42):
        self.user_pos = user_pos
        self.num_items = num_items
        self.rng = np.random.default_rng(seed)

    def sample(self, users: np.ndarray, num_neg: int) -> np.ndarray:
        negs = np.empty((len(users), num_neg), dtype=np.int64)
        for idx, u in enumerate(users):
            pos = self.user_pos.get(int(u), set())
            for j in range(num_neg):
                while True:
                    item = int(self.rng.integers(0, self.num_items))
                    if item not in pos:
                        negs[idx, j] = item
                        break
        return negs


def train_lightgcn(
    edges: np.ndarray,
    user_pos: Dict[int, set],
    num_users: int,
    num_items: int,
    config: LightGCNConfig,
    val_y_true: Optional[Dict[int, set]] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    torch.manual_seed(config.seed)
    np.random.seed(config.seed)
    device = torch.device(config.device or ("cuda" if torch.cuda.is_available() else "cpu"))

    norm_adj = build_norm_adj(edges, num_users, num_items, device)
    model = LightGCN(num_users, num_items, config.embedding_dim, config.num_layers, norm_adj).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)

    sampler = NegativeSampler(user_pos, num_items, seed=config.seed)
    users = edges[:, 0].astype(np.int64)
    items = edges[:, 1].astype(np.int64)
    idx = np.arange(len(edges))

    best_ndcg = -1.0
    best_user_emb = None
    best_item_emb = None
    patience_left = config.patience

    for epoch in range(1, config.epochs + 1):
        np.random.shuffle(idx)
        for start in range(0, len(idx), config.batch_size):
            batch_idx = idx[start : start + config.batch_size]
            batch_users = users[batch_idx]
            batch_pos = items[batch_idx]
            batch_negs = sampler.sample(batch_users, config.num_neg)

            u = torch.tensor(batch_users, dtype=torch.long, device=device)
            i = torch.tensor(batch_pos, dtype=torch.long, device=device)
            j = torch.tensor(batch_negs, dtype=torch.long, device=device)

            user_emb, item_emb = model()
            u_emb = user_emb[u]
            i_emb = item_emb[i]
            j_emb = item_emb[j]

            pos_scores = (u_emb * i_emb).sum(dim=1)
            neg_scores = (u_emb[:, None, :] * j_emb).sum(dim=2)
            loss = -torch.log(torch.sigmoid(pos_scores[:, None] - neg_scores) + 1e-8).mean()
            reg = config.reg * (u_emb.norm(2).pow(2) + i_emb.norm(2).pow(2) + j_emb.norm(2).pow(2)) / len(u)
            loss = loss + reg

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if val_y_true and config.eval_every and epoch % config.eval_every == 0:
            user_emb_eval, item_emb_eval = model()
            user_emb_np = user_emb_eval.detach().cpu().numpy()
            item_emb_np = item_emb_eval.detach().cpu().numpy()
            recs = recommend_lightgcn(
                user_emb_np,
                item_emb_np,
                user_pos,
                config.eval_k,
                batch_size=config.score_batch,
            )
            ndcg = ndcg_at_k(val_y_true, recs, config.eval_k)
            if ndcg > best_ndcg + 1e-6:
                best_ndcg = ndcg
                best_user_emb = user_emb_np
                best_item_emb = item_emb_np
                patience_left = config.patience
            else:
                patience_left -= 1
                if patience_left <= 0:
                    break

    if best_user_emb is None or best_item_emb is None:
        user_emb, item_emb = model()
        best_user_emb = user_emb.detach().cpu().numpy()
        best_item_emb = item_emb.detach().cpu().numpy()

    metrics = {"device": str(device), "best_ndcg": best_ndcg, "stopped_epoch": epoch}
    return best_user_emb, best_item_emb, metrics


def recommend_lightgcn(
    user_emb: np.ndarray,
    item_emb: np.ndarray,
    user_pos: Dict[int, set],
    k: int,
    batch_size: int = 512,
) -> Dict[int, List[int]]:
    n_users = user_emb.shape[0]
    recommendations: Dict[int, List[int]] = {}
    for start in range(0, n_users, batch_size):
        end = min(start + batch_size, n_users)
        batch_users = np.arange(start, end)
        batch_scores = user_emb[batch_users] @ item_emb.T
        for idx, u in enumerate(batch_users):
            seen = user_pos.get(int(u), set())
            if seen:
                batch_scores[idx, list(seen)] = -np.inf
        topk = np.argpartition(batch_scores, -k)[:, -k:]
        topk_sorted = np.take_along_axis(topk, np.argsort(batch_scores[np.arange(end - start)[:, None], topk], axis=1)[:, ::-1], axis=1)
        for i, u in enumerate(batch_users):
            recommendations[int(u)] = topk_sorted[i].tolist()
    return recommendations
