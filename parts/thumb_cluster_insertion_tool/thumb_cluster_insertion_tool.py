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
    (thumb_base, down_key, outer_lower_key, outer_upper_key, inner_key, mode_key,
     insertion_tool, clip, pcb) = lalboard.full_thumb(left_hand=False)
    insertion_tool.rx(180)
    insertion_tool.create_occurrence(scale=.1)


def run(_):
    lalboard.run_design(design, message_box_on_error=False, document_name=__name__)
