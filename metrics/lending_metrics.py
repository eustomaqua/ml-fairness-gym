# coding=utf-8
# Copyright 2019 The ML Fairness Gym Authors.
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

"""Metrics for lending environments."""

from __future__ import absolute_import
from __future__ import division

from __future__ import print_function

import core
from environments import lending
import numpy as np
from typing import Dict, Text


class CreditDistribution(core.Metric):
  """Metric that returns a report of the population credit distribution."""

  def __init__(self, env, step=-1, realign_fn=None):
    super(CreditDistribution, self).__init__(env, realign_fn=realign_fn)
    self.step = step

  def measure(self, env):
    """Returns the distribution of credit scores for each group."""
    history = self._extract_history(env)
    params = history[self.step].state.params
    result = {}
    for component in params.applicant_distribution.components:
      group_id = np.argmax(component.components[0].group_membership.mean)
      result[str(group_id)] = component.weights
    return result


class CumulativeLoans(core.Metric):
  """Returns the cumulative number of loans given to each group over time."""

  def measure(self, env):
    """Returns an array of size (num_groups) x (num_steps).

    Cell (i, j) contains the cumulative number of loans given at time j to group
    members of group i.

    Args:
      env: The environment to be measured.
    """

    history = self._extract_history(env)
    result = []
    for history_item in history:
      state = history_item.state  # type: lending.State
      # Take advantage of the one-hot encoding of state.group in order to build
      # a (num_steps) x (num_groups) array with 1s where loans were given.
      # Multiplying by action makes a row of all zeros if the loan was rejected.
      result.append(np.array(state.group) * history_item.action)
    return np.cumsum(result, 0).T
