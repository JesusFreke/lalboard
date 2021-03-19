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
    thumb_base, _ = lalboard.thumb_base("thumb_cluster_right")
    pcb = lalboard.thumb_pcb(thumb_base, name="thumb_pcb_right")
    pcb.scale(-1, 1, 1)

    pcb_bottom_tool = pcb.bounding_box.make_box()
    pcb_bottom_tool.place(
        ~pcb_bottom_tool == ~pcb,
        ~pcb_bottom_tool == ~pcb,
        +pcb_bottom_tool == -pcb)

    pcb_bottom = pcb.find_faces(pcb_bottom_tool)[0]

    occurrence = pcb_bottom.make_component(name="pcb_bottom").create_occurrence(scale=.1, create_children=False)

    # This serves as a virtual "locating pin" that helps position the outlines when updating the outline in an existing
    # kicad pcb design.
    origin_locator = Cylinder(1, 1).create_occurrence(scale=.1)

    sketch = root().sketches.add(root().xYConstructionPlane)
    sketch.project(occurrence.bRepBodies[0].faces[0])
    sketch.project(origin_locator.bRepBodies[0])
    sketch.name = "thumb_pcb_right"

    occurrence.deleteMe()
    origin_locator.deleteMe()


def run(_):
    lalboard.run_design(design)
