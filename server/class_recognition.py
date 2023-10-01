from torchvision.transforms.functional import pil_to_tensor
from torchvision.models import resnet50, ResNet50_Weights
import torch.nn as nn


def do_inference(img_pil):
    weights = ResNet50_Weights.DEFAULT
    model = resnet50(weights=weights)
    model.eval()

    preprocess = weights.transforms()

    img = pil_to_tensor(img_pil)
    batch = preprocess(img).unsqueeze(0)
    modelNoFN = nn.Sequential(*list(model.children())[:-1])

    prediction = model(batch).squeeze(0).softmax(0)
    embedded_representation = modelNoFN(batch).squeeze(0)
    class_id = prediction.argmax().item()
    score = prediction[class_id].item()
    category_name = weights.meta["categories"][class_id]
    return category_name, score, embedded_representation
