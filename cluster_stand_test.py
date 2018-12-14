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


ball_radius = 3
screw_radius = 1.5


def vertical_magnet_cutout():
    bottom = rect(3.4, 3.4, name="bottom")
    top = place(rect(3, 3, name="top"),
                midAt(atMid(bottom)), midAt(atMid(bottom)), midAt(3.3))
    return loft(bottom, top, name="magnet_cutout")


def base_plate():
    base = box(25, 42, 2, name="base")

    standoff_base = cylinder(ball_radius * .8, ball_radius+1, name="standoff_base")

    standoff_base = union(standoff_base, threads(standoff_base, ((0, 0), (.99, .99), (0, .99)), 1))

    standoff_hole = sphere(ball_radius)

    standoff_hole = place(standoff_hole,
          midAt(atMid(standoff_base)),
          midAt(atMid(standoff_base)),
          minAt(atMin(standoff_base)))
    standoff = difference(standoff_base, standoff_hole)

    place(standoff,
          midAt(atMid(base)),
          minAt(lambda i: atMin(base)(i)),
          minAt(atMax(base)))

    standoff2 = duplicate_of(standoff)
    place(standoff2,
          minAt(lambda i: atMin(base)(i)),
          maxAt(lambda i: atMax(base)(i)),
          minAt(atMax(base)))

    standoff3 = duplicate_of(standoff2)
    place(standoff3,
          maxAt(atMax(base)),
          maxAt(atMax(base)),
          minAt(atMax(base)))

    base = difference(base, *find_all_duplicates(standoff_hole))
    union(base, standoff, standoff2, standoff3)


def ball_socket_cap():
    # how much gap should be left between the bottom of the socket cap and the bottom of the base place
    # this ensures there's a bit of extra room to tighten the cap down onto the ball snugly
    screw_gap = .3

    socket_cap_bottom = regular_polygon(6, regular_polygon_radius_for_width((ball_radius + 2.5)*2, 6),
                                        name="socket_cap_bottom")
    socket_cap_base = extrude(socket_cap_bottom, ball_radius * 2 * .8 - .3, name="socket_cap")

    inner_cavity = cylinder(ball_radius * .8, ball_radius+1+.1, name="inner_cavity")
    socket_cap = difference(socket_cap_base, inner_cavity, threads(inner_cavity, ((0, 0), (.99, .99), (0, .99)), 1))

    socket = place(sphere(ball_radius),
                   midAt(atMid(socket_cap)), midAt(atMid(socket_cap)), minAt(lambda i: atMin(socket_cap)(i) - .3))
    socket = difference(socket_cap, socket)
    rx(socket, 180, center=midOf(socket).asArray())


def stand():
    circ = circle(2.1)
    sph = sphere(2.1)

    sphere_placement = .15

    place(sph,
          midAt(atMid(circ)), midAt(atMid(circ)), minAt(lambda i: atMid(circ)(i) - sizeOf(sph).z * sphere_placement))

    cyl_top = tz(intersection(circ, duplicate_of(sph), name="cyl_top"), 12)
    cyl_bottom = circle(5, name="cyl_bottom")
    base = loft(cyl_bottom, cyl_top, name="base")
    place(sph,
          midAt(atMid(base)), midAt(atMid(base)), minAt(lambda i: atMax(base)(i) - sizeOf(sph).z * sphere_placement))

    stand = union(base, sph, name="stand")

    cutout = place(vertical_magnet_cutout(), midAt(atMid(stand)), midAt(atMid(stand)), minAt(atMin(stand)))
    stand = difference(stand, cutout)

    chamfer(edges(faces(stand, "start"), faces(stand, list(cutout.bRepBodies[0].faces))), .2, .4)


def stand_base():
    bottom = regular_polygon(6, regular_polygon_radius_for_width(10, 6), name="bottom")

    base = extrude(bottom, 10, name="stand_base")

    cutout = place(vertical_magnet_cutout(), midAt(atMid(base)), midAt(atMid(base)), minAt(atMin(base)))

    hole = place(cylinder(maxOf(base).z - maxOf(cutout).z, screw_radius+.1, name="hole"),
                 midAt(atMid(base)), midAt(atMid(base)), minAt(atMax(cutout)))

    base = difference(base, hole, cutout,
                      threads(hole, ((0, 0), (.99, .99), (0, .99)), 1))

    base = rx(base, 180, center=(midOf(base).asArray()))

    inner_radius = get_face(hole, "side").geometry.radius * 10
    return difference(base, cylinder(1, inner_radius + 1, inner_radius, name="chamfer"))


def stand_screwball():

    ball = sphere(ball_radius+.1, name="ball_head")
    ball = intersection(ball,
                        place(box((ball_radius+.1)*2, (ball_radius+.1)*2, ((ball_radius+.1)*2)*.95),
                              midAt(atMid(ball)), midAt(atMid(ball)), minAt(atMin(ball))))


    threaded_section = cylinder(6, screw_radius-.1, name="threaded_section")
    unthreaded_section = place(cylinder(3.5, screw_radius-.1, name="unthreaded_section"),
                               midAt(atMid(threaded_section)),
                               midAt(atMid(threaded_section)),
                               minAt(atMax(threaded_section)))
    threaded_section = union(threaded_section, threads(threaded_section, ((0, 0), (.99, .99), (0, .99)), 1))

    place(ball,
          midAt(atMid(unthreaded_section)),
          midAt(atMid(unthreaded_section)),
          midAt(atMax(unthreaded_section)))

    return union(threaded_section, unthreaded_section, ball, name="screwball")


def mydesign():
    start = datetime.datetime.now()

    #stand_base()

    #stand_screwball()

    #base_plate()
    ball_socket_cap()

    end = datetime.datetime.now()
    print((end-start).total_seconds())


def run(context):
    run_design(mydesign, message_box_on_error=False, document_name=__name__)

