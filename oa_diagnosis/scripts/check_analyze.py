from oa_diagnosis.tools.imaging_analysis import analyze_imaging
import json
ids=["9001695|20041203/00422803_1x1.jpg", "9001695|20050104/10098604_2x2.jpg", "9001695|20050104/10098607_2x2.jpg"]
out=[]
for i in ids:
    r=analyze_imaging(i)
    out.append({ 'id': i, 'status': r.get('status'), 'image_path': r.get('image_path'), 'kl_grade': r.get('kl_grade'), 'prediction': r.get('resnet_prediction') })
print(json.dumps(out, indent=2))
