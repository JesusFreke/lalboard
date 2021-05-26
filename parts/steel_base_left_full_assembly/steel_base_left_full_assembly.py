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

    clusters = [
        context.positioned_cluster_assembly(
            down_key_top_center=Point3D.create(8.43, 116.23, 31.09 + z_delta),
            rx=13.45,
            ry=-.16,
            rz=1.46),
        context.positioned_cluster_assembly(
            down_key_top_center=Point3D.create(-17.77, 120.09, 30.46 + z_delta),
            rx=13.12,
            ry=-2.05,
            rz=14.03),
        context.positioned_cluster_assembly(
            down_key_top_center=Point3D.create(-43.61, 110.04, 27.73 + z_delta),
            rx=12.75,
            ry=-11.36,
            rz=21.95),
        context.positioned_cluster_assembly(
            down_key_top_center=Point3D.create(-56.37, 85.04, 21.62 + z_delta),
            rx=9.68,
            ry=-12.95,
            rz=41.31,
            tall_clip=True),
        context.positioned_thumb_assembly(
            front_mid_point=Point3D.create(47.97893425529047, 81.74006227791716, 35.11242627971235 + z_delta),
            rx=9.19,
            ry=-2.67,
            rz=14.28,
            left_hand=True)]

    Group([*clusters, *base.children()]).tz(-z_delta).create_occurrence(scale=.1)


def run(context):
    lalboard.run_design(design, context=context)
