from __future__ import (print_function, absolute_import, division)

import os
import yaml

import rospy
from funcy.py3 import walk_keys
from pathlib2 import Path
from ros_parameter_store_msgs.srv import SaveParam, SaveParamRequest, SaveParamResponse


def _normalise_name(parameter_name):
    """Normalise parameter names

    :type parameter_name: str
    :rtype: str
    """
    if parameter_name[0] != '/':
        return '/' + parameter_name
    return parameter_name


def _normalise_dict(parameters):
    """Normalise all the parameters in the dictionary keys

    :type parameters: Dict[str, Any]
    :rtype: Dict[str, Any]
    """
    return walk_keys(_normalise_name, parameters)


def _load_file(file_name):
    """Load a file with parameters

    :type file_name: Path
    :param file_name: File name to load

    :rtype: Dict[str, Any]
    """
    with file_name.open(mode='rb') as fh:
        return _normalise_dict(yaml.safe_load(fh))


class Node(object):
    """Main node class"""

    def __init__(self):
        """Constructor"""
        # Path with yaml files with default values
        self._defaults_path = Path(rospy.get_param('~defaults_path'))
        # YAML file to save parameters to
        self._save_path = Path(rospy.get_param('~save_path'))
        self._managed_parameters = {}

        self._save_srv = rospy.Service('save_param', SaveParam, self._callback_save_param)

        # Load defaults
        for p in self._defaults_path.rglob('*.yaml'):  # type: Path
            self._managed_parameters.update(_load_file(p))

        # Load persisted values
        try:
            self._managed_parameters.update(_load_file(self._save_path))
        except IOError:
            rospy.logwarn("Failed to load persisted file. Ignoring and assuming first run.")

        # Push parameters
        self._restore_to_ros()

    def _save_parameters(self):
        """Save managed parameters"""
        with self._save_path.open(mode='wb') as fh:
            yaml.safe_dump(self._managed_parameters, fh)
            fh.flush()
            os.fsync(fh.fileno())

    def _restore_to_ros(self):
        """Restore all managed parameters to parameter server"""
        for name, value in self._managed_parameters.items():
            rospy.set_param(name, value)

    def _callback_save_param(self, req):
        """Handle persisting a parameter

        :type req: SaveParamRequest
        :rtype: SaveParamResponse
        """
        param_name = _normalise_name(req.param)
        try:
            value = rospy.get_param(param_name)
        except KeyError as e:
            rospy.logerr("Asked to save non-existing parameter %r" % param_name)
            return SaveParamResponse(success=False)

        rospy.loginfo("Saving %r - %r" % (param_name, value))
        self._managed_parameters[param_name] = value
        self._save_parameters()
        return SaveParamResponse(success=True)


def main():
    """Main program entry point"""
    rospy.init_node("oru_ipw_controller")

    ros_node = Node()

    # Spin on ROS message bus
    rospy.spin()
