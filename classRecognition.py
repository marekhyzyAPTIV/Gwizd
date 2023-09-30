from torchvision.io import read_image
from torchvision.models import resnet50, ResNet50_Weights
import torch.nn as nn


img = read_image("./dog.jpg")

weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=weights)
model.eval()

preprocess = weights.transforms()

batch = preprocess(img).unsqueeze(0)
modelNoFN = nn.Sequential(*list(model.children())[:-1])

prediction = model(batch).squeeze(0).softmax(0)
embeddedRepresentation = modelNoFN(batch).squeeze(0)
class_id = prediction.argmax().item()
score = prediction[class_id].item()
category_name = weights.meta["categories"][class_id]
print(f"{category_name}: {100 * score:.1f}%")
