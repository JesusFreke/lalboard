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
    steel_sheet = base.find_children("steel_sheet", recursive=False)[0]

    handrest = base.find_children("right_handrest")[0]

    # The coordinates below assume that the bottom of the clusters are even with the bottom of the handrest.
    # But the handrest of this base is slightly higher than the steel sheet, so this takes that into account
    z_delta = handrest.min().z - steel_sheet.max().z
    base.tz(z_delta)

    clusters = [
        context.positioned_cluster_assembly(
            down_key_top_center=Point3D.create(-20.79, 114.83, 30.37 + z_delta),
            rx=13.74,
            ry=3.31,
            rz=-8.19),
        context.positioned_cluster_assembly(
            down_key_top_center=Point3D.create(7.53, 121.52, 31.49 + z_delta),
            rx=10.65,
            ry=8.44,
            rz=-17.92),
        context.positioned_cluster_assembly(
            down_key_top_center=Point3D.create(30.53, 111.16, 28.05 + z_delta),
            rx=8.51,
            ry=6.45,
            rz=-25.54),
        context.positioned_cluster_assembly(
            down_key_top_center=Point3D.create(47.28, 89.18, 21.66 + z_delta),
            rx=10.65,
            ry=13.16,
            rz=-37.05,
            tall_clip=True),
        context.positioned_thumb_assembly(
            front_mid_point=Point3D.create(-50.35, 83.96, 36.26 + z_delta),
            rx=10.39,
            ry=-1.44,
            rz=-7.77,
            left_hand=False)]

    Group([*clusters, *base.children()]).tz(-z_delta).create_occurrence(scale=.1)


def run(context):
    lalboard.run_design(design, context=context)
