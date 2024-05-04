import argparse
import os

import matplotlib.pyplot as plt
import torch
import yaml
from torch.utils.data import DataLoader

from models import *  # This is necessary, do not remove it
from torchvision.transforms import transforms
from datasets.embeddings_localization_dataset import EmbeddingsLocalizationDataset
from datasets.transforms import SolubilityToInt, ToTensor
from utils.general import normalize, padded_permuted_collate

checkpoint = 'runs/..finalModels/LightAttention_t5-encoderOnly_22-12_18-35-28'
embeddings = 'data/embeddings/test_t5-encoderOnly.h5'
remapping = 'data/fasta_files/test_as_per_deeploc.fasta'
batch_size = 8


def explore_embeddings(args):
    transform = transforms.Compose([SolubilityToInt(), ToTensor()])
    dataset = EmbeddingsLocalizationDataset(embeddings, remapping, unknown_solubility=False, transform=transform,
                                            descriptions_with_hash=False)

    if len(dataset[0][0].shape) == 2:  # if we have per residue embeddings they have an additional lenght dim
        collate_function = padded_permuted_collate
    else:  # if we have reduced sequence wise embeddings use the default collate function by passing None
        collate_function = None

    data_loader = DataLoader(dataset, batch_size=3, shuffle=True, collate_fn=collate_function)

    # Needs "from models import *" to work
    model = globals()[args.model_type](embeddings_dim=dataset[0][0].shape[-1], **args.model_parameters)

    with torch.no_grad():
        embedding, localization, solubility, metadata = next(iter(data_loader))

        # register defined hooks and run trough some example in the dataset
        # model.conv1.register_forward_hook(visualize_activation_hook)
        model.softmax.register_forward_hook(visualize_activation_hook)

        # create mask corresponding to the zero padding used for the shorter sequecnes in the batch. All values corresponding to padding are False and the rest is True.
        mask = torch.arange(metadata['length'].max())[None, :] < metadata['length'][:, None]  # [batchsize, seq_len]
        model(embedding, mask)

        plt.plot(torch.max(embedding[1], dim=0)[0])
        plt.title('embedding max')
        plt.show()


def visualize_activation_hook(self, input, output, clamp=True):
    print('Inside ' + self.__class__.__name__ + ' forward')
    print('')
    print('input size:', input[0].size())
    print('output size:', output.data.size())
    print('output norm:', output.data.norm())
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams["image.cmap"] = 'viridis'
    inp = input[0][1].squeeze()
    out = output.data[1].squeeze()
    inp_max = torch.max(inp, dim=0)[0]
    out_avg = torch.mean(out, dim=0)
    if clamp:
        out_avg = out_avg.clamp(out_avg.max() - 0.00005, out_avg.max())
    out_max = torch.max(out, dim=0)[0]
    plt.plot(inp_max)
    plt.title('input max')
    plt.show()
    plt.plot(out_avg)
    plt.title('output avg')
    plt.show()
    plt.plot(out_max)
    plt.title('output max')
    plt.show()
    plt.imshow(normalize(out))
    plt.title('output')
    plt.show()
    plt.imshow(normalize(inp))
    plt.title('input')
    plt.show()


def parse_arguments():
    p = argparse.ArgumentParser()
    args = p.parse_args()
    arg_dict = args.__dict__
    data = yaml.load(open(os.path.join(checkpoint, 'train_arguments.yaml'), 'r'), Loader=yaml.FullLoader)
    for key, value in data.items():
        if isinstance(value, list):
            for v in value:
                arg_dict[key].append(v)
        else:
            arg_dict[key] = value
    return args


if __name__ == '__main__':
    os.chdir('./..')
    explore_embeddings(parse_arguments())
