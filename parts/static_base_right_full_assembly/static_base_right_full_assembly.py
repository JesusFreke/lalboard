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
                .set_cylindrical(116.70, 30.37, gap=-21.12)
                .set_rotation_by_euler_angles(13.74, 3.31, -8.19)
                .resolve(None, left_hand=False),
            add_clip=False))
    finger_clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(121.75, 31.49, gap=.36)
                .set_rotation_by_euler_angles(10.65, 8.44, -17.92)
                .resolve(finger_clusters[-1], left_hand=False),
            add_clip=False))
    finger_clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(115.28, 28.05)
                .set_rotation_by_euler_angles(8.51, 6.45, -25.54)
                .resolve(finger_clusters[-1], left_hand=False),
            add_clip=False))
    finger_clusters.append(
        context.positioned_cluster_assembly(
            lalboard.RelativeFingerClusterPlacement(context)
                .set_cylindrical(100.94, 21.66, gap=.33)
                .set_rotation_by_euler_angles(10.65, 13.16, -37.05)
                .resolve(finger_clusters[-1], left_hand=False),
            add_clip=False))

    thumb_cluster = context.positioned_thumb_assembly(
        lalboard.AbsoluteThumbClusterPlacement(context)
            .set_cartesian(-50.35, 83.96, 36.26)
            .set_rotation_by_euler_angles(10.39, -1.44, -7.77),
        left_hand=False)

    static_base = context.static_base(
        finger_clusters,
        thumb_cluster,
        left_hand=False)

    central_pcb = static_base.find_children("central_pcb")[0]
    central_pcb_spacer = context.central_pcb_spacer()
    central_pcb_spacer.place(
        ~central_pcb_spacer == ~central_pcb,
        +central_pcb_spacer == +central_pcb,
        +central_pcb_spacer == -central_pcb)

    Group([
        *finger_clusters,
        thumb_cluster,
        *static_base.children(),
        central_pcb,
        central_pcb_spacer]).create_occurrence(scale=.1)


def run(context):
    lalboard.run_design(design, context=context)
