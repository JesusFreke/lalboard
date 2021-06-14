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
    base = context.steel_base(left_hand=True)
    steel_sheet = base.find_children("steel_sheet", recursive=True)[0]
    handrest = base.find_children("left_handrest")[0]

    # The coordinates below assume that the bottom of the clusters are even with the bottom of the handrest.
    # But the handrest of this base is slightly higher than the steel sheet, so this takes that into account
    z_delta = handrest.min().z - steel_sheet.max().z
    base.tz(z_delta)

    clusters = []
    clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(116.53, 31.09 + z_delta, gap=-8.44)
                .set_rotation_by_support_lengths(23.36, 28.55, 28.60, rz=1.46)
                #.set_rotation_by_euler_angles(13.45, -.16, 1.46)
                .resolve(None, left_hand=True)))
    clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(121.40, 30.46 + z_delta)
                .set_rotation_by_support_lengths(22.84, 27.49, 28.13, rz=14.03)
                #.set_rotation_by_euler_angles(13.12, -2.05, 14.03)
                .resolve(clusters[-1], left_hand=True)))
    clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(118.37, 27.73 + z_delta)
                .set_rotation_by_support_lengths(20.49, 23.33, 26.86, rz=21.95)
                #.set_rotation_by_euler_angles(12.75, -11.36, 21.95)
                .resolve(clusters[-1], left_hand=True)))
    clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(102.03, 21.62 + z_delta)
                .set_rotation_by_support_lengths(17.97, 15.81, 19.83, rz=41.31, tall_front_clip=True)
                #.set_rotation_by_euler_angles(9.68, -12.95, 41.31)
                .resolve(clusters[-1], left_hand=True),
            tall_clip=True))
    clusters.append(context.positioned_thumb_assembly(
        lalboard.AbsoluteThumbClusterPlacement(context)
            .set_cartesian(47.98, 81.74, 35.11 + z_delta)
            .set_rotation_by_support_lengths(23.46, 27.41, 30.33, rz=14.28, left_hand=True),
            #.set_rotation_by_euler_angles(9.19, -2.67, 14.28),
        left_hand=True))

    standoffs = []
    for cluster in clusters[0:4]:
        standoffs.append(context.add_standoffs(cluster))
    standoffs.append(context.add_thumb_standoffs(clusters[4]))

    Group([*clusters, *standoffs, *base.children()]).tz(-z_delta).create_occurrence(scale=.1)


def run(context):
    lalboard.run_design(design, context=context)
