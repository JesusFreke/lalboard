# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import adsk.core

from fscad import *
relative_import("../../lalboard.py")
import lalboard


def design():
    sheet = lalboard.steel_sheet_design(left_hand=True)

    occurrence = sheet.create_occurrence(scale=.1)

    sketch = root().sketches.add(root().xYConstructionPlane)
    sketch.project(occurrence.bRepBodies[0].faces[0])
    sketch.name = "cluster_pcb_sketch"


def run(_):
    lalboard.run_design(design)
