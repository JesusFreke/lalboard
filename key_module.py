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
import time

from fscad import *

key_thickness = 1.8
post_width = 4.5


def small_pin(length):
    return Cylinder(length, .4, name="small_pin")


def make_pt_cavity(block: Component, base_height):
    lens_height = 4.5
    lens_radius = .75

    body = Box(1.8, 5, block.size().z, "body")

    lens_hole = Cylinder(block.size().y, lens_radius, name="lens_hole")
    lens_hole.ry(90).place(-lens_hole == +body, ~lens_hole == ~body, ~lens_hole == lens_height)
    lens_slot = Box(lens_radius + .05, lens_radius * 2 + .1, block.size().y, "lens_slot")
    lens_slot.place(-lens_slot == +body, ~lens_slot == ~body, -lens_slot == ~lens_hole)

    cavity = Union(body, lens_hole, lens_slot, name="phototransistor_cavity")

    temp = Union(body.copy(), lens_slot.copy())
    cavity.place(~temp == ~block, ~temp == ~block, -temp == -block)
    cavity = Intersection(cavity, block.copy())

    leg = small_pin(base_height)
    leg.place(~leg == ~body, (~leg == ~body) + 2.54/2, +leg == -body)
    legs = Union(leg, leg.copy().ty(-2.54), name="legs")

    return Union(cavity, legs)


def make_led_cavity(block, base_height):
    lens_radius = .75
    lens_height = 2.9

    body = Box(1.8, 5.1, block.size().z - 1.6, "body")

    slot = Box(1.1, body.size().y, body.size().z, "slot")
    slot.place(+slot == -body, ~slot == ~body, -slot == -body)

    lens_hole = Cylinder(block.size().y, lens_radius, name="lens_hole").ry(90)
    lens_hole.place(+lens_hole == -body, ~lens_hole == ~body, ~lens_hole == lens_height)

    cavity = Union(body, slot, lens_hole, name="led_cavity")
    temp = Union(body.copy(), slot.copy())

    cavity.place((~temp == ~block) - .125, ~temp == ~block, +temp == +block)
    cavity = Intersection(cavity, block.copy())

    leg = small_pin(base_height + 1.6)
    leg.place((~leg == +body) - .9,
              (~leg == ~body) + 2.54/2,
              +leg == -body)
    legs = Union(leg, leg.copy().ty(-2.54), name="legs")
    return Union(cavity, legs)


def vertical_key_base(base_height):
    front = Box(5, 2.2, 6.4, "front")
    pt_base = Box(5, 6.15, 6.4, "phototransistor_base")
    pt_base.place(+pt_base == -front, +pt_base == +front, -pt_base == -front)

    led_base = Box(6, 6.15, 6.4, "led_base")
    led_base.place(-led_base == +front, +led_base == +front, -led_base == -front)

    pt_cavity = make_pt_cavity(pt_base, base_height)
    led_cavity = make_led_cavity(led_base, base_height)

    return Union(front,
                 Difference(pt_base, pt_cavity),
                 Difference(led_base, led_cavity))


def _design():
    start = time.time()

    vertical_key_base(2).scale(.1, .1, .1).create_occurrence(False)

    end = time.time()
    print(end-start)


def run(_):
    run_design(_design, message_box_on_error=False, document_name=__name__)
