# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""TFX StatisticsGen component definition."""
from typing import List, Optional

from absl import logging
import tensorflow_data_validation as tfdv
from tfx import types
from tfx.components.statistics_gen import executor
from tfx.dsl.components.base import base_beam_component
from tfx.dsl.components.base import executor_spec
from tfx.types import standard_artifacts
from tfx.types import standard_component_specs
from tfx.utils import json_utils


class StatisticsGen(base_beam_component.BaseBeamComponent):
  """Official TFX StatisticsGen component.

  The StatisticsGen component generates features statistics and random samples
  over training data, which can be used for visualization and validation.
  StatisticsGen uses Apache Beam and approximate algorithms to scale to large
  datasets.

  ## Example
  ```
    # Computes statistics over data for visualization and example validation.
    statistics_gen = StatisticsGen(examples=example_gen.outputs['examples'])
  ```

  Component `outputs` contains:
   - `statistics`: Channel of type `standard_artifacts.ExampleStatistics` for
                   statistics of each split provided in the input examples.

  Please see [the StatisticsGen
  guide](https://www.tensorflow.org/tfx/guide/statsgen) for more details.
  """

  SPEC_CLASS = standard_component_specs.StatisticsGenSpec
  EXECUTOR_SPEC = executor_spec.BeamExecutorSpec(executor.Executor)

  def __init__(self,
               examples: types.Channel,
               schema: Optional[types.Channel] = None,
               stats_options: Optional[tfdv.StatsOptions] = None,
               exclude_splits: Optional[List[str]] = None):
    """Construct a StatisticsGen component.

    Args:
      examples: A Channel of `ExamplesPath` type, likely generated by the
        [ExampleGen component](https://www.tensorflow.org/tfx/guide/examplegen).
        This needs to contain two splits labeled `train` and `eval`. _required_
      schema: A `Schema` channel to use for automatically configuring the value
        of stats options passed to TFDV.
      stats_options: The StatsOptions instance to configure optional TFDV
        behavior. When stats_options.schema is set, it will be used instead of
        the `schema` channel input. Due to the requirement that stats_options be
        serialized, the slicer functions and custom stats generators are dropped
        and are therefore not usable.
      exclude_splits: Names of splits where statistics and sample should not
        be generated. Default behavior (when exclude_splits is set to None)
        is excluding no splits.
    """
    if exclude_splits is None:
      exclude_splits = []
      logging.info('Excluding no splits because exclude_splits is not set.')
    statistics = types.Channel(type=standard_artifacts.ExampleStatistics)
    # TODO(b/150802589): Move jsonable interface to tfx_bsl and use json_utils.
    stats_options_json = stats_options.to_json() if stats_options else None
    spec = standard_component_specs.StatisticsGenSpec(
        examples=examples,
        schema=schema,
        stats_options_json=stats_options_json,
        exclude_splits=json_utils.dumps(exclude_splits),
        statistics=statistics)
    super().__init__(spec=spec)
