import os
import datetime
import random
import itertools
from collections import OrderedDict

'''
The base config class is extended to create all other config classes
'''

def config_checker(config_properties=None):
    """
    Decorator checks to make sure the function contains the neccessary config values
    :param config_properties: [string] list of strings of properties used in function
    :return: function
    """
    def decorator(func):
        def wrapped(*args, **kwargs):
            assert kwargs.get('config', None) is not None, '%s needs config argument' % func.__name__
            for prop in (config_properties or []):
                assert kwargs['config'].__getattribute__(prop) is not None, \
                    '%s needs the (not None) property %s' % (func.__name__, prop)
            return func(*args, **kwargs)
        return wrapped
    return decorator

class Config(object):
    # Root directory for entire repo
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    # Local directories contain logs, datasets, saved model
    data_dir = os.path.join(root_dir, 'local', 'data')
    log_dir = os.path.join(root_dir, 'local', 'logs')
    model_dir = os.path.join(root_dir, 'local', 'models')

    # Images dimmensions
    image_width = 128
    image_height = 96
    image_channels = 3
    image_channels_input = 3
    # Grayscale images are quicker, and depending on problem color is not important
    grayscale = True
    if grayscale:
        image_channels = 1

    def build_dataset_config(self):
        self.dataset_path = os.path.join(self.data_dir, self.dataset_name)
        self.tfrecord_path = os.path.join(self.dataset_path, self.tfrecord_name)

    def build_experiment_config(self):
        d = datetime.datetime.today()
        experiment_name = '%s_%sm_%sd_%shr_%smin' % (self.experiment_name, d.month, d.day, d.hour, d.minute)
        # Create experiment specific log and checkpoint directories
        self.log_path = os.path.join(self.log_dir, experiment_name)
        self.checkpoint_path = os.path.join(self.model_dir, experiment_name)
        self._make_path(self.log_path)
        self._make_path(self.checkpoint_path)
        print('Created log and checkpoint directories for experiment %s' % experiment_name)

    def build_hyperparameter_config(self, exp_config_handle=None):
        # Dictionary of all hyperparameter values
        self.hyperparams = OrderedDict()
        # Runs are required when configs contain hyperparameters
        self.run_log_path = None
        self.run_checkpoint_path = None
        # List of all runs within experiment
        self.runs = []
        if exp_config_handle is not None:
            # Take log and checkpoint paths from experiment
            self.log_path = exp_config_handle.log_path
            self.checkpoint_path = exp_config_handle.checkpoint_path

    def prepare_run(self, idx):
        self.set_hyperparams(idx)
        self.create_run_directories()

    def generate_runs(self):
        # Generate all runs (all possible permutations of hyperparameters)
        permutation_builder = []
        for key, value in self.hyperparams.items():
            permutation_builder.append(range(len(value)))
        # Get all possible permutations from the permutations builder
        permutations = list(itertools.product(*permutation_builder))
        permutations = [list(a) for a in permutations]
        # Shuffle prevents it from being a grid search
        random.shuffle(permutations)
        # Add run-related properties to config class
        self.runs = permutations
        self.num_runs = len(self.runs)

    def set_hyperparams(self, idx):
        permutation = self.runs[idx]
        self.run_hyperparams = OrderedDict()
        for i, key in enumerate(self.hyperparams.keys()):
            value = self.hyperparams[key][permutation[i]]
            self.run_hyperparams[key] = value
            setattr(self, key, value)

    def create_run_directories(self):
        run_specific_name = self.model_name
        for key, value in self.run_hyperparams.items():
            str_value = str(value)
            if isinstance(value, list):
                str_value = '_'.join(str(a) for a in value)
            run_specific_name += '_%s_%s' % (key, str_value)
        self.run_log_path = os.path.join(self.log_path, run_specific_name)
        self._make_path(self.run_log_path)
        self.run_checkpoint_path = os.path.join(self.checkpoint_path, run_specific_name)
        self._make_path(self.run_checkpoint_path)

    @staticmethod
    def _make_path(path):
        if not os.path.exists(path):
            os.mkdir(path)
