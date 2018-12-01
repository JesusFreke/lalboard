# Copyright 2019 Google LLC
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
import adsk.fusion

from fscad import *

key_radius = 8
outer_radius = 12.5
key_thickness = 1.8
post_width = 4.5


def tapered_cube(bottom, top, height, name):
    bottom_face = rect(1.55, 1.55, name="bottom")
    top_face = place(rect(1.7, 1.7, name="top"),
                     midAt(atMid(bottom_face)),
                     midAt(atMid(bottom_face)),
                     midAt(height))
    return loft(bottom_face, top_face, name=name)


def vertical_key_post(post_length, groove_height, magnet_height):
    post = box(post_width, post_length, key_thickness, name="post")
    fillet(edges(post, ["front"], ["top", "bottom"]), sizeOf(post).z/2)

    magnet_hole = place(tapered_cube(1.55, 1.7, sizeOf(post).z - .2, "magnet_hole"),
                        midAt(atMid(post)), midAt(magnet_height), maxAt(atMax(post)))

    groove_size = .6
    groove = place(box(sizeOf(post).x, groove_size, groove_size, name="groove"),
                   midAt(atMid(post)), minAt(groove_height), minAt(atMin(post)))
    return difference(post, magnet_hole, groove)


def vertical_key(post_length, key_width, key_height, key_protrusion, key_displacement, groove_height, magnet_height):
    post = vertical_key_post(post_length, groove_height, magnet_height)

    if key_protrusion:
        place(box(post_width, post_width, key_protrusion),
              midAt(atMid(post)), maxAt(atMax(post)), minAt(atMin(post)))

    key_base = place(box(13, key_height, 10, name="key_base"),
                     midAt(atMid(post)), minAt(atMax(post)), minAt(atMin(post)))

    key_dish = place(rx(cylinder(sizeOf(key_base).y, 15), 90),
                     midAt(atMid(post)), midAt(atMid(key_base)), minAt(atMax(post)))
    dished_key = difference(key_base, key_dish, name="dished_key")

    face_list = [get_face(key_dish, "side"), "left", "right", "back"]
    fillet(edges(dished_key, face_list, face_list), .5, False)


def side_key(key_height):
    vertical_key(
        post_length=10,
        key_width=13,
        key_height=key_height,
        key_protrusion=False,
        key_displacement=False,
        groove_height=.7,
        magnet_height=5.45)


def design():
    side_key(5)


def run(context):
    run_design(design, message_box_on_error=False, document_name=__name__)
