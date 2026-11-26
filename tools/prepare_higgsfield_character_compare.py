"""Compare the two prepared Blender views: python compare.py BEFORE AFTER OUTPUT."""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image
import numpy as np


def compare(before, after, output):
    references = [json.loads((p / "views.json").read_text()) for p in [before, after]]
    keys = ["blender", "scriptSha256", "renderer", "samples", "seed", "size", "viewTransform", "cameraTargetOffsetAndOrthoScaleBlender"]
    for key in keys:
        if references[0][key] != references[1][key]:
            raise ValueError(f"Incompatible view setting: {key}")
    report = {
        "sourceSha256": references[0]["sourceSha256"],
        "candidateSha256": references[1]["sourceSha256"],
        "settings": {k: references[0][k] for k in keys},
        "coverage": "Alpha >= 128 in the original RGBA render. IoU is overlap/union; numerator and denominator are retained.",
        "color": "Mean absolute difference of 8-bit displayed RGB over pixels where both alphas >= 250, in 0-255 levels; includes render noise.",
        "views": {},
    }
    for name in ["silhouette", "face", "hand"]:
        images = []
        for directory, ref in zip([before, after], references):
            file = directory / f"{name}.png"
            if hashlib.sha256(file.read_bytes()).hexdigest() != ref["images"][name]["sha256"]:
                raise ValueError(f"Image changed: {file}")
            with Image.open(file) as im:
                images.append(np.array(im.convert("RGBA")))
        a,b = images
        m,v = a[:,:,3]>=128,b[:,:,3]>=128
        opaque = (a[:,:,3]>=250)&(b[:,:,3]>=250)
        common, union = int((m&v).sum()), int((m|v).sum())
        if not (common and union and opaque.any()):
            raise ValueError("Missing foreground")
        report["views"][name] = {
            "overlapPixels":common,"unionPixels":union,"maskIoU":common/union,
            "lostPixels":int((m&~v).sum()),"addedPixels":int((v&~m).sum()),
            "commonOpaquePixels":int(opaque.sum()),
            "meanAbsoluteRGBLevelDifference":float(np.abs(a[:,:,:3].astype(float)-b[:,:,:3].astype(float))[opaque].mean()),
        }
    with output.open("x") as f:
        json.dump(report,f,indent=2)
        f.write("\n")


if __name__=="__main__":
    compare(*map(Path,sys.argv[1:]))
