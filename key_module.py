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


def small_pin():
    return Circle(.4, name="small_pin")


def tapered_box(bottom_x, bottom_y, top_x, top_y, height, name):
    bottom_face = Rect(bottom_x, bottom_y, "tapered_box_bottom")
    top_face = Rect(top_x, top_y, "tapered_box_top")
    top_face.place(~top_face == ~bottom_face,
                   ~top_face == ~bottom_face,
                   ~top_face == height)
    return Loft(bottom_face, top_face, name=name)


def horizontal_magnet_cutout(depth=1.8, name="magnet_cutout"):
    return tapered_box(1.45, 1.8, 1.7, 1.8, depth, name=name).rx(90)


def make_pt_cavity():
    lens_height = 4.5
    lens_radius = .75

    body = Box(1.8, 5, 5.7, "body")

    lens_hole = Circle(lens_radius, name="lens_hole")
    lens_hole.ry(90).place(-lens_hole == +body, ~lens_hole == ~body, ~lens_hole == lens_height)
    lens_slot = Box(lens_radius + .05, lens_radius * 2 + .1, body.max().z - lens_hole.min().z, "lens_slot")
    lens_slot.place(-lens_slot == +body, ~lens_slot == ~body, -lens_slot == -lens_hole)
    lens_hole.place(~lens_hole == +lens_slot)

    cavity = Union(body, lens_slot, name="phototransistor_cavity")
    cavity = SplitFace(cavity, lens_hole)

    leg = small_pin()
    leg.place(~leg == ~body, (~leg == ~body) + 2.54/2, +leg == -body)
    leg2 = leg.copy().ty(-2.54)
    legs = Union(leg, leg2, name="legs")
    cavity = SplitFace(cavity, legs)

    cavity.add_faces("legs", *cavity.find_faces((leg, leg2)))
    cavity.add_faces("lens_hole", *cavity.find_faces(lens_hole))
    cavity.add_faces("top", *cavity.find_faces(body.top))

    cavity.add_point("lens_center",
                     (cavity.mid().x, cavity.mid().y, lens_hole.bodies()[0].faces[0].brep.centroid.z))

    return cavity


def make_led_cavity():
    lens_radius = .75
    lens_height = 2.9

    body = Box(1.8, 5.1, 4.8, "body")

    slot = Box(1.1, body.size().y, body.size().z, "slot")
    slot.place(+slot == -body, ~slot == ~body, -slot == -body)

    lens_hole = Circle(lens_radius, name="lens_hole").ry(90)
    lens_hole.place(+lens_hole == -slot, ~lens_hole == ~body, ~lens_hole == lens_height)

    cavity = Union(body, slot, name="led_cavity")
    cavity = SplitFace(cavity, lens_hole)

    leg = small_pin()
    leg.place((~leg == +body) - .9,
              (~leg == ~body) + 2.54/2,
              +leg == -body)
    leg2 = leg.copy().ty(-2.54)
    legs = Union(leg, leg2, name="legs")

    cavity = SplitFace(cavity, legs)

    cavity.add_faces("legs", *cavity.find_faces((leg, leg2)))
    cavity.add_faces("lens_hole", *cavity.find_faces(lens_hole))
    cavity.add_faces("top", *cavity.find_faces((body.top, slot.top)))

    cavity.add_point("lens_center",
                     (cavity.mid().x, cavity.mid().y, lens_hole.bodies()[0].faces[0].brep.centroid.z))

    return cavity


def vertical_key_base(base_height, pressed_key_angle=20):
    front = Box(5, 2.2, 6.4, "front")

    pt_base = Box(5, 6.15, 6.4, "phototransistor_base")
    pt_base.place(+pt_base == -front, +pt_base == +front, -pt_base == -front)
    pt_cavity = make_pt_cavity()
    pt_cavity.place(~pt_cavity.point("lens_center") == ~pt_base,
                    ~pt_cavity.point("lens_center") == ~pt_base,
                    (~pt_cavity.point("lens_center") == +pt_base) - 1.9)

    led_base = Box(6, 6.15, 6.4, "led_base")
    led_base.place(-led_base == +front, +led_base == +front, -led_base == -front)
    led_cavity = make_led_cavity()
    led_cavity.place((~led_cavity.point("lens_center") == ~led_base) - .125,
                     ~led_cavity.point("lens_center") == ~led_base,
                     (~led_cavity.point("lens_center") == +led_base) - 1.9)

    temp = Union(front.copy(), pt_base.copy(), led_base.copy())
    base = Box(temp.size().x, temp.size().y, base_height, name="base")
    base.place(-base == -temp,
               -base == -temp,
               +base == -temp)

    key_pivot = Cylinder(front.size().x, 1, name="key-pivot").ry(90)
    key_pivot.place(~key_pivot == ~front,
                    +key_pivot == -front,
                    ~key_pivot == -front)

    sloped_key = Box(front.size().x, key_pivot.size().y, front.size().z * 2, "sloped_key")
    sloped_key.place(~sloped_key == ~key_pivot,
                     ~sloped_key == ~key_pivot,
                     -sloped_key == ~key_pivot)
    sloped_key = Union(sloped_key, key_pivot).rx(pressed_key_angle, center=(0, sloped_key.mid().y, 0))

    target_tip_thickness = .8
    back_bottom = Rect(front.size().x, led_base.size().y - front.size().y - key_pivot.size().y - target_tip_thickness,
                       "back_bottom")
    back_bottom.place(~back_bottom == ~front,
                      (-back_bottom == -led_base) + target_tip_thickness)
    back_bottom = Difference(back_bottom, sloped_key.copy())
    back_sloped = ExtrudeTo(back_bottom, sloped_key, "back_sloped")

    remaining_back = Box(front.size().x, target_tip_thickness, back_sloped.size().z, "remaining_back")
    remaining_back.place(~remaining_back == ~front,
                         +remaining_back == -back_sloped,
                         -remaining_back == -back_sloped)
    back = Union(remaining_back, back_sloped, name="back")

    retaining_ridge = Box(back.size().x, .5, .5, "retaining_ridge").rx(45)
    retaining_ridge.place(~retaining_ridge == ~back,
                          ~retaining_ridge == +remaining_back.top,
                          +retaining_ridge == +back)

    result = Union(pt_base, led_base, front, back, base, name="vertical_key_base")
    result = Difference(result, sloped_key)
    result = Union(result, retaining_ridge)

    magnet_cutout = horizontal_magnet_cutout()
    magnet_cutout.place(~magnet_cutout == ~front,
                        -magnet_cutout == -front,
                        (+magnet_cutout == +front) - .45)

    result.add_point("midpoint", (magnet_cutout.mid().x, result.mid().y, result.mid().z))

    extruded_led_cavity = ExtrudeTo(led_cavity.faces("lens_hole"), result.copy(False))
    extruded_led_cavity = ExtrudeTo(
        extruded_led_cavity.find_faces(led_cavity.faces("legs")), result.copy(False))

    extruded_pt_cavity = ExtrudeTo(pt_cavity.faces("lens_hole"), result.copy(False))
    extruded_pt_cavity = ExtrudeTo(extruded_pt_cavity.find_faces(pt_cavity.faces("legs")), result.copy(False))
    extruded_pt_cavity = ExtrudeTo(extruded_pt_cavity.find_faces(pt_cavity.faces("top")), result.copy(False))

    return result, Union(
        extruded_pt_cavity, extruded_led_cavity, magnet_cutout, key_pivot, name="vertical_key_base_negative")


def cluster():
    base = Box(24.9, 24.9, 2, "base")
    key_base, key_base_negative = vertical_key_base(2)

    key_base_negative.place(~key_base.point("midpoint") == ~base,
                            -key_base == -base,
                            -key_base == -base)
    key_base.place(~key_base.point("midpoint") == ~base,
                   -key_base == -base,
                   -key_base == -base)

    key_bases = (
        key_base.copy().scale(-1, 1, 1, center=key_base.point("midpoint")),
        key_base.copy().rz(90, base.mid()),
        key_base.copy().scale(-1, 1, 1, center=key_base.point("midpoint")).rz(180, base.mid()),
        key_base.rz(270, base.mid())
    )
    key_base_negatives = (
        key_base_negative.copy().scale(-1, 1, 1, center=key_bases[0].point("midpoint")),
        key_base_negative.copy().rz(90, base.mid()),
        key_base_negative.copy().scale(-1, 1, 1, center=key_bases[0].point("midpoint")).rz(180, base.mid()),
        key_base_negative.rz(270, base.mid())
    )

    return Difference(Union(base, *key_bases), *key_base_negatives)


def _design():
    start = time.time()

    result = cluster().scale(.1, .1, .1).create_occurrence(True)
    #result = vertical_key_base(2)
    #Difference(result[0], result[1]).scale(.1, .1, .1).create_occurrence(True)

    end = time.time()
    print(end-start)


def run(_):
    run_design(_design, message_box_on_error=False, document_name=__name__)
