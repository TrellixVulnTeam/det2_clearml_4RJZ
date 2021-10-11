from pathlib import Path
import json
import numpy as np
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
from copy import deepcopy
from pprint import pprint

STATS = ["AP", "AP@0.5", "AP@0.75", "AP@small", "AP@medium", "AP@large"]


def coco_eval(pred_path, local_data_dir, val_str="val"):
    pred_path = Path(pred_path)
    local_data_dir = Path(local_data_dir)

    assert pred_path.is_file()
    pred_dict = json.load(open(str(pred_path)))

    evals = {}

    for gt_path in local_data_dir.rglob(f"{val_str}*.json"):
        print(f"Evaluating {gt_path.stem}")
        cocoGt = COCO(str(gt_path))

        gt_img_ids = cocoGt.getImgIds()
        pred_dict_copy = deepcopy(pred_dict)
        new_DT_annotations = [
            instance
            for instance in pred_dict_copy
            if instance["image_id"] in gt_img_ids
        ]

        cocoDt = cocoGt.loadRes(new_DT_annotations)

        cocoEval = COCOeval(cocoGt, cocoDt, "bbox")
        cocoEval.evaluate()
        cocoEval.accumulate()
        cocoEval.summarize()

        evals[gt_path.stem] = {
            k: v for k, v in zip(STATS, cocoEval.stats[: len(STATS)])
        }

    pprint(evals)
    return evals


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("pred")
    ap.add_argument("local_data_dir")
    args = ap.parse_args()

    coco_eval(args.pred, args.local_data_dir)
