import unittest
import torch
from typing import Dict
from PIL import Image
import torch.nn as nn
import pytorch_lightning as pl
from torch_utils import im2tensor
from vision.models.detection import detr
from vision.models.detection.detr import create_detr_backbone
from vision.models import model_utils
from vision.losses import detr_loss
from vision.models.detection.detr import engine
from dataset_utils import DummyDetectionDataset

if(torch.cuda.is_available()):
    from torch.cuda import amp

train_dataset = DummyDetectionDataset(img_shape=(3, 256, 256), num_classes=3,
                                      num_samples=10, box_fmt="cxcywh")
val_dataset = DummyDetectionDataset(img_shape=(3, 256, 256), num_classes=3,
                                    num_samples=10, box_fmt="cxcywh")

supported_detr_backbones = ["resnet50", "resnet50_dc5", "resnet101", "resnet101_dc5"]
error_bbone = "invalid_model"
some_supported_backbones = ["resnet50"]


def collate_fn(batch):
    return tuple(zip(*batch))


train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=2,
                                           shuffle=False, collate_fn=collate_fn)

val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=2,
                                         shuffle=False, collate_fn=collate_fn)


class ModelFactoryTester(unittest.TestCase):
    def test_detr_backbones(self):
        for supp_bb in supported_detr_backbones:
            bbone = detr.create_detr_backbone(supp_bb, pretrained=False)
            self.assertTrue(isinstance(bbone, nn.Module))

    def test_detr_invalidbackbone(self):
        self.assertRaises(ValueError, create_detr_backbone, error_bbone)

    def test_vision_detr(self):
        for supp_bb in supported_detr_backbones:
            bbone = detr.create_detr_backbone(supp_bb, pretrained=False)
            self.assertTrue(isinstance(bbone, nn.Module))
            model = detr.vision_detr(num_classes=91, num_queries=5, backbone=bbone)
            self.assertTrue(isinstance(bbone, nn.Module))

    def test_create_vision_detr(self):
        for supp_bb in supported_detr_backbones:
            bbone = detr.create_detr_backbone(supp_bb, pretrained=False)
            self.assertTrue(isinstance(bbone, nn.Module))
            model = detr.create_vision_detr(num_classes=91, num_queries=5, backbone=bbone)
            self.assertTrue(isinstance(bbone, nn.Module))


class EngineTester(unittest.TestCase):
    def test_train(self):
        # Read Image using PIL Here
        # Do forward over image
        image = Image.open("tests/assets/grace_hopper_517x606.jpg")
        img_tensor = im2tensor(image)
        self.assertEqual(img_tensor.ndim, 4)
        # Detr Input format is (xc, yc, w, h) Normalized to the image.
        boxes = torch.tensor([[0, 0, 100, 100], [0, 1, 2, 2],
                             [10, 15, 30, 35], [23, 35, 93, 95]], dtype=torch.float)
        labels = torch.tensor([1, 2, 3, 4], dtype=torch.int64)
        targets = [{"boxes": boxes, "labels": labels}]
        return True

    def test_infer(self):
        # Infer over an image
        image = Image.open("tests/assets/grace_hopper_517x606.jpg")
        tensor = im2tensor(image)
        self.assertEqual(tensor.ndim, 4)
        return True

    def test_train_step(self):
        for bbone in some_supported_backbones:
            backbone = detr.create_detr_backbone(name=bbone, pretrained=False)
            self.assertTrue(isinstance(backbone, nn.Module))
            detr_model = detr.create_vision_detr(num_classes=3, num_queries=5, backbone=backbone)
            self.assertTrue(isinstance(detr_model, nn.Module))
            opt = torch.optim.Adam(detr_model.parameters(), lr=1e-3)
            matcher = detr_loss.HungarianMatcher()
            weight_dict = {"loss_ce": 1, "loss_bbox": 1, "loss_giou": 1}
            losses = ["labels", "boxes", "cardinality"]
            criterion = detr_loss.SetCriterion(2, matcher, weight_dict, eos_coef=0.5, losses=losses)
            met = detr.train_step(detr_model, train_loader, criterion, "cpu", opt, num_batches=10)
            self.assertIsInstance(met, Dict)
            exp_keys = ("total_loss", "giou_loss", "bbox_loss", "labels_loss")
            for exp_k in exp_keys:
                self.assertTrue(exp_k in met.keys())

    @unittest.skipIf(not torch.cuda.is_available(), "CUDA unavailable")
    def test_train_step_cuda(self):
        for bbone in some_supported_backbones:
            backbone = detr.create_detr_backbone(name=bbone, pretrained=False)
            self.assertTrue(isinstance(backbone, nn.Module))
            detr_model = detr.create_vision_detr(num_classes=3, num_queries=5, backbone=backbone)
            self.assertTrue(isinstance(detr_model, nn.Module))
            opt = torch.optim.Adam(detr_model.parameters(), lr=1e-3)
            matcher = detr_loss.HungarianMatcher()
            weight_dict = {"loss_ce": 1, "loss_bbox": 1, "loss_giou": 1}
            losses = ["labels", "boxes", "cardinality"]
            criterion = detr_loss.SetCriterion(2, matcher, weight_dict, eos_coef=0.5, losses=losses)
            met = detr.train_step(detr_model, train_loader, criterion, "cuda", opt, num_batches=10)
            self.assertIsInstance(met, Dict)
            exp_keys = ("total_loss", "loss_bbox", "loss_giou", "loss_ce")
            for exp_k in exp_keys:
                self.assertTrue(exp_k in met.keys())

    def test_val_step(self):
        for bbone in some_supported_backbones:
            backbone = detr.create_detr_backbone(name=bbone, pretrained=False)
            self.assertTrue(isinstance(backbone, nn.Module))
            detr_model = detr.create_vision_detr(num_classes=3, num_queries=5, backbone=backbone)
            self.assertTrue(isinstance(detr_model, nn.Module))
            matcher = detr_loss.HungarianMatcher()
            weight_dict = {"loss_ce": 1, "loss_bbox": 1, "loss_giou": 1}
            losses = ["labels", "boxes", "cardinality"]
            criterion = detr_loss.SetCriterion(2, matcher, weight_dict, eos_coef=0.5, losses=losses)
            met = detr.val_step(detr_model, train_loader, criterion, "cpu", num_batches=10)
            self.assertIsInstance(met, Dict)
            exp_keys = ("total_loss", "giou_loss", "bbox_loss", "labels_loss")
            for exp_k in exp_keys:
                self.assertTrue(exp_k in met.keys())

    def test_fit(self):
        pass

    @unittest.skipIf(not torch.cuda.is_available(), "CUDA unavailable")
    def test_fit_cuda(self):
        pass

    def test_train_sanity_fit(self):
        pass

    @unittest.skipIf(not torch.cuda.is_available(), "CUDA unavailable")
    def test_train_sanity_fit_cuda(self):
        pass

    def test_val_sanity_fit(self):
        pass

    def test_sanity_fit(self):
        pass

    @unittest.skipIf(not torch.cuda.is_available(), "CUDA unavailable")
    def test_sanity_fit_cuda(self):
        pass


class LightningTester(unittest.TestCase):
    def test_lit_detr(self):
        flag = False
        for bbone in supported_detr_backbones:
            model = detr.lit_detr(num_classes=3, num_queries=5, pretrained=False, backbone=bbone)
            trainer = pl.Trainer(fast_dev_run=True)
            trainer.fit(model, train_loader, val_loader)
        flag = True
        self.assertTrue(flag)

    @unittest.skipIf(not torch.cuda.is_available(), "CUDA unavailable")
    def test_lit_detr_cuda(self):
        flag = False
        for bbone in supported_detr_backbones:
            model = detr.lit_detr(num_classes=3, num_queries=5, pretrained=False, backbone=bbone)
            trainer = pl.Trainer(fast_dev_run=True)
            trainer.fit(model, train_loader, val_loader)
        flag = True
        self.assertTrue(flag)

    def test_lit_forward(self):
        model = detr.lit_detr(num_classes=3, num_queries=5, pretrained=False)
        image = torch.rand(1, 3, 400, 400)
        out = model(image)
        self.assertIsInstance(out, Dict)
        self.assertIsInstance(out['pred_logits'], torch.Tensor)
        self.assertIsInstance(out['pred_boxes'], torch.Tensor)


if __name__ == '__main__':
    unittest.main()
