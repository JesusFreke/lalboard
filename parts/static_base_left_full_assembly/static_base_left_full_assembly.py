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
from adsk.core import Point3D

from fscad.fscad import *

relative_import("../../lalboard.py")
import lalboard


def design(context: lalboard.Lalboard):

    finger_clusters = []
    finger_clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(116.53, 31.09, gap=-8.44)
                .set_rotation_by_euler_angles(13.45, -.16, 1.46)
                .resolve(None, left_hand=True),
        add_clip=False))
    finger_clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(121.40, 30.46)
                .set_rotation_by_euler_angles(13.12, -2.05, 14.03)
                .resolve(finger_clusters[-1], left_hand=True),
        add_clip=False))
    finger_clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(118.37, 27.73)
                .set_rotation_by_euler_angles(12.75, -11.36, 21.95)
                .resolve(finger_clusters[-1], left_hand=True),
            add_clip=False))
    finger_clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(102.03, 21.62)
                .set_rotation_by_euler_angles(9.68, -12.95, 41.31)
                .resolve(finger_clusters[-1], left_hand=True),
            add_clip=False))

    thumb_cluster = context.positioned_thumb_assembly(
        lalboard.AbsoluteThumbClusterPlacement(context)
            .set_cartesian(47.98, 81.74, 35.11)
            .set_rotation_by_euler_angles(9.19, -2.67, 14.28),
        left_hand=True)

    static_base = context.static_base(
        finger_clusters,
        thumb_cluster,
        left_hand=True)

    Group([*finger_clusters, thumb_cluster, *static_base.children()]).create_occurrence(scale=.1)


def run(context):
    lalboard.run_design(design, context=context)
