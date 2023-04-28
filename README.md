# ROS parameter store

**NOTE**: I no longer work in the field of robotics, this is not maintained. But
hopefully the ideas and techniques presented here might be of use to you. Or the
software itself might even still work!

---

Implements parameter store to file. Inspired by [mongodb_store]() but designed
to be simpler and more reliable to power failures. The API is designed to be
similar to a subset of [mongodb_store]().

# File format

The file format used both for default values and the persisted data is YAML,
but slightly different than what mongodb_store uses. The keys are the parameter
names and the value the parameter value. You should not use YAML dictionaries to
represent namespaces. For example:

```yaml
/my_parameter_in_root_ns: 2
/namespace/my_list_parameter:
  - {some_key: some_value}
  - 42
```

# Parameters

This node has two mandatory parameters:

* `~defaults_path` (`string`) - Path to *directory* containing default YAML files
  that should be loaded
* `~save_path` (`string`) - Path to *file* that will be used to store parameters
  to.

# Services

* `save_param` (`ros_parameter_store_msgs/SaveParam`) - Save a single parameter,
  reading the current value from the parameter server. Always use absolute paths
  for the parameter name to ensure consistency even if this node runs in a
  namespace.

[mongodb_store]: https://github.com/strands-project/mongodb_store
