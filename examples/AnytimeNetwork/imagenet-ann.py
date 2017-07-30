#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cv2
import sys
import argparse
import numpy as np
import os
import multiprocessing

import tensorflow as tf
from tensorpack import *
from tensorpack.tfutils.symbolic_functions import *
from tensorpack.tfutils.summary import *
from tensorpack.utils import logger
from tensorpack.utils import utils
from tensorpack.utils.stats import RatioCounter

from tensorpack.network_models import anytime_network
from tensorpack.network_models.anytime_network import AnytimeResnet

import get_augmented_data

args = None
INPUT_SIZE = 224

#def get_data(train_or_test):
#    isTrain = train_or_test == 'train'
#    ds = dataset.ILSVRC12TFRecord(args.data_dir, 
#                                  train_or_test, 
#                                  args.batch_size // args.nr_gpu, 
#                                  height=INPUT_SIZE, 
#                                  width=INPUT_SIZE)
#    return ds

def get_data(train_or_test):
    return get_augmented_data.get_ilsvrc_augmented_data(train_or_test, args)


def get_config():
    # prepare dataset
    if args.is_toy:
        dataset_train = get_data('toy_train')
        dataset_val = get_data('toy_validation')
    else:
        dataset_train = get_data('train')
        dataset_val = get_data('validation')
    steps_per_epoch = dataset_train.size() // args.nr_gpu

    model=AnytimeResnet(INPUT_SIZE, args)
    classification_cbs = model.compute_classification_callbacks()
    loss_select_cbs = model.compute_loss_select_callbacks()
    #lr_schedule = [(1, 1e-1/2), (30, 1e-2 /2 ), (60, 1e-3/2), (90, 1e-4/2), (105, 1e-5/2)]
    lr_schedule = [(1, 1e-1 /2), (60, 1e-2 /2 ), (90, 1e-3 /2), (105, 1e-4 /2)]
    return TrainConfig(
        dataflow=dataset_train,
        callbacks=[
            ModelSaver(checkpoint_dir=args.model_dir, keep_freq=12),
            InferenceRunner(dataset_val, classification_cbs),
            ScheduledHyperParamSetter('learning_rate', lr_schedule),
            HumanHyperParamSetter('learning_rate'),
        ] + loss_select_cbs,
        model=model,
        steps_per_epoch=steps_per_epoch,
        max_epoch=128,
    )

def eval_on_ILSVRC12(model_file, data_dir):
    ds = get_data('val')
    model = AnytimeResnet(INPUT_SIZE, args)
    pred_config = PredictConfig(
        model=model,
        session_init=get_model_loader(model_file),
        input_names=['input', 'label'],
        output_names=['wrong-top1', 'wrong-top5']
    )
    pred = SimpleDatasetPredictor(pred_config, ds)
    acc1, acc5 = RatioCounter(), RatioCounter()
    for o in pred.get_result():
        batch_size = o[0].shape[0]
        acc1.feed(o[0].sum(), batch_size)
        acc5.feed(o[1].sum(), batch_size)
    print("Top1 Error: {}".format(acc1.ratio))
    print("Top5 Error: {}".format(acc5.ratio))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', help='ILSVRC dataset dir that contains the tf records directly')
    parser.add_argument('--log_dir', help='log_dir for stdout')
    parser.add_argument('--model_dir', help='dir for saving models')
    parser.add_argument('--batch_size', help='Batch size for train/testing', 
                        type=int, default=128)
    parser.add_argument('--load', help='load model')
    parser.add_argument('--nr_gpu', help='Number of GPU to use', type=int, default=1)
    parser.add_argument('--eval', action='store_true')
    parser.add_argument('--is_toy', help='Whether to have data size of only 1024',
                        type=bool, default=False)
    anytime_network.parser_add_resnet_arguments(parser)
    args = parser.parse_args()
    
    assert args.init_channel == 64
    assert args.num_classes == 1000
    args.do_mean_std_gpu_process = True
    args.input_type = 'uint8'
    args.mean = get_augmented_data.ilsvrc_mean
    args.std = get_augmented_data.ilsvrc_std
    assert args.do_mean_std_gpu_process and args.input_type == 'uint8'
    assert args.mean is not None and args.std is not None

    # directory setup
    logger.set_log_root(log_root=args.log_dir)
    logger.auto_set_dir()

    #if args.eval:
    #    BATCH_SIZE = 128    # something that can run on one gpu
    #    eval_on_ILSVRC12(args.load, args.data_dir)
    #    sys.exit()

    config = get_config()
    if args.load and os.path.exists(args.load):
        config.session_init = SaverRestore(args.load)
    config.nr_tower = args.nr_gpu
    SyncMultiGPUTrainer(config).train()
