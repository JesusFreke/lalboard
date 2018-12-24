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
from fscad import Circle

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

    cavity.add_faces("legs", *cavity.find_faces((leg, leg2)))
    cavity.add_faces("lens_hole", *cavity.find_faces(lens_hole))
    cavity.add_faces("top", *cavity.find_faces((body.top, slot.top)))

    cavity.add_point("lens_center",
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

    extruded_led_cavity = ExtrudeTo(led_cavity.faces("lens_hole"), result.copy(False))
    extruded_led_cavity = ExtrudeTo(
        extruded_led_cavity.find_faces(led_cavity.faces("legs")), result.copy(False))

    extruded_pt_cavity = ExtrudeTo(pt_cavity.faces("lens_hole"), result.copy(False))
    extruded_pt_cavity = ExtrudeTo(extruded_pt_cavity.find_faces(pt_cavity.faces("legs")), result.copy(False))
    extruded_pt_cavity = ExtrudeTo(extruded_pt_cavity.find_faces(pt_cavity.faces("top")), result.copy(False))

    result = Difference(result, extruded_pt_cavity, extruded_led_cavity, magnet_cutout, key_pivot)

    result.add_point("midpoint", (magnet_cutout.mid().x, result.mid().y, result.mid().z))

    return result, Difference(result.bounding_box.make_box(), result.copy(False), name="vertical_key_base_negative")


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

    combined_cluster = Union(base, *key_bases)

    center_floor = Box(1, 1, 1.9, "center_floor")
    center_floor.place(~center_floor == ~base,
                       ~center_floor == ~base,
                       -center_floor == +base)

    for face in (center_floor.left, center_floor.right, center_floor.front, center_floor.back):
        center_floor = ExtrudeTo(center_floor.find_faces(face)[0], combined_cluster.copy(False))

    combined_cluster.add(center_floor)

    center_hole = Cylinder(combined_cluster.size().z, 2.5, name="center_hole")
    center_hole.place(~center_hole == ~base,
                      ~center_hole == ~base,
                      -center_hole == -base)
    flat = Box(center_hole.size().x, center_hole.size().y - .5, center_hole.size().z, "flat")
    flat.place(~flat == ~center_hole,
               -flat == -center_hole,
               ~flat == ~center_hole)
    center_hole = Intersection(center_hole, flat)

    central_magnet_riser = Box(4.55, .1, combined_cluster.max().z - center_floor.max().z, "central_magnet_riser")
    central_magnet_riser.place(~central_magnet_riser == ~base,
                               -central_magnet_riser == +center_hole,
                               -central_magnet_riser == +center_floor)
    central_magnet_riser = ExtrudeTo(central_magnet_riser.back, combined_cluster.copy(False))

    central_magnet_cutout = horizontal_magnet_cutout(name="central_magnet_cutout")
    central_magnet_cutout.place(~central_magnet_cutout == ~central_magnet_riser,
                                -central_magnet_cutout == -central_magnet_riser,
                                (+central_magnet_cutout == +central_magnet_riser) - .8)

    combined_cluster.add(central_magnet_riser)

    # TODO: is there a better way to find the desired children?
    bottom_cavity = key_base_negatives[0]
    left_cavity = key_base_negatives[3]
    right_cavity = key_base_negatives[1]

    central_led_cavity = make_led_cavity().scale(-1, 1, 1)
    central_led_cavity.place(-central_led_cavity == -center_floor,
                             -central_led_cavity == -center_floor,
                             (~central_led_cavity.point("lens_center") == +center_floor) + 1.6)
    central_led_cavity.align_to(left_cavity.bodies[0], Vector3D.create(-1, 0, 0))
    central_led_cavity.align_to(bottom_cavity.bodies[0], Vector3D.create(0, -1, 0))

    central_pt_cavity = make_pt_cavity().scale(-1, 1, 1)
    central_pt_cavity.place(+central_pt_cavity == +center_floor,
                            -central_pt_cavity == -center_floor,
                            (~central_pt_cavity.point("lens_center") == +center_floor) + 1.6)
    central_pt_cavity.align_to(right_cavity.bodies[0], Vector3D.create(1, 0, 0))
    central_pt_cavity.align_to(bottom_cavity.bodies[0], Vector3D.create(0, -1, 0))

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

    extruded_led_cavity = ExtrudeTo(central_led_cavity.faces("lens_hole"), combined_cluster.copy(False))
    extruded_led_cavity = ExtrudeTo(extruded_led_cavity.find_faces(central_led_cavity.faces("legs")),
                                    combined_cluster.copy(False))
    extruded_led_cavity = ExtrudeTo(extruded_led_cavity.find_faces(central_led_cavity.faces("top")),
                                    combined_cluster.copy(False))

    extruded_pt_cavity = ExtrudeTo(central_pt_cavity.faces("lens_hole"), combined_cluster.copy(False))
    extruded_pt_cavity = ExtrudeTo(extruded_pt_cavity.find_faces(central_pt_cavity.faces("legs")),
                                   combined_cluster.copy(False))
    extruded_pt_cavity = ExtrudeTo(extruded_pt_cavity.find_faces(central_pt_cavity.faces("top")),
                                   combined_cluster.copy(False))

    return Difference(combined_cluster, *key_base_negatives, center_hole, central_magnet_cutout,
                      extruded_led_cavity, extruded_pt_cavity)


def cluster_pcb(cluster):
    center = Circle(5)
    center.place(~center == ~cluster,
                 ~center == ~cluster,
                 ~center == -cluster)

    bottom = cluster.find_faces(center)[0]

    base = Extrude(Union(BRepComponent(bottom.brep), center).bodies[0].faces[0], 2)

    base_extension = Box(base.size().x, 6, base.size().z)
    base_extension.place(~base_extension == ~base,
                         -base_extension == +base,
                         -base_extension == -base)

    connector_holes = hole_array(.4, 1.5, 7)
    connector_holes.place(~connector_holes == ~base_extension,
                          (~connector_holes == +base_extension) - 1.3,
                          ~connector_holes == +base_extension)
    extension_holes = ExtrudeTo(connector_holes, base_extension.bottom)

    through_holes = hole_array(.4, 1.5, 7)
    through_holes.place(~through_holes == ~base_extension,
                        (-through_holes == ~connector_holes) - 1.3-2.2,
                        ~through_holes == +base_extension)
    through_holes = ExtrudeTo(through_holes, base_extension.bottom)

    base_extension = Difference(base_extension, extension_holes, through_holes)

    base = Union(base, base_extension)
    base.add_faces("bottom", *base.find_faces(bottom))
    return base


def cluster_pcb_sketch(cluster_pcb_bottom: Component):
    rects = []
    for edge in cluster_pcb_bottom.bodies[0].brep.edges:
        if not isinstance(edge.geometry, adsk.core.Circle3D):
            continue

        if cluster_pcb_bottom.max().y - edge.geometry.center.y < 5:
            rect_size = 1.25
        else:
            rect_size = 2

        rect = Rect(rect_size, rect_size)
        rect.place(~rect == edge.geometry.center,
                   ~rect == edge.geometry.center,
                   ~rect == edge.geometry.center)
        rects.append(rect)
    split_face = SplitFace(cluster_pcb_bottom, Union(*rects))
    occurrence = split_face.scale(.1, .1, .1).create_occurrence(False)
    sketch = occurrence.component.sketches.add(occurrence.bRepBodies[0].faces[0])
    for face in occurrence.bRepBodies[0].faces:
        sketch.include(face)


def extended_cluster():
    base_cluster = cluster()


def ball_socket_ball():
    return Sphere(3, "ball")


def ball_socket_base(base_height):

    pin_hole_radius = 2.4

    ball = ball_socket_ball()
    ball_radius = ball.size().x / 2

    # the radio of the total diameter of the ball to sink into the base. The size of the hole for the downwards-facing
    # pin is determined by the intersection of the top of the base with the sphere, so sinking the ball lower results
    # in a larger opening and more range of motion for the pin, but also a shorter standoff
    ball_sink_ratio = .05

    # tall enough to reach the middle of the ball
    base = Cylinder(
        ball_radius - (ball_radius * 2 * ball_sink_ratio), ball_radius + .8, name="ball_socket_base")
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

    return base, Union(ball_socket_opening, ball)


def find_tangent_intersection_on_circle(circle: Circle, point: Point3D):
    left_point_to_mid = point.vectorTo(circle.mid())
    left_point_to_mid.scaleBy(.5)
    point.translateBy(left_point_to_mid)
    intersecting_circle = Circle(left_point_to_mid.length)
    intersecting_circle.place(~intersecting_circle == point,
                              ~intersecting_circle == point,
                              ~intersecting_circle == point)

    vertices = list(Intersection(circle, intersecting_circle).bodies[0].brep.vertices)
    return vertices


def cluster_front(cluster: Component, base_height):
    extension_y_size = 13

    socket_base, opening = ball_socket_base(2)

    opening.place(~socket_base == ~cluster,
                  (~socket_base == -cluster) - extension_y_size / 2)

    socket_base.place(~socket_base == ~cluster,
                      (~socket_base == -cluster) - extension_y_size / 2)

    socket_base_circle = Circle(socket_base.size().x/2)
    socket_base_circle.place(~socket_base_circle == ~socket_base,
                             ~socket_base_circle == ~socket_base)
    left_point = Point3D.create(cluster.min().x, cluster.min().y, 0)
    left_tangents = find_tangent_intersection_on_circle(socket_base_circle, left_point)
    if left_tangents[0].geometry.x < left_tangents[1].geometry.x:
        left_tangent_point = left_tangents[0].geometry
    else:
        left_tangent_point = left_tangents[1].geometry

    right_tangent_point = Point3D.create(cluster.mid().x + (cluster.mid().x - left_tangent_point.x),
                                         left_tangent_point.y, left_tangent_point.z)

    base = Polygon((cluster.min().x, cluster.min().y),
                   left_tangent_point, right_tangent_point,
                   (cluster.max().x, cluster.min().y))

    base = Extrude(base, base_height)
    rounded_end = Cylinder(base_height, socket_base.size().x/2, name="rounded_end")
    rounded_end.place(~rounded_end == ~socket_base,
                      ~rounded_end == ~socket_base,
                      -rounded_end == -base)
    base = Union(base, rounded_end)

    base.place(~base == ~cluster,
               +base == -cluster,
               -base == -cluster)

    opening.place(z=-socket_base == +base)
    socket_base.place(z=-socket_base == +base)

    return Difference(Union(base, socket_base), opening)


def cluster_back(cluster: Component, pcb: Component, base_height: float):
    # TODO: use a fillet to round off the outer corners
    # TODO: we may need to push out the sockets a bit more, so the lower base can screw in all the way, without hitting
    # the pcb. On the other hand, the back is most likely going to be higher than the front, so maybe not a problem.
    base = Box(cluster.size().x, 15, base_height)
    base.place(~base == ~cluster,
               -base == +cluster,
               -base == -cluster)

    socket_base, opening = ball_socket_base(2)
    opening.place(-socket_base == -cluster,
                  +socket_base == +base,
                  -socket_base == +base)
    socket_base.place(-socket_base == -cluster,
                      +socket_base == +base,
                      -socket_base == +base)

    other_socket_base = socket_base.copy()
    other_opening = opening.copy()
    other_opening.place(+other_socket_base == +cluster)
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


def pcb_holder(pcb) -> Component:
    holder = Box(pcb.size().x + 10.2, pcb.size().y + 10.2, pcb.size().z)
    holder.place(~holder == ~pcb,
                 ~holder == ~pcb,
                 ~holder == ~pcb)

    pcb_outline = Box(pcb.size().x + .2, pcb.size().y + .2, pcb.size().z)
    pcb_outline.place(~pcb_outline == ~holder,
                      ~pcb_outline == ~holder,
                      ~pcb_outline == ~holder)
    return Difference(holder, pcb_outline)


def center_key():
    size = 6.1 * 2
    key_radius = 7.5
    key_thickness = 2.5
    post_length = 8.4
    post_radius = 2.3

    key = Cylinder(key_thickness, key_radius, name="key")
    post = Cylinder(post_length, post_radius, name="post")
    post.place(~post == ~key,
               ~post == ~key,
               -post == +key)

    back_stop = Box(3.5, 5.7, 4, name="back_stop")
    back_stop.place(~back_stop == ~key,
                    -back_stop == ~key,
                    -back_stop == +key)

    side_stop_start = Box(5.9, 3, 4, name="side_stop_start")
    side_stop_start.place(-side_stop_start == ~key,
                          ~side_stop_start == ~key,
                          -side_stop_start == +key)

    side_stop_end = Box(3.4, 5.9, 4, name="side_stop_end")
    side_stop_end.place(+side_stop_end == +side_stop_start,
                        +side_stop_end == ~key,
                        -side_stop_end == -side_stop_start)

    side_stop = Union(side_stop_start, side_stop_end, name="side_stop")
    other_side_stop = side_stop.copy(False)
    other_side_stop.scale(-1, 1, 1, center=key.mid())

    post_flat_face_right = Rect(post_length, key_radius).ry(90)
    post_flat_face_right.place(~post_flat_face_right == ~post,
                               +post_flat_face_right == -2,
                               -post_flat_face_right == +key)
    post_flat_face_right.align_to(side_stop, Vector3D.create(1, 0, 0))

    post_flat_face_left = post_flat_face_right.copy()
    post_flat_face_left.align_to(other_side_stop, Vector3D.create(-1, 0, 0))

    post_flat_face = Loft(post_flat_face_left, post_flat_face_right, name="post_flat_face")

    magnet = horizontal_magnet_cutout(1.8)
    magnet.place(~magnet == ~post,
                 -magnet == +post_flat_face,
                 (~magnet == +post) - 4.2)

    result = Difference(Union(key, post, back_stop, side_stop, other_side_stop),
                        post_flat_face, magnet)

    bounding_cylinder = Cylinder(post.max().z - key.min().z, key_radius)
    bounding_cylinder.place(~bounding_cylinder == ~result,
                            ~bounding_cylinder == ~result,
                            -bounding_cylinder == -result)
    return Intersection(result, bounding_cylinder)


def _design():
    start = time.time()

    #base, diff = vertical_key_base(2)
    #Difference(base, diff).create_occurrence(True, scale=.1)

    clust = cluster()
    clust.rz(180, center=clust.mid())


    #clust.create_occurrence(True, scale=.1)
    pcb = cluster_pcb(clust)
    #pcb.create_occurrence(False, scale=.1)

    cluster_pcb_sketch(BRepComponent(pcb.faces("bottom")[0].brep))

    clust = Union(clust, cluster_front(clust, 2))

    back, pcb_relief = cluster_back(clust, pcb, 2)

    Difference(Union(clust, back), pcb_relief).create_occurrence(False, scale=.1)

    end = time.time()
    print(end-start)


def run(_):
    run_design(_design, message_box_on_error=False, document_name=__name__)
