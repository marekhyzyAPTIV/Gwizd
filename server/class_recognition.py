from torchvision.models import resnet50, ResNet50_Weights
import torch
import torch.nn as nn
from io import BytesIO
import numpy as np

def do_inference(img_pil):
    weights = ResNet50_Weights.DEFAULT
    model = resnet50(weights=weights)
    model.eval()

    preprocess = weights.transforms()

    batch = preprocess(img_pil).unsqueeze(0)
    modelNoFN = nn.Sequential(*list(model.children())[:-1])

    prediction = model(batch).squeeze(0).softmax(0)
    embedded_representation = modelNoFN(batch).flatten()
    class_id = prediction.argmax().item()
    score = prediction[class_id].item()
    category_name = weights.meta["categories"][class_id]
    return category_name, score, embedded_representation

def tensor_to_bytes(tensor: torch.Tensor):
    out = BytesIO()
    arr = tensor.detach().numpy()
    np.save(out, arr)
    out.seek(0)
    return out.read()