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
    base = context.steel_base(left_hand=False)
    steel_sheet = base.find_children("steel_sheet", recursive=True)[0]
    handrest = base.find_children("right_handrest")[0]

    # The coordinates below assume that the bottom of the clusters are even with the bottom of the handrest.
    # But the handrest of this base is slightly higher than the steel sheet, so this takes that into account
    z_delta = handrest.min().z - steel_sheet.max().z
    base.tz(z_delta)

    clusters = []
    clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(116.70, 30.37 + z_delta, gap=-21.12)
                .set_rotation_by_support_lengths(22.57, 28.50, 27.47, rz=-8.19)
                #.set_rotation_by_euler_angles(13.74, 3.31, -8.19)
                .resolve(None, left_hand=False)))
    clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(121.75, 31.49 + z_delta)
                .set_rotation_by_support_lengths(24.83, 29.25, 26.62, rz=-17.92)
                #.set_rotation_by_euler_angles(10.65, 8.44, -17.92)
                .resolve(clusters[-1], left_hand=False)))
    clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(115.28, 28.05 + z_delta)
                .set_rotation_by_support_lengths(22.06, 24.60, 22.59, rz=-25.54)
                #.set_rotation_by_euler_angles(8.51, 6.45, -25.54)
                .resolve(clusters[-1], left_hand=False)))
    clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(100.94, 21.66 + z_delta)
                .set_rotation_by_support_lengths(17.68, 20.29, 16.21, rz=-37.05, tall_front_clip=True)
                #.set_rotation_by_euler_angles(10.65, 13.16, -37.05)
                .resolve(clusters[-1], left_hand=False),
            tall_clip=True))
    clusters.append(
        context.positioned_thumb_assembly(
            lalboard.AbsoluteThumbClusterPlacement(context)
                .set_cartesian(-50.35, 83.96, 36.26 + z_delta)
                .set_rotation_by_support_lengths(24.60, 27.24, 31.63, rz=-7.77),
                #.set_rotation_by_euler_angles(10.39, -1.44, -7.77),
            left_hand=False))

    standoffs = []
    for cluster in clusters[0:4]:
        standoffs.append(context.add_standoffs(cluster))
    standoffs.append(context.add_thumb_standoffs(clusters[4]))

    Group([*clusters, *standoffs, *base.children()]).tz(-z_delta).create_occurrence(scale=.1)


def run(context):
    lalboard.run_design(design, context=context)
