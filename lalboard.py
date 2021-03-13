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

"""
This file contains the logic for generating all the various parts. This script itself can't be run directly, but it used
by the various part scripts in the "parts" directory.
"""

import adsk.core
import adsk.fusion
import inspect
import math
import pathlib
import os

from fscad import *

key_thickness = 1.8
post_width = 7.3


def small_pin():
    return Circle(.4, name="small_pin")


def tapered_box(bottom_x, bottom_y, top_x, top_y, height, name):
    bottom_face = Rect(bottom_x, bottom_y, "tapered_box_bottom")
    top_face = Rect(top_x, top_y, "tapered_box_top")
    top_face.place(~top_face == ~bottom_face,
                   ~top_face == ~bottom_face,
                   ~top_face == height)
    return Loft(bottom_face, top_face, name=name)


def horizontal_rotated_magnet_cutout(depth=1.8, name="magnet_cutout"):
    result = tapered_box(1.45, 1.45, 1.7, 1.7, depth, name=name).rx(90).ry(45)
    result.add_named_faces("front", result.top)
    return result


def horizontal_magnet_cutout(depth=1.8, name="magnet_cutout"):
    return tapered_box(1.45, 1.8, 1.7, 1.8, depth, name=name).rx(90)


def horizontal_tiny_magnet_cutout(depth=1.3, name="magnet_cutout"):
    return tapered_box(.9, 1.2, 1.1, 1.2, depth, name=name).rx(90)


def horizontal_large_thin_magnet_cutout(depth=1.8, name="magnet_cutout"):
    return tapered_box(1.45*2, 1.8*2, 1.7*2, 1.8*2, depth, name=name).rx(90)


def vertical_magnet_cutout(depth=1.6, name="magnet_cutout"):
    return tapered_box(1.55, 1.55, 1.7, 1.7, depth, name)


def vertical_rotated_magnet_cutout(depth=1.6, name="magnet_cutout"):
    result = tapered_box(1.7, 1.7, 1.8, 1.8, depth, name).rz(45)
    result.add_named_faces("front", result.top)
    return result


def vertical_large_magnet_cutout(name="magnet_cutout"):
    base = Box(2.9, 2.9, 2, name=name + "_base")
    taper = tapered_box(2.9, 2.9, 3.1, 3.1, 1.3, name=name + "_taper")
    taper.place(~taper == ~base,
                ~taper == ~base,
                -taper == +base)
    return Union(base, taper, name=name)


def vertical_large_thin_magnet_cutout(name="magnet_cutout", depth=1.8, taper=.15):
    upper_taper = tapered_box(3.35, 3.35, 3.35 + taper, 3.35 + taper, min(.7, depth), name=name + "_taper")

    if depth > .7:
        base = Box(3.35, 3.35, depth - upper_taper.size().z, name=name + "_base")
        upper_taper.place(~upper_taper == ~base,
                          ~upper_taper == ~base,
                          -upper_taper == +base)
        return Union(base, upper_taper, name=name)
    else:
        return Union(upper_taper, name=name)


def vertical_large_thin_double_magnet_cutout(extra_depth=0.0, name="magnet_cutout"):
    base = Box(3.0*2, 3.0, 1 + extra_depth, name=name + "_base")
    taper = tapered_box(3.05*2, 3.0, 3.25*2, 3.2, .7, name=name + "_taper")
    taper.place(~taper == ~base,
                ~taper == ~base,
                -taper == +base)
    return Union(base, taper, name=name)


def make_bottom_entry_led_cavity(name="led_cavity"):
    lens_height = 4.5
    lens_radius = .75

    body = Box(1.8, 5, 5.8, "body")

    lens_hole = Circle(lens_radius, name="lens_hole")
    lens_hole.ry(90).place(-lens_hole == +body, ~lens_hole == ~body, ~lens_hole == lens_height)
    lens_slot = Box(lens_radius + .05, lens_radius * 2 + .1, lens_hole.max().z - body.min().z, "lens_slot")
    lens_slot.place(-lens_slot == +body, ~lens_slot == ~body, +lens_slot == +lens_hole)
    lens_hole.place(~lens_hole == +lens_slot)

    cavity = Union(body, lens_slot)
    cavity = SplitFace(cavity, lens_hole, name=name)

    leg = small_pin()
    leg.place(~leg == ~body, (~leg == ~body) + 2.54/2, +leg == -body)
    leg2 = leg.copy().ty(-2.54)
    legs = Union(leg, leg2, name="legs")
    cavity = SplitFace(cavity, legs)

    cavity.add_named_faces("legs", *cavity.find_faces((leg, leg2)))

    cavity.add_named_faces("lens_hole", *cavity.find_faces(lens_hole))
    cavity.add_named_faces("bottom", *cavity.find_faces(body.bottom))

    cavity.add_named_point("lens_center",
                           (cavity.mid().x, cavity.mid().y, lens_hole.bodies[0].faces[0].brep.centroid.z))

    return cavity


def hole_array(radius, pitch, count):
    hole = Circle(radius)
    holes = []
    for i in range(0, count):
        holes.append(hole.copy().tx(pitch * i))
    return Union(*holes)


def retaining_ridge_design(pressed_key_angle, length):
    def rotated(vector, angle):
        vector = vector.copy()
        matrix = Matrix3D.create()
        matrix.setToRotation(math.radians(angle), Vector3D.create(0, 0, 1), Point3D.create(0, 0, 0))
        vector.transformBy(matrix)
        return vector

    def vectorTo(point, vector, length):
        vector = vector.copy()
        vector.scaleBy(length)
        point = point.copy()
        point.translateBy(vector)
        return point

    # how much it sticks out
    retaining_ridge_thickness = .3
    retaining_ridge_lower_angle = 45
    # the length of the "face" of the ridge
    retaining_ridge_width = .3

    origin = Point3D.create(0, 0, 0)
    up = Vector3D.create(0, 1, 0)
    right = rotated(up, -90)
    down = rotated(right, -90)
    left = rotated(down, -90)

    lines = []
    lines.append(adsk.core.InfiniteLine3D.create(
        origin,
        rotated(down, -pressed_key_angle)))
    lines.append(adsk.core.InfiniteLine3D.create(
        origin,
        left))

    point = vectorTo(origin, rotated(left, -pressed_key_angle), retaining_ridge_thickness)
    lines.append(adsk.core.InfiniteLine3D.create(
        point,
        rotated(down, -pressed_key_angle)))

    point = lines[1].intersectWithCurve(lines[2])[0]
    lines.append(adsk.core.InfiniteLine3D.create(
        vectorTo(point, rotated(down, -pressed_key_angle), retaining_ridge_width),
        rotated(down, retaining_ridge_lower_angle)))

    points = []
    for i in range(-1, 3):
        points.append(lines[i].intersectWithCurve(lines[i+1])[0])

    retaining_ridge = Polygon(*points, name="retaining_ridge_profile")
    retaining_ridge = Extrude(retaining_ridge, length)

    retaining_ridge.rz(-90)
    retaining_ridge.ry(-90)

    return retaining_ridge


def vertical_key_base(extra_height=0.0, pressed_key_angle=12.5, extra_optical_width=0.0, name=None):
    post_hole_width = post_width + .3

    key_well = Box(
        post_hole_width + .525*2,
        4.75,
        8.0 + extra_height, "key_well")

    pt_cavity = make_bottom_entry_led_cavity(name="pt_cavity")
    led_cavity = make_bottom_entry_led_cavity(name="led_cavity")

    upper_base = Box(
        14.9,
        6.55,
        led_cavity.find_children("body")[0].size().z + .4,
        name="upper_base")

    upper_base.place(
        ~upper_base == ~key_well,
        -upper_base == -key_well,
        +upper_base == +key_well)

    pt_cavity.place((+pt_cavity == -key_well) - extra_optical_width/2,
                    (-pt_cavity == -upper_base) + .525,
                    (+pt_cavity == +upper_base) - .4)

    led_cavity.rz(180)
    led_cavity.place((-led_cavity == +key_well) + extra_optical_width/2,
                     (-led_cavity == -upper_base) + .525,
                     +led_cavity == +pt_cavity)

    key_pivot = Cylinder(post_hole_width, 1, name="key-pivot").ry(90)
    key_pivot.place(~key_pivot == ~key_well,
                    (+key_pivot == +upper_base) - 2.6,
                    (~key_pivot == -key_well) + 1.4)

    pivot_vee = Box(
        key_pivot.size().x,
        key_pivot.radius,
        key_pivot.radius)
    pivot_vee.rx(45)

    pivot_vee.place(
        ~pivot_vee == ~key_pivot,
        ~pivot_vee == ~key_pivot,
        +pivot_vee == ~key_pivot)

    pivot_vee_flat_bottom = pivot_vee.bounding_box.make_box()
    pivot_vee_flat_bottom.place(
        ~pivot_vee_flat_bottom == ~pivot_vee,
        ~pivot_vee_flat_bottom == ~pivot_vee,
        +pivot_vee_flat_bottom == -key_pivot)

    pivot_vee = Difference(pivot_vee, pivot_vee_flat_bottom)

    straight_key = Box(post_hole_width, key_pivot.size().y, key_well.size().z * 2, "straight_key")
    straight_key.place(
        ~straight_key == ~key_pivot,
        ~straight_key == ~key_pivot,
        -straight_key == ~key_pivot)

    sloped_key = Box(post_hole_width, key_pivot.size().y, key_well.size().z * 2, "sloped_key")
    sloped_key.place(~sloped_key == ~key_pivot,
                     ~sloped_key == ~key_pivot,
                     -sloped_key == ~key_pivot)
    sloped_key = Union(sloped_key, key_pivot).rx(pressed_key_angle, center=(0, key_pivot.mid().y, key_pivot.mid().z))

    retaining_ridge = retaining_ridge_design(pressed_key_angle, post_hole_width)

    sloped_key_front = sloped_key.find_children("sloped_key")[0].front

    retaining_ridge.place(~retaining_ridge == ~key_well,
                          (+retaining_ridge == -key_pivot) - .05,
                          +retaining_ridge == +upper_base)

    retaining_ridge.align_to(sloped_key_front, Vector3D.create(0, 0, -1))

    sloped_key = Difference(sloped_key, retaining_ridge)

    result = Union(key_well, upper_base)
    result = Difference(result, sloped_key, straight_key)

    magnet_cutout = horizontal_rotated_magnet_cutout()
    magnet_cutout.place(~magnet_cutout == ~key_well,
                        -magnet_cutout == +straight_key,
                        (+magnet_cutout == +key_well) - .4)

    extruded_led_cavity = ExtrudeTo(led_cavity.named_faces("lens_hole"), result.copy(False))
    extruded_pt_cavity = ExtrudeTo(pt_cavity.named_faces("lens_hole"), result.copy(False))

    negatives = Union(
        extruded_pt_cavity, extruded_led_cavity, magnet_cutout, straight_key, sloped_key, pivot_vee, name="negatives")

    result = Difference(result, negatives,  name=name or "vertical_key_base")

    return result


def cluster_design():
    """
    The design for the individual finger clusters, including front and back extensions.
    """

    base_cluster = base_cluster_design()

    base_cluster, front = cluster_front(base_cluster)
    back = cluster_back(base_cluster)

    _, connector_legs_cutout = cluster_pcb(base_cluster, front, back)

    return Difference(
        Union(base_cluster, front, back),
        connector_legs_cutout,
        name="cluster")


def base_cluster_design():
    """
    The design of the main part of a cluster, not including the front or back extensions.
    """
    key_base = vertical_key_base()

    key_base_upper = key_base.find_children("upper_base")[0]

    base = Box(24.9, 24.9, key_base_upper.size().z, "base")

    key_well: Box = key_base.find_children("key_well")[0]
    key_base = Fillet(
        key_base.shared_edges(
            key_base.find_faces(key_well.back),
            key_base.find_faces([key_well.left, key_well.right])),
        .8)

    key_base.place(~key_base == ~base,
                   -key_base == -base,
                   +key_base == +base)

    back_key_base = vertical_key_base(extra_optical_width=2.5)
    back_key_base.place(
        ~back_key_base == ~key_base,
        ~back_key_base == ~key_base,
        ~back_key_base == ~key_base)
    back_key_base = Fillet(
        back_key_base.shared_edges(
            back_key_base.find_faces(key_well.front),
            back_key_base.find_faces([key_well.left, key_well.right])),
        .8)
    back_key_base.scale(-1, 1, 1, center=key_base.mid()).rz(180, base.mid())

    key_bases = (
        key_base.copy().scale(-1, 1, 1, center=key_base.mid()),
        key_base.copy().rz(90, base.mid()),
        back_key_base,
        key_base.rz(270, base.mid())
    )
    key_base_negatives = (
        key_bases[0].find_children("negatives")[0],
        key_bases[1].find_children("negatives")[0],
        key_bases[2].find_children("negatives")[0],
        key_bases[3].find_children("negatives")[0])

    front_base = key_bases[0]
    right_base = key_bases[1]
    back_base = key_bases[2]
    left_base = key_bases[3]
    front_base.name = "front_base"
    right_base.name = "right_base"
    back_base.name = "back_base"
    left_base.name = "left_base"

    combined_cluster = Union(base, *key_bases, name="combined_cluster")

    center_hole = Box(5, 5, combined_cluster.size().z, name="center_hole")
    center_hole.place(~center_hole == ~base,
                      ~center_hole == ~base,
                      -center_hole == -base)

    center_nub_hole = Box(center_hole.size().x, 2.6, 4.6)
    center_nub_hole.place(
        ~center_nub_hole == ~base,
        (-center_nub_hole == +center_hole) + .8,
        +center_nub_hole == +combined_cluster)

    central_magnet_cutout = horizontal_magnet_cutout(name="central_magnet_cutout")
    central_magnet_cutout.place(~central_magnet_cutout == ~center_hole,
                                +central_magnet_cutout == -center_hole,
                                (~central_magnet_cutout == +combined_cluster) - 3.5)

    left_cavity = key_base_negatives[3]
    left_pt_cavity = left_cavity.find_children("pt_cavity")[0]
    right_cavity = key_base_negatives[1]
    right_led_cavity = right_cavity.find_children("led_cavity")[0]

    right_base = key_bases[1]
    left_base = key_bases[3]

    central_led_cavity = make_bottom_entry_led_cavity(name="led_cavity")
    central_led_cavity.rz(180)
    central_led_cavity.place(+central_led_cavity == -right_led_cavity,
                             +central_led_cavity == +right_led_cavity,
                             +central_led_cavity == +right_led_cavity)

    central_pt_cavity = make_bottom_entry_led_cavity(name="pt_cavity")
    central_pt_cavity.place(-central_pt_cavity == +left_pt_cavity,
                            +central_pt_cavity == +left_pt_cavity,
                            +central_pt_cavity == +left_pt_cavity)

    extruded_led_cavity = ExtrudeTo(central_led_cavity.named_faces("lens_hole"), central_pt_cavity.copy(False))
    extruded_pt_cavity = ExtrudeTo(central_pt_cavity.named_faces("lens_hole"), central_led_cavity.copy(False))

    result = Difference(combined_cluster, *key_base_negatives, center_hole, center_nub_hole, central_magnet_cutout,
                        extruded_led_cavity, extruded_pt_cavity)

    result.add_named_point("lower_left_corner", [left_base.min().x, left_base.min().y, 0])
    result.add_named_point("lower_right_corner", [right_base.max().x, right_base.min().y, 0])
    return result


def cluster_pcb(cluster, front, back):
    hole_size = .35

    full_cluster = Union(cluster, front, back).copy(copy_children=False)

    pcb_plane = Rect(1, 1, 1)
    pcb_plane.place(
        ~pcb_plane == ~cluster,
        ~pcb_plane == ~cluster,
        +pcb_plane == -back)

    pcb_silhouette = Silhouette(full_cluster, pcb_plane.get_plane())

    bottom_finder = full_cluster.bounding_box.make_box()
    bottom_finder.place(
        ~bottom_finder == ~full_cluster,
        ~bottom_finder == ~full_cluster,
        +bottom_finder == -full_cluster)

    key_wells = Extrude(
        Union(*[face.make_component() for face in full_cluster.find_faces(bottom_finder)]),
        -full_cluster.size().z)

    front_edge_finder = full_cluster.bounding_box.make_box()
    front_edge_finder.place(
        ~front_edge_finder == ~back,
        +front_edge_finder == -key_wells,
        +front_edge_finder == -front)
    front_bottom_face = full_cluster.find_faces(front_edge_finder.top)[0]

    front_key_well_face = full_cluster.find_faces(front_edge_finder.back)[0]
    front_cut_out = Extrude(front_key_well_face.make_component(), full_cluster.size().y)

    front_trim_tool = full_cluster.bounding_box.make_box()
    front_trim_tool.place(
        ~front_trim_tool == ~full_cluster,
        +front_trim_tool == -front_bottom_face,
        ~front_trim_tool == ~pcb_silhouette)

    back_trim_tool = full_cluster.bounding_box.make_box()
    back_trim_tool.place(
        ~back_trim_tool == ~full_cluster,
        (-back_trim_tool == -back) + 4.8,
        ~back_trim_tool == ~pcb_silhouette)

    pcb_back = Rect(
        8,
        back.max().y - back_trim_tool.min().y,
        name="pcb_back")
    pcb_back.place(
        ~pcb_back == ~back,
        +pcb_back == +back)

    pcb_silhouette = Union(
        Difference(pcb_silhouette, key_wells, front_trim_tool, front_cut_out, back_trim_tool),
        pcb_back)

    for loop in pcb_silhouette.faces[0].loops:
        offset_amount = -.2
        if abs(loop.size().x - loop.size().y) < app().pointTolerance:
            # for the square hole in the center, enlarge it enough to ensure the rounded corners don't interfere
            # with the center key post
            offset_amount = -.4
        pcb_silhouette = OffsetEdges(pcb_silhouette.faces[0],
                                     pcb_silhouette.find_edges(loop.edges),
                                     offset_amount)

    connector_holes = hole_array(hole_size, 1.5, 7)
    connector_holes.place((~connector_holes == ~pcb_silhouette),
                          (~connector_holes == -back_trim_tool) - 2.2,
                          ~connector_holes == ~pcb_silhouette)

    # A cutout behind the pcb in the cluster, for the soldered connector legs.
    connector_legs_cutout = Box(
        connector_holes.size().x + 2,
        connector_holes.size().y + 2,
        2.5,
        name="connector_legs_cutout")
    connector_legs_cutout.place(
        ~connector_legs_cutout == ~connector_holes,
        ~connector_legs_cutout == ~connector_holes,
        -connector_legs_cutout == ~connector_holes)

    legs = Union(*cluster.find_children("legs"))
    legs.place(
        z=~legs == ~pcb_silhouette)

    screw_hole = back.find_children("screw_hole")[0]

    pcb_silhouette = Difference(pcb_silhouette, connector_holes, legs, screw_hole)

    return Extrude(pcb_silhouette, -1.6, name="pcb"), connector_legs_cutout


def ball_magnet():
    return Sphere(2.5, "ball_magnet")


def underside_magnetic_attachment(base_height, name=None):
    """This is the design for the magnetic attachments on the normal and thumb clusters.

    It consists of a rectangular magnet partially sticking out of the underside of the cluster. The other side
    of the attachment will have a rectangular hole that fits over the part of the magnet sticking out, along with
    another magnet to hold them together.

    For example, for a ball magnet mount, there could be a separate part with the rectangular hole on one side and a
    spherical divot on the other side, to interface between the rectangular magnet and a spherical magnet, holding
    both in place relative to each other.
    """

    # A bit shallower than the thickness of the magnet, so the magnet sticks out a bit. The mating part will have
    # a hole that fits over the extending part of the magnet, to keep it from sliding.
    magnet_hole = vertical_large_thin_magnet_cutout(depth=1)
    magnet_hole.rx(180)

    base = Cylinder(base_height, 3.5)

    magnet_hole.place(
        ~magnet_hole == ~base,
        ~magnet_hole == ~base,
        -magnet_hole == -base)

    negatives = Union(magnet_hole, name="negatives")

    return Difference(base, negatives, name=name or "attachment")


def magnetic_attachment(ball_depth, rectangular_depth, radius=None, name="attachment"):
    """This is the design for the magnetic attachments on the normal and thumb clusters.

    It consists of an upper part that holds a small rectangular magnet, and then a lower part that is a spherical
    indentation for a 5mm ball magnet.
    """
    ball = ball_magnet()
    ball_radius = ball.size().x / 2

    test_base = Cylinder(ball_depth, ball_radius*2)

    # place the bottom at the height where the sphere's tangent is 45 degrees
    test_base.place(
        ~test_base == ~ball,
        ~test_base == ~ball,
        (-test_base == ~ball) + (ball.size().z/2) * math.sin(math.radians(45)))

    test_base_bottom = BRepComponent(test_base.bottom.brep)
    cone_bottom = Intersection(ball, test_base_bottom)

    cone_bottom_radius = cone_bottom.size().x / 2

    # create a 45 degree cone that starts where the sphere's tangent is 45 degrees
    cone_height = ball.max().z - test_base.min().z
    cone = Cylinder(cone_height, cone_bottom_radius, cone_bottom_radius - cone_height)
    cone.place(
        ~cone == ~ball,
        ~cone == ~ball,
        +cone == +ball)

    # now place the test base to match where the actual cluster base will be
    test_base.place(
        ~test_base == ~ball,
        ~test_base == ~ball,
        +test_base == +ball)

    magnet_hole = vertical_large_thin_magnet_cutout(depth=rectangular_depth)

    if radius is None:
        radius = Intersection(ball, test_base).size().x/2 + .8

    base = Cylinder(ball_depth + rectangular_depth, radius)
    base.place(
        ~base == ~ball,
        ~base == ~ball,
        (-base == +ball) - ball_depth)

    magnet_hole.place(
        ~magnet_hole == ~ball,
        ~magnet_hole == ~ball,
        -magnet_hole == +ball)

    negatives = Union(ball, cone, magnet_hole, name="negatives")

    return Difference(base, negatives, name=name)


def find_tangent_intersection_on_circle(circle: Circle, point: Point3D):
    left_point_to_mid = point.vectorTo(circle.mid())
    left_point_to_mid.scaleBy(.5)
    midpoint = point.copy()
    midpoint.translateBy(left_point_to_mid)
    intersecting_circle = Circle(left_point_to_mid.length)
    intersecting_circle.place(~intersecting_circle == midpoint,
                              ~intersecting_circle == midpoint,
                              ~intersecting_circle == midpoint)

    vertices = list(Intersection(circle, intersecting_circle).bodies[0].brep.vertices)
    return vertices


def cluster_front(cluster: Component):
    front_base = cluster.find_children("front_base")[0]
    upper_base = front_base.find_children("upper_base")[0]
    front_key_well = front_base.find_children("key_well")[0]

    front_length = 4
    front_width = 13

    left_point = cluster.named_point("lower_left_corner").point
    right_point = cluster.named_point("lower_right_corner").point

    front_nose = Box(
        front_width,
        front_length,
        upper_base.size().z)
    front_nose.place(
        ~front_nose == ~cluster,
        +front_nose == -cluster,
        +front_nose == +cluster)

    front_left_point = front_nose.min()
    front_right_point = Point3D.create(
        front_nose.max().x,
        front_nose.min().y,
        front_nose.min().z)

    front_base = Extrude(Polygon(front_left_point, front_right_point, right_point, left_point), upper_base.size().z)

    front_cutout = Box(
        front_key_well.size().x,
        front_length - 1,
        cluster.size().z, name="front_cutout")
    front_cutout.place(
        ~front_cutout == ~cluster,
        +front_cutout == -cluster,
        (+front_cutout == +cluster) - 1)

    front_notch = Box(
        front_cutout.size().x,
        front_cutout.size().y * 10,
        front_cutout.size().z, name="front_notch")
    front_notch.place(
        ~front_notch == ~front_cutout,
        +front_notch == ~front_cutout,
        (+front_notch == +cluster) - 3)

    front_left_cut_corner = Point3D.create(
        cluster.min().x,
        front_base.min().y,
        front_base.min().z)
    front_right_cut_corner = Point3D.create(
        cluster.max().x,
        front_base.min().y,
        front_base.min().z)

    left_cut = Extrude(
        Polygon(front_left_cut_corner, front_left_point, left_point), front_base.size().z, name="left_cut")

    right_cut = Extrude(
        Polygon(right_point, front_right_point, front_right_cut_corner), front_base.size().z, name="right_cut")

    cluster = Difference(
        cluster, left_cut, right_cut)

    return cluster, Difference(
        front_base, cluster.bounding_box.make_box(), front_cutout, front_notch, name="cluster_front")


def cluster_back(cluster: Component):
    upper_base = cluster.find_children("upper_base")[0]

    attachment = underside_magnetic_attachment(upper_base.size().z)

    base = Box(cluster.size().x, attachment.size().y + 5, upper_base.size().z)
    base.place(~base == ~cluster,
               -base == +cluster,
               +base == +cluster)

    attachment.place(-attachment == -cluster,
                     +attachment == +base,
                     +attachment == +base)

    other_attachment = attachment.copy()
    other_attachment.place(+attachment == +cluster)

    screw_hole = Cylinder(base.size().z * 10, 3.1/2, name="screw_hole")
    screw_hole.place(
        ~screw_hole == ~base,
        ~screw_hole == ~attachment,
        (+screw_hole == +base) - .4)

    nut_cutout = Box(
        5.8,
        cluster.size().y * 10,
        2.6)
    nut_cutout.place(
        ~nut_cutout == ~screw_hole,
        (-nut_cutout == ~screw_hole) - nut_cutout.size().x / 2,
        (+nut_cutout == +screw_hole) - 1.5)

    # This will give a single .2 layer on "top" (when printed upside down) of the nut cavity, so that it can be
    # bridged over. This will fill in the screw hole, but a single layer can be cleaned out/pushed through easily.
    nut_cutout_ceiling = Box(
        nut_cutout.size().x,
        nut_cutout.size().x,
        .2)
    nut_cutout_ceiling.place(
        ~nut_cutout_ceiling == ~nut_cutout,
        -nut_cutout_ceiling == -nut_cutout,
        +nut_cutout_ceiling == -nut_cutout)

    base = Fillet(base.shared_edges([base.back], [base.left, base.right]), attachment.size().x/2)

    return Union(
        Difference(Union(base, attachment, other_attachment),
                   attachment.find_children("negatives")[0],
                   other_attachment.find_children("negatives")[0],
                   screw_hole,
                   nut_cutout),
        nut_cutout_ceiling,
        name="cluster_back")


def cluster_front_mount_clip(front, extra_height=0, name="cluster_front_mount_clip"):
    cutout = front.find_children("front_cutout")[0]
    notch = front.find_children("front_notch")[0]

    insert = Box(
        cutout.size().x - .2,
        cutout.size().y - .2,
        (cutout.max().z - notch.max().z) - .2)
    insert.place(
        ~insert == ~cutout,
        ~insert == ~cutout,
        (+insert == +cutout) - .2)

    bottom = Box(
        insert.size().x,
        (insert.max().y - front.min().y) + 1.6,
        1)
    bottom.place(
        ~bottom == ~insert,
        +bottom == +insert,
        +bottom == -insert)

    front_riser = Box(
        insert.size().x,
        1.5,
        front.max().z - bottom.max().z + extra_height)
    front_riser.place(
        ~front_riser == ~insert,
        -front_riser == -bottom,
        -front_riser == +bottom)

    attachment = underside_magnetic_attachment(1.4)
    attachment.place(
        ~attachment == ~insert,
        +attachment == -front_riser,
        +attachment == +front_riser)

    attachment_top_finder = attachment.bounding_box.make_box()
    attachment_top_finder.place(
        ~attachment_top_finder == ~attachment,
        ~attachment_top_finder == ~attachment,
        -attachment_top_finder == +attachment)
    attachment_attachment = Extrude(
        Hull(
            Union(
                attachment.find_faces(attachment_top_finder)[0].make_component(),
                front_riser.top.make_component())),
        -attachment.size().z)

    return Difference(
        Union(insert, bottom, front_riser, attachment, attachment_attachment),
        *attachment.find_children("negatives"),
        name=name)


def center_key():
    key_radius = 7.5
    key_rim_height = .5
    key_thickness = 2
    post_length = 7.9 + 2
    key_travel = 1.9

    fillet_radius = 1.2

    key = Cylinder(key_thickness, key_radius, name="key")
    key_rim = Cylinder(key_rim_height, key_radius)
    key_rim.place(~key_rim == ~key,
                  ~key_rim == ~key,
                  -key_rim == +key)
    key_rim_hollow = Cylinder(key_rim_height, key_radius - 1)
    key_rim_hollow.place(~key_rim_hollow == ~key,
                         ~key_rim_hollow == ~key,
                         -key_rim_hollow == -key_rim)
    key_rim = Difference(key_rim, key_rim_hollow)

    center_post = Box(5 - .2, 5 - .1, post_length + key_rim_height, name="center_post")

    center_post.place(
        ~center_post == ~key,
        (~center_post == ~key) + .05,
        -center_post == +key)

    interruptor_post = Box(3.5, 2, .65 + key_travel + key_rim_height, name="interruptor_post")
    interruptor_post.place(
        ~interruptor_post == ~key,
        (-interruptor_post == +center_post) + 1.2,
        -interruptor_post == +key)
    fillet_edges = interruptor_post.shared_edges(
        [interruptor_post.top, interruptor_post.back, interruptor_post.right, interruptor_post.left],
        [interruptor_post.top, interruptor_post.back, interruptor_post.right, interruptor_post.left])
    interruptor_post = Fillet(fillet_edges, fillet_radius)

    bounding_cylinder = Cylinder(center_post.max().z - key.min().z, key_radius)
    bounding_cylinder.place(~bounding_cylinder == ~key,
                            ~bounding_cylinder == ~key,
                            -bounding_cylinder == -key)

    magnet = horizontal_tiny_magnet_cutout(1.3)
    magnet.place(~magnet == ~center_post,
                 -magnet == -center_post,
                 (~magnet == +key_rim) + 3.5 + key_travel)

    result = Difference(Union(key, key_rim, center_post, interruptor_post), magnet, name="center_key")

    return result


def vertical_key_post(post_length, groove_height, magnet_height, groove_width=.6):
    post = Box(post_width, post_length, key_thickness, name="post")
    post = Fillet(post.shared_edges([post.front], [post.top, post.bottom]), post.size().z/2)

    magnet = vertical_rotated_magnet_cutout()
    magnet.place(~magnet == ~post,
                 ~magnet == magnet_height + key_thickness/2,
                 +magnet == +post)

    groove_depth = .7
    groove = Box(post.size().x, groove_width, groove_depth, name="groove")
    groove.place(~groove == ~post,
                 (-groove == -post) + groove_height + key_thickness/2,
                 -groove == -post)

    return Difference(post, magnet, groove)


def vertical_key(post_length, key_width, key_height, key_angle, key_protrusion, key_displacement, groove_height,
                 magnet_height, name):
    post = vertical_key_post(post_length, groove_height, magnet_height)

    key_base = Box(13, key_height, 10, name="key_base")
    key_base.place(~key_base == ~post,
                   -key_base == +post,
                   -key_base == -post)

    key_dish = Cylinder(key_base.size().y * 2, 15).rx(90)
    key_dish.place(~key_dish == ~post,
                   -key_dish == -key_base,
                   -key_dish == +post)
    key_dish.rx(key_angle, center=key_dish.min())

    dished_key = Difference(key_base, key_dish, name="dished_key")
    dished_key = Fillet(
        dished_key.shared_edges([key_dish.side, key_base.back],
                                [key_base.left, key_base.right, key_base.back]), 1, False)
    dished_key = Scale(dished_key, sx=key_width/13, center=dished_key.mid(), name="dished_key")

    if key_displacement:
        dished_key.ty(key_displacement)

    if key_protrusion:
        riser = Box(post_width, post_width, key_protrusion, name="riser")
        riser.place(~riser == ~post, -riser == +post, -riser == -post)
        dished_key.place(z=-dished_key == +riser)
        return Union(post, dished_key, riser, name=name)
    return Union(post, dished_key, name=name)


def side_key(key_height, key_angle, name):
    return vertical_key(
        post_length=10,
        key_width=13,
        key_height=key_height,
        key_angle=key_angle,
        key_protrusion=False,
        key_displacement=False,
        groove_height=1.503,
        magnet_height=5.4,
        name=name)


def short_side_key():
    return side_key(5, 0, "short_side_key")


def long_side_key():
    return side_key(11, 10, "long_side_key")


def thumb_side_key(key_width, key_height, groove_height, key_displacement: float=-3, name="thumb_side_key"):
    return vertical_key(
        post_length=11.5,
        key_width=key_width,
        key_height=key_height,
        key_angle=0,
        key_protrusion=6.5,
        key_displacement=key_displacement,
        groove_height=groove_height,
        magnet_height=8.748,
        name=name)


def inner_thumb_key():
    return vertical_key(
        post_length=12,
        key_width=25,
        key_height=13.5,
        key_angle=0,
        key_protrusion=2.5,
        key_displacement=0,
        groove_height=2.68,
        magnet_height=8.748,
        name="inner_thumb_key")


def outer_upper_thumb_key():
    return vertical_key(
        post_length=12,
        key_width=20,
        key_height=14,
        key_angle=0,
        key_protrusion=4.5,
        key_displacement=0,
        groove_height=2.68,
        magnet_height=8.748,
        name="outer_upper_thumb_key")


def outer_lower_thumb_key():
    return vertical_key(
        post_length=12,
        key_width=20,
        key_height=18,
        key_angle=0,
        key_protrusion=4.5,
        key_displacement=0,
        groove_height=4.546,
        magnet_height=8.748,
        name="outer_lower_thumb_key")


def thumb_mode_key(name=None):
    key_post = vertical_key_post(18, 2.68, 9.05, groove_width=1)

    face_finder = Box(1, 1, 1)
    face_finder.place(~face_finder == ~key_post,
                      -face_finder == +key_post,
                      ~face_finder == ~key_post)

    end_face = key_post.find_faces(face_finder)[0]

    end_face = BRepComponent(end_face.brep)

    mid_section_end = end_face.copy()
    mid_section_end.translate(5.5, 14, 3.5)
    mid_section = Loft(end_face, mid_section_end)

    horizontal_section = Box(key_post.size().x, key_post.size().z * .25, 4.3)
    horizontal_section.place(
        ~horizontal_section == ~mid_section_end,
        -horizontal_section == -mid_section_end,
        -horizontal_section == -mid_section_end)

    end_section = Box(key_post.size().x, 11, key_post.size().z)
    end_section.place(
        ~end_section == ~horizontal_section,
        -end_section == -horizontal_section,
        +end_section == +horizontal_section)

    end_section_end_face = end_section.back

    filleted_end_section = Fillet(end_section_end_face.edges, key_thickness/2, False)

    result = Union(key_post, mid_section, horizontal_section, filleted_end_section)

    result = Fillet(result.shared_edges(
        [horizontal_section.front, horizontal_section.back],
        [horizontal_section.top, horizontal_section.bottom, mid_section, end_section.bottom]), 3,
        name=name or "thumb_mode_key")

    return result


def thumb_cluster_insertion_tool(cluster):
    upper_base = cluster.find_children("upper_key_base")[0]
    upper_base_upper_base = upper_base.find_children("upper_base")[0]

    face = upper_base.find_children("magnet_cutout")[0].named_faces("front")[0]

    target_x_axis = face.get_plane().normal
    target_x_axis.scaleBy(-1)
    target_z_axis = Vector3D.create(0, 0, 1)
    target_y_axis = target_x_axis.crossProduct(target_z_axis)

    source_x_axis = Vector3D.create(-1, 0, 0)
    source_y_axis = Vector3D.create(0, 1, 0)
    source_z_axis = Vector3D.create(0, 0, 1)

    matrix = Matrix3D.create()
    matrix.setToAlignCoordinateSystems(
        Point3D.create(0, 0, 0),
        target_x_axis,
        target_y_axis,
        target_z_axis,
        Point3D.create(0, 0, 0),
        source_x_axis,
        source_y_axis,
        source_z_axis)

    cluster.transform(matrix)

    right_plier_void = Box(5, 6, upper_base_upper_base.size().z)
    right_plier_void.place(
        (+right_plier_void == ~face) - 12,
        ~right_plier_void == ~face,
        +right_plier_void == +cluster)

    height_bounds = Box(
        cluster.bounding_box.size().x,
        cluster.bounding_box.size().y,
        upper_base_upper_base.size().z,
        name="height_bounds")
    height_bounds.place(
        ~height_bounds == ~cluster,
        ~height_bounds == ~cluster,
        -height_bounds == -upper_base_upper_base)

    down_key_void = cluster.find_children("down_key_void")[0]

    tool_base = Intersection(down_key_void, height_bounds)

    matrix.invert()
    cluster.transform(matrix)
    tool_base.transform(matrix)
    right_plier_void.transform(matrix)

    left_plier_void = right_plier_void.copy(copy_children=False)
    left_plier_void.scale(-1, 1, 1, center=tool_base.mid())

    result = Difference(tool_base, right_plier_void, left_plier_void, name="thumb_cluster_insertion_tool")

    result = result.scale(.975, .975, .975, center=result.mid())


    return result


def thumb_down_key():
    key_base = Box(14.5, 29, 2.5)

    filleted_key_base = Fillet(key_base.shared_edges([key_base.back], [key_base.left, key_base.right]), 1)

    post = Box(7.3, 2.6, 9, name="post")
    post.place(~post == ~key_base,
               -post == -key_base,
               -post == +key_base)

    key_base_extension = Box(key_base.size().x, 2.5, key_base.size().z)
    key_base_extension.place(
        ~key_base_extension == ~key_base,
        +key_base_extension == -key_base,
        ~key_base_extension == ~key_base)

    angled_back_base = Box(key_base.size().x, 10, 10)
    angled_back_base.place(
        ~angled_back_base == ~key_base,
        (-angled_back_base == +post) + 2.75,
        -angled_back_base == +key_base)
    angled_back_base.rx(-9, center=(
        angled_back_base.mid().x,
        angled_back_base.min().y,
        angled_back_base.min().z))

    angled_back_bottom_tool = Box(
        angled_back_base.size().x,
        key_base.size().y,
        angled_back_base.size().z)
    angled_back_bottom_tool.place(
        ~angled_back_bottom_tool == ~angled_back_base,
        -angled_back_bottom_tool == -angled_back_base,
        (-angled_back_bottom_tool == +key_base) + 2.5)

    angled_back_back_tool = angled_back_bottom_tool.copy()
    angled_back_back_tool.place(
        ~angled_back_back_tool == ~angled_back_base,
        (-angled_back_back_tool == -angled_back_base) + 2,
        -angled_back_back_tool == +key_base)

    angled_back = Difference(angled_back_base, angled_back_bottom_tool, angled_back_back_tool)

    magnet = horizontal_rotated_magnet_cutout(name="magnet")
    magnet.rz(180)
    magnet.place(~magnet == ~key_base,
                 +magnet == +post,
                 (~magnet == +post) - 1.9)

    assembly = Difference(
        Union(filleted_key_base, key_base_extension, post, angled_back),
        magnet, name="thumb_down_key")

    assembly.add_named_edges("pivot", assembly.shared_edges(
        assembly.find_faces(angled_back_base.front),
        assembly.find_faces(key_base.top))[0])

    assembly.add_named_edges("back_lower_edge", assembly.shared_edges(
        assembly.find_faces(key_base.top),
        assembly.find_faces(key_base.back))[0])

    assembly.add_named_faces("pivot_back_face", assembly.find_faces(
        angled_back_back_tool.front)[0])

    return assembly


def cluster_assembly():
    cluster = base_cluster_design()
    cluster, front = cluster_front(cluster)
    back = cluster_back(cluster)
    pcb, connector_legs_cutout = cluster_pcb(cluster, front, back)

    front_clip = cluster_front_mount_clip(front)

    return Difference(Union(cluster, front, back), connector_legs_cutout, name="cluster"), pcb, front_clip


def male_thread_chamfer_tool(end_radius, angle):
    negative = Cylinder(
        end_radius * 10,
        end_radius,
        end_radius + (end_radius * 10 * math.tan(math.radians(angle))),
        name="negative")

    positive = Cylinder(end_radius * 10, end_radius * 2, end_radius * 2, name="positive")
    positive.place(
        ~positive == ~negative,
        ~positive == ~negative,
        (+positive == -negative) + end_radius)
    chamfer_tool = Difference(positive, negative, name="chamfer_tool")

    chamfer_tool.add_named_point("end_point", Point3D.create(
        negative.mid().x,
        negative.mid().y,
        negative.min().z))

    return chamfer_tool


def screw_thread_profile(pitch=1.4, angle=37.5, flat_height=.2):
    sloped_side_height = (pitch - flat_height*2)/2

    return (((0, flat_height/2),
             (sloped_side_height / math.tan(math.radians(angle)), flat_height/2 + sloped_side_height),
             (sloped_side_height / math.tan(math.radians(angle)), flat_height/2 + sloped_side_height + flat_height),
             (0, pitch - flat_height/2)), pitch)


def screw_design(screw_length, radius_adjustment=-.2, name="screw"):
    screw_nominal_radius, screw_radius_adjustment, _, _, _ = screw_base_parameters()

    screw_radius = screw_nominal_radius + radius_adjustment

    ball = ball_magnet()

    screw = Cylinder(screw_length, screw_radius)
    neck_intersection_tool = Cylinder(1.5, screw_radius)

    neck_intersection_tool.place(
        ~neck_intersection_tool == ~screw,
        ~neck_intersection_tool == ~screw,
        -neck_intersection_tool == +screw)

    ball.place(
        ~ball == ~neck_intersection_tool,
        ~ball == ~neck_intersection_tool,
        (-ball == +neck_intersection_tool) - (ball.size().z / 8))

    ball_intersection = Intersection(ball, neck_intersection_tool)

    neck = Cylinder(neck_intersection_tool.height, screw_radius, ball_intersection.size().x/2 + .45)
    neck.place(
        ~neck == ~screw,
        ~neck == ~screw,
        -neck == +screw)

    screw = Threads(screw,
                    *screw_thread_profile())

    return Difference(Union(screw, neck), ball, name=name)


def screw_base_flare(clearance=0.0):
    _, _, _, base_min_radius, _ = screw_base_parameters()

    flare_bottom_polygon = RegularPolygon(
        6, base_min_radius + .5 + clearance, is_outer_radius=False, name="flare_bottom_polygon")

    flare_mid_polygon = flare_bottom_polygon.copy()
    flare_mid_polygon.name = "flare_mid_polygon"
    flare_mid_polygon.tz(1)

    flare_top_polygon = RegularPolygon(6, base_min_radius + clearance, is_outer_radius=False, name="polygon")
    flare_top_polygon.name = "flare_top_polygon"
    flare_top_polygon.place(
        z=(~flare_top_polygon == ~flare_mid_polygon) + 1)

    return Union(
        Loft(flare_bottom_polygon, flare_mid_polygon),
        Loft(flare_mid_polygon, flare_top_polygon),
        name="flare")


def screw_base_parameters():
    screw_nominal_radius = 3.0
    screw_radius_adjustment = -.2
    screw_hole_radius_adjustment = .1

    screw_hole = Cylinder(10, screw_nominal_radius + screw_hole_radius_adjustment)
    temp_threads = Threads(screw_hole, *screw_thread_profile())
    base_min_radius = temp_threads.size().x/2 + .8
    base_flare_size = .5

    base_clearance = .1

    return (screw_nominal_radius, screw_radius_adjustment, screw_hole_radius_adjustment, base_min_radius,
            base_clearance)


def screw_base(screw_length, flared_base=True, name=None):
    screw_nominal_radius, _, screw_hole_radius_adjustment, base_min_radius, _ = screw_base_parameters()
    screw_hole = Cylinder(screw_length, screw_nominal_radius + screw_hole_radius_adjustment)

    base_polygon = RegularPolygon(6, base_min_radius, is_outer_radius=False, name="polygon")
    base = Extrude(base_polygon, screw_length)

    screw_hole.place(~screw_hole == ~base,
                     ~screw_hole == ~base,
                     -screw_hole == -base)

    if flared_base:
        base = Union(base, screw_base_flare())

    return Threads(
        Difference(base, screw_hole),
        *screw_thread_profile(),
        name=name or "screw_base")


def support_base():
    _, _, _, base_min_radius, base_clearance = screw_base_parameters()

    hole_body_polygon = RegularPolygon(6, base_min_radius + base_clearance, is_outer_radius=False)
    hole_body = Extrude(hole_body_polygon, 4)
    hole_body.rz(360/12)
    flare = screw_base_flare(clearance=base_clearance)
    flare.place(
        ~flare == ~hole_body,
        ~flare == ~hole_body,
        -flare == -hole_body)
    flare.rz(360/12)
    hole = Union(hole_body, flare)

    upper_magnet = vertical_large_thin_double_magnet_cutout(extra_depth=.2)

    upper_magnet.place(
        ~upper_magnet == ~hole,
        (-upper_magnet == +hole) + 1,
        -upper_magnet == -hole)

    lower_magnet = upper_magnet.copy()
    lower_magnet.place(
        ~lower_magnet == ~hole,
        (+lower_magnet == -hole) - 1,
        -lower_magnet == -hole)

    lower_body_polygon = RegularPolygon(6, base_min_radius + base_clearance + .8, is_outer_radius=False)
    lower_body_polygon.rz(360/12)

    upper_base = Circle(lower_body_polygon.size().x / 2)
    upper_base.place(
        ~upper_base == ~lower_body_polygon,
        (+upper_base == +upper_magnet) + 2,
        -upper_base == -lower_body_polygon)

    lower_base = upper_base.copy()
    lower_base.place(
        ~lower_base == ~lower_body_polygon,
        (-lower_base == -lower_magnet) - 2,
        -lower_base == -lower_body_polygon)

    mid_side_cutout_bottom = Rect(
        lower_body_polygon.size().x,
        flare.size().x * math.tan(math.radians(360/12.0)))
    mid_side_cutout_mid = mid_side_cutout_bottom.copy()
    mid_side_cutout_mid.tz(1)
    mid_side_cutout_top = Rect(
        lower_body_polygon.size().x,
        2 * (base_min_radius + base_clearance) * math.tan(math.radians(360/12.0)))
    mid_side_cutout_top.place(
        ~mid_side_cutout_top == ~mid_side_cutout_bottom,
        ~mid_side_cutout_top == ~mid_side_cutout_bottom,
        (~mid_side_cutout_top == ~mid_side_cutout_bottom) + flare.size().z)

    mid_side_cutout = Union(
        Loft(mid_side_cutout_bottom, mid_side_cutout_mid),
        Loft(mid_side_cutout_mid, mid_side_cutout_top))

    mid_side_cutout.place(
        ~mid_side_cutout == ~lower_body_polygon,
        ~mid_side_cutout == ~lower_body_polygon,
        -mid_side_cutout == -lower_body_polygon)

    assembly = Difference(
        Extrude(Hull(Union(lower_body_polygon, upper_base, lower_base)), 4),
        mid_side_cutout,
        hole,
        upper_magnet,
        lower_magnet, name="support_base")
    return assembly


def thumb_base(name=None):
    down_key = thumb_down_key()
    down_key.ry(180)

    upper_outer_base = vertical_key_base(
        extra_height=4, pressed_key_angle=7, name="upper_outer_base")

    upper_outer_base_magnet_front = upper_outer_base.find_children("magnet_cutout")[0].named_faces("front")[0]
    upper_outer_base_negatives = upper_outer_base.find_children("negatives")[0]
    upper_outer_base.rz(-90)
    upper_outer_base.place(
        (~upper_outer_base_magnet_front == ~down_key) - 13.525,
        (~upper_outer_base_magnet_front == +down_key) - 3.55,
        (+upper_outer_base == -down_key.named_edges("pivot")[0]))

    down_key_body_hole = Box(
        down_key.size().x + 1,
        (down_key.named_edges("back_lower_edge")[0].mid().y - down_key.named_edges("pivot")[0].mid().y) + .55,
        upper_outer_base.find_children("upper_base")[0].size().z,
        name="down_key_body_hole")

    down_key_body_hole.place(
        ~down_key_body_hole == ~down_key,
        (-down_key_body_hole == ~down_key.named_edges("pivot")[0]) - .15,
        +down_key_body_hole == +upper_outer_base)

    lower_outer_base = vertical_key_base(
        extra_height=4, pressed_key_angle=4.2, name="lower_outer_base")
    lower_outer_base_magnet_front = lower_outer_base.find_children("magnet_cutout")[0].named_faces("front")[0]
    lower_outer_base_negatives = lower_outer_base.find_children("negatives")[0]
    lower_outer_base.rz(-90)
    lower_outer_base.place(
        -lower_outer_base == -upper_outer_base,
        (-lower_outer_base_magnet_front == +down_key) - 30.65,
        +lower_outer_base == +upper_outer_base)

    inner_base = vertical_key_base(
        extra_height=4, pressed_key_angle=7, name="inner_key_base")
    inner_base_magnet_front = inner_base.find_children("magnet_cutout")[0].named_faces("front")[0]
    inner_base_negatives = inner_base.find_children("negatives")[0]
    inner_base.rz(90 + 20)
    inner_base.place(
        (~inner_base_magnet_front == ~down_key) + 12.392,
        (~inner_base_magnet_front == +down_key) - 3.2,
        +inner_base == +upper_outer_base)

    upper_base = vertical_key_base(
        extra_height=4, pressed_key_angle=7, name="upper_key_base")
    upper_base_magnet_front = upper_base.find_children("magnet_cutout")[0].named_faces("front")[0]
    upper_base_negatives = upper_base.find_children("negatives")[0]
    upper_base.rz(90)
    # rotate inner_base back to an orthogonal rotation so we can easily place upper_base behind it
    inner_base.rz(-20, center=(0, 0, 0))
    upper_base.place(
        (-upper_base_magnet_front == +inner_base) + 1.85,
        (~upper_base_magnet_front == ~inner_base),
        +upper_base == +upper_outer_base)

    # Find and extrude the lower face of the keywell, to join the bottom part of the two keywells.
    back_face_finder = Box(1, 1, 1)
    back_face_finder.place(
        +back_face_finder == -upper_base,
        ~back_face_finder == ~upper_base,
        (+back_face_finder == -upper_base) + .01)
    upper_base = ExtrudeTo(
        upper_base.find_faces(back_face_finder.align_to(upper_base, Vector3D.create(1, 0, 0))),
        inner_base, name="extruded_upper_base")

    # rotate both bases together back in place
    inner_base.rz(20, center=(0, 0, 0))
    upper_base.rz(20, center=(0, 0, 0))

    key_base_upper = upper_outer_base.find_children("upper_base")[0]

    lower_attachment = underside_magnetic_attachment(key_base_upper.size().z, name="lower_attachment")
    lower_attachment.place(
        +lower_attachment == -upper_base,
        -lower_attachment == -lower_outer_base,
        +lower_attachment == +upper_outer_base)

    upper_attachment = underside_magnetic_attachment(key_base_upper.size().z, name="upper_attachment")
    upper_attachment.place(
        ~upper_attachment == ~down_key,
        -upper_attachment == +down_key_body_hole,
        +upper_attachment == +upper_outer_base)

    side_attachment = underside_magnetic_attachment(key_base_upper.size().z, name="side_attachment")
    side_attachment.place(
        -side_attachment == -upper_outer_base,
        ~side_attachment == (upper_outer_base.min().y + lower_outer_base.max().y)/2,
        +side_attachment == +upper_outer_base)

    body_entities = Union(
        upper_outer_base,
        lower_outer_base,
        inner_base,
        upper_base,
        lower_attachment,
        upper_attachment,
        side_attachment)

    top_face_finder = body_entities.bounding_box.make_box()
    top_face_finder.place(z=-top_face_finder == +body_entities)

    body = Extrude(
        Hull(Union(*[face.make_component() for face in body_entities.find_faces(top_face_finder)])),
        -key_base_upper.size().z,
        name="body")

    down_key_slot = Box(
        down_key.find_children("post")[0].size().x + 1, 5, body.size().z * 2, name="down_key_slot")
    down_key_slot.place(
        ~down_key_slot == ~down_key,
        +down_key_slot == +down_key.find_children("magnet")[0],
        +down_key_slot == +body)

    down_key_right_stop = body.bounding_box.make_box()
    down_key_right_stop.place(
        +down_key_right_stop == +down_key_body_hole,
        ~down_key_right_stop == ~body,
        +down_key_right_stop == +body)

    down_key_right_stop.ry(-45, center=(
        down_key_right_stop.max().x,
        down_key_right_stop.mid().y,
        down_key_right_stop.max().z))
    down_key_right_stop.rx(-9, center=(
        down_key_body_hole.max().x,
        down_key_body_hole.min().y,
        down_key_body_hole.max().z))

    down_key_right_stop_bounds_tool = down_key_right_stop.bounding_box.make_box()
    down_key_right_stop_bounds_tool .place(
        (-down_key_right_stop_bounds_tool == +down_key_body_hole) - 1,
        (-down_key_right_stop_bounds_tool == ~down_key.named_faces("pivot_back_face")[0]) + .2,
        ~down_key_right_stop_bounds_tool == ~down_key_right_stop)

    down_key_right_stop = Intersection(down_key_right_stop, down_key_right_stop_bounds_tool)

    down_key_left_stop = down_key_right_stop.copy().scale(-1, 1, 1, center=down_key_body_hole.mid())

    down_key_magnet_extension = Box(
        down_key_slot.size().x,
        (down_key_body_hole.min().y - down_key.find_children("magnet")[0].max().y),
        body.min().z - down_key.min().z,
        name="down_key_magnet_extension")
    down_key_magnet_extension.place(
        ~down_key_magnet_extension == ~down_key,
        -down_key_magnet_extension == +down_key.find_children("magnet")[0],
        +down_key_magnet_extension == -body)

    down_key_magnet = horizontal_rotated_magnet_cutout(1.8)
    down_key_magnet.place(
        ~down_key_magnet == ~down_key_magnet_extension,
        -down_key_magnet == -down_key_magnet_extension,
        ~down_key_magnet == ~down_key.find_children("magnet")[0])

    down_key_led_cavity = make_bottom_entry_led_cavity("down_key_led_cavity")
    down_key_led_cavity.rz(180)
    upper_outer_led_cavity = upper_outer_base.find_children("led_cavity")[0]
    down_key_led_cavity.place(
        (-down_key_led_cavity == +down_key_body_hole) + .8,
        (~down_key_led_cavity == -down_key_body_hole) + 16,
        +down_key_led_cavity == +upper_outer_led_cavity)
    down_key_led_cavity = ExtrudeTo(down_key_led_cavity.named_faces("lens_hole"), down_key_body_hole)

    down_key_pt_cavity = make_bottom_entry_led_cavity("down_key_pt_cavity")
    down_key_pt_cavity.place(
        (+down_key_pt_cavity == -down_key_body_hole) - .8,
        ~down_key_pt_cavity == ~down_key_led_cavity,
        +down_key_pt_cavity == +upper_outer_led_cavity)
    down_key_pt_cavity = ExtrudeTo(down_key_pt_cavity.named_faces("lens_hole"), down_key_body_hole)

    assembly = Difference(
        Union(body, body_entities, down_key_magnet_extension),
        upper_outer_base_negatives, lower_outer_base_negatives,
        inner_base_negatives, upper_base_negatives,
        *lower_attachment.find_children("negatives"),
        *upper_attachment.find_children("negatives"),
        *side_attachment.find_children("negatives"),
        down_key_slot, down_key_magnet, down_key_led_cavity, down_key_pt_cavity,
        Difference(down_key_body_hole, down_key_right_stop, down_key_left_stop, name="down_key_void"),
        name=name or "thumb_cluster")

    assembly.add_named_faces(
        "body_bottom",
        *assembly.find_faces(body.end_faces))

    return assembly, down_key


def thumb_clip(thumb_cluster: Component, name="thumb_clip"):
    side_attachment = magnetic_attachment(
        ball_depth=1.8, rectangular_depth=.6, radius=3.5, name="side_attachment")
    side_attachment.place(
        ~side_attachment == ~thumb_cluster.find_children("side_attachment")[0],
        ~side_attachment == ~thumb_cluster.find_children("side_attachment")[0],
        +side_attachment == -thumb_cluster.find_children("side_attachment")[0])
    upper_attachment = magnetic_attachment(
        ball_depth=1.8, rectangular_depth=.6, radius=3.5,
        name="upper_attachment")
    upper_attachment.place(
        ~upper_attachment == ~thumb_cluster.find_children("upper_attachment")[0],
        ~upper_attachment == ~thumb_cluster.find_children("upper_attachment")[0],
        +upper_attachment == -thumb_cluster.find_children("upper_attachment")[0])
    lower_attachment = magnetic_attachment(
        ball_depth=1.8, rectangular_depth=.6, radius=3.5,
        name="lower_attachment")
    lower_attachment.place(
        ~lower_attachment == ~thumb_cluster.find_children("lower_attachment")[0],
        ~lower_attachment == ~thumb_cluster.find_children("lower_attachment")[0],
        +lower_attachment == -thumb_cluster.find_children("lower_attachment")[0])

    side_middle = Cylinder(side_attachment.size().z, side_attachment.size().x / 2)
    side_middle.place(
        ~side_middle == ~lower_attachment,
        (~side_middle == ~side_attachment) - 5,
        ~side_middle == ~side_attachment)

    middle = Cylinder(side_attachment.size().z, (side_attachment.size().x / 2) * 1.5)
    middle.place(
        (~middle == ~upper_attachment),
        ~middle == ~side_attachment,
        ~middle == ~side_attachment)

    bottoms_finder = thumb_cluster.bounding_box.make_box()
    bottoms_finder.place(
        ~bottoms_finder == ~thumb_cluster,
        ~bottoms_finder == ~thumb_cluster,
        +bottoms_finder == -side_middle)

    upper_hull = Hull(Union(
        upper_attachment.find_faces(bottoms_finder)[0].make_component(),
        middle.find_faces(bottoms_finder)[0].make_component()))
    side_hull = Hull(Union(
        side_attachment.find_faces(bottoms_finder)[0].make_component(),
        middle.find_faces(bottoms_finder)[0].make_component()))
    lower_hull = Hull(Union(
        lower_attachment.find_faces(bottoms_finder)[0].make_component(),
        side_middle.find_faces(bottoms_finder)[0].make_component()))
    middle_hull = Hull(Union(
        middle.find_faces(bottoms_finder)[0].make_component(),
        side_middle.find_faces(bottoms_finder)[0].make_component()))
    attachments = Group([upper_attachment, side_attachment, lower_attachment])

    # Add a hole for an fully inserted magnet, near where the magnet on the cluster will be. The magnet should be
    # in the opposite orientation as the one on the cluster, and will provide a slight upwards force - enough to
    # lightly hold the clip in place.
    attachment_magnet = vertical_large_thin_magnet_cutout()
    attachment_magnet.place(
        ~attachment_magnet == ~lower_attachment,
        (-attachment_magnet == +lower_attachment.find_children("magnet_cutout")[0]) + .8,
        +attachment_magnet == +lower_attachment)

    attachment_magnet_extension = Cylinder(lower_attachment.size().z, lower_attachment.size().x / 2)
    attachment_magnet_extension.place(
        ~attachment_magnet_extension == ~lower_attachment,
        (~attachment_magnet_extension == ~attachment_magnet),
        ~attachment_magnet_extension == ~lower_attachment)
    attachment_magnet_hull = Hull(Union(
        attachment_magnet_extension.find_faces(bottoms_finder)[0].make_component(),
        lower_attachment.find_faces(bottoms_finder)[0].make_component()))
    attachment_magnet_extension = Extrude(attachment_magnet_hull, -lower_attachment.size().z)

    attachment_negatives = attachments.find_children("negatives")
    result = Difference(
        Union(attachments, attachment_magnet_extension,
              Extrude(Union(upper_hull, side_hull, lower_hull, middle_hull), -(side_middle.size().z - 1.6))),
        *attachment_negatives,
        attachment_magnet,
        name=name)

    return result


def thumb_pcb(thumb_cluster: Component, thumb_clip: Component, name="thumb_pcb"):
    hole_size = .35

    down_key_magnet_extension = thumb_cluster.find_children("down_key_magnet_extension")[0]

    body_bottom_face = thumb_cluster.named_faces("body_bottom")[0]
    pcb_silhouette = Silhouette(thumb_cluster, body_bottom_face.get_plane())

    pcb_silhouette = Silhouette(pcb_silhouette.faces[0].outer_edges, pcb_silhouette.get_plane())

    top_finder = thumb_cluster.bounding_box.make_box()
    top_finder.place(
        ~top_finder == ~thumb_cluster,
        ~top_finder == ~thumb_cluster,
        -top_finder == +thumb_clip)

    clip_outlines = Union(*[Silhouette(face.outer_edges, pcb_silhouette.get_plane())
                            for face in thumb_clip.find_faces(top_finder)])

    side_attachment_face = clip_outlines.find_faces(thumb_clip.find_children("side_attachment"))[0]
    upper_attachment_face = clip_outlines.find_faces(thumb_clip.find_children("upper_attachment"))[0]

    lower_cutout = thumb_cluster.bounding_box.make_box()
    lower_cutout.place(
        -lower_cutout == -down_key_magnet_extension,
        +lower_cutout == +down_key_magnet_extension,
        ~lower_cutout == ~pcb_silhouette)

    pcb_silhouette = Difference(
        pcb_silhouette,
        side_attachment_face.bounding_box.make_box(),
        upper_attachment_face.bounding_box.make_box(),
        lower_cutout,
        thumb_cluster.find_children("down_key_slot")[0])

    pcb_silhouette.tz(-.01)

    bottom_finder = thumb_cluster.bounding_box.make_box()
    bottom_finder.place(
        ~bottom_finder == ~thumb_cluster,
        ~bottom_finder == ~thumb_cluster,
        +bottom_finder == -thumb_cluster)

    pcb_silhouette = Difference(
        pcb_silhouette,
        ExtrudeTo(
            Union(*[face.make_component() for face in thumb_cluster.find_faces(bottom_finder)]),
            body_bottom_face),
        down_key_magnet_extension)

    pcb_silhouette = OffsetEdges(
        pcb_silhouette.faces[0],
        pcb_silhouette.faces[0].outer_edges,
        -.2)

    legs = Union(*thumb_cluster.find_children("legs"))
    legs.place(
        z=~legs == ~pcb_silhouette)

    down_key_body_hole = thumb_cluster.find_children("down_key_body_hole")[0]

    connector_holes = hole_array(hole_size, 1.5, 7)
    connector_holes.rz(90)
    connector_holes.place(~connector_holes == ~down_key_body_hole,
                          ~connector_holes == ~down_key_body_hole,
                          ~connector_holes == ~pcb_silhouette)

    # A cutout in the clip for the connector

    connector_cutout = Box(
        5,
        13,
        thumb_clip.size().z,
        name="connector_cutout")
    connector_cutout.place(
        ~connector_cutout == ~connector_holes,
        ~connector_cutout == ~connector_holes,
        -connector_cutout == -thumb_clip)

    pcb_silhouette = Difference(pcb_silhouette, legs, connector_holes)

    pcb = Extrude(pcb_silhouette, -1.6, name=name)

    pcb = SplitFace(pcb, thumb_clip, name=pcb.name)

    return pcb, connector_cutout


def _align_key(base_magnet_cutout: Component, key: Component):
    key_magnet_cutout = key.find_children("magnet_cutout")[0]

    vertical = Vector3D.create(0, 0, 1)
    key_normal = key_magnet_cutout.named_faces("front")[0].get_plane().normal
    key_other = key_normal.crossProduct(vertical)

    base_reverse_normal = base_magnet_cutout.named_faces("front")[0].get_plane().normal
    base_reverse_normal.scaleBy(-1)
    base_other = base_reverse_normal.crossProduct(vertical)

    matrix = Matrix3D.create()
    matrix.setToAlignCoordinateSystems(
        key_magnet_cutout.named_faces("front")[0].mid(),
        key_normal, key_other, vertical,
        base_magnet_cutout.named_faces("front")[0].mid(),
        base_reverse_normal, base_other, vertical)

    key.transform(matrix)


def full_thumb(left_hand=False):
    suffix = "left" if left_hand else "right"
    base, down_key = thumb_base("thumb_cluster_" + suffix)

    outer_lower_key = outer_lower_thumb_key()
    outer_lower_key.rx(90)
    _align_key(base.find_children("lower_outer_base")[0].find_children("magnet_cutout")[0], outer_lower_key)

    outer_upper_key = outer_upper_thumb_key()
    outer_upper_key.rx(90)
    _align_key(base.find_children("upper_outer_base")[0].find_children("magnet_cutout")[0], outer_upper_key)

    inner_key = inner_thumb_key()
    inner_key.rx(90)
    _align_key(base.find_children("inner_key_base")[0].find_children("magnet_cutout")[0], inner_key)

    mode_key = thumb_mode_key("thumb_mode_key_" + suffix)
    mode_key.rx(90)
    _align_key(base.find_children("upper_key_base")[0].find_children("magnet_cutout")[0], mode_key)

    insertion_tool = thumb_cluster_insertion_tool(base)

    clip = thumb_clip(base, name="thumb_clip_" + suffix)

    pcb, connector_cutout = thumb_pcb(base, clip, name="thumb_pcb_" + suffix)

    clip = Difference(
        clip, connector_cutout, name=clip.name)

    all_components = [base, down_key, outer_lower_key, outer_upper_key, inner_key, mode_key, insertion_tool, clip, pcb]

    if left_hand:
        Group(all_components).scale(-1, 1, 1)

    return tuple(all_components)


def place_header(header: Component, x: int, y: int):
    pin_size = min(header.size().x, header.size().y)

    header.place((-header == x * 2.54) + pin_size / 2,
                 (-header == y * 2.54) + pin_size / 2,
                 ~header == 0)


def central_pcb():
    base = Box(42, 50, 1.2)

    teensy_left = hole_array(.4, 2.54, 12).rz(90)
    place_header(teensy_left, 0, 0)

    teensy_back = hole_array(.4, 2.54, 5)
    place_header(teensy_back, 1, 11)

    teensy_right = hole_array(.4, 2.54, 12).rz(90)
    place_header(teensy_right, 6, 0)

    driver_right = hole_array(.4, 2.54, 10).rz(90)
    place_header(driver_right, -1, 0)

    driver_left = driver_right.copy()
    place_header(driver_left, -4, 0)

    conn1 = hole_array(.35, 1.5, 7)
    conn1.place((+conn1 == -driver_left) - 2.54,
                (-conn1 == -driver_left) + 2.54,
                ~conn1 == ~driver_left)
    conns = [conn1]
    prev = conn1
    for i in range(0, 4):
        conn = prev.copy()
        conn.place(~conn == ~prev,
                   (~conn == ~prev) + 2.54 * 2,
                   ~conn == ~prev)
        conns.append(conn)
        prev = conn

    i2c_conn = hole_array(.35, 1.5, 7).rz(90)
    place_header(i2c_conn, 3, 3)

    all_holes = Union(
        teensy_left, teensy_back, teensy_right, driver_right, driver_left, *conns, i2c_conn)

    all_holes.place(~all_holes == ~base,
                    (-all_holes == -base) + 2.54*3,
                    ~all_holes == +base)

    result = Difference(base, ExtrudeTo(all_holes, base), name="central_pcb")
    result.add_named_faces("bottom", *result.find_faces(base.bottom))
    return result


def central_pcb_sketch():
    pcb = central_pcb()

    pcb_bottom = BRepComponent(pcb.named_faces("bottom")[0].brep)

    rects = []
    for edge in pcb_bottom.bodies[0].brep.edges:
        if not isinstance(edge.geometry, adsk.core.Circle3D):
            continue

        if edge.geometry.radius < .4:
            rect_size = (1.25, 1.25)
        else:
            rect_size = (2, 2)

        rect = Rect(*rect_size)
        rect.place(~rect == edge.geometry.center,
                   ~rect == edge.geometry.center,
                   ~rect == edge.geometry.center)
        rects.append(rect)
    split_face = SplitFace(pcb_bottom, Union(*rects), name="central_pcb_sketch")
    occurrence = split_face.scale(.1, .1, .1).create_occurrence(False)
    sketch = occurrence.component.sketches.add(occurrence.bRepBodies[0].faces[0])
    sketch.name = "central_pcb_sketch"
    for face in occurrence.bRepBodies[0].faces:
        sketch.include(face)

    return sketch


def central_pcb_tray():
    pcb = central_pcb()

    bottom_thickness = 1.2
    base = Box(pcb.size().x + 2.3*2,
               pcb.size().y + 2.3*2,
               10)

    base.place(~base == ~pcb,
               ~base == ~pcb,
               (-base == -pcb) - bottom_thickness)

    back_magnet = horizontal_large_thin_magnet_cutout(name="back_cutout")
    back_magnet.rz(180)
    back_magnet.place(~back_magnet == ~base,
                      +back_magnet == +base,
                      +back_magnet == 8)

    left_magnet = horizontal_large_thin_magnet_cutout(name="left_cutout")
    left_magnet.rz(-90)
    left_magnet.place(-left_magnet == -base,
                      (-left_magnet == -base) + 5,
                      +left_magnet == 8)

    right_magnet = horizontal_large_thin_magnet_cutout(name="left_cutout")
    right_magnet.rz(90)
    right_magnet.place(+right_magnet == +base,
                       (-right_magnet == -base) + 5,
                       +right_magnet == 8)

    hollow = Box(pcb.bounding_box.size().x+.2,
                 pcb.bounding_box.size().y+.2,
                 base.size().z)
    hollow.place(~hollow == ~pcb,
                 ~hollow == ~pcb,
                 -hollow == -pcb)

    front_opening = Box(pcb.bounding_box.size().x + .2,
                        pcb.bounding_box.size().y,
                        base.size().z)
    front_opening.place(~front_opening == ~base,
                        ~front_opening == -base,
                        (-front_opening == -base) + 1.2 + 2)

    return Difference(base, back_magnet, left_magnet, right_magnet, hollow, front_opening, name="central_pcb_tray")


def key_breakout_pcb():
    base = Box(20, 13, 1.2)

    upper_connector_holes = hole_array(.35, 1.5, 7)
    upper_connector_holes.place(~upper_connector_holes == ~base,
                                (~upper_connector_holes == +base) - 2.2,
                                -upper_connector_holes == -base)

    lower_connector_holes = upper_connector_holes.copy()
    lower_connector_holes.place(y=(~lower_connector_holes == -base) + 2.2)

    header_holes = hole_array(.40, 2.54, 7)
    header_holes.place(~header_holes == ~base,
                       ~header_holes == ~base,
                       -header_holes == -base)

    all_holes = Union(upper_connector_holes, lower_connector_holes, header_holes)
    all_holes = ExtrudeTo(all_holes, base)

    result = Difference(base, all_holes)
    result.add_named_faces("bottom", *result.find_faces(base.bottom))
    return result


def key_breakout_pcb_sketch():
    pcb = key_breakout_pcb()

    pcb_bottom = BRepComponent(pcb.named_faces("bottom")[0].brep)

    rects = []
    for edge in pcb_bottom.bodies[0].brep.edges:
        if not isinstance(edge.geometry, adsk.core.Circle3D):
            continue

        if edge.geometry.radius < .4:
            rect_size = (1.25, 1.25)
        else:
            rect_size = (2, 2)

        rect = Rect(*rect_size)
        rect.place(~rect == edge.geometry.center,
                   ~rect == edge.geometry.center,
                   ~rect == edge.geometry.center)
        rects.append(rect)
    split_face = SplitFace(pcb_bottom, Union(*rects))
    occurrence = split_face.scale(.1, .1, .1).create_occurrence(False)
    sketch = occurrence.component.sketches.add(occurrence.bRepBodies[0].faces[0])
    for face in occurrence.bRepBodies[0].faces:
        sketch.include(face)

    return sketch


def handrest(left_hand=False):
    script_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
    script_dir = os.path.dirname(script_path)

    handrest_model = import_fusion_archive(
        os.path.join(script_dir, "left_handrest_scan_reduced_brep.f3d"), name="handrest")
    handrest_model.scale(10, 10, 10)
    handrest_model.rz(-90)
    handrest_model.place(~handrest_model == 0,
                         ~handrest_model == 0,
                         -handrest_model == 0)

    pcb_tray = central_pcb_tray()

    tray_slot = Box(pcb_tray.bounding_box.size().x + .2,
                    pcb_tray.bounding_box.size().y * 10,
                    24)
    tray_slot.place(~tray_slot == ~handrest_model,
                    (+tray_slot == -handrest_model) + pcb_tray.bounding_box.size().y + 15,
                    -tray_slot == -handrest_model)

    back_magnet = Box(3.9, 3.9, 1.8).rx(90)
    back_magnet.place(~back_magnet == ~tray_slot,
                      -back_magnet == +tray_slot,
                      (+back_magnet == -handrest_model) + 9.2)

    left_magnet = back_magnet.copy()
    left_magnet.rz(90)
    left_magnet.place(+left_magnet == -tray_slot,
                      (+left_magnet == +tray_slot) - 46.2,
                      +left_magnet == +back_magnet)

    right_magnet = back_magnet.copy()
    right_magnet.rz(-90)
    right_magnet.place(-right_magnet == +tray_slot,
                       +right_magnet == +left_magnet,
                       +right_magnet == +left_magnet)

    front_left_bottom_magnet = Box(3.6, 6.8, 1.8, name="bottom_magnet")
    front_left_bottom_magnet.place((~front_left_bottom_magnet == ~handrest_model) + 27.778,
                                   (~front_left_bottom_magnet == ~handrest_model) - 17.2784,
                                   -front_left_bottom_magnet == -handrest_model)

    front_right_bottom_magnet = Box(3.6, 6.8, 1.8, name="bottom_magnet")
    front_right_bottom_magnet.place((~front_right_bottom_magnet == ~handrest_model) - 29.829,
                                    (~front_right_bottom_magnet == ~handrest_model) - 17.2782,
                                    -front_right_bottom_magnet == -handrest_model)

    back_right_bottom_magnet = Box(3.6, 6.8, 1.8, name="bottom_magnet")
    back_right_bottom_magnet.place((~back_right_bottom_magnet == ~handrest_model) - 29.829,
                                   (~back_right_bottom_magnet == ~handrest_model) + 37.7218,
                                   -back_right_bottom_magnet == -handrest_model)

    back_left_bottom_magnet = Box(3.6, 6.8, 1.8, name="bottom_magnet")
    back_left_bottom_magnet.place((~back_left_bottom_magnet == ~handrest_model) + 27.778,
                                  (~back_left_bottom_magnet == ~handrest_model) + 37.7218,
                                  -back_left_bottom_magnet == -handrest_model)

    assembly = Difference(handrest_model, tray_slot, back_magnet, left_magnet, right_magnet, front_left_bottom_magnet,
                          front_right_bottom_magnet, back_right_bottom_magnet, back_left_bottom_magnet,
                          name="left_handrest" if left_hand else "right_handrest")
    if not left_hand:
        assembly.scale(-1, 1, 1)
    return assembly


def run_design(design_func, message_box_on_error=False, print_runtime=True, document_name=None):
    """
    Exactly the same as the standard fscad.run_design, except message_box_on_error is False by default.
    """
    if not document_name:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        filename = module.__file__
        document_name = pathlib.Path(filename).stem

    import fscad
    fscad.run_design(design_func, message_box_on_error, print_runtime, document_name)
