"""Test the full featurizer class"""
import os
import pytest
import shutil

import numpy as np
import pandas as pd

from pic2vec import ImageFeaturizer
from .build_featurizer_test import ATOL

# Constant paths
TEST_CSV_NAME = 'tests/ImageFeaturizer_testing/csv_tests/generated_images_csv_test'
IMAGE_LIST = ['arendt.bmp', 'borges.jpg', 'sappho.png']
CHECK_ARRAY = 'tests/ImageFeaturizer_testing/array_tests/check_prediction_array_{}.npy'
CHECK_CSV = 'tests/ImageFeaturizer_testing/csv_checking/{}_check_csv'

CSV_NAME_MULT = 'tests/ImageFeaturizer_testing/csv_checking/mult_check_csv.csv'
CHECK_CSV_MULT = 'tests/ImageFeaturizer_testing/csv_checking/{}_check_csv_mult'
IMAGE_LIST_MULT = [['arendt.bmp', 'sappho.png', ''], ['borges.jpg', '', '']]
CHECK_ARRAY_MULT = 'tests/ImageFeaturizer_testing/array_tests/check_prediction_array_{}_mult.npy'

# Supported models
MODELS = ['squeezenet', 'vgg16', 'vgg19', 'resnet50', 'inceptionv3', 'xception']

# Arguments to load the data into the featurizers
LOAD_DATA_ARGS = {
    'image_column_headers': 'images',
    'image_path': 'tests/feature_preprocessing_testing/test_images',
    'new_csv_name': TEST_CSV_NAME
}

# Static expected attributes to compare with the featurizer attributes
COMPARE_ARGS = {
    'downsample_size': 0,
    'image_column_headers': ['images'],
    'automatic_downsample': False,
    'csv_path': TEST_CSV_NAME,
    'image_dict': {'images': IMAGE_LIST},
    'depth': 1
}

LOAD_DATA_ARGS_MULT_ERROR = {
    'image_column_headers': ['images_1', 'images_2'],
    'image_path': 'tests/feature_preprocessing_testing/test_images',
    'new_csv_name': TEST_CSV_NAME
}

LOAD_DATA_ARGS_MULT = {
    'image_column_headers': ['images_1', 'images_2'],
    'image_path': 'tests/feature_preprocessing_testing/test_images',
    'csv_path': CSV_NAME_MULT
}

COMPARE_ARGS_MULT = {
    'downsample_size': 0,
    'image_column_headers': ['images_1', 'images_2'],
    'automatic_downsample': True,
    'csv_path': CSV_NAME_MULT,
    'image_dict': {'images_1': IMAGE_LIST_MULT[0], 'images_2': IMAGE_LIST_MULT[1]},
    'depth': 1,
}
# Variable attributes to load the featurizer with
LOAD_PARAMS = [
    ('squeezenet', (227, 227), CHECK_ARRAY.format('squeezenet')),
    ('vgg16', (224, 224), CHECK_ARRAY.format('vgg16')),
    ('vgg19', (224, 224), CHECK_ARRAY.format('vgg19')),
    ('resnet50', (224, 224), CHECK_ARRAY.format('resnet50')),
    ('inceptionv3', (299, 299), CHECK_ARRAY.format('inceptionv3')),
    ('xception', (299, 299), CHECK_ARRAY.format('xception'))
]

LOAD_PARAMS_MULT = [
    ('squeezenet', (227, 227), CHECK_ARRAY_MULT.format('squeezenet')),
    ('vgg16', (224, 224), CHECK_ARRAY_MULT.format('vgg16')),
    ('vgg19', (224, 224), CHECK_ARRAY_MULT.format('vgg19')),
    ('resnet50', (224, 224), CHECK_ARRAY_MULT.format('resnet50')),
    ('inceptionv3', (299, 299), CHECK_ARRAY_MULT.format('inceptionv3')),
    ('xception', (299, 299), CHECK_ARRAY_MULT.format('xception'))
]


# Remove path to the generated csv if it currently exists
if os.path.isdir('tests/ImageFeaturizer_testing/csv_tests'):
    shutil.rmtree('tests/ImageFeaturizer_testing/csv_tests')


def compare_featurizer_class(featurizer,
                             scaled_size,
                             featurized_data,
                             downsample_size,
                             image_column_headers,
                             automatic_downsample,
                             csv_path,
                             image_dict,
                             depth,
                             featurized=False,
                             check_csv='',
                             saved_data=True):
    """Check the necessary assertions for a featurizer image."""
    assert featurizer.scaled_size == scaled_size
    assert np.allclose(featurizer.features.astype(float).as_matrix(), featurized_data, atol=ATOL)
    assert featurizer.downsample_size == downsample_size
    assert featurizer.image_column_headers == image_column_headers
    assert featurizer.autosample == automatic_downsample
    assert featurizer.csv_path == csv_path
    assert featurizer.image_dict == image_dict
    assert featurizer.depth == depth
    if featurized:
        assert np.array_equal(pd.read_csv(check_csv).columns, featurizer.features.columns)
        assert np.allclose(featurizer.features.astype(float), pd.read_csv(check_csv).astype(float),
                           atol=ATOL)


def compare_empty_input(featurizer):
    assert np.array_equal(featurizer.data, np.zeros((1)))
    assert featurizer.features.equals(pd.DataFrame())
    assert featurizer.full_dataframe.equals(pd.DataFrame())
    assert featurizer.csv_path == ''
    assert featurizer.image_list == ''
    assert featurizer.image_column_headers == ''
    assert featurizer.image_path == ''


@pytest.fixture(scope='module')
def featurizer():
    return ImageFeaturizer()


@pytest.fixture(scope='module')
def featurizer_autosample():
    return ImageFeaturizer(autosample=True)


def test_featurize_first(featurizer):
    """Test that the featurizer raises an error if featurize is called before loading data"""
    # Raise error if attempting to featurize before loading data
    with pytest.raises(IOError):
        featurizer.featurize_preloaded_data()


def test_featurizer_build(featurizer):
    """Test that the featurizer saves empty attributes correctly after initializing"""
    compare_featurizer_class(featurizer, (0, 0), np.zeros((1)), 0, '', False, '', {}, 1)


def test_load_data_single_column(featurizer):
    """Test that the featurizer saves attributes correctly after loading data"""
    featurizer.load_data(**LOAD_DATA_ARGS)
    compare_featurizer_class(featurizer, (227, 227), np.zeros((1)), **COMPARE_ARGS)


def test_load_data_multiple_columns_no_csv(featurizer):
    """Test featurizer raises error if multiple columns passed with only a directory"""
    with pytest.raises(ValueError):
        featurizer.load_data(**LOAD_DATA_ARGS_MULT_ERROR)


def test_load_data_multiple_columns(featurizer_autosample):
    """Test featurizer loads data correctly with multiple image columns"""
    featurizer_autosample.load_data(**LOAD_DATA_ARGS_MULT)
    compare_featurizer_class(featurizer_autosample, (227, 227), np.zeros((1)), **COMPARE_ARGS_MULT)


def test_load_and_featurize_save_csv(featurizer):
    """Make sure the featurizer writes the name correctly to csv with robust naming config"""

    name, ext = os.path.splitext(CSV_NAME_MULT)
    check_array_path = "{}_{}".format(name, 'squeezenet_depth-1_output-512')
    featurizer.featurize(save_csv=True, save_features=True, omit_time=True,
                         **LOAD_DATA_ARGS_MULT)

    full_check = "{}{}{}".format(check_array_path, '_full', ext)
    feature_check = "{}{}{}".format(check_array_path, '_features_only', ext)

    featurizer.save_csv(save_features=True, omit_time=True)

    try:
        assert os.path.isfile(full_check)
        assert os.path.isfile(feature_check)

    finally:
        if os.path.isfile("{}{}{}".format(check_array_path, '_features_only', ext)):
            os.remove("{}{}{}".format(check_array_path, '_features_only', ext))
        if os.path.isfile("{}{}{}".format(check_array_path, '_full', ext)):
            os.remove("{}{}{}".format(check_array_path, '_full', ext))


def test_load_then_featurize_save_csv(featurizer):
    """Make sure the featurizer writes the name correctly to csv with robust naming config"""

    name, ext = os.path.splitext(CSV_NAME_MULT)
    check_array_path = "{}_{}".format(name, 'squeezenet_depth-1_output-512')
    featurizer.load_data(**LOAD_DATA_ARGS_MULT)
    featurizer.featurize_preloaded_data(save_csv=True, save_features=True, omit_time=True,
                                        batch_processing=False)

    full_check = "{}{}{}".format(check_array_path, '_full', ext)
    feature_check = "{}{}{}".format(check_array_path, '_features_only', ext)

    featurizer.save_csv(save_features=True, omit_time=True)

    try:
        assert os.path.isfile(full_check)
        assert os.path.isfile(feature_check)

    finally:
        if os.path.isfile("{}{}{}".format(check_array_path, '_features_only', ext)):
            os.remove("{}{}{}".format(check_array_path, '_features_only', ext))
        if os.path.isfile("{}{}{}".format(check_array_path, '_full', ext)):
            os.remove("{}{}{}".format(check_array_path, '_full', ext))


def test_clear_input(featurizer):
    featurizer.featurize(save_features=True, omit_time=True, omit_model=True,
                         omit_depth=True, omit_output=True, **LOAD_DATA_ARGS)

    featurizer.clear_input(confirm=True)
    compare_empty_input(featurizer)


def test_clear_input_no_confirm(featurizer):
    with pytest.raises(ValueError):
        featurizer.clear_input()


def test_load_then_featurize_data_multiple_columns(featurizer_autosample):
    """Test featurizations and attributes for each model are correct with multiple image columns"""
    featurizer_autosample.load_data(**LOAD_DATA_ARGS_MULT)
    featurizer_autosample.featurize_preloaded_data(save_features=True)
    check_array = np.load(CHECK_ARRAY_MULT.format('squeezenet'))

    compare_featurizer_class(featurizer_autosample, (227, 227), check_array, featurized=True,
                             check_csv=CHECK_CSV_MULT.format('squeezenet'), **COMPARE_ARGS_MULT)


def test_load_then_featurize_data_single_column(featurizer):
    """Test featurizations and attributes for each model are correct with multiple image columns"""
    featurizer.load_data(**LOAD_DATA_ARGS)
    featurizer.featurize_preloaded_data(save_features=True)
    check_array = np.load(CHECK_ARRAY.format('squeezenet'))

    compare_featurizer_class(featurizer, (227, 227), check_array, featurized=True,
                             check_csv=CHECK_CSV.format('squeezenet'), **COMPARE_ARGS)


def test_load_then_featurize_data_no_save_features(featurizer):
    """Test featurizations and attributes for each model are correct with multiple image columns"""
    featurizer.load_data(**LOAD_DATA_ARGS)
    featurizer.featurize_preloaded_data()
    check_array = np.load(CHECK_ARRAY.format('squeezenet'))

    compare_featurizer_class(featurizer, (227, 227), check_array, featurized=True,
                             check_csv=CHECK_CSV.format('squeezenet'), **COMPARE_ARGS)


def test_load_and_featurize_data_multiple_columns_batch_overflow(featurizer_autosample):
    """Test featurizations and attributes for each model are correct with multiple image columns"""
    featurizer_autosample.featurize(save_features=True, **LOAD_DATA_ARGS_MULT)
    check_array = np.load(CHECK_ARRAY_MULT.format('squeezenet'))

    compare_featurizer_class(featurizer_autosample, (227, 227), check_array, featurized=True,
                             check_csv=CHECK_CSV_MULT.format('squeezenet'), **COMPARE_ARGS_MULT)


def test_load_and_featurize_data_single_column_batch_overflow(featurizer):
    """Test featurizations and attributes for each model are correct with multiple image columns"""
    featurizer.featurize(save_features=True, **LOAD_DATA_ARGS)
    check_array = np.load(CHECK_ARRAY.format('squeezenet'))

    compare_featurizer_class(featurizer, (227, 227), check_array, featurized=True,
                             check_csv=CHECK_CSV.format('squeezenet'), **COMPARE_ARGS)


@pytest.mark.parametrize('model,size,array_path', LOAD_PARAMS_MULT, ids=MODELS)
def test_load_and_featurize_data_multiple_columns_no_batch_processing(model, size, array_path):
    """Test featurizations and attributes for each model are correct with multiple image columns"""
    feat = ImageFeaturizer(model=model, autosample=True)
    feat.featurize(batch_processing=False, save_features=True, **LOAD_DATA_ARGS_MULT)
    check_array = np.load(array_path)

    compare_featurizer_class(feat, size, check_array, featurized=True,
                             check_csv=CHECK_CSV_MULT.format(model), **COMPARE_ARGS_MULT)


@pytest.mark.parametrize('model,size,array_path', LOAD_PARAMS_MULT, ids=MODELS)
def test_load_and_featurize_data_multiple_columns_with_batch_processing(model, size, array_path):
    """Test featurizations and attributes for each model are correct with multiple image columns"""
    feat = ImageFeaturizer(model=model, autosample=True)
    feat.featurize(batch_size=2, save_features=True, **LOAD_DATA_ARGS_MULT)
    check_array = np.load(array_path)

    compare_featurizer_class(feat, size, check_array, featurized=True,
                             check_csv=CHECK_CSV_MULT.format(model), **COMPARE_ARGS_MULT)


@pytest.mark.parametrize('model,size,array_path', LOAD_PARAMS, ids=MODELS)
def test_load_and_featurize_single_column_no_batch_processing(model, size, array_path):
    """Test that all of the featurizations and attributes for each model are correct"""
    feat = ImageFeaturizer(model=model)
    feat.featurize(batch_size=0, save_features=True, **LOAD_DATA_ARGS)

    check_array = np.load(array_path)

    compare_featurizer_class(feat, size, check_array, featurized=True,
                             check_csv=CHECK_CSV.format(model), **COMPARE_ARGS)


@pytest.mark.parametrize('model,size,array_path', LOAD_PARAMS, ids=MODELS)
def test_load_and_featurize_single_column_with_batch_processing(model, size, array_path):
    """Test that all of the featurizations and attributes for each model are correct"""
    feat = ImageFeaturizer(model=model)
    feat.featurize(batch_size=2, save_features=True, **LOAD_DATA_ARGS)

    check_array = np.load(array_path)

    compare_featurizer_class(feat, size, check_array, featurized=True,
                             check_csv=CHECK_CSV.format(model), **COMPARE_ARGS)
