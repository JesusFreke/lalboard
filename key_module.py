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
import datetime

from fscad import *

key_thickness = 1.8
post_width = 4.5


def tapered_box(bottom_x, bottom_y, top_x, top_y, height, name):
    bottom_face = rect(bottom_x, bottom_y)
    top_face = place(rect(top_x, top_y),
                     midAt(atMid(bottom_face)),
                     midAt(atMid(bottom_face)),
                     midAt(height))
    return loft(bottom_face, top_face, name=name)


def tapered_cube(bottom, top, height, name):
    return tapered_box(bottom, bottom, top, top, height, name)


def vertical_key_post(post_length, groove_height, magnet_height):
    post = box(post_width, post_length, key_thickness, name="post")
    fillet(edges(post, ["front"], ["top", "bottom"]), sizeOf(post).z/2)

    magnet_hole = place(tapered_cube(1.55, 1.7, sizeOf(post).z - .2, "magnet_hole"),
                        midAt(atMid(post)), midAt(magnet_height + key_thickness/2), maxAt(atMax(post)))

    groove_size = .6
    groove = place(box(sizeOf(post).x, groove_size, groove_size, name="groove"),
                   midAt(atMid(post)), minAt(groove_height + key_thickness/2), minAt(atMin(post)))
    return difference(post, magnet_hole, groove)


def vertical_key(post_length, key_width, key_height, key_protrusion, key_displacement, groove_height, magnet_height,
                 name):
    with Joiner(union, name) as join:
        post = join(vertical_key_post(post_length, groove_height, magnet_height))

        key_base = place(box(13, key_height, 10, name="key_base"),
                         midAt(atMid(post)), minAt(atMax(post)), minAt(atMin(post)))

        key_dish = place(rx(cylinder(sizeOf(key_base).y, 15), 90),
                         midAt(atMid(post)), midAt(atMid(key_base)), minAt(atMax(post)))
        dished_key = difference(key_base, key_dish, name="dished_key")
        join(scale(dished_key, (key_width/13, 1, 1), center=midOf(dished_key).asArray()))

        if key_displacement:
            ty(dished_key, key_displacement)

        if key_protrusion:
            riser = join(place(box(post_width, post_width, key_protrusion, name="riser"),
                               midAt(atMid(post)), minAt(atMax(post)), minAt(atMin(post))))
            place(dished_key, z=minAt(atMax(riser)))

        face_list = [get_face(key_dish, "side"), "left", "right", "back"]
        fillet(edges(dished_key, face_list, face_list), .5, False)
    return join.result()


def center_key():
    size = 6.1 * 2
    key_radius = 7.5
    key_thickness = 2.5
    post_length = 8.4
    post_radius = 2.3

    with Joiner(union, name="center_key") as join:
        key = join(cylinder(key_thickness, key_radius, name="key"))

        post = join(place(cylinder(post_length, post_radius, name="post"), z=minAt(atMax(key))))

        back_stop = join(place(box(3.5, 5.7, 4, name="back_stop"),
                      midAt(atMid(key)), minAt(atMid(key)), minAt(atMax(key))))

        side_stop_start = place(box(5.9, 3.5, 4, name="side_stop_start"),
                                minAt(atMid(key)), midAt(atMid(key)), minAt(atMax(key)))
        side_stop_end = place(box(3.4, 5.9, 4, name="side_stop_end"),
                              maxAt(atMax(side_stop_start)), maxAt(atMid(key)), minAt(atMin(side_stop_start)))
        side_stop = union(side_stop_start, side_stop_end, name="side_stop")
        join(duplicate(scale, ((1, 1, 1), (-1, 1, 1)), side_stop))

    center_key_base = join.result()

    post_flat_face = place(box(minOf(side_stop_end).x*2, key_radius, post_length, name="post_flat_face"),
                           midAt(atMid(post)), maxAt(-2), minAt(atMax(key)))
    magnet_hole = place(rx(tapered_box(1.7, 1.8, 1.45, 1.8, 2, name="magnet_hole"),
                           -90),
                        midAt(atMid(post)), minAt(atMax(post_flat_face)), midAt(post_length + key_thickness - 4.2))

    return intersection(difference(center_key_base, post_flat_face, magnet_hole),
                        cylinder(post_length + key_thickness, key_radius, name="trim"))


def small_pin(length):
    return cylinder(length, .4, name="small_pin")


@autokeep
def make_pt_cavity(block, base_height):
    lens_height = 4.5
    lens_radius = .75

    body = box(1.8, 5, sizeOf(block).z, name="body")
    lens_hole = place(ry(cylinder(sizeOf(block).y, lens_radius, name="lens_hole"), 90),
                      minAt(atMax(body)), midAt(atMid(body)), midAt(lens_height))
    lens_slot = place(box(lens_radius + .05, lens_radius * 2 + .1, sizeOf(block).y, name="lens_slot"),
                      minAt(atMax(body)), midAt(atMid(body)), minAt(atMin(lens_hole)))
    cavity = union(body, lens_hole, lens_slot, name="phototransistor_cavity")

    get_placement([body, lens_slot],
                  midAt(atMid(block)), midAt(atMid(block)), minAt(atMin(block)))\
        .apply(cavity)
    cavity = intersection(cavity, duplicate_of(block))

    legs = union(duplicate(ty, (0, -2.54), place(small_pin(base_height),
                                                 midAt(atMid(body)),
                                                 midAt(lambda i: atMid(body)(i) + 2.54/2),
                                                 maxAt(atMin(body)))),
                 name="phototransistor_legs")
    return union(cavity, legs)


@autokeep
def make_led_cavity(block, base_height):
    lens_radius = .75
    lens_height = 2.9

    body = box(1.8, 5.1, sizeOf(block).z - 1.6, name="body")
    slot = place(box(1.1, sizeOf(body).y, sizeOf(body).z, name="slot"),
                 maxAt(atMin(body)), midAt(atMid(body)), minAt(atMin(body)))
    lens_hole = place(ry(cylinder(sizeOf(block).y, lens_radius, name="lens_hole"), 90),
                      maxAt(atMin(body)), midAt(atMid(body)), midAt(lens_height))

    cavity = union(body, slot, lens_hole, name="led_cavity")
    get_placement([body, slot],
                  midAt(atMid(block)), midAt(atMid(block)), maxAt(atMax(block))) \
        .apply(cavity)
    cavity = intersection(cavity, duplicate_of(block))

    legs = duplicate(ty, (0, -2.54),
                     place(small_pin(base_height + 1.6),
                           midAt(lambda i: atMax(body)(i) - .9),
                           midAt(lambda i: atMid(body)(i) + 2.54/2),
                           maxAt(atMin(body))),
                     name="phototransistor_legs")
    return union(cavity, legs)


@autokeep
def vertical_key_base(base_height, pressed_key_angle=20):
    front = box(5, 2.2, 6.4, name="front")

    pt_base = place(box(5, 6.15, 6.4, name="phototransistor_base"),
                    maxAt(atMin(front)), maxAt(atMax(front)), minAt(atMin(front)))
    led_base = place(box(6, 6.15, 6.4, name="led_base"),
                     minAt(atMax(front)), maxAt(atMax(front)), minAt(atMin(front)))

    target_tip_thickness = .8

    base_elements = front, pt_base, led_base
    base_size = sizeOf(*base_elements)
    base = box(base_size.x, base_size.y, base_height, name="base")
    place(base,
          minAt(atMin(*base_elements)),
          minAt(atMin(*base_elements)),
          maxAt(atMin(*base_elements)))

    pt_cavity = make_pt_cavity(pt_base, base_height)
    led_cavity = make_led_cavity(led_base, base_height)

    key_pivot = place(ry(cylinder(sizeOf(front).x, 1, name="key_pivot"), 90),
                      midAt(atMid(front)), maxAt(atMin(front)), midAt(atMin(front)))

    sloped_key = place(box(sizeOf(front).x, sizeOf(key_pivot).y, sizeOf(front).z * 2, name="sloped_key"),
                       midAt(atMid(key_pivot)), midAt(atMid(key_pivot)), minAt(atMid(key_pivot)))
    sloped_key = union(sloped_key, key_pivot)
    rx(sloped_key, pressed_key_angle, center=(0, midOf(sloped_key).y, 0))

    target_tip_thickness = .8
    back_base = difference(
        place(rect(sizeOf(front).x, sizeOf(led_base).y - sizeOf(front).y - sizeOf(key_pivot).y - target_tip_thickness,
                   name="back_base"),
              midAt(atMid(front)), minAt(lambda i: atMin(led_base)(i) + target_tip_thickness)),
        duplicate_of(sloped_key))

    back_sloped = extrude_to(back_base, sloped_key, name="back_sloped")
    remaining_back = place(box(sizeOf(front).x, target_tip_thickness, sizeOf(back_sloped).z, name="remaining_back"),
                           midAt(atMid(front)), maxAt(atMin(back_sloped)), minAt(atMin(back_sloped)))
    back = union(remaining_back, back_sloped, name="back")

    top_face = get_face(back, get_face(remaining_back, "top"))

    vertical_key_base = difference(
        union(pt_base, led_base, front, back, base, name="vertical_key_base"),
        sloped_key)

    retaining_ridge = place(rx(box(sizeOf(back).x, .5, .5, name="retaining_ridge"), 45),
                            midAt(atMid(back)), midAt(atMax(top_face)), maxAt(atMax(back)))
    vertical_key_base = union(vertical_key_base, retaining_ridge)

    magnet_cutout = place(rx(tapered_box(1.45, 1.8, 1.7, 1.8, 1.8, name="magnet"), 90),
                          midAt(atMid(front)), minAt(atMin(front)), maxAt(lambda i: atMax(front)(i) - .45))

    return (vertical_key_base,
            pare_occurrence(union(pt_cavity, led_cavity, magnet_cutout, name="vertical_key_base_negative")))


def side_key(key_height, name):
    vertical_key(
        post_length=10,
        key_width=13,
        key_height=key_height,
        key_protrusion=False,
        key_displacement=False,
        groove_height=2.7,
        magnet_height=5.45,
        name=name)


def short_side_key():
    side_key(5, "short_side_key")


def long_side_key():
    side_key(11, "long_side_key")


def thumb_side_key(key_width, key_height, name):
    vertical_key(
        post_length=11.5,
        key_width=key_width,
        key_height=key_height,
        key_protrusion=6.5,
        key_displacement=-3,
        groove_height=6.6,
        magnet_height=9.05,
        name=name)


def outer_upper_thumb_key():
    thumb_side_key(25, 16, "outer_upper_thumb_key")


def outer_lower_thumb_key():
    thumb_side_key(20, 20, "outer_lower_thumb_key")


def inner_thumb_key():
    thumb_side_key(20, 16, "inner_thumb_key")


def mydesign():
    start = datetime.datetime.now()

    with keep_subtree(False):
        positive, negative = vertical_key_base(2)

    end = datetime.datetime.now()
    print((end-start).total_seconds())


def run(context):
    run_design(mydesign, message_box_on_error=False, document_name=__name__)
