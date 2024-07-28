_base_ = [
    '../../_base_/datasets/cars_bs256_strong.py',
    '../../_base_/schedules/downstream_bs256_adamw.py',
    '../../_base_/default_runtime.py',
]



runner = dict(
    type='IterBasedRunner', # Type of runner to use (i.e. IterBasedRunner or EpochBasedRunner)
    max_iters=40000) # Total number of iterations. For EpochBasedRunner use max_epochs


optimizer = dict(
    _delete_=True,
    type='AdamW',
    lr=5e-4 * 256 / 512,
    weight_decay=0.05,
    eps=1e-8,
    betas=(0.9, 0.999),
    paramwise_cfg=dict(norm_decay_mult=0., bypass_duplicate=True))

fp16 = dict(loss_scale=512.0)
model = dict(
    type='ImageClassifier',
    backbone=dict(
        type='DeRy',
        block_fixed=False,
        base_channels=64,
        block_list=[[
            'resnet50', 'layer1.0', 'layer1.1', 'pytorch'
        ],
            [
            'regnet_y_3_2gf', 'trunk_output.block2.block2-1',
            'trunk_output.block3.block3-1', 'pytorch'
        ],
            [
            'resnet101', 'layer3.8', 'layer3.22', 'pytorch'
        ],
            [
            'resnet50', 'layer3.4', 'layer4.2', 'pytorch'
        ]],
        adapter_list=[
            dict(
                input_channel=256,
                output_channel=216,
                stride=2,
                num_fc=0,
                num_conv=1,
                mode='cnn2cnn'),
            dict(
                input_channel=576,
                output_channel=1024,
                stride=1,
                num_fc=0,
                num_conv=1,
                mode='cnn2cnn'),
            dict(
                input_channel=1024,
                output_channel=1024,
                stride=1,
                num_fc=0,
                num_conv=1,
                mode='cnn2cnn')
        ],
        out_indices=(3, )),
    neck=dict(type='GlobalAveragePooling'),
    head=dict(
        type='LinearClsHead',
        num_classes={{_base_.dataset_num_classes}},
        in_channels=2048,
        loss=dict(
            type='LabelSmoothLoss',
            label_smooth_val=0.1,
            num_classes={{_base_.dataset_num_classes}},
            reduction='mean',
            loss_weight=1.0),
        topk=(1, 5),
        cal_acc=False),
    train_cfg=dict(augments=[
        dict(type='BatchMixup', alpha=0.1,
             num_classes={{_base_.dataset_num_classes}}, prob=0.5),
        dict(type='BatchCutMix', alpha=1.0,
             num_classes={{_base_.dataset_num_classes}}, prob=0.5)
    ]))

custom_hooks = [
    dict(type='EMAHook', momentum=0.0005)
]

evaluation = dict(interval=2000, metric='accuracy')
# evaluation = dict(interval=2000, metric='per_class_acc')
checkpoint_config = dict(interval=2000, max_keep_ckpts=1)

            
