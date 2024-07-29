import argparse
import copy
import pickle
import torch
from mmcv import Config
from utils import MODEL_ZOO, Block, Block_Assign, Block_Sim

from mmcls.datasets.builder import build_dataloader, build_dataset
from simlarity.model_creater import Model_Creator
from simlarity.zero_nas import ZeroNas
from mmcv.cnn.utils import get_model_complexity_info

input_shape = (3, 224, 224)

def parse_args():
    parser = argparse.ArgumentParser(description='mmcls test model')
    parser.add_argument('--path', default='out/assignment/assignment_hybrid_4.pkl')
    parser.add_argument('--C', type=float, default=30.)
    parser.add_argument('--minC', type=float, default=0.)
    parser.add_argument('--flop_C', type=float, default=10.)
    parser.add_argument('--minflop_C', type=float, default=0.)
    parser.add_argument('--trial', type=int, default=10)
    parser.add_argument('--num_batch', type=int, default=5)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--zero_proxy', type=str, choices=['jacov', 'grad_norm', 'naswot', 'synflow', 'snip', 'fisher'])
    parser.add_argument('--data_config', type=str, default='configs/_base_/datasets/imagenet_bs64.py')
    parser.add_argument('--blocks', type=str, nargs='+', help='格式为：ResNet50:15 ResNet18:0 ResNet50:13 ResNet50:11')

    args = parser.parse_args()

    args.maxC = args.C
    args.maxflop_C = args.flop_C

    return args

def parse_block_arg(block_arg, all_blocks):
    selected_blocks = []
    for block_str in block_arg:
        model_name, block_stage = block_str.split(':')
        model_name = model_name.lower()
        block_stage = int(block_stage)
        print(f"Looking for block {model_name}:{block_stage}")  # Debug print
        for block in all_blocks:
            if block.model_name == model_name and block.block_index == block_stage:
                selected_blocks.append(block)
                break
    return selected_blocks

def check_valid(selected_block):
    cnn_max = 0
    vit_min = len(selected_block)
    for s in selected_block:
        if s is not None:
            if (s.model_name.startswith('vit') or s.model_name.startswith('swin')):
                if s.block_index < vit_min:
                    vit_min = s.block_index
            else:
                if s.block_index > cnn_max:
                    cnn_max = s.block_index
    return cnn_max < vit_min

def main():
    args = parse_args()
    with open(args.path, 'rb') as file:
        assignment = pickle.load(file)
    assert isinstance(assignment, Block_Assign)
    all_blocks = []
    for group in assignment.center2block:
        all_blocks.extend(group)
    all_blocks = [b for b in all_blocks if b.model_name in MODEL_ZOO]

    print(f"All blocks: {[f'{b.model_name}:{b.block_index}' for b in all_blocks]}")  # Debug print

    selected_blocks = parse_block_arg(args.blocks, all_blocks)

    if not selected_blocks:
        print("No blocks were selected. Please check your --blocks argument.")
        return

    if not check_valid(selected_blocks):
        print("The selected blocks are not valid as a combination.")
        return

    distributed = False
    data_cfg = Config.fromfile(args.data_config)
    dataset = build_dataset(data_cfg.data.train)
    data_cfg.data.samples_per_gpu = args.batch_size
    data_loader = build_dataloader(
        dataset,
        samples_per_gpu=data_cfg.data.samples_per_gpu,
        workers_per_gpu=data_cfg.data.workers_per_gpu,
        dist=distributed,
        shuffle=False,
        round_up=True)
    print('*'*10 + 'Dataloader Created' + '*'*10)
    indicator = ZeroNas(dataloader=data_loader,
                        indicator=args.zero_proxy,
                        num_batch=args.num_batch)
    creator = Model_Creator()

    model = creator.create_hybrid(selected_blocks)
    if model is None:
        print("The model could not be created with the selected blocks.")
        return

    try:
        new_flops, new_size = get_model_complexity_info(
            model, input_shape, print_per_layer_stat=False, as_strings=False)
        new_flops = round(new_flops / 10.**9, 3)
        new_size = sum(p.numel() for p in model.parameters())/1e6
    except Exception as e:
        print(f"Error computing model complexity: {e}")
        return

    if new_size <= args.maxC and new_size > args.minC and new_flops <= args.maxflop_C and new_flops > args.minflop_C:
        pass
    else:
        print(
            f'current size {new_size}M, current flops {new_flops}G, \tParam Range ({args.minC}M,{args.maxC}M), \tFLOPs Range ({args.minflop_C}GFLOPs,{args.maxflop_C}GFLOPs)')
        return

    new_value = indicator.get_score(model)[args.zero_proxy]

    print(
        f'Current score {new_value}, current size {new_size}M, current flops {new_flops}G')

    print(selected_blocks)
    selected_blocks = list(
        sorted(selected_blocks, key=lambda x: x.block_index))
    model = creator.create_hybrid(selected_blocks)
    assert model is not None, "Searched model can not be none"
    size = sum(p.numel() for p in model.parameters())/1e6
    print(f'Final size {size}, capacity {args.C}')
    best_model_cfg = creator.create_hybrid_cfg(selected_blocks)

    dataname = data_cfg.data.train.type
    file_name = f'reassembly_C-{args.C}_FLOPsC-{args.flop_C}_zeroproxy_hybrid_{dataname}-{args.zero_proxy}.py'
    best_model_cfg = Config(dict(model=best_model_cfg))
    print(best_model_cfg.pretty_text)

    with open(file_name, 'w') as f:
        f.write(best_model_cfg.pretty_text)

if __name__ == '__main__':
    main()
