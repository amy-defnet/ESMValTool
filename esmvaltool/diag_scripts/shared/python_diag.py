"""Convenience classes and functions to implement python diagnostics.

Example
-------
Import and use these basic classes by e.g.::

    import esmvaltool.diag_scripts.shared as e
    models = e.Models(cfg)

Notes
-----
An example diagnostic using these classes is given in
`diag_scripts/examples/diagnostic.py`

"""


import collections
import logging

logger = logging.getLogger(__name__)


# Global variables relevant for all diagnostics
TIME = 'time'
YEAR = 'year'
MONTH = 'month_number'
DAY_Y = 'day_of_year'
DAY_M = 'day_of_month'
LAT = 'latitude'
LON = 'longitude'
HEIGHT = 'height'

EXP_STR = 'exp'
MODEL_STR = 'model'
OBS_STR = 'OBS'
PROJECT_STR = 'project'
SHORT_NAME_STR = 'short_name'


# Variables for the following classes
DEFAULT_INFO_STR = 'not_specified'
INPUT_DATA_STR = 'input_data'
VAR_LONG_NAME_STR = 'long_name'
VAR_SHORT_NAME_STR = 'short_name'
VAR_STD_NAME_STR = 'standard_name'
VAR_UNITS_STR = 'units'


# Variable class containing all relevant information
Variable = collections.namedtuple('Variable', [VAR_SHORT_NAME_STR,
                                               VAR_STD_NAME_STR,
                                               VAR_LONG_NAME_STR,
                                               VAR_UNITS_STR])


class Variables(object):
    """Class to easily access a namelist's variables.

    This class is designed to easily access variables in the diagnostic script.

    Examples
    --------
    Get all variables of a namelist configuration `cfg`::

        vars = Variables(cfg)

    Access `short_name` (as str) of a variable `tas`::

        vars.tas

    Access all other information of a variable `tas`::

        vars.TAS.short_name
        vars.TAS.standard_name
        vars.TAS.long_name
        vars.TAS.units

    """

    def __init__(self, cfg=None, **names):
        """Load variables.

        Parameters
        ----------
        cfg : dict, optional
            Configuation dictionary of the namelist.
        **names : tuple or Variable, optional
            Keyword arguments of the form `short_name=Variable_object` where
            `Variable_object` can be given as tuple or Variable.

        """
        self._dict = {}

        # Add variables from cfg file
        if (cfg is not None):
            success = True
            if isinstance(cfg, dict):
                data = cfg.get(INPUT_DATA_STR)
                if isinstance(data, dict):
                    for info in data.values():
                        name = info.get(VAR_SHORT_NAME_STR, DEFAULT_INFO_STR)
                        attr = Variable(
                            name,
                            info.get(VAR_STD_NAME_STR, DEFAULT_INFO_STR),
                            info.get(VAR_LONG_NAME_STR, DEFAULT_INFO_STR),
                            info.get(VAR_UNITS_STR, DEFAULT_INFO_STR))
                        self._add_to_dict(name, attr)
                else:
                    success = False
            else:
                success = False
            if (not success):
                logger.warning("{} is not a valid ".format(repr(cfg)) +
                               "configuration file!")

        # Add costum variables
        for name in names:
            attr = Variable(*names[name])
            self._add_to_dict(name, attr)
        if (not self._dict):
            logger.warning("No variables found!")

    def __repr__(self):
        """Representation of the class.

        """
        return repr(self.short_names())

    def _add_to_dict(self, name, attr):
        """Internal method to add a variable to class.

        Parameters
        ----------
        name : str
            `short_name` of the variable.
        attr : Variable
            All other information of the variable.

        """
        if (name not in self._dict):
            logger.debug("Added variable '{}' to collection".format(name))
        setattr(self, name, name)
        setattr(self, name.upper(), attr)
        self._dict[name] = attr

    def add_var(self, **names):
        """Add a costum variable to the class member.

        Parameters
        ----------
        **names : tuple or Variable, optional
            Keyword arguments of the form `short_name=Variable_object` where
            `Variable_object` can be given as tuple or Variable.

        """
        for name in names:
            attr = Variable(*names[name])
            self._add_to_dict(name, attr)

    def short_names(self):
        """Get list of all `short_names`.

        Returns
        -------
        list
            List of all `short_names`.
        """
        return list(self._dict)

    def standard_names(self):
        """Get list of all `standard_names`.

        Returns
        -------
        list
            List of all `standard_names`.

        """
        return [getattr(self._dict[name], VAR_STD_NAME_STR) for
                name in self._dict]


class Models(object):
    """Class to easily access a namelist's datasets

    This class is designed to easily access datasets in the diagnostic script.

    Examples
    --------
    Get all variables of a namelist configuration `cfg`::

        models = Models(cfg)

    Access data of a model with path `path`::

        models.get_data(model_path=path)

    Access model information of the model::

        models.get_model_info(model_path=path)

    Access the data of all models with `exp=piControl'::

        models.get_data_list(exp=piControl)

    """

    def __init__(self, cfg):
        """Load models.

        Load all datasets of the namelist and store them in three internal
        dictionaries/lists (`self._paths`, `self._data` and `self._models`).

        Parameters
        ----------
        cfg : dict, optional
            Configuation dictionary of the namelist.

        """

        self._paths = []
        self._data = {}
        success = True
        if isinstance(cfg, dict):
            input_data = cfg.get(INPUT_DATA_STR)
            if isinstance(input_data, dict):
                for path in input_data:
                    model_info = input_data[path]
                    if (not isinstance(model_info, dict)):
                        success = False
                        break
                    self._paths.append(path)
                    self._data[path] = None
                self._models = input_data
            else:
                success = False
        else:
            success = False
        if (not success):
            raise TypeError("{} is not a valid ".format(repr(cfg)) +
                            "configuration file")
        self._n_models = len(self._paths)

    def __repr__(self):
        """Representation of the class.

        """
        output = ''
        for path in self._models:
            output += repr(self._models[path]) + '\n'
        return output

    def __iter__(self):
        """Allow iteration through class.

        """
        self._iter_counter = 0
        return self

    def __next__(self):
        """Allow iteration through class.

        """
        if (self._iter_counter >= self._n_models):
            raise StopIteration()
        else:
            next_element = self._paths[self._iter_counter]
            self._iter_counter += 1
            return next_element

    def add_model(self, path, data=None, **model_info):
        """Add model to class.

        Parameters
        ----------
        path : str
            (Unique) path to the dataset.
        data, optional
            Arbitrary object to be save as data for the model.
        **model_info, optional
            Keyword arguments describing the model, e.g. `model=CanESM2`,
            `exp=piControl` or `short_name=tas`.

        """
        if (path in self._paths):
            logger.warning("{} already exists! ".format(path) +
                           "Overwriting old data.")
            self._paths.remove(path)
        self._paths.append(path)
        self._data[path] = data
        self._models[path] = model_info

    def add_to_data(self, data, model_path=None, **model_info):
        """Add element to a model's data.

        Notes
        -----
        Either `model_path` or a unique `model_info` description have to be
        given. Prints warning and does nothing if given information is
        ambiguous.

        Parameters
        ----------
        data
            Element to be added to the model's data.
        model_path : str, optional
            Path to the dataset
        **model_info, optional
            Keyword arguments describing the model, e.g. `model=CanESM2`,
            `exp=piControl` or `short_name=tas`.

        """
        if (model_path is not None):
            if (model_path in self._paths):
                self._data[model_path] += data
                return None
            else:
                logger.warning("{} is not a valid ".format(model_path) +
                               "model path")
                return None
        paths = list(self._models)
        for info in model_info:
            paths = [path for path in paths if
                     self._models[path].get(info) == model_info[info]]
        if (not paths):
            logger.warning("Data could no be saved: " +
                           "{} does not match any model".format(model_info))
            return None
        if (len(paths) != 1):
            logger.warning("Data could no be saved: " +
                           "{} is ambiguous".format(model_info))
            return None
        self._data[path] += data

    def get_data(self, model_path=None, **model_info):
        """Access a model's data.

        Notes
        -----
        Either `model_path` or a unique `model_info` description have to be
        given. Fails when given information is ambiguous.

        Parameters
        ----------
        model_path : str, optional
            Path to the dataset
        **model_info, optional
            Keyword arguments describing the model, e.g. `model=CanESM2`,
            `exp=piControl` or `short_name=tas`.

        Returns
        -------
        data_object
            Data of the selected model

        Raises
        ------
        RuntimeError
            If data given by `model_info` is ambiguous.

        """
        if (model_path is not None):
            if (model_path in self._paths):
                return self._data.get(model_path)
            else:
                logger.warning("{} is not a valid ".format(model_path) +
                               "model path")
                return None
        paths = list(self._models)
        for info in model_info:
            paths = [path for path in paths if
                     self._models[path].get(info) == model_info[info]]
        if (not paths):
            logger.warning("No data could be returned: " +
                           "{} does not match any model".format(model_info))
            return None
        if (len(paths) > 1):
            msg = 'Given model information is ambiguous'
            logger.error(msg)
            raise RuntimeError(msg)
        return self._data[paths[0]]

    def get_data_list(self, **model_info):
        """Access the models' data in a list.

        Notes
        -----
        The returned data is sorted alphabetically respective to the `paths`.

        Parameters
        ----------
        **model_info, optional
            Keyword arguments describing the model, e.g. `model=CanESM2`,
            `exp=piControl` or `short_name=tas`.

        Returns
        -------
        list
            Data of the selected models.

        """
        paths = list(self._models)
        for info in model_info:
            paths = [path for path in paths if
                     self._models[path].get(info) == model_info[info]]
        if (not paths):
            logger.warning("No data could be returned: " +
                           "{} does not match any model".format(model_info))
        paths = sorted(paths)
        return [self._data[path] for path in paths]

    def get_exp(self, model_path):
        """Access a model's `exp`.

        Notes
        -----
        If the `model_info` does not contain an `exp` value, returns None.

        Parameters
        ----------
        model_path : str
            Path to the dataset

        Returns
        -------
        str
            `exp` information of the given model.

        """
        if (model_path in self._paths):
            output = self._models[model_path].get(EXP_STR)
            if (output is None):
                logger.warning("Model {} does not ".format(model_path) +
                               "contain 'exp' information")
            return output
        else:
            logger.warning("{} is not a valid ".format(model_path) +
                           "model path")
            return None

    def get_model(self, model_path):
        """Access a model's `model`.

        Notes
        -----
        If the `model_info` does not contain a `model` value, returns None.

        Parameters
        ----------
        model_path : str
            Path to the dataset

        Returns
        -------
        str
            `model` information of the given model.

        """
        if (model_path in self._paths):
            output = self._models[model_path].get(MODEL_STR)
            if (output is None):
                logger.warning("Model {} does not ".format(model_path) +
                               "contain 'model' information")
            return output
        else:
            logger.warning("{} is not a valid ".format(model_path) +
                           "model path")
            return None

    def get_model_info(self, model_path=None, **model_info):
        """Access a model's information.

        Notes
        -----
        Either `model_path` or a unique `model_info` description have to be
        given. Fails when given information is ambiguous.

        Parameters
        ----------
        model_path : str, optional
            Path to the dataset
        **model_info, optional
            Keyword arguments describing the model, e.g. `model=CanESM2`,
            `exp=piControl` or `short_name=tas`.

        Returns
        -------
        dict
            All model information.

        Raises
        ------
        RuntimeError
            If data given by `model_info` is ambiguous.

        """
        if (model_path is not None):
            if (model_path in self._paths):
                return self._models.get(model_path)
            else:
                logger.warning("{} is not a valid ".format(model_path) +
                               "model path")
                return None
        paths = list(self._models)
        for info in model_info:
            paths = [path for path in paths if
                     self._models[path].get(info) == model_info[info]]
        if (not paths):
            logger.warning("No data could be returned: " +
                           "{} does not match any model".format(model_info))
            return None
        if (len(paths) > 1):
            msg = 'Given model information is ambiguous'
            logger.error(msg)
            raise RuntimeError(msg)
        return self._models[paths[0]]

    def get_model_info_list(self, **model_info):
        """Access models information in a list.

        Notes
        -----
        The returned data is sorted alphabetically respective to the `paths`.

        Parameters
        ----------
        **model_info, optional
            Keyword arguments describing the model, e.g. `model=CanESM2`,
            `exp=piControl` or `short_name=tas`.

        Returns
        -------
        list
            Information dictionaries of the selected models.

        """
        paths = list(self._models)
        for info in model_info:
            paths = [path for path in paths if
                     self._models[path].get(info) == model_info[info]]
        if (not paths):
            logger.warning("No data could be returned: " +
                           "{} does not match any model".format(model_info))
        paths = sorted(paths)
        return [self._models[path] for path in paths]

    def get_path(self, **model_info):
        """Access a model's path

        Notes
        -----
        A unique `model_info` description has to be given. Fails when given
        information is ambiguous.

        Parameters
        ----------
        **model_info, optional
            Keyword arguments describing the model, e.g. `model=CanESM2`,
            `exp=piControl` or `short_name=tas`.

        Returns
        -------
        str
            Path of the selected model.

        Raises
        ------
        RuntimeError
            If data given by `model_info` is ambiguous.

        """
        paths = list(self._models)
        for info in model_info:
            paths = [path for path in paths if
                     self._models[path].get(info) == model_info[info]]
        if (not paths):
            logger.warning("No paths could be returned: " +
                           "{} does not match any model".format(model_info))
            return None
        if (len(paths) > 1):
            msg = 'Given model information is ambiguous'
            logger.error(msg)
            raise RuntimeError(msg)
        return paths[0]

    def get_path_list(self, **model_info):
        """Access models paths in a list.

        Notes
        -----
        The returned data is sorted alphabetically respective to the `paths`.

        Parameters
        ----------
        **model_info, optional
            Keyword arguments describing the model, e.g. `model=CanESM2`,
            `exp=piControl` or `short_name=tas`.

        Returns
        -------
        list
            Paths of the selected models.

        """
        paths = list(self._models)
        for info in model_info:
            paths = [path for path in paths if
                     self._models[path].get(info) == model_info[info]]
        if (not paths):
            logger.warning("No paths could be returned: " +
                           "{} does not match any model".format(model_info))
        paths = sorted(paths)
        return paths

    def get_project(self, model_path):
        """Access a model's `project`.

        Notes
        -----
        If the `model_info` does not contain a `project` value, returns None.

        Parameters
        ----------
        model_path : str
            Path to the dataset

        Returns
        -------
        str
            `project` information of the given model.

        """
        if (model_path in self._paths):
            output = self._models[model_path].get(PROJECT_STR)
            if (output is None):
                logger.warning("Model {} does not ".format(model_path) +
                               "contain 'project' information")
            return output
        else:
            logger.warning("{} is not a valid ".format(model_path) +
                           "model path")
            return None

    def get_short_name(self, model_path):
        """Access a model's `short_name`.

        Notes
        -----
        If the `model_info` does not contain a `short_name` value, returns
        None.

        Parameters
        ----------
        model_path : str
            Path to the dataset

        Returns
        -------
        str
            `short_name` information of the given model.

        """
        if (model_path in self._paths):
            output = self._models[model_path].get(SHORT_NAME_STR)
            if (output is None):
                logger.warning("Model {} does not ".format(model_path) +
                               "contain 'short_name' information")
            return output
        else:
            logger.warning("{} is not a valid ".format(model_path) +
                           "model path")
            return None

    def set_data(self, data, model_path=None, **model_info):
        """Set element as a model's data.

        Notes
        -----
        Either `model_path` or a unique `model_info` description have to be
        given. Prints warning and does nothing if given information is
        ambiguous.

        Parameters
        ----------
        data
            Element to be set as the model's data.
        model_path : str, optional
            Path to the dataset
        **model_info, optional
            Keyword arguments describing the model, e.g. `model=CanESM2`,
            `exp=piControl` or `short_name=tas`.

        """
        if (model_path is not None):
            if (model_path in self._paths):
                self._data[model_path] = data
                return None
            else:
                logger.warning("{} is not a valid ".format(model_path) +
                               "model path")
                return None
        paths = list(self._models)
        for info in model_info:
            paths = [path for path in paths if
                     self._models[path].get(info) == model_info[info]]
        if (not paths):
            logger.warning("Data could no be saved: " +
                           "{} does not match any model".format(model_info))
            return None
        if (len(paths) != 1):
            logger.warning("Data could no be saved: " +
                           "{} is ambiguous".format(model_info))
            return None
        self._data[path] = data
