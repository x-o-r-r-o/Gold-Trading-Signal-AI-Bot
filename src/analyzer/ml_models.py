# src/analyzer/ml_models.py

from typing import Dict, List, Tuple, Optional
import json
import os

import torch
import torch.nn as nn

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # YAML optional; JSON always supported


class SignalMLP(nn.Module):
    """
    Simple MLP for multi-class signal classification.
      - input_dim: number of input features
      - hidden_layers: list of hidden layer sizes, e.g. [64, 32]
      - output_dim: number of classes (3: SELL, HOLD, BUY)
    """

    def __init__(self, input_dim: int, hidden_layers: List[int], output_dim: int):
        super().__init__()

        layers: List[nn.Module] = []
        prev_dim = input_dim

        for hidden_dim in hidden_layers:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, output_dim))

        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def _load_yaml(path: str) -> Dict:
    if yaml is None:
        raise RuntimeError("PyYAML is not installed, cannot load YAML config.")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_model_config(config_path: str) -> Dict:
    """
    Load model metadata config (YAML or JSON).

    The config is expected to contain:
      - model: { input_dim, hidden_layers, output_dim, state_dict_path, default_device, ... }
      - features: { order, normalization }
      - classes: { index_to_label, label_to_index, label_to_score }
    """
    ext = os.path.splitext(config_path)[1].lower()
    if ext in (".yaml", ".yml"):
        return _load_yaml(config_path)
    if ext == ".json":
        return _load_json(config_path)
    # Fallback: try JSON, then YAML
    try:
        return _load_json(config_path)
    except Exception:
        return _load_yaml(config_path)


def _resolve_device(config: Dict, override_device: Optional[str]) -> str:
    if override_device:
        return override_device
    model_cfg = config.get("model", {}) or {}
    dev = model_cfg.get("default_device", "cpu")
    dev = str(dev).lower()
    if dev == "cuda" and not torch.cuda.is_available():
        return "cpu"
    return dev


def load_signal_model(
    config: Dict,
    override_device: Optional[str] = None,
) -> Tuple[SignalMLP, str]:
    """
    Instantiate a SignalMLP and load weights from config["model"]["state_dict_path"].

    Returns:
      - model (in eval mode)
      - device_str actually used ("cpu" or "cuda")
    """
    model_cfg = config.get("model", {}) or {}
    input_dim = int(model_cfg.get("input_dim", 0) or 0)
    hidden_layers = model_cfg.get("hidden_layers", []) or []
    output_dim = int(model_cfg.get("output_dim", 0) or 0)
    state_dict_path = model_cfg.get("state_dict_path")

    if not state_dict_path:
        raise ValueError("model.state_dict_path is missing in model config.")

    device_str = _resolve_device(config, override_device)
    device = torch.device(device_str)

    model = SignalMLP(input_dim=input_dim, hidden_layers=hidden_layers, output_dim=output_dim)
    model.to(device)

    state_dict = torch.load(state_dict_path, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()

    return model, device_str


def predict_signal_proba(
    model: SignalMLP,
    device: str,
    feature_vector: List[float],
) -> List[float]:
    """
    Run a forward pass and return class probabilities [p_sell, p_hold, p_buy].

    - feature_vector is already normalized.
    """
    dev = torch.device(device)
    with torch.no_grad():
        x = torch.tensor(feature_vector, dtype=torch.float32, device=dev).unsqueeze(0)  # [1, input_dim]
        logits = model(x)  # [1, 3]
        probs = torch.softmax(logits, dim=1)  # [1, 3]
        return probs[0].cpu().tolist()


def decode_prediction(
    probs: List[float],
    config: Dict,
) -> Dict:
    """
    Decode probabilities into:
      - pred_index
      - pred_label
      - pred_score (mapped from label_to_score)
      - confidence (max probability)
      - probs (original list)
    """
    if not probs:
        raise ValueError("Empty probability list.")

    pred_index = int(max(range(len(probs)), key=lambda i: probs[i]))
    confidence = float(max(probs))

    classes_cfg = config.get("classes", {}) or {}
    index_to_label = classes_cfg.get("index_to_label", {}) or {}
    label_to_score = classes_cfg.get("label_to_score", {}) or {}

    label = index_to_label.get(str(pred_index), "UNKNOWN")
    score = float(label_to_score.get(label, 0.0) or 0.0)

    return {
        "pred_index": pred_index,
        "pred_label": label,
        "pred_score": score,
        "confidence": confidence,
        "probs": probs,
    }