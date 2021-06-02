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

from fscad.fscad import *
import fscad.fscad
relative_import("../../lalboard.py")
import lalboard


# don't export an stl of this, it's only for development
EXPORT = False


def design(context: lalboard.Lalboard):

    thumb_cluster = context.positioned_thumb_assembly(
        lalboard.AbsoluteThumbClusterPlacement(context)
            .set_cartesian(47.98, 81.74, 35.11)
            .set_rotation_by_euler_angles(9.19, -2.67, 14.28),
        left_hand=False)

    thumb_cluster.create_occurrence(scale=.1)
    context.static_thumb_support(thumb_cluster).create_occurrence(scale=.1)


def run(context):
    lalboard.run_design(design, context=context)
