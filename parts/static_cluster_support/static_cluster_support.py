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
relative_import("../../lalboard.py")
import lalboard


# don't export an stl of this, it's only for development
EXPORT = False


def design(context: lalboard.Lalboard):
    cluster = context.positioned_cluster_assembly(
        lalboard.RelativeFingerClusterPlacement(context)
            .set_cylindrical(116.53, 31.09, gap=-8.44)
            .set_rotation_by_euler_angles(13.45, -.16, 1.46)
            .resolve(None, left_hand=True),
        add_clip=False)
    cluster.create_occurrence(scale=.1)
    context.static_cluster_support(cluster).create_occurrence(scale=.1)


def run(context):
    lalboard.run_design(design, context=context)
