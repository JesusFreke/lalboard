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
import inspect
import math
import os
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


def horizontal_rotated_magnet_cutout(depth=1.8, name="magnet_cutout"):
    return tapered_box(1.45, 1.45, 1.7, 1.7, depth, name=name).rx(90).ry(45)


def horizontal_magnet_cutout(depth=1.8, name="magnet_cutout"):
    return tapered_box(1.45, 1.8, 1.7, 1.8, depth, name=name).rx(90)


def horizontal_large_thin_magnet_cutout(depth=1.8, name="magnet_cutout"):
    return tapered_box(1.45*2, 1.8*2, 1.7*2, 1.8*2, depth, name=name).rx(90)


def vertical_magnet_cutout(depth=1.6, name="magnet_cutout"):
    return tapered_box(1.55, 1.55, 1.7, 1.7, depth, name)


def vertical_large_magnet_cutout(name="magnet_cutout"):
    base = Box(2.9, 2.9, 2, name=name + "_base")
    taper = tapered_box(2.9, 2.9, 3.1, 3.1, 1.3, name=name + "_taper")
    taper.place(~taper == ~base,
                ~taper == ~base,
                -taper == +base)
    return Union(base, taper, name=name)


def vertical_large_thin_magnet_cutout(name="magnet_cutout"):
    base = Box(3.0*2, 3.0, 1, name=name + "_base")
    taper = tapered_box(3.05*2, 3.0, 3.25*2, 3.2, .7, name=name + "_taper")
    taper.place(~taper == ~base,
                ~taper == ~base,
                -taper == +base)
    return Union(base, taper, name=name)


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

    cavity.add_named_faces("legs", *cavity.find_faces((leg, leg2)))
    cavity.add_named_faces("lens_hole", *cavity.find_faces(lens_hole))
    cavity.add_named_faces("top", *cavity.find_faces(body.top))

    cavity.add_named_point("lens_center",
                           (cavity.mid().x, cavity.mid().y, lens_hole.bodies[0].faces[0].brep.centroid.z))

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

    cavity.add_named_faces("legs", *cavity.find_faces((leg, leg2)))
    cavity.add_named_faces("lens_hole", *cavity.find_faces(lens_hole))
    cavity.add_named_faces("top", *cavity.find_faces((body.top, slot.top)))

    cavity.add_named_point("lens_center",
                           (cavity.mid().x, cavity.mid().y, lens_hole.bodies[0].faces[0].brep.centroid.z))

    return cavity


def hole_array(radius, pitch, count):
    hole = Circle(radius)
    union = None
    for i in range(0, count):
        hole_copy = hole.copy().tx(pitch * i)
        if not union:
            union = Union(hole_copy)
        else:
            union.add(hole_copy)
    return union


def vertical_key_base(base_height, extra_height=0, pressed_key_angle=12.5, mirrored=False):
    front = Box(5, 2.2, 6.4 + extra_height, "front")

    pt_base = Box(5, 6.15, front.size().z, "phototransistor_base")
    pt_base.place(+pt_base == -front, +pt_base == +front, -pt_base == -front)
    pt_cavity = make_pt_cavity()
    pt_cavity.place(~pt_cavity.named_point("lens_center") == ~pt_base,
                    ~pt_cavity.named_point("lens_center") == ~pt_base,
                    (~pt_cavity.named_point("lens_center") == +pt_base) - 1.9)

    led_base = Box(6, 6.15, front.size().z, "led_base")
    led_base.place(-led_base == +front, +led_base == +front, -led_base == -front)
    led_cavity = make_led_cavity()
    led_cavity.place((~led_cavity.named_point("lens_center") == ~led_base) - .125,
                     ~led_cavity.named_point("lens_center") == ~led_base,
                     (~led_cavity.named_point("lens_center") == +led_base) - 1.9)

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

    # the distance along the angled backstop from where the flat part meets the bottom cylindrical part
    # this is placed so that there's just enough room for the key to be able to slid into place vertically,
    # but as soon as it starts to rotate, the groove in the key post engages with the ridge, retaining the key
    retaining_ridge_dist = retaining_ridge_thickness / math.tan(math.radians(pressed_key_angle))
    retaining_ridge_y = retaining_ridge_dist * math.sin(math.radians(pressed_key_angle))
    retaining_ridge_z = retaining_ridge_dist * math.cos(math.radians(pressed_key_angle))

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
    retaining_ridge = Extrude(retaining_ridge, back.size().x)

    retaining_ridge.rz(-90)
    retaining_ridge.ry(-90)

    lowest_edge = None
    for edge in retaining_ridge.bodies[0].brep.edges:
        if lowest_edge is None or edge.pointOnEdge.z < lowest_edge.pointOnEdge.z:
            lowest_edge = edge

    retaining_ridge.add_named_point("lowest_edge", Point3D.create(
        retaining_ridge.mid().x, lowest_edge.pointOnEdge.y, lowest_edge.pointOnEdge.z))

    retaining_ridge.place(~retaining_ridge == ~back,
                          (~retaining_ridge.named_point("lowest_edge") == +back_sloped) - retaining_ridge_y,
                          (~retaining_ridge.named_point("lowest_edge") == -back_sloped) + retaining_ridge_z)

    result = Union(pt_base, led_base, front, back, base)
    result = Difference(result, sloped_key)
    result = Union(result, retaining_ridge)

    magnet_cutout = horizontal_rotated_magnet_cutout()
    magnet_cutout.place(~magnet_cutout == ~front,
                        -magnet_cutout == -front,
                        (+magnet_cutout == +front) - .45)

    extruded_led_cavity = ExtrudeTo(led_cavity.named_faces("lens_hole"), result.copy(False))
    extruded_led_cavity = ExtrudeTo(
        extruded_led_cavity.find_faces(led_cavity.named_faces("legs")), result.copy(False))

    extruded_pt_cavity = ExtrudeTo(pt_cavity.named_faces("lens_hole"), result.copy(False))
    extruded_pt_cavity = ExtrudeTo(extruded_pt_cavity.find_faces(pt_cavity.named_faces("legs")), result.copy(False))
    extruded_pt_cavity = ExtrudeTo(extruded_pt_cavity.find_faces(pt_cavity.named_faces("top")), result.copy(False))

    negatives = Union(extruded_pt_cavity, extruded_led_cavity, magnet_cutout, key_pivot)
    bounding_box = Box(
        result.bounding_box.size().x,
        result.bounding_box.size().y,
        min(result.bounding_box.size().z, 6.4 + extra_height + base_height))
    bounding_box.place(-bounding_box == -result,
                       -bounding_box == -result,
                       -bounding_box == -result)

    negatives = Intersection(negatives, bounding_box, name="negatives")

    result = Difference(Intersection(result, bounding_box), negatives,  name="vertical_key_base")

    result.add_named_point("midpoint", (magnet_cutout.mid().x, result.mid().y, result.mid().z))

    if mirrored:
        result.scale(-1, 1, 1, center=result.mid())

    return result


def cluster():
    base = Box(24.9, 24.9, 2, "base")
    key_base = vertical_key_base(2)

    key_base.place(~key_base.named_point("midpoint") == ~base,
                   -key_base == -base,
                   -key_base == -base)

    key_bases = (
        key_base.copy().scale(-1, 1, 1, center=key_base.named_point("midpoint")),
        key_base.copy().rz(90, base.mid()),
        key_base.copy().scale(-1, 1, 1, center=key_base.named_point("midpoint")).rz(180, base.mid()),
        key_base.rz(270, base.mid())
    )
    key_base_negatives = (
        key_bases[0].find_children("negatives")[0],
        key_bases[1].find_children("negatives")[0],
        key_bases[2].find_children("negatives")[0],
        key_bases[3].find_children("negatives")[0]
    )

    combined_cluster = Union(base, *key_bases)

    center_floor = Box(1, 1, 1.9, "center_floor")
    center_floor.place(~center_floor == ~base,
                       ~center_floor == ~base,
                       -center_floor == +base)

    for face in (center_floor.left, center_floor.right, center_floor.front, center_floor.back):
        center_floor = ExtrudeTo(center_floor.find_faces(face)[0], combined_cluster.copy(False))

    combined_cluster.add(center_floor)

    center_hole = Box(5, 5, combined_cluster.size().z, name="center_hole")
    center_hole.place(~center_hole == ~base,
                      ~center_hole == ~base,
                      -center_hole == -base)

    central_post = Box(center_hole.size().x + 1.6,
                       center_hole.size().x + 1.6,
                       combined_cluster.size().z, name="center_post")
    central_post.place(~central_post == ~center_hole,
                       ~central_post == ~center_hole,
                       -central_post == -base)

    combined_cluster_copy = combined_cluster.copy(False)
    center = ExtrudeTo(central_post.back,
                       combined_cluster_copy)
    center = ExtrudeTo(center.find_faces(central_post.left), combined_cluster_copy)
    center = ExtrudeTo(center.find_faces(central_post.right), combined_cluster_copy, name="center")

    combined_cluster.add(center)

    central_magnet_cutout = horizontal_rotated_magnet_cutout(name="central_magnet_cutout")
    central_magnet_cutout.place(~central_magnet_cutout == ~center_hole,
                                -central_magnet_cutout == +center_hole,
                                (+central_magnet_cutout == +center) - .8)

    # TODO: is there a better way to find the desired children?
    back = key_base_negatives[0]
    left_cavity = key_base_negatives[3]
    right_cavity = key_base_negatives[1]

    right_base = key_bases[1]
    left_base = key_bases[3]

    central_led_cavity = make_led_cavity().scale(-1, 1, 1)
    central_led_cavity.place(-central_led_cavity == -center_floor,
                             -central_led_cavity == -center_floor,
                             (~central_led_cavity.named_point("lens_center") == +center_floor) + 1.6)
    central_led_cavity.align_to(left_cavity.bodies[0], Vector3D.create(-1, 0, 0))
    central_led_cavity.align_to(back.bodies[0], Vector3D.create(0, -1, 0))

    central_pt_cavity = make_pt_cavity().scale(-1, 1, 1)
    central_pt_cavity.place(+central_pt_cavity == +center_floor,
                            -central_pt_cavity == -center_floor,
                            (~central_pt_cavity.named_point("lens_center") == +center_floor) + 1.6)
    central_pt_cavity.align_to(right_cavity.bodies[0], Vector3D.create(1, 0, 0))
    central_pt_cavity.align_to(back.bodies[0], Vector3D.create(0, -1, 0))

    central_led_base = Box(2.8,
                           central_led_cavity.max().y - center_floor.min().y,
                           combined_cluster.max().z - center_floor.max().z)
    central_led_base.place(-central_led_base == -center_floor,
                           -central_led_base == -center_floor,
                           -central_led_base == +center_floor)

    central_pt_base = Box(2.8,
                          central_pt_cavity.max().y - center_floor.min().y,
                          combined_cluster.max().z - center_floor.max().z)
    central_pt_base.place(+central_pt_base == +center_floor,
                          -central_pt_base == -center_floor,
                          -central_pt_base == +center_floor)

    combined_cluster.add(central_led_base)
    combined_cluster.add(central_pt_base)

    extruded_led_cavity = ExtrudeTo(central_led_cavity.named_faces("lens_hole"), combined_cluster.copy(False))
    extruded_led_cavity = ExtrudeTo(extruded_led_cavity.find_faces(central_led_cavity.named_faces("legs")),
                                    combined_cluster.copy(False))
    extruded_led_cavity = ExtrudeTo(extruded_led_cavity.find_faces(central_led_cavity.named_faces("top")),
                                    combined_cluster.copy(False))

    extruded_pt_cavity = ExtrudeTo(central_pt_cavity.named_faces("lens_hole"), combined_cluster.copy(False))
    extruded_pt_cavity = ExtrudeTo(extruded_pt_cavity.find_faces(central_pt_cavity.named_faces("legs")),
                                   combined_cluster.copy(False))
    extruded_pt_cavity = ExtrudeTo(extruded_pt_cavity.find_faces(central_pt_cavity.named_faces("top")),
                                   combined_cluster.copy(False))

    result = Difference(combined_cluster, *key_base_negatives, center_hole, central_magnet_cutout,
                        extruded_led_cavity, extruded_pt_cavity)
    result.add_named_point("lower_left_corner", [right_base.max().x, right_base.max().y, 0])
    result.add_named_point("lower_right_corner", [left_base.min().x, left_base.max().y, 0])
    return result


def cluster_pcb(cluster):
    hole_size = .35

    bottom_finder = Circle(5)
    bottom_finder.place(~bottom_finder == ~cluster,
                        ~bottom_finder == ~cluster,
                        ~bottom_finder == -cluster)

    bottom = cluster.find_faces(bottom_finder)[0]

    base = Extrude(BRepComponent(bottom.brep).bodies[0].faces[0], 1.2)

    base_extension = Box(base.size().x, 7, base.size().z)
    base_extension.place(~base_extension == ~base,
                         -base_extension == +base,
                         -base_extension == -base)

    connector_holes = hole_array(hole_size, 1.5, 7)
    connector_holes.place((~connector_holes == ~base_extension) - 1.8375,
                          (~connector_holes == +base_extension) - 2.2,
                          ~connector_holes == +base_extension)
    extension_holes = ExtrudeTo(connector_holes, base_extension.bottom)

    through_holes = hole_array(hole_size, 2.1, 7)
    through_holes.place(~through_holes == ~connector_holes,
                        (-through_holes == ~connector_holes) - 1.3-2.5,
                        ~through_holes == +base_extension)
    through_holes = ExtrudeTo(through_holes, base_extension.bottom)

    base_extension = Difference(base_extension, extension_holes, through_holes)

    base = Union(base, base_extension, name="cluster_pcb")
    base.add_named_faces("bottom", *base.find_faces(bottom))
    return base


def cluster_pcb_sketch(cluster_pcb_bottom: Component):
    rects = []
    for edge in cluster_pcb_bottom.bodies[0].brep.edges:
        if not isinstance(edge.geometry, adsk.core.Circle3D):
            continue

        if cluster_pcb_bottom.max().y - edge.geometry.center.y < 3:
            rect_size = (1.25, 1.25)
        elif cluster_pcb_bottom.max().y - edge.geometry.center.y < 6:
            rect_size = (1.75, 2)
        else:
            rect_size = (2, 2)

        rect = Rect(*rect_size)
        rect.place(~rect == edge.geometry.center,
                   ~rect == edge.geometry.center,
                   ~rect == edge.geometry.center)
        rects.append(rect)
    split_face = SplitFace(cluster_pcb_bottom, Union(*rects), name="cluster_pcb_sketch")
    occurrence = split_face.scale(.1, .1, .1).create_occurrence(False)
    sketch = occurrence.component.sketches.add(occurrence.bRepBodies[0].faces[0])
    sketch.name = "cluster_pcb_sketch"
    for face in occurrence.bRepBodies[0].faces:
        sketch.include(face)


def ball_socket_ball():
    return Sphere(3, "ball")


def ball_socket_base(base_height, mirrored=False):
    pin_hole_radius = 2.4

    ball = ball_socket_ball()
    ball_radius = ball.size().x / 2

    # the radio of the total diameter of the ball to sink into the base. The size of the hole for the downwards-facing
    # pin is determined by the intersection of the top of the base with the sphere, so sinking the ball lower results
    # in a larger opening and more range of motion for the pin, but also a shorter standoff
    ball_sink_ratio = .05

    # tall enough to reach the middle of the ball
    base = Cylinder(
        ball_radius - (ball_radius * 2 * ball_sink_ratio), ball_radius + .8)
    base = Threads(base, ((0, 0), (.99, .99), (0, .99)), 1)
    ball.place(~ball == ~base,
               ~ball == ~base,
               (-ball == -base) - (ball_radius * ball_sink_ratio * 2))

    pin_hole = Cylinder(base.size().z, pin_hole_radius)
    base = Difference(base, ball, pin_hole)

    # This is the cone that a line from the center of the ball would form if it swept along the hole.
    # cone_inverse_slope = pin_hole_radius / (ball.mid().z - base.find_faces(pin_hole.side)[0].size().z / 2)
    ball_socket_opening = Cylinder(
        base_height + base.find_faces(pin_hole)[0].size().z/2, ball_radius + .8 + .59, pin_hole_radius,
        "ball_socket_opening")

    ball_socket_opening.place(~ball_socket_opening == ~ball,
                              ~ball_socket_opening == ~ball,
                              (-ball_socket_opening == -base) - base_height)

    negatives = Union(ball_socket_opening, ball, name="negatives")
    result = Difference(base, negatives, name="ball_socket_base")

    if mirrored:
        result.scale(-1, 1, 1, center=base.mid())

    return result


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


def cluster_front(cluster: Component, base_height):
    extension_y_size = 13

    socket_base = ball_socket_base(2)
    opening = socket_base.find_children("negatives")[0]

    socket_base.place(~socket_base == ~cluster,
                      (~socket_base == -cluster) - extension_y_size / 2)

    socket_base_circle = Circle(socket_base.size().x/2)
    socket_base_circle.place(~socket_base_circle == ~socket_base,
                             ~socket_base_circle == ~socket_base)
    left_point = cluster.named_point("lower_left_corner").point
    right_point = cluster.named_point("lower_right_corner").point
    left_tangents = find_tangent_intersection_on_circle(socket_base_circle, left_point)
    if left_tangents[0].geometry.y < left_tangents[1].geometry.y:
        left_tangent_point = left_tangents[0].geometry
    else:
        left_tangent_point = left_tangents[1].geometry

    right_tangents = find_tangent_intersection_on_circle(socket_base_circle, right_point)
    if right_tangents[0].geometry.y < right_tangents[1].geometry.y:
        right_tangent_point = right_tangents[0].geometry
    else:
        right_tangent_point = right_tangents[1].geometry

    base = Polygon(left_point, left_tangent_point, right_tangent_point, right_point)

    base = Extrude(base, base_height)
    rounded_end = Cylinder(base_height, socket_base.size().x/2, name="rounded_end")
    rounded_end.place(~rounded_end == ~socket_base,
                      ~rounded_end == ~socket_base,
                      -rounded_end == -base)
    base = Union(base, rounded_end)
    base.place(~base == ~cluster,
               +base == right_point.y,
               -base == -cluster)

    base = Difference(base, cluster.bounding_box.make_box())

    cluster = Difference(cluster, Extrude(Polygon(left_tangent_point, left_point, cluster.min()), base_height),
                         Extrude(Polygon(right_point, right_tangent_point,
                                         Point3D.create(cluster.max().x, cluster.min().y, 0)), base_height))

    socket_base.place(z=-socket_base == +base)

    return cluster, Difference(Union(base, socket_base), opening)


def cluster_back(cluster: Component, pcb: Component, base_height: float):
    socket_base = ball_socket_base(2)
    opening = socket_base.find_children("negatives")[0]

    base = Box(cluster.size().x, pcb.max().y - cluster.max().y + 6.5 + socket_base.size().y/2, base_height)
    base.place(~base == ~cluster,
               -base == +cluster,
               -base == -cluster)

    socket_base.place(-socket_base == -cluster,
                      +socket_base == +base,
                      -socket_base == +base)

    other_socket_base = socket_base.copy()
    other_opening = other_socket_base.find_children("negatives")[0]
    other_socket_base.place(+other_socket_base == +cluster)

    hole_bounding_box = None
    for body in pcb.bodies:
        for face in body.faces:
            if isinstance(face.brep.geometry, adsk.core.Cylinder):
                if face.brep.centroid.y > cluster.max().y:
                    if hole_bounding_box is None:
                        hole_bounding_box = face.bounding_box.raw_bounding_box
                    else:
                        hole_bounding_box.combine(face.bounding_box.raw_bounding_box)

    holes_mid_point = Point3D.create((hole_bounding_box.minPoint.x + hole_bounding_box.maxPoint.x) / 2,
                                     (hole_bounding_box.minPoint.y + hole_bounding_box.maxPoint.y) / 2,
                                     (hole_bounding_box.minPoint.z + hole_bounding_box.maxPoint.z) / 2)
    pcb_relief = Box(hole_bounding_box.maxPoint.x - hole_bounding_box.minPoint.x + 2,
                     hole_bounding_box.maxPoint.y - hole_bounding_box.minPoint.y + 2,
                     base_height/2)
    pcb_relief.place(~pcb_relief == holes_mid_point,
                     ~pcb_relief == holes_mid_point,
                     -pcb_relief == -base)

    base = Fillet(base.shared_edges([base.back], [base.left, base.right]), socket_base.size().x/2)

    return Difference(Union(base, socket_base, other_socket_base), opening, other_opening), pcb_relief


def center_key():
    key_radius = 7.5
    key_rim_height = .5
    key_thickness = 2
    post_length = 8.4 + 2.5
    key_travel = 2.4

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

    post = Box(5 - .2, 5 - .2, post_length + key_rim_height, name="post")
    post.place(~post == ~key,
               ~post == ~key,
               -post == +key)
    post = Fillet(post.shared_edges([post.top], [post.front, post.back, post.left, post.right]), fillet_radius,
                  name="filleted_post")

    back_stop = Box(3.5, 2.45, 4.5, name="back_stop")
    back_stop.place(~back_stop == ~key,
                    (-back_stop == +post) + 1.1,
                    -back_stop == +key)
    fillet_edges = back_stop.shared_edges(
        [back_stop.top, back_stop.front, back_stop.back, back_stop.right, back_stop.left],
        [back_stop.top, back_stop.front, back_stop.back, back_stop.right, back_stop.left])
    back_stop = Fillet(fillet_edges, fillet_radius, False)

    bounding_cylinder = Cylinder(post.max().z - key.min().z, key_radius)
    bounding_cylinder.place(~bounding_cylinder == ~key,
                            ~bounding_cylinder == ~key,
                            -bounding_cylinder == -key)

    magnet = horizontal_rotated_magnet_cutout(1.8)
    magnet.place(~magnet == ~post,
                 -magnet == -post,
                 (~magnet == +key_rim) + 1.7 + key_travel)

    result = Difference(Union(key, key_rim, post, back_stop), magnet, name="center_key")

    return result


def vertical_key_post(post_length, groove_height, magnet_height):
    post = Box(post_width, post_length, key_thickness, name="post")
    post = Fillet(post.shared_edges([post.front], [post.top, post.bottom]), post.size().z/2)

    magnet = vertical_magnet_cutout().rz(45)
    magnet.place(~magnet == ~post,
                 ~magnet == magnet_height + key_thickness/2,
                 +magnet == +post)

    groove_width = .6
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
        groove_height=1.575,
        magnet_height=5.6,
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
        magnet_height=9.05,
        name=name)


def inner_thumb_key():
    return thumb_side_key(25, 13.5, 2.443, key_displacement=-.5, name="inner_thumb_key")


def outer_upper_thumb_key():
    return thumb_side_key(20, 16, 2.566, name="outer_upper_thumb_key")


def outer_lower_thumb_key():
    return thumb_side_key(20, 20, 4.159, name="outer_lower_thumb_key")


def thumb_mode_key(mirrored=False, name=None):
    key_post = vertical_key_post(23, 2.566, 9.05)

    face_finder = Box(1, 1, 1)
    face_finder.place(~face_finder == ~key_post,
                      -face_finder == +key_post,
                      ~face_finder == ~key_post)

    end_face = key_post.find_faces(face_finder)[0]

    end_face = BRepComponent(end_face.brep)

    mid_section_end = end_face.copy()
    mid_section_end.ry(20, center=mid_section_end.mid())
    mid_section_end .translate(-10, 10, math.sqrt(2*math.pow(10, 2)) * math.sin(math.radians(20)))

    end_section_end = mid_section_end.copy()
    end_section_end.ty(10)

    mid_section = Loft(end_face, mid_section_end)
    end_section = Loft(mid_section_end, end_section_end)

    end_section_end_face = end_section.find_faces(end_section_end)[0]

    end_section = Fillet(end_section_end_face.edges, key_thickness/2, False)

    result = Union(key_post, mid_section, end_section, name=name)
    if mirrored:
        result.scale(-1, 1, 1)
    return result


def thumb_down_key():
    key_base = Box(15, 29, 2.5)
    post = Box(4.5, 2.2, 9)
    post.place(~post == ~key_base,
               -post == -key_base,
               -post == +key_base)

    slot = Box(key_base.size().x, 2, post.size().z*2)
    slot = Fillet(slot.shared_edges([slot.front, slot.back], [slot.bottom]), slot.size().y/2)
    slot.place(~slot == ~key_base,
               -slot == +post,
               -slot == +key_base)
    angled_slot = slot.copy()
    angled_slot.rx(-9, center=(0, slot.mid().y, slot.min().z + slot.size().y/2))

    slot_backing = Box(key_base.size().x, post.size().y + slot.size().y, 1.8)
    slot_backing.place(~slot_backing == ~key_base,
                       -slot_backing == -key_base,
                       -slot_backing == +key_base)
    slot_stop = Box(key_base.size().x, 1.5, 4)
    slot_stop.place(~slot_stop == ~key_base,
                    -slot_stop == +slot_backing,
                    -slot_stop == +key_base)

    interruptor = Box(2, 3.5, 4.7)
    interruptor.place(~interruptor == ~key_base,
                      (~interruptor == ~key_base) - 1,
                      -interruptor == +key_base)

    magnet = horizontal_magnet_cutout()
    magnet.rz(180)
    magnet.place(~magnet == ~key_base,
                 +magnet == +post,
                 (+magnet == +post) - 1)

    return Difference(Union(key_base, post, slot_backing, slot_stop, interruptor), slot, angled_slot, magnet,
                      name="thumb_down_key")


def full_cluster(add_pcb=True, add_pcb_sketch=True, create_children=False):
    clust = cluster()
    clust.rz(180, center=clust.mid())

    clust, front = cluster_front(clust, 2)

    pcb = cluster_pcb(clust)

    back, pcb_relief = cluster_back(clust, pcb, 2)

    Difference(Union(clust, front, back), pcb_relief, name="cluster").create_occurrence(create_children, scale=.1)

    if add_pcb:
        pcb.create_occurrence(create_children, scale=.1)

    if add_pcb_sketch:
        cluster_pcb_sketch(BRepComponent(pcb.named_faces("bottom")[0].brep, name="cluster_pcb_sketch"))


def jst_adaptor():
    jst_holes = hole_array(.35, 1.5, 7)

    header_holes = hole_array(.35, 2.54, 7)
    header_holes.place(~header_holes == ~jst_holes,
                       (~header_holes == ~jst_holes) + 3,
                       ~header_holes == ~jst_holes)

    holes = Union(jst_holes, header_holes)

    base = Box(22, holes.size().y + 2.2*2, 1.2)
    base.place(~base == ~holes,
               ~base == ~holes,
               -base == ~holes)

    return Difference(base, ExtrudeTo(holes, base))


def ballscrew(screw_length, name):
    screw_radius = 1.5
    neck_length = 3
    neck_lower_radius = 2
    neck_upper_radius = 1.75

    ball = ball_socket_ball()

    tmp = Cylinder(ball.size().z/2, neck_upper_radius)
    tmp.place(~tmp == ~ball,
              ~tmp == ~ball,
              -tmp == ~ball)
    screw_ball_intersection = Intersection(ball.copy(), tmp)
    screw_ball_intersection_height = screw_ball_intersection.shared_edges(
        ball.bodies[0].faces[0], tmp.side)[0].brep.pointOnEdge.z

    ball_flattener = Box(ball.size().x, ball.size().y, screw_ball_intersection_height - ball.min().z)
    ball_flattener.place(~ball_flattener == ~ball,
                         ~ball_flattener == ~ball,
                         +ball_flattener == +ball)
    flat_ball = Intersection(ball, ball_flattener)

    screw = Cylinder(screw_length - neck_length, screw_radius)

    screw_neck = Cylinder(neck_length, neck_lower_radius, neck_upper_radius)
    screw_neck.place(~screw_neck == ~screw,
                     ~screw_neck == ~screw,
                     -screw_neck == +screw)

    flat_ball.place(~flat_ball == ~screw,
                    ~flat_ball == ~screw,
                    -flat_ball == +screw_neck)

    screw = Threads(screw, ((0, 0), (.95, .95), (0, .95)), 1.0)

    return Union(screw, screw_neck, flat_ball, name=name)


def ballscrew_cap():
    ball = ball_socket_ball()

    ball_radius = ball.size().x / 2

    hexagon_width = ball_radius + 2.5

    base_polygon = RegularPolygon(6, hexagon_width, is_outer_radius=False)
    base = Extrude(base_polygon, ball.size().x * .8 - .3)

    screw_cavity = Cylinder(ball_radius * .8, ball_radius + 1 + .1)
    screw_cavity.place(~screw_cavity == ~base,
                       ~screw_cavity == ~base,
                       +screw_cavity == +base)

    base = Difference(base, screw_cavity)

    base = Threads(base, ((0, 0), (.99, .99), (0, .99)), 1.0, reverse_axis=True)

    ball.place(~ball == ~base,
               ~ball == ~base,
               (~ball == -screw_cavity) + .8)

    remaining_ball_height = ball_radius - ball.mid().z
    extension_height = remaining_ball_height + 1
    base = Extrude(base.find_faces(base_polygon), extension_height)

    bottom_face = None
    for face in base.end_faces:
        if face.mid().z < 0:
            bottom_face = face
            break

    base = Chamfer(base.shared_edges(base.side_faces, bottom_face), extension_height)

    bottom_face = base.find_faces(bottom_face)[0]

    base = Fillet(base.shared_edges(bottom_face.connected_faces, bottom_face.connected_faces), hexagon_width)

    base = Difference(base, ball)

    return base


def ballscrew_base(screw_length, name):
    screw_length = screw_length - 2
    magnet = vertical_large_thin_magnet_cutout()

    base_polygon = RegularPolygon(6, 5, is_outer_radius=False)
    base = Extrude(base_polygon, screw_length + magnet.size().z)

    magnet.place(~magnet == ~base,
                 ~magnet == ~base,
                 +magnet == +base)

    screw_hole = Cylinder(screw_length, 1.65)
    screw_hole.place(~screw_hole == ~base,
                     ~screw_hole == ~base,
                     -screw_hole == -base)

    base = Difference(base, magnet, screw_hole)
    return Threads(base, ((0, 0), (.99, .99), (0, .99)), 1, reverse_axis=True, name=name)


def thin_ballscrew_base(screw_length, name):
    screw_length = screw_length - 2
    magnet = vertical_large_thin_magnet_cutout()

    base_polygon = RegularPolygon(6, 5, is_outer_radius=False)
    base = Extrude(base_polygon, screw_length + magnet.size().z)

    magnet.place(~magnet == ~base,
                 ~magnet == ~base,
                 +magnet == +base)

    screw_hole = Cylinder(screw_length, 1.6)
    screw_hole.place(~screw_hole == ~base,
                     ~screw_hole == ~base,
                     -screw_hole == -base)

    base = Difference(base, magnet, screw_hole)
    return Threads(base, ((0, 0), (.99, .99), (0, .99)), 1, reverse_axis=True, name=name)


def thumb_base(mirrored=False):
    base = Box(44 - .55 - 1.05, 44.5, 2)

    key_stand_lower = Box(15, 2.2, 3)
    key_stand_lower.place((-key_stand_lower == -base) + 11.45,
                          (-key_stand_lower == -base) + 11.3,
                          -key_stand_lower == +base)

    key_stand_transition_top = Rect(15, 1.8)
    key_stand_transition_top.place(~key_stand_transition_top == ~key_stand_lower,
                                   -key_stand_transition_top == -key_stand_lower,
                                   (~key_stand_transition_top == +key_stand_lower) + 1)
    key_stand_transition = Loft(BRepComponent(key_stand_lower.top.brep), key_stand_transition_top)
    key_stand_upper = Box(15, 1.8, 4 + 1.8/2)
    key_stand_upper.place(~key_stand_upper == ~key_stand_lower,
                          -key_stand_upper == -key_stand_lower,
                          -key_stand_upper == +key_stand_transition)
    key_stand_upper = Fillet(key_stand_upper.shared_edges(
        key_stand_upper.top,
        [key_stand_upper.front, key_stand_upper.back]),
        key_stand_upper.size().y/2)

    magnet = horizontal_magnet_cutout(1.8)
    magnet.place(~magnet == ~key_stand_lower,
                 -magnet == -key_stand_lower,
                 (-magnet == +base) + 1)

    mid_key_stop = Box(15, 3, 5.1)
    mid_key_stop.place(~mid_key_stop == ~key_stand_lower,
                       (~mid_key_stop == +key_stand_lower) + 23,
                       -mid_key_stop == +base)

    mid_pt_base = Box(5, 5.9, 5.1)
    pt_cavity = make_pt_cavity()
    if mirrored:
        mid_pt_base.place((-mid_pt_base == ~key_stand_lower) + 1.5,
                          (~mid_pt_base == +key_stand_lower) + 9,
                          -mid_pt_base == +base)
        pt_cavity.rz(180)
    else:
        mid_pt_base.place((+mid_pt_base == ~key_stand_lower) - 1.5,
                          (~mid_pt_base == +key_stand_lower) + 9,
                          -mid_pt_base == +base)
    pt_cavity.place(~pt_cavity.named_point("lens_center") == ~mid_pt_base,
                    ~pt_cavity.named_point("lens_center") == ~mid_pt_base,
                    (~pt_cavity.named_point("lens_center") == +mid_pt_base) - 1.8)
    extruded_pt_cavity = ExtrudeTo(pt_cavity.named_faces("top"), mid_pt_base)
    extruded_pt_cavity = ExtrudeTo(extruded_pt_cavity.find_faces(pt_cavity.named_faces("lens_hole")), mid_pt_base)
    extruded_pt_cavity = ExtrudeTo(extruded_pt_cavity.find_faces(pt_cavity.named_faces("legs")), base)

    mid_led_base = Box(5.5, 5.9, 5.1)
    led_cavity = make_led_cavity()
    if mirrored:
        mid_led_base.place((+mid_led_base == ~key_stand_lower) - 1.5,
                           (~mid_led_base == ~mid_pt_base),
                           -mid_led_base == +base)
        led_cavity.rz(180)
    else:
        mid_led_base.place((-mid_led_base == ~key_stand_lower) + 1.5,
                           (~mid_led_base == ~mid_pt_base),
                           -mid_led_base == +base)
    led_cavity.place(~led_cavity.named_point("lens_center") == ~mid_led_base,
                     ~led_cavity.named_point("lens_center") == ~mid_led_base,
                     ~led_cavity.named_point("lens_center") == pt_cavity.named_point("lens_center").point)
    extruded_led_cavity = ExtrudeTo(led_cavity.named_faces("top"), mid_led_base)
    extruded_led_cavity = ExtrudeTo(extruded_led_cavity.find_faces(led_cavity.named_faces("lens_hole")), mid_led_base)
    extruded_led_cavity = ExtrudeTo(extruded_led_cavity.find_faces(led_cavity.named_faces("legs")), base.bottom)

    upper_outer_base = vertical_key_base(
        base.size().z, extra_height=4, pressed_key_angle=7, mirrored=not mirrored)
    upper_outer_base_negatives = upper_outer_base.find_children("negatives")[0]
    upper_outer_base.rz(-90)

    upper_outer_base.place((-upper_outer_base == -base),
                           (+upper_outer_base == +base) - 2.5,
                           -upper_outer_base == -base)

    lower_outer_base = vertical_key_base(
        base.size().z, extra_height=4, pressed_key_angle=4.2, mirrored=not mirrored)
    lower_outer_base_negatives = lower_outer_base.find_children("negatives")[0]
    lower_outer_base.rz(-90)
    lower_outer_base.place(-lower_outer_base == -upper_outer_base,
                           (-lower_outer_base == -base),
                           -lower_outer_base == -upper_outer_base)

    inner_base = vertical_key_base(
        base.size().z, extra_height=4, pressed_key_angle=7, mirrored=not mirrored)
    inner_base_negatives = inner_base.find_children("negatives")[0]
    inner_base.rz(90 + 20)
    inner_base.place((+inner_base == +base) - .1,
                     +inner_base == +base,
                     -inner_base == -base)

    upper_base = vertical_key_base(
        base.size().z, extra_height=4, pressed_key_angle=7, mirrored=not mirrored)
    upper_base_negatives = upper_base.find_children("negatives")[0]
    upper_base.rz(90)
    upper_base.place((+upper_base == +base),
                     (-upper_base == -base) + 11,
                     -upper_base == -base)

    lower_ball_socket = ball_socket_base(2, mirrored)
    lower_ball_socket_negatives = lower_ball_socket.find_children("negatives")[0]
    lower_ball_socket.place(~lower_ball_socket == (upper_base.min().x + key_stand_lower.max().x) / 2,
                            -lower_ball_socket == -base,
                            -lower_ball_socket == +base)

    upper_ball_socket = ball_socket_base(2, mirrored)
    upper_ball_socket_negatives = upper_ball_socket.find_children("negatives")[0]
    upper_ball_socket.place(~upper_ball_socket == ~mid_key_stop,
                            (~upper_ball_socket == +mid_key_stop) + 7,
                            -upper_ball_socket == +base)
    upper_ball_socket_base = Cylinder(base.size().z, upper_ball_socket.size().y/2)
    upper_ball_socket_base.place(~upper_ball_socket_base == ~upper_ball_socket,
                                 ~upper_ball_socket_base == ~upper_ball_socket,
                                 -upper_ball_socket_base == -base)

    extension_point_finder = Box(1, 100, 2)
    extension_point = extension_point_finder.rz(-45, center=extension_point_finder.max()).closest_points(
        upper_ball_socket_base)[1]
    extension_point2 = Point3D.create(2 * upper_ball_socket_base.mid().x - extension_point.x,
                                      extension_point.y,
                                      extension_point.z)
    upper_extension_face = Rect(extension_point2.x - extension_point.x, base.size().z).rx(90)
    upper_extension_face.place(~upper_extension_face == ~upper_ball_socket_base,
                               ~upper_extension_face == extension_point.y,
                               -upper_extension_face == -base)
    upper_extension_face2 = Rect(extension_point2.x - extension_point.x + (extension_point.y - base.max().y) * 2,
                                 base.size().z)
    upper_extension_face2.rx(90)
    upper_extension_face2.place(~upper_extension_face2 == ~upper_ball_socket_base,
                                (~upper_extension_face2 == +base),
                                -upper_extension_face2 == -base)
    upper_extension = Loft(upper_extension_face, upper_extension_face2)

    side_ball_socket = ball_socket_base(2, mirrored)
    side_ball_socket_negatives = side_ball_socket.find_children("negatives")[0]

    upper_circle = Cylinder(1, 7)
    upper_circle.place(~upper_circle == upper_outer_base.min(),
                       ~upper_circle == upper_outer_base.min(),
                       ~upper_circle == -base)
    lower_circle = Cylinder(1, 7)
    lower_circle.place(~lower_circle == lower_outer_base.min(),
                       ~lower_circle == lower_outer_base.max(),
                       ~lower_circle == -base)

    side_ball_socket_placement = Intersection(upper_circle, lower_circle)
    side_ball_socket_center = None
    for edge in side_ball_socket_placement.shared_edges(upper_circle.side, lower_circle.side):
        if edge.brep.pointOnEdge.x < upper_outer_base.min().x:
            side_ball_socket_center = edge.brep.pointOnEdge

    side_ball_socket.place(~side_ball_socket == side_ball_socket_center,
                           ~side_ball_socket == side_ball_socket_center,
                           -side_ball_socket == +base)
    side_ball_socket_base = Cylinder(base.size().z, side_ball_socket.size().x/2)
    side_ball_socket_base.place(~side_ball_socket_base == ~side_ball_socket,
                                ~side_ball_socket_base == ~side_ball_socket,
                                -side_ball_socket_base == -base)

    extension_point = Box(1, 100, 2).rz(45).closest_points(side_ball_socket_base)[1]
    extension_point2 = Point3D.create(extension_point.x,
                                      2 * side_ball_socket_base.mid().y - extension_point.y,
                                      extension_point.z)

    side_extension_face = Rect(extension_point2.y - extension_point.y, base.size().z).rx(90).rz(90)
    side_extension_face.place(~side_extension_face == extension_point.x,
                              ~side_extension_face == ~side_ball_socket_base,
                              -side_extension_face == -base)
    side_extension_face2 = Rect(extension_point2.y - extension_point.y + (base.min().x - extension_point.x) * 2,
                                base.size().z)
    side_extension_face2.rx(90).rz(90)
    side_extension_face2.place((~side_extension_face2 == -base),
                               ~side_extension_face2 == ~side_ball_socket_base,
                               -side_extension_face2 == -base)
    side_extension = Loft(side_extension_face, side_extension_face2)

    lower_ball_socket_circle = Circle(lower_ball_socket.size().x/2)
    lower_ball_socket_circle.place(~lower_ball_socket_circle == ~lower_ball_socket,
                                   ~lower_ball_socket_circle == ~lower_ball_socket,
                                   ~lower_ball_socket_circle == +base)
    upper_base_corner = Point3D.create(
        upper_base.max().x,
        upper_base.min().y,
        base.max().z)

    lower_ball_socket_tangents = find_tangent_intersection_on_circle(lower_ball_socket_circle, upper_base_corner)
    if lower_ball_socket_tangents[0].geometry.x > lower_ball_socket_tangents[1].geometry.x:
        lower_ball_socket_tangent = lower_ball_socket_tangents[0].geometry
    else:
        lower_ball_socket_tangent = lower_ball_socket_tangents[1].geometry

    tangent_vector = upper_base_corner.vectorTo(lower_ball_socket_tangent)
    tangent_vector.scaleBy(2)
    tangent_line_corner = upper_base_corner.copy()
    tangent_line_corner.translateBy(tangent_vector)
    lower_cut_corner = Polygon(
        upper_base_corner, tangent_line_corner, Point3D.create(base.max().x, base.min().y, base.max().z))
    lower_cut_corner = ExtrudeTo(lower_cut_corner, base.bottom)

    upper_cut_corner = Box(100, 100, 100).rz(20)
    upper_cut_corner.place(-upper_cut_corner == +base,
                           ~upper_cut_corner == +base,
                           -upper_cut_corner == -base)
    upper_cut_corner.align_to(inner_base, Vector3D.create(-1, 0, 0))

    result = Difference(
        Union(
            base, key_stand_lower, key_stand_transition, key_stand_upper, mid_key_stop, mid_pt_base, mid_led_base,
            upper_outer_base, lower_outer_base, inner_base, upper_base, lower_ball_socket, upper_ball_socket,
            upper_extension, upper_ball_socket_base, side_ball_socket, side_extension, side_ball_socket_base),
        magnet, extruded_pt_cavity, extruded_led_cavity, upper_outer_base_negatives, lower_outer_base_negatives,
        inner_base_negatives, upper_base_negatives, lower_ball_socket_negatives, upper_ball_socket_negatives,
        side_ball_socket_negatives, lower_cut_corner, upper_cut_corner)

    result = SplitFace(result, base.bottom, name="left_thumb_cluster" if mirrored else "right_thumb_cluster")
    result.add_named_faces("bottom", *result.find_faces(base.bottom))

    return result


def thumb_pcb(thumb_base: Component):
    bottom = thumb_base.named_faces("bottom")[0]
    pcb_thickness = 1.2

    cone_centers = []
    for edge in bottom.brep.edges:
        if ((isinstance(edge.geometry, adsk.core.Circle3D) or isinstance(edge.geometry, adsk.core.Arc3D)) and
                edge.geometry.radius > 1):
            center = edge.geometry.center.asArray()
            if center not in cone_centers:
                cone_centers.append(center)

    standoff_cutouts = []
    for cone_center in cone_centers:
        cone_center = Point3D.create(*cone_center)
        circle = Cylinder(pcb_thickness, 8.2)
        circle.place(~circle == cone_center,
                     ~circle == cone_center,
                     +circle == ~bottom)
        standoff_cutouts.append(circle)
        if cone_center.y - bottom.min().y < 10:
            cutout = Box(8.2*2, 8.2, pcb_thickness)
            cutout.place(~cutout == ~circle,
                         +cutout == cone_center,
                         +cutout == ~bottom)
            standoff_cutouts.append(cutout)
            cutout = Box(bottom.max().x - cone_center.x, 12, pcb_thickness)
            cutout.place(+cutout == +bottom,
                         -cutout == -bottom,
                         +cutout == ~bottom)
            standoff_cutouts.append(cutout)
        elif bottom.max().y - cone_center.y < 5:
            cutout = Box(8.2*2, 8.2, pcb_thickness)
            cutout.place(~cutout == ~circle,
                         -cutout == cone_center,
                         +cutout == ~bottom)
            standoff_cutouts.append(cutout)

    jst_holes = hole_array(.35, 1.5, 7)
    jst_holes.place(~jst_holes == ~bottom,
                    (~jst_holes == +bottom) - 11,
                    ~jst_holes == ~bottom)

    through_holes = hole_array(.35, 2.54, 7)
    through_holes.place(~through_holes == ~jst_holes,
                        (~through_holes == ~jst_holes) - 19,
                        ~jst_holes == ~bottom)

    base = Union(Extrude(BRepComponent(brep().copy(bottom.brep)), 1.2))

    result = Difference(base, *standoff_cutouts, ExtrudeTo(jst_holes, base), ExtrudeTo(through_holes, base),
                        name=thumb_base.name + "_pcb")
    result.add_named_faces("bottom", *result.find_faces(bottom))

    jst_relief = Box(jst_holes.size().x + 2, jst_holes.size().y + 4.5, 1)
    jst_relief.place(~jst_relief == ~jst_holes,
                     (+jst_relief == +jst_holes) + 1.5,
                     -jst_relief == +result)

    through_hole_relief = Box(through_holes.size().x + 3, through_holes.size().y + 4, 1)
    through_hole_relief.place(~through_hole_relief == ~through_holes,
                              (-through_hole_relief == -through_holes) - 1,
                              -through_hole_relief == +result)

    return result, Union(jst_relief, through_hole_relief)


def thumb_pcb_sketch(pcb_bottom, name):
    rects = []
    for edge in pcb_bottom.bodies[0].brep.edges:
        if not isinstance(edge.geometry, adsk.core.Circle3D):
            continue

        if edge.geometry.radius < .4 and pcb_bottom.max().y - edge.geometry.center.y < 12:
            rect_size = (1.25, 1.25)
        else:
            rect_size = (2, 2)

        rect = Rect(*rect_size)
        rect.place(~rect == edge.geometry.center,
                   ~rect == edge.geometry.center,
                   ~rect == edge.geometry.center)
        rects.append(rect)
    split_face = SplitFace(pcb_bottom, Union(*rects), name=name)
    occurrence = split_face.scale(.1, .1, .1).create_occurrence(False)
    sketch = occurrence.component.sketches.add(occurrence.bRepBodies[0].faces[0])
    sketch.name = name
    for face in occurrence.bRepBodies[0].faces:
        sketch.include(face)


def full_thumb(mirrored=False):
    base = thumb_base(mirrored)
    pcb, relief = thumb_pcb(base)

    base = Difference(base, relief, name=base.name)

    prefix = "left_" if mirrored else "right_"

    if mirrored:
        base.scale(-1, 1, 1, center=base.mid())
        pcb.scale(-1, 1, 1, center=base.mid())

    thumb_pcb_sketch(BRepComponent(pcb.named_faces("bottom")[0].brep), name=prefix + "thumb_cluster_pcb_sketch")

    base.create_occurrence(False, .1)
    pcb.create_occurrence(False, .1)


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


def central_pcb_sketch(pcb_bottom):
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


def full_central_pcb():
    pcb = central_pcb()
    pcb.create_occurrence(False, .1)
    central_pcb_sketch(BRepComponent(pcb.named_faces("bottom")[0].brep))

    central_pcb_tray(pcb).create_occurrence(False, .1)


def central_pcb_tray(pcb):
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


def key_breakout_pcb_sketch(pcb_bottom):
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


def full_key_breakout_pcb():
    pcb = key_breakout_pcb()
    pcb.create_occurrence(False, .1)
    key_breakout_pcb_sketch(BRepComponent(pcb.named_faces("bottom")[0].brep))


def handrest(mirrored=False):
    script_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
    script_dir = os.path.dirname(script_path)

    handrest = import_fusion_archive(os.path.join(script_dir, "left_handrest_scan_reduced_brep.f3d"), name="handrest")
    handrest.scale(10, 10, 10)
    handrest.rz(-90)
    handrest.place(~handrest == 0,
                   ~handrest == 0,
                   -handrest == 0)

    pcb = central_pcb()
    pcb_tray = central_pcb_tray(pcb)

    tray_slot = Box(pcb_tray.bounding_box.size().x + .2,
                    pcb_tray.bounding_box.size().y * 10,
                    24)
    tray_slot.place(~tray_slot == ~handrest,
                    (+tray_slot == -handrest) + pcb_tray.bounding_box.size().y + 15,
                    -tray_slot == -handrest)

    back_magnet = Box(3.9, 3.9, 1.8).rx(90)
    back_magnet.place(~back_magnet == ~tray_slot,
                      -back_magnet == +tray_slot,
                      (+back_magnet == -handrest) + 9.2)

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
    front_left_bottom_magnet.place((~front_left_bottom_magnet == ~handrest) + 27.778,
                                   (~front_left_bottom_magnet == ~handrest) - 17.2784,
                                   -front_left_bottom_magnet == -handrest)

    front_right_bottom_magnet = Box(3.6, 6.8, 1.8, name="bottom_magnet")
    front_right_bottom_magnet.place((~front_right_bottom_magnet == ~handrest) - 29.829,
                                    (~front_right_bottom_magnet == ~handrest) - 17.2782,
                                    -front_right_bottom_magnet == -handrest)

    back_right_bottom_magnet = Box(3.6, 6.8, 1.8, name="bottom_magnet")
    back_right_bottom_magnet.place((~back_right_bottom_magnet == ~handrest) - 29.829,
                                   (~back_right_bottom_magnet == ~handrest) + 37.7218,
                                   -back_right_bottom_magnet == -handrest)

    back_left_bottom_magnet = Box(3.6, 6.8, 1.8, name="bottom_magnet")
    back_left_bottom_magnet.place((~back_left_bottom_magnet == ~handrest) + 27.778,
                                  (~back_left_bottom_magnet == ~handrest) + 37.7218,
                                  -back_left_bottom_magnet == -handrest)

    return Difference(handrest, tray_slot, back_magnet, left_magnet, right_magnet, front_left_bottom_magnet,
                      front_right_bottom_magnet, back_right_bottom_magnet, back_left_bottom_magnet,
                      name="right_handrest" if mirrored else "left_handrest")


def design():
    start = time.time()

    # uncomment one of the function calls below to generate the corresponding part(s)

    full_cluster(add_pcb=True, add_pcb_sketch=True, create_children=False)
    # center_key().create_occurrence(False, .1)
    # short_side_key().create_occurrence(False, .1)
    # long_side_key().create_occurrence(True, .1)

    # outer_upper_thumb_key().create_occurrence(False, .1)
    # outer_lower_thumb_key().create_occurrence(False, .1)
    # inner_thumb_key().create_occurrence(False, .1)
    # thumb_mode_key(name="right_thumb_mode_key").create_occurrence(True, .1)
    # thumb_mode_key(mirrored=True, name="left_thumb_mode_key").create_occurrence(True, .1)
    # thumb_down_key().create_occurrence(True, .1)

    # jst_adaptor().create_occurrence(True, .1)
    # ballscrew(7, name="ballscrew_tiny").create_occurrence(True, .1)
    # ballscrew(10, name="ballscrew_short").create_occurrence(True, .1)
    # ballscrew(15, name="ballscrew_tall").create_occurrence(True, .1)
    # ballscrew_cap().create_occurrence(True, .1)
    # ballscrew_base(10, name="ballscrew_base_short").create_occurrence(True, .1)
    # ballscrew_base(15, name="ballscrew_base_tall").create_occurrence(True, .1)
    # thin_ballscrew_base(5, name="ballscrew_base_tiny").create_occurrence(True, .1)

    # full_thumb(mirrored=False)
    # full_thumb(mirrored=True)

    # full_central_pcb()

    # full_key_breakout_pcb()

    # handrest().create_occurrence(False, .1)
    # handrest(mirrored=True).create_occurrence(False, .1)

    end = time.time()
    print(end-start)


def run(_):
    run_design(design, message_box_on_error=False, document_name=__name__)
