
from lasagne.layers import InputLayer, DenseLayer, NonlinearityLayer, Layer
from lasagne.layers import Conv2DLayer as ConvLayer
from lasagne.layers import Pool2DLayer as PoolLayer
from lasagne.nonlinearities import softmax
import lasagne
import os
import pickle
import skimage.transform
import numpy as np
import typing


def flip_filters_convlayer_network(layers: typing.Iterable[Layer]) -> None:
    """
    Model weights are computed with a cuDNN version which have the weights flipped
    :param layers: an iterable of lasagne.layers
    """
    for layer in layers:
        if isinstance(layer, lasagne.layers.Conv2DLayer):
            weight_param = layer.get_params()[0]
            assert(weight_param.name == 'W')
            weight_param.set_value(weight_param.get_value()[:, :, ::-1, ::-1])


def prep_image_vgg(im: np.ndarray, mean_value: np.ndarray) -> np.ndarray:
    """
    Preprocess the image to be inputted to the network,
     resize bigger dimension to 256 and extract center 224x224 (no warping)
    :param im: image to be processed
    :param mean_value: mean value to be substracted [B,G,R]
    :return: the pre-processed image
    """
    if len(im.shape) == 2:
        im = np.repeat(im[:, :, np.newaxis], 3, axis=2)
    elif im.shape[2] == 4:
        im = im[:, :, :3]
    # Resize so smallest dim = 256, preserving aspect ratio
    h, w, _ = im.shape
    if h < w:
        im = skimage.transform.resize(im, (256, w*256//h), preserve_range=True)
    else:
        im = skimage.transform.resize(im, (h*256//w, 256), preserve_range=True)

    # Central crop to 224x224
    h, w, _ = im.shape
    im = im[h//2-112:h//2+112, w//2-112:w//2+112]

    # Shuffle axes to c01
    im = np.swapaxes(np.swapaxes(im, 1, 2), 0, 1)

    # Convert to BGR
    im = im[::-1, :, :]
    im = im - mean_value[:, np.newaxis, np.newaxis]
    return im[np.newaxis].astype(np.float32)


def build_model_vgg16() -> typing.Tuple[typing.Dict[str, Layer], np.ndarray]:
    """
    Build the VGG16 model
    :return: [network, mean_value]
    """
    net = dict()
    net['input'] = InputLayer((None, 3, 224, 224))
    net['conv1_1'] = ConvLayer(net['input'], 64, 3, pad=1)
    net['conv1_2'] = ConvLayer(net['conv1_1'], 64, 3, pad=1)
    net['pool1'] = PoolLayer(net['conv1_2'], 2)
    net['conv2_1'] = ConvLayer(net['pool1'], 128, 3, pad=1)
    net['conv2_2'] = ConvLayer(net['conv2_1'], 128, 3, pad=1)
    net['pool2'] = PoolLayer(net['conv2_2'], 2)
    net['conv3_1'] = ConvLayer(net['pool2'], 256, 3, pad=1)
    net['conv3_2'] = ConvLayer(net['conv3_1'], 256, 3, pad=1)
    net['conv3_3'] = ConvLayer(net['conv3_2'], 256, 3, pad=1)
    net['pool3'] = PoolLayer(net['conv3_3'], 2)
    net['conv4_1'] = ConvLayer(net['pool3'], 512, 3, pad=1)
    net['conv4_2'] = ConvLayer(net['conv4_1'], 512, 3, pad=1)
    net['conv4_3'] = ConvLayer(net['conv4_2'], 512, 3, pad=1)
    net['pool4'] = PoolLayer(net['conv4_3'], 2)
    net['conv5_1'] = ConvLayer(net['pool4'], 512, 3, pad=1)
    net['conv5_2'] = ConvLayer(net['conv5_1'], 512, 3, pad=1)
    net['conv5_3'] = ConvLayer(net['conv5_2'], 512, 3, pad=1)
    net['pool5'] = PoolLayer(net['conv5_3'], 2)
    net['fc6'] = DenseLayer(net['pool5'], num_units=4096)
    net['fc7'] = DenseLayer(net['fc6'], num_units=4096)
    net['fc8'] = DenseLayer(net['fc7'], num_units=1000, nonlinearity=None)
    net['prob'] = NonlinearityLayer(net['fc8'], lasagne.nonlinearities.softmax)

    params_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vgg16.pkl')
    if not os.path.exists(params_file):
        print('Weight file not found, downloading...')
        os.system('wget -O {} https://s3.amazonaws.com/lasagne/recipes/pretrained/imagenet/vgg16.pkl'
                  .format(params_file))
    params_data = pickle.load(open(params_file, 'rb'), encoding='latin-1')
    lasagne.layers.set_all_param_values(net['prob'], params_data['param values'])
    flip_filters_convlayer_network(net.values())
    # CLASSES = params_data['synset words']
    mean_value = params_data['mean value']
    return net, mean_value


def build_model_vgg19() -> typing.Tuple[typing.Dict[str, Layer], np.ndarray]:
    net = dict()
    net['input'] = InputLayer((None, 3, 224, 224))
    net['conv1_1'] = ConvLayer(net['input'], 64, 3, pad=1)
    net['conv1_2'] = ConvLayer(net['conv1_1'], 64, 3, pad=1)
    net['pool1'] = PoolLayer(net['conv1_2'], 2)
    net['conv2_1'] = ConvLayer(net['pool1'], 128, 3, pad=1)
    net['conv2_2'] = ConvLayer(net['conv2_1'], 128, 3, pad=1)
    net['pool2'] = PoolLayer(net['conv2_2'], 2)
    net['conv3_1'] = ConvLayer(net['pool2'], 256, 3, pad=1)
    net['conv3_2'] = ConvLayer(net['conv3_1'], 256, 3, pad=1)
    net['conv3_3'] = ConvLayer(net['conv3_2'], 256, 3, pad=1)
    net['conv3_4'] = ConvLayer(net['conv3_3'], 256, 3, pad=1)
    net['pool3'] = PoolLayer(net['conv3_4'], 2)
    net['conv4_1'] = ConvLayer(net['pool3'], 512, 3, pad=1)
    net['conv4_2'] = ConvLayer(net['conv4_1'], 512, 3, pad=1)
    net['conv4_3'] = ConvLayer(net['conv4_2'], 512, 3, pad=1)
    net['conv4_4'] = ConvLayer(net['conv4_3'], 512, 3, pad=1)
    net['pool4'] = PoolLayer(net['conv4_4'], 2)
    net['conv5_1'] = ConvLayer(net['pool4'], 512, 3, pad=1)
    net['conv5_2'] = ConvLayer(net['conv5_1'], 512, 3, pad=1)
    net['conv5_3'] = ConvLayer(net['conv5_2'], 512, 3, pad=1)
    net['conv5_4'] = ConvLayer(net['conv5_3'], 512, 3, pad=1)
    net['pool5'] = PoolLayer(net['conv5_4'], 2)
    net['fc6'] = DenseLayer(net['pool5'], num_units=4096)
    net['fc7'] = DenseLayer(net['fc6'], num_units=4096)
    net['fc8'] = DenseLayer(net['fc7'], num_units=1000, nonlinearity=None)
    net['prob'] = NonlinearityLayer(net['fc8'], softmax)

    params_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vgg19.pkl')
    if not os.path.exists(params_file):
        print('Weight file not found, downloading...')
        os.system('wget -O {} https://s3.amazonaws.com/lasagne/recipes/pretrained/imagenet/vgg19.pkl'
                  .format(params_file))
    params_data = pickle.load(open(params_file, 'rb'), encoding='latin-1')
    lasagne.layers.set_all_param_values(net['prob'], params_data['param values'])
    flip_filters_convlayer_network(net.values())
    # CLASSES = params_data['synset words']
    mean_value = params_data['mean value']
    return net, mean_value


def build_model_vgg19_normalized() -> typing.Tuple[typing.Dict[str, Layer], np.ndarray]:
    net = dict()
    net['input'] = InputLayer((1, 3, None, None))
    net['conv1_1'] = ConvLayer(net['input'], 64, 3, pad=1)
    net['conv1_2'] = ConvLayer(net['conv1_1'], 64, 3, pad=1)
    net['pool1'] = PoolLayer(net['conv1_2'], 2, mode='average_exc_pad')
    net['conv2_1'] = ConvLayer(net['pool1'], 128, 3, pad=1)
    net['conv2_2'] = ConvLayer(net['conv2_1'], 128, 3, pad=1)
    net['pool2'] = PoolLayer(net['conv2_2'], 2, mode='average_exc_pad')
    net['conv3_1'] = ConvLayer(net['pool2'], 256, 3, pad=1)
    net['conv3_2'] = ConvLayer(net['conv3_1'], 256, 3, pad=1)
    net['conv3_3'] = ConvLayer(net['conv3_2'], 256, 3, pad=1)
    net['conv3_4'] = ConvLayer(net['conv3_3'], 256, 3, pad=1)
    net['pool3'] = PoolLayer(net['conv3_4'], 2, mode='average_exc_pad')
    net['conv4_1'] = ConvLayer(net['pool3'], 512, 3, pad=1)
    net['conv4_2'] = ConvLayer(net['conv4_1'], 512, 3, pad=1)
    net['conv4_3'] = ConvLayer(net['conv4_2'], 512, 3, pad=1)
    net['conv4_4'] = ConvLayer(net['conv4_3'], 512, 3, pad=1)
    net['pool4'] = PoolLayer(net['conv4_4'], 2, mode='average_exc_pad')
    net['conv5_1'] = ConvLayer(net['pool4'], 512, 3, pad=1)
    net['conv5_2'] = ConvLayer(net['conv5_1'], 512, 3, pad=1)
    net['conv5_3'] = ConvLayer(net['conv5_2'], 512, 3, pad=1)
    net['conv5_4'] = ConvLayer(net['conv5_3'], 512, 3, pad=1)
    net['pool5'] = PoolLayer(net['conv5_4'], 2, mode='average_exc_pad')

    params_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vgg19_normalized.pkl')
    if not os.path.exists(params_file):
        print('Weight file not found, downloading...')
        os.system('wget -O {} https://s3.amazonaws.com/lasagne/recipes/pretrained/imagenet/vgg19_normalized.pkl'
                  .format(params_file))
    params_data = pickle.load(open(params_file, 'rb'), encoding='latin-1')
    lasagne.layers.set_all_param_values(net['pool5'], params_data['param values'])
    flip_filters_convlayer_network(net.values())
    # CLASSES = params_data['synset words']
    mean_value = params_data['mean value']
    return net, mean_value
