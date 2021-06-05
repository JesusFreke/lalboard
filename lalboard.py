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

import inspect
import math
import os
import pathlib
from typing import Optional, Sequence, Tuple

import adsk.core
import adsk.fusion
from adsk.core import Matrix3D, Point3D, Vector3D

import fscad.fscad
from fscad.fscad import *
from fscad.fscad import Component

key_thickness = 1.8
post_width = 7.3


# noinspection PyMethodMayBeStatic
class Lalboard(MemoizableDesign):

    def small_pin(self):
        return Circle(.4, name="small_pin")

    def tapered_box(self, bottom_x, bottom_y, top_x, top_y, height, name):
        bottom_face = Rect(bottom_x, bottom_y, "tapered_box_bottom")
        top_face = Rect(top_x, top_y, "tapered_box_top")
        top_face.place(~top_face == ~bottom_face,
                       ~top_face == ~bottom_face,
                       ~top_face == height)
        return Loft(bottom_face, top_face, name=name)

    def horizontal_rotated_magnet_cutout(self, depth=1.8, name="magnet_cutout"):
        result = self.tapered_box(1.45, 1.45, 1.7, 1.7, depth, name=name).rx(90).ry(45)
        result.add_named_faces("front", result.top)
        return result

    def horizontal_magnet_cutout(self, depth=1.8, name="magnet_cutout"):
        return self.tapered_box(1.45, 1.8, 1.7, 1.8, depth, name=name).rx(90)

    def horizontal_tiny_magnet_cutout(self, depth=1.3, name="magnet_cutout"):
        return self.tapered_box(.9, 1.2, 1.1, 1.2, depth, name=name).rx(90)

    def horizontal_large_thin_magnet_cutout(self, depth=1.8, name="magnet_cutout"):
        return self.tapered_box(1.45*2, 1.8*2, 1.7*2, 1.8*2, depth, name=name).rx(90)

    def vertical_magnet_cutout(self, depth=1.6, name="magnet_cutout"):
        return self.tapered_box(1.55, 1.55, 1.7, 1.7, depth, name)

    def vertical_rotated_magnet_cutout(self, depth=1.6, name="magnet_cutout"):
        result = self.tapered_box(1.7, 1.7, 1.8, 1.8, depth, name).rz(45)
        result.add_named_faces("front", result.top)
        return result

    def vertical_large_magnet_cutout(self, name="magnet_cutout"):
        base = Box(2.9, 2.9, 2, name=name + "_base")
        taper = self.tapered_box(2.9, 2.9, 3.1, 3.1, 1.3, name=name + "_taper")
        taper.place(~taper == ~base,
                    ~taper == ~base,
                    -taper == +base)
        return Union(base, taper, name=name)

    def deep_large_thin_magnet_cutout(self, name="magnet_cutout", depth=2.375, bottom_flare=.4):
        """The cutout for a magnet that is inserted deeper than the surface of the part.

        This can be used in conjuction with a magnet sticking out a bit on the mating part. That magnet will insert
        into the remaining part of the hole for this magnet. This holds the part down magnetically, and keeps it
        from sliding around due to the mechanical constraint of the magnet inserted into the hole.
        """

        # Add a flare to the bottom of the hole, to avoid glue from squeezing out above the magnet
        lower_taper = self.tapered_box(
            3.35 + bottom_flare, 3.35 + bottom_flare, 3.35, 3.35,
            height=.8, name=name + "_taper")

        base = Box(3.35, 3.35, depth - .8, name=name + "_base")
        base.place(
            ~base == ~lower_taper,
            ~base == ~lower_taper,
            -base == +lower_taper)
        return Union(lower_taper, base, name=name)


    def vertical_large_thin_magnet_cutout(self, name="magnet_cutout", depth=1.8, taper=.15):
        upper_taper = self.tapered_box(3.35, 3.35, 3.35 + taper, 3.35 + taper, min(.7, depth), name=name + "_taper")

        if depth > .7:
            base = Box(3.35, 3.35, depth - upper_taper.size().z, name=name + "_base")
            upper_taper.place(~upper_taper == ~base,
                              ~upper_taper == ~base,
                              -upper_taper == +base)
            return Union(base, upper_taper, name=name)
        else:
            return Union(upper_taper, name=name)

    def vertical_large_thin_double_magnet_cutout(self, extra_depth=0.0, name="magnet_cutout"):
        base = Box(3.1*2, 3.1, 1 + extra_depth, name=name + "_base")
        taper = self.tapered_box(3.1*2, 3.1, 3.25*2, 3.2, .7, name=name + "_taper")
        taper.place(~taper == ~base,
                    ~taper == ~base,
                    -taper == +base)
        return Union(base, taper, name=name)

    def make_bottom_entry_led_cavity(self, name="led_cavity"):
        lens_height = 4.5
        lens_radius = .75

        body = Box(1.8, 5, 5.8, "body")

        lens_hole = Circle(lens_radius, name="lens_hole")
        lens_hole.ry(90).place(-lens_hole == +body, ~lens_hole == ~body, ~lens_hole == lens_height)
        lens_slot = Box(lens_radius + .05 - .275, lens_radius * 2 + .1, lens_hole.max().z - body.min().z, "lens_slot")
        lens_slot.place(-lens_slot == +body, ~lens_slot == ~body, +lens_slot == +lens_hole)
        lens_hole.place(~lens_hole == +lens_slot)

        cavity = Union(body, lens_slot)
        cavity = SplitFace(cavity, lens_hole, name=name)

        leg = self.small_pin()
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

    def hole_array(self, radius, pitch, count):
        hole = Circle(radius)
        holes = []
        for i in range(0, count):
            holes.append(hole.copy().tx(pitch * i))
        return Union(*holes)

    def retaining_ridge_design(self, pressed_key_angle, length):
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

    @MemoizableDesign.MemoizeComponent
    def vertical_key_base(self, extra_height=0.0, pressed_key_angle=12.5, extra_optical_width=0.55,
                          fillet_back_keywell_corners=False, fillet_front_keywell_corners=False, name=None):
        post_hole_width = post_width + .3

        key_well = Box(
            post_hole_width + .525*2,
            4.75,
            8.0 + extra_height, "key_well")

        filleted_edges = []
        if fillet_back_keywell_corners:
            filleted_edges.extend(key_well.shared_edges(key_well.back, [key_well.left, key_well.right]))
        if fillet_front_keywell_corners:
            filleted_edges.extend(key_well.shared_edges(key_well.front, [key_well.left, key_well.right]))
        if filleted_edges:
            key_well = Fillet(filleted_edges, .8)

        pt_cavity = self.make_bottom_entry_led_cavity(name="pt_cavity")
        led_cavity = self.make_bottom_entry_led_cavity(name="led_cavity")

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

        key_pivot = Cylinder(post_hole_width, 1, name="key_pivot").ry(90)
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

        retaining_ridge = self.retaining_ridge_design(pressed_key_angle, post_hole_width)

        sloped_key_front = sloped_key.find_children("sloped_key")[0].front

        retaining_ridge.place(~retaining_ridge == ~key_well,
                              (+retaining_ridge == -key_pivot) - .05,
                              +retaining_ridge == +upper_base)

        retaining_ridge.align_to(sloped_key_front, Vector3D.create(0, 0, -1))

        sloped_key = Difference(sloped_key, retaining_ridge)

        result = Union(key_well, upper_base)
        result = Difference(result, sloped_key, straight_key)

        magnet_cutout = self.horizontal_rotated_magnet_cutout()
        magnet_cutout.place(~magnet_cutout == ~key_well,
                            -magnet_cutout == +straight_key,
                            (+magnet_cutout == +key_well) - .4)

        extruded_led_cavity = ExtrudeTo(led_cavity.named_faces("lens_hole"), result.copy(False))
        extruded_pt_cavity = ExtrudeTo(pt_cavity.named_faces("lens_hole"), result.copy(False))

        negatives = Union(
            extruded_pt_cavity, extruded_led_cavity, magnet_cutout, straight_key, sloped_key, pivot_vee, name="negatives")

        result = Difference(result, negatives,  name=name or "vertical_key_base")

        return result

    @MemoizableDesign.MemoizeComponent
    def cluster_design(self):
        """
        The design for the individual finger clusters, including front and back extensions.
        """

        base_cluster = self.base_cluster_design()

        base_cluster, front = self.cluster_front(base_cluster)
        back = self.cluster_back(base_cluster)

        _, connector_legs_cutout = self.cluster_pcb(base_cluster, front, back)

        return Difference(
            Union(base_cluster, front, back),
            connector_legs_cutout,
            name="cluster")

    @MemoizableDesign.MemoizeComponent
    def cluster_silhouette(self):
        cluster = self.cluster_design()

        cluster_back = cluster.find_children("cluster_back")[0]

        silhouette = Silhouette(
            cluster,
            adsk.core.Plane.create(Point3D.create(0, 0, 0), Vector3D.create(0, 0, 1)),
            name="cluster_silhouette")
        silhouette.place(z=~silhouette == -cluster_back)

        # The silhouette seems to have some extraneous vertices, which cause the bounding box to be larger than
        # expected. This removes the extraneous stuff, leaving on the single face geometry
        return silhouette.faces[0].make_component(name="cluster_silhouette")

    def base_cluster_design(self):
        """
        The design of the main part of a cluster, not including the front or back extensions.
        """
        temp_key_base = self.vertical_key_base()
        temp_key_base_upper = temp_key_base.find_children("upper_base")[0]
        base = Box(24.9, 24.9, temp_key_base_upper.size().z, "base")

        south_base = self.vertical_key_base(fillet_back_keywell_corners=True, name="south_base")
        south_base.scale(-1, 1, 1)
        south_base.place(~south_base == ~base,
                         -south_base == -base,
                         +south_base == +base)

        west_base = self.vertical_key_base(fillet_back_keywell_corners=True, name="west_base")
        west_base.rz(-90)
        west_base.place(-west_base == -base,
                        ~west_base == ~base,
                        +west_base == +base)

        north_base = self.vertical_key_base(
            extra_optical_width=2.5, fillet_back_keywell_corners=True, fillet_front_keywell_corners=True,
            name="north_base")
        north_base.scale(-1, 1, 1).rz(180)
        north_base.place(
            ~north_base == ~base,
            +north_base == +base,
            +north_base == +base)

        east_base = self.vertical_key_base(fillet_back_keywell_corners=True, name="east_base")
        east_base.rz(90)
        east_base.place(+east_base == +base,
                        ~east_base == ~base,
                        +east_base == +base)

        key_bases = (
            south_base,
            west_base,
            north_base,
            east_base)
        key_base_negatives = (key_base.find_children("negatives")[0] for key_base in key_bases)

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

        central_magnet_cutout = self.horizontal_magnet_cutout(name="central_magnet_cutout")
        central_magnet_cutout.place(~central_magnet_cutout == ~center_hole,
                                    +central_magnet_cutout == -center_hole,
                                    (~central_magnet_cutout == +combined_cluster) - 3.5)

        west_cavity = west_base.find_children("negatives")[0]
        west_pt_cavity = west_cavity.find_children("pt_cavity")[0]
        east_cavity = east_base.find_children("negatives")[0]
        east_led_cavity = east_cavity.find_children("led_cavity")[0]

        central_led_cavity = self.make_bottom_entry_led_cavity(name="led_cavity")
        central_led_cavity.rz(180)
        central_led_cavity.place(+central_led_cavity == -east_led_cavity,
                                 +central_led_cavity == +east_led_cavity,
                                 +central_led_cavity == +east_led_cavity)

        central_pt_cavity = self.make_bottom_entry_led_cavity(name="pt_cavity")
        central_pt_cavity.place(-central_pt_cavity == +west_pt_cavity,
                                +central_pt_cavity == +west_pt_cavity,
                                +central_pt_cavity == +west_pt_cavity)

        extruded_led_cavity = ExtrudeTo(central_led_cavity.named_faces("lens_hole"), central_pt_cavity.copy(False))
        extruded_pt_cavity = ExtrudeTo(central_pt_cavity.named_faces("lens_hole"), central_led_cavity.copy(False))

        result = Difference(combined_cluster, *key_base_negatives, center_hole, center_nub_hole, central_magnet_cutout,
                            extruded_led_cavity, extruded_pt_cavity)

        result.add_named_point("lower_left_corner", [west_base.min().x, west_base.min().y, 0])
        result.add_named_point("lower_right_corner", [east_base.max().x, east_base.min().y, 0])
        return result

    def cluster_pcb(self, cluster, front, back):
        hole_size = .35

        full_cluster = Union(cluster, front, back).copy(copy_children=False)

        pcb_plane = Rect(1, 1, 1)
        pcb_plane.place(
            ~pcb_plane == ~cluster,
            ~pcb_plane == ~cluster,
            +pcb_plane == -back)

        center_hole: Box = cluster.find_children("center_hole")[0]
        full_cluster = Fillet(
            full_cluster.shared_edges(
                full_cluster.find_faces([center_hole.left, center_hole.right]),
                full_cluster.find_faces([center_hole.front, center_hole.back])),
            .8)

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

        front_key_well_face = full_cluster.find_faces(front_edge_finder.back)[0]
        front_cut_out = cluster.bounding_box.make_box()
        front_cut_out.name = "front_cut_out"
        front_cut_out.place(
            ~front_cut_out == ~cluster,
            +front_cut_out == ~front_key_well_face,
            ~front_cut_out == ~pcb_silhouette)

        back_trim_tool = full_cluster.bounding_box.make_box()
        back_trim_tool.place(
            ~back_trim_tool == ~full_cluster,
            (-back_trim_tool == -back) + 5,
            ~back_trim_tool == ~pcb_silhouette)

        pcb_back_box = Box(
            8,
            back.max().y - back_trim_tool.min().y,
            1,
            name="pcb_back_box")
        pcb_back_box.place(
            ~pcb_back_box == ~back,
            +pcb_back_box == +back,
            -pcb_back_box == ~pcb_silhouette)
        pcb_back_connection = full_cluster.bounding_box.make_box()
        pcb_back_connection.place(
            ~pcb_back_connection == ~full_cluster,
            +pcb_back_connection == -pcb_back_box,
            -pcb_back_connection == -pcb_back_box)
        pcb_back_intermediate = Union(pcb_back_box, pcb_back_connection)
        filleted_pcb_back = Fillet(
            pcb_back_intermediate.shared_edges(
                pcb_back_intermediate.find_faces([pcb_back_box.left, pcb_back_box.right]),
                pcb_back_intermediate.find_faces(pcb_back_connection.back)),
            .8)
        pcb_back = Difference(
            filleted_pcb_back.find_faces(pcb_back_box.bottom)[0].make_component(name="pcb_back"),
            pcb_back_connection)

        pcb_silhouette = Union(
            Difference(pcb_silhouette, key_wells, front_cut_out, back_trim_tool),
            pcb_back)

        for loop in pcb_silhouette.faces[0].loops:
            offset_amount = -.2
            pcb_silhouette = OffsetEdges(pcb_silhouette.faces[0],
                                         pcb_silhouette.find_edges(loop.edges),
                                         offset_amount)

        connector_holes = self.hole_array(hole_size, 1.5, 7)
        connector_holes.place((~connector_holes == ~pcb_silhouette),
                              (~connector_holes == -back_trim_tool) - 1.6,
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

        extruded_pcb = Extrude(pcb_silhouette, -1.6, name="pcb")

        extruded_pcb.add_named_faces("top", *extruded_pcb.start_faces)

        extruded_pcb.add_named_faces("bottom", *extruded_pcb.end_faces)
        return extruded_pcb, connector_legs_cutout

    def ball_magnet(self):
        return Sphere(2.5, "ball_magnet")

    def large_magnet(self):
        return Box(3.175, 3.175, 1.5875, name="large_magnet")

    def underside_magnetic_attachment(self, base_height, name=None):
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
        magnet_hole = self.vertical_large_thin_magnet_cutout(depth=1)
        magnet_hole.rx(180)

        base = Cylinder(base_height, 3.5)

        magnet_hole.place(
            ~magnet_hole == ~base,
            ~magnet_hole == ~base,
            -magnet_hole == -base)

        negatives = Union(magnet_hole, name="negatives")

        return Difference(base, negatives, name=name or "attachment")

    def magnetic_attachment(self, ball_depth, rectangular_depth, radius=None, name="attachment"):
        """This is the design for the magnetic attachments on the normal and thumb clusters.

        It consists of an upper part that holds a small rectangular magnet, and then a lower part that is a spherical
        indentation for a 5mm ball magnet.
        """
        ball = self.ball_magnet()
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

        magnet_hole = self.vertical_large_thin_magnet_cutout(depth=rectangular_depth)

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

    def find_tangent_intersection_on_circle(self, circle: Circle, point: Point3D):
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

    def cluster_front(self, cluster: Component):
        front_base = cluster.find_children("south_base")[0]
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
            +front_notch == +front_cutout,
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

    def cluster_back(self, cluster: Component):
        upper_base = cluster.find_children("upper_base")[0]

        attachment = self.underside_magnetic_attachment(upper_base.size().z)

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
            2.8)
        nut_cutout.place(
            ~nut_cutout == ~screw_hole,
            (-nut_cutout == ~screw_hole) - nut_cutout.size().x / 2,
            (+nut_cutout == +base) - 1.8)

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

    def cluster_front_mount_clip(self, front, extra_height=0.0, name="cluster_front_mount_clip"):
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

        attachment = self.underside_magnetic_attachment(1.4)
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

    def cluster_front_mount_clip_tall(self, front, name="cluster_front_mount_clip_tall"):
        return self.cluster_front_mount_clip(front, extra_height=2.6, name=name)

    @MemoizableDesign.MemoizeComponent
    def center_key(self):
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
        center_post = Fillet(
            center_post.shared_edges(
                [center_post.front, center_post.back],
                [center_post.right, center_post.left]),
            .8)

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

        magnet = self.horizontal_tiny_magnet_cutout(1.3)
        magnet.place(~magnet == ~center_post,
                     -magnet == -center_post,
                     (~magnet == +key_rim) + 3.5 + key_travel)

        result = Difference(Union(key, key_rim, center_post, interruptor_post), magnet, name="center_key")

        return result

    def vertical_key_post(self, post_length, groove_height, groove_width, magnet_height):
        post = Box(post_width, post_length - key_thickness/2, key_thickness, name="post")

        pivot = Cylinder(post_width, key_thickness/2, name="pivot")
        pivot.ry(90)
        pivot.place(
            ~pivot == ~post,
            ~pivot == -post,
            ~pivot == ~post)

        magnet = self.vertical_rotated_magnet_cutout()
        magnet.place(~magnet == ~post,
                     (~magnet == -pivot) + magnet_height + key_thickness/2,
                     +magnet == +post)

        groove_depth = .7
        groove = Box(post.size().x, groove_width, groove_depth, name="groove")
        groove.place(~groove == ~post,
                     (-groove == -pivot) + groove_height + key_thickness/2,
                     -groove == -post)

        end_fillet_tool_negative = Union(post.copy(), pivot.copy()).bounding_box.make_box()
        end_fillet_tool_negative = Fillet(
            end_fillet_tool_negative.shared_edges(
                end_fillet_tool_negative.front,
                [end_fillet_tool_negative.left, end_fillet_tool_negative.right]),
            1.5)

        end_fillet_tool_positive = Union(post.copy(), pivot.copy()).bounding_box.make_box()
        end_fillet_tool = Difference(end_fillet_tool_positive, end_fillet_tool_negative)

        assembly = Difference(Union(post, pivot), magnet, groove, end_fillet_tool)

        assembly = Fillet(assembly.shared_edges(
            post.top,
            [post.left, post.right]), .5)

        return assembly

    def vertical_key(self, post_length, key_width, key_height, key_angle, key_protrusion, key_displacement, groove_height,
                     groove_width, magnet_height, name):
        post = self.vertical_key_post(post_length, groove_height, groove_width, magnet_height)

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

    def side_key(self, key_height, key_angle, name):
        return self.vertical_key(
            post_length=10,
            key_width=13,
            key_height=key_height,
            key_angle=key_angle,
            key_protrusion=False,
            key_displacement=False,
            groove_height=1.353,
            groove_width=.75,
            magnet_height=5.4,
            name=name)

    @MemoizableDesign.MemoizeComponent
    def cluster_key_short(self, name="cluster_key_short"):
        return self.side_key(5, 0, name)

    @MemoizableDesign.MemoizeComponent
    def cluster_key_tall(self, name="cluster_key_tall"):
        return self.side_key(11, 10, name)

    @MemoizableDesign.MemoizeComponent
    def thumb_side_key(self, key_width, key_height, groove_height, key_displacement: float = -3, name="thumb_side_key"):
        return self.vertical_key(
            post_length=11.5,
            key_width=key_width,
            key_height=key_height,
            key_angle=0,
            key_protrusion=6.5,
            key_displacement=key_displacement,
            groove_height=groove_height,
            groove_width=.6,
            magnet_height=8.748,
            name=name)

    @MemoizableDesign.MemoizeComponent
    def inner_thumb_key(self):
        return self.vertical_key(
            post_length=12,
            key_width=25,
            key_height=13.5,
            key_angle=0,
            key_protrusion=2.5,
            key_displacement=0,
            groove_height=2.68,
            groove_width=.6,
            magnet_height=8.748,
            name="inner_thumb_key")

    @MemoizableDesign.MemoizeComponent
    def outer_upper_thumb_key(self):
        return self.vertical_key(
            post_length=12,
            key_width=20,
            key_height=14,
            key_angle=0,
            key_protrusion=4.5,
            key_displacement=0,
            groove_height=2.68,
            groove_width=.6,
            magnet_height=8.748,
            name="outer_upper_thumb_key")

    @MemoizableDesign.MemoizeComponent
    def outer_lower_thumb_key(self):
        return self.vertical_key(
            post_length=12,
            key_width=20,
            key_height=18,
            key_angle=0,
            key_protrusion=4.5,
            key_displacement=0,
            groove_height=4.546,
            groove_width=.6,
            magnet_height=8.748,
            name="outer_lower_thumb_key")

    @MemoizableDesign.MemoizeComponent
    def thumb_mode_key(self, name=None):
        key_post = self.vertical_key_post(18, 2.68, 1, 9.05)

        face_finder = Box(1, 1, 1)
        face_finder.place(~face_finder == ~key_post,
                          -face_finder == +key_post,
                          ~face_finder == ~key_post)

        end_face = key_post.find_faces(face_finder)[0]

        end_face = BRepComponent(end_face.brep)

        mid_section_mid = Rect(end_face.size().x, end_face.size().z)
        mid_section_mid.rx(90)
        mid_section_mid.place(
            (~mid_section_mid == ~end_face) + 5.5/2,
            (~mid_section_mid == ~end_face) + 14/2,
            (~mid_section_mid == ~end_face) + 3.5/2)

        mid_section_end = Rect(end_face.size().x, end_face.size().z)
        mid_section_end.rx(90)
        mid_section_end.place(
            (~mid_section_end == ~end_face) + 5.5,
            (~mid_section_end == ~end_face) + 14,
            (~mid_section_end == ~end_face) + 3.5)

        lower_extension_length = 2
        lower_extension_mid_face = end_face.copy(copy_children=False)
        lower_extension_mid_face.ty(lower_extension_length)
        lower_extension_mid_face.tx(
            -lower_extension_length *
            (end_face.mid().x - mid_section_end.mid().x) / (mid_section_end.mid().y - end_face.mid().y))

        lower_extension_end_face = end_face.copy(copy_children=False)
        lower_extension_end_face.ty(lower_extension_length + 1)
        lower_extension_end_face = Scale(lower_extension_end_face, 1, 1, .5, center=lower_extension_end_face.min())
        lower_extension_end_face.tx(
            -(lower_extension_length + 1) *
            (end_face.mid().x - mid_section_end.mid().x) / (mid_section_end.mid().y - end_face.mid().y))
        lower_extension_end_face.tz(1)

        lower_extension = Union(
            Loft(end_face, lower_extension_mid_face),
            Loft(lower_extension_mid_face, lower_extension_end_face))

        mid_section = Loft(end_face, mid_section_mid, mid_section_end)

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

        filleted_end_section = Fillet(
            end_section.find_edges(end_section_end_face.edges), key_thickness/2, False)

        result = Union(key_post, mid_section, horizontal_section, filleted_end_section, lower_extension)

        result = Fillet(result.shared_edges(
            [horizontal_section.front, horizontal_section.back],
            [horizontal_section.top, horizontal_section.bottom, mid_section, end_section.bottom]), 3,
            name=name or "thumb_mode_key")

        return result

    @MemoizableDesign.MemoizeComponent
    def thumb_cluster_insertion_tool(self, cluster):
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

    @MemoizableDesign.MemoizeComponent
    def thumb_down_key(self):
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

        magnet = self.horizontal_rotated_magnet_cutout(name="magnet")
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

        # the key is upside down, so we actually want the bottom face
        assembly.add_named_faces("top", assembly.find_faces(
            key_base.bottom)[0])

        return assembly

    @MemoizableDesign.MemoizeComponent
    def cluster_body_assembly(self, tall_clip=False):
        cluster = self.base_cluster_design()
        cluster, front = self.cluster_front(cluster)
        back = self.cluster_back(cluster)
        pcb, connector_legs_cutout = self.cluster_pcb(cluster, front, back)

        if tall_clip:
            front_clip = self.cluster_front_mount_clip_tall(front, name="cluster_front_mount_clip")
        else:
            front_clip = self.cluster_front_mount_clip(front)

        cluster = Difference(Union(cluster, front, back), connector_legs_cutout, name="cluster")
        return Group([cluster, pcb, front_clip], name="cluster_body_assembly")

    def standoff_by_ball_center(self, point, name="standoff"):
        """Generate a standoff sub-assembly with the center of the ball magnet at the specified point."""
        screw_lengths = [11, 7]
        standoff_heights = [4, 6, 8, 14, 20]

        screws = [self.screw_design(length) for length in screw_lengths]

        # Find the tallest screw shorter than what's needed for the given point
        selected_screw = None
        ball = None
        for screw in screws:
            ball = screw.find_children("ball_magnet")[0]
            if ball.mid().z < point.z:
                selected_screw = screw
                break
        if not selected_screw:
            selected_screw = screws[-1]

        selected_screw.place(
            ~ball == point,
            ~ball == point,
            ~ball == point)

        minimum_standoff_height = selected_screw.min().z + 1
        selected_standoff_height = None
        for standoff_height in standoff_heights:
            if standoff_height > minimum_standoff_height:
                selected_standoff_height = standoff_height
                break
        if not selected_standoff_height:
            selected_standoff_height = standoff_heights[-1]

        standoff = self.screw_base_design(selected_standoff_height)
        standoff.rz(360/12)
        standoff.place(
            ~standoff == ~selected_screw,
            ~standoff == ~selected_screw)

        nut = self.screw_nut_design()
        nut.place(
            ~nut == ~standoff,
            ~nut == ~standoff,
            -nut == +standoff)
        support_base = self.support_base_design()

        support_base.place(
            ~support_base == ~standoff,
            ~support_base == ~standoff)

        return Group([
            support_base, standoff, nut, selected_screw, selected_screw.find_children("ball_magnet")[0]], name=name)

    def add_standoffs(self, cluster):
        """Add standoffs to a cluster assembly

        :param cluster: A cluster assembly, as returned by positioned_cluster_assembly
        :return: A Group containing the 3 standoffs for the given cluster
        """

        front_magnet: Box = cluster.find_children("front_magnet")[0]
        down_normal = front_magnet.bottom.get_plane().normal
        ball_magnet_radius = self.ball_magnet().size().z / 2
        down_normal.normalize()
        down_normal.scaleBy(-ball_magnet_radius)
        ball_magnet_center_vector = down_normal

        cluster_transform = cluster.find_children("cluster", recursive=False)[0].world_transform()
        cluster_transform_array = cluster_transform.asArray()

        rz = math.degrees(math.atan2(cluster_transform_array[4], cluster_transform_array[0]))

        front_point = cluster.find_children("front_magnet")[0].named_point("center_bottom").point
        front_point.translateBy(ball_magnet_center_vector)
        front_standoff = self.standoff_by_ball_center(front_point, name="front_standoff")
        front_standoff.rz(rz, center=front_standoff.mid())

        back_left_point = cluster.find_children("back_left_magnet")[0].named_point("center_bottom").point
        back_left_point.translateBy(ball_magnet_center_vector)
        back_left_standoff = self.standoff_by_ball_center(back_left_point, name="back_left_standoff")
        back_left_standoff.rz(rz, center=back_left_standoff.mid())

        back_right_point = cluster.find_children("back_right_magnet")[0].named_point("center_bottom").point
        back_right_point.translateBy(ball_magnet_center_vector)
        back_right_standoff = self.standoff_by_ball_center(back_right_point, name="back_right_standoff")
        back_right_standoff.rz(rz, center=back_right_standoff.mid())

        return Group([front_standoff, back_left_standoff, back_right_standoff], name="standoffs")

    def positioned_cluster_assembly(
            self,
            placement: 'AbsoluteFingerClusterPlacement',
            add_clip=True,
            tall_clip=False):
        body_assembly = self.cluster_body_assembly(tall_clip=tall_clip)
        cluster = body_assembly.find_children("cluster", recursive=False)[0]
        pcb = body_assembly.find_children("pcb", recursive=False)[0]
        front_clip = body_assembly.find_children("cluster_front_mount_clip", recursive=False)[0]

        south_key = self.cluster_key_short(name="south_key")
        south_key.rx(90).rz(180)
        east_key = self.cluster_key_short(name="east_key")
        east_key.rx(90).rz(270)
        west_key = self.cluster_key_short(name="west_key")
        west_key.rx(90).rz(90)
        north_key = self.cluster_key_tall(name="north_key")
        north_key.rx(90)
        down_key = self.center_key()

        self._align_side_key(cluster.find_children("south_base")[0], south_key)
        self._align_side_key(cluster.find_children("east_base")[0], east_key)
        self._align_side_key(cluster.find_children("west_base")[0], west_key)
        self._align_side_key(cluster.find_children("north_base")[0], north_key)

        center_key_magnet = down_key.find_children("magnet_cutout")[0]
        center_cluster_magnet = cluster.find_children("central_magnet_cutout")[0]
        down_key.rx(180).rz(180)
        down_key.place(
            ~center_key_magnet == ~center_cluster_magnet,
            -center_key_magnet == +center_cluster_magnet,
            ~center_key_magnet == ~center_cluster_magnet)

        down_key_top_finder = down_key.bounding_box.make_box()
        down_key_top_finder.place(
            ~down_key_top_finder == ~down_key,
            ~down_key_top_finder == ~down_key,
            -down_key_top_finder == +down_key)
        down_key_top = down_key.find_faces(down_key_top_finder)[0]

        front_magnet = Box((1/8) * 25.4, (1/8) * 25.4, (1/16) * 25.4, name="front_magnet")
        back_left_magnet = Box((1/8) * 25.4, (1/8) * 25.4, (1/16) * 25.4, name="back_left_magnet")
        back_right_magnet = Box((1/8) * 25.4, (1/8) * 25.4, (1/16) * 25.4, name="back_right_magnet")

        front_clip_magnet_cutout = front_clip.find_children("magnet_cutout")[0]
        front_magnet.place(
            ~front_magnet == ~front_clip_magnet_cutout,
            ~front_magnet == ~front_clip_magnet_cutout,
            +front_magnet == +front_clip_magnet_cutout)
        front_magnet.add_named_point("center_bottom",
                                     Point3D.create(
                                         front_magnet.mid().x,
                                         front_magnet.mid().y,
                                         front_magnet.min().z))

        back_magnet_cutouts = cluster.find_children("cluster_back")[0].find_children("magnet_cutout")
        if back_magnet_cutouts[0].mid().x < back_magnet_cutouts[1].mid().x:
            back_left_magnet_cutout = back_magnet_cutouts[0]
            back_right_magnet_cutout = back_magnet_cutouts[1]
        else:
            back_right_magnet_cutout = back_magnet_cutouts[0]
            back_left_magnet_cutout = back_magnet_cutouts[1]

        back_left_magnet.place(
            ~back_left_magnet == ~back_left_magnet_cutout,
            ~back_left_magnet == ~back_left_magnet_cutout,
            +back_left_magnet == +back_left_magnet_cutout)
        back_left_magnet.add_named_point("center_bottom",
                                         Point3D.create(
                                             back_left_magnet.mid().x,
                                             back_left_magnet.mid().y,
                                             back_left_magnet.min().z))

        back_right_magnet.place(
            ~back_right_magnet == ~back_right_magnet_cutout,
            ~back_right_magnet == ~back_right_magnet_cutout,
            +back_right_magnet == +back_right_magnet_cutout)
        back_right_magnet.add_named_point("center_bottom",
                                          Point3D.create(
                                              back_right_magnet.mid().x,
                                              back_right_magnet.mid().y,
                                              back_right_magnet.min().z))

        ball_magnet_radius = self.ball_magnet().size().x / 2

        cluster_group_children = [cluster,
                                  pcb,
                                  south_key,
                                  east_key,
                                  west_key,
                                  north_key,
                                  down_key,
                                  back_left_magnet,
                                  back_right_magnet]
        if add_clip:
            cluster_group_children.append(front_clip)
            cluster_group_children.append(front_magnet)
        cluster_group = Group(cluster_group_children, name="cluster")

        cluster_group.add_named_point("down_key_top_center", down_key_top.mid())

        cluster_group.transform(placement.rotation_matrix)
        rotation_matrix_array = placement.rotation_matrix.asArray()

        cluster_group.place(
            ~cluster_group.named_point("down_key_top_center") == placement.position,
            ~cluster_group.named_point("down_key_top_center") == placement.position,
            ~cluster_group.named_point("down_key_top_center") == placement.position)

        normal = down_key_top.get_plane().normal

        ball_magnet_center_vector = normal.copy()
        ball_magnet_center_vector.scaleBy(-ball_magnet_radius)

        cluster_group = Group(
            [*cluster_group.children()],
            name="cluster_assembly")

        return cluster_group

    @MemoizableDesign.MemoizeComponent
    def cluster_assembly(self):
        body_assembly = self.cluster_body_assembly()
        cluster = body_assembly.find_children("cluster", recursive=False)[0]
        pcb = body_assembly.find_children("pcb", recursive=False)[0]
        front_clip = body_assembly.find_children("cluster_front_mount_clip", recursive=False)[0]

        south_key = self.cluster_key_short(name="south_key")
        south_key.rx(90).rz(180)
        east_key = self.cluster_key_short(name="east_key")
        east_key.rx(90).rz(270)
        west_key = self.cluster_key_short(name="west_key")
        west_key.rx(90).rz(90)
        north_key = self.cluster_key_tall(name="north_key")
        north_key.rx(90)
        down_key = self.center_key()

        self._align_side_key(cluster.find_children("south_base")[0], south_key)
        self._align_side_key(cluster.find_children("east_base")[0], east_key)
        self._align_side_key(cluster.find_children("west_base")[0], west_key)
        self._align_side_key(cluster.find_children("north_base")[0], north_key)

        center_key_magnet = down_key.find_children("magnet_cutout")[0]
        center_cluster_magnet = cluster.find_children("central_magnet_cutout")[0]
        down_key.rx(180).rz(180)
        down_key.place(
            ~center_key_magnet == ~center_cluster_magnet,
            -center_key_magnet == +center_cluster_magnet,
            ~center_key_magnet == ~center_cluster_magnet)

        front_magnet = Box((1/8) * 25.4, (1/8) * 25.4, (1/16) * 25.4, name="front_magnet")
        back_left_magnet = Box((1/8) * 25.4, (1/8) * 25.4, (1/16) * 25.4, name="back_left_magnet")
        back_right_magnet = Box((1/8) * 25.4, (1/8) * 25.4, (1/16) * 25.4, name="back_right_magnet")

        front_clip_magnet_cutout = front_clip.find_children("magnet_cutout")[0]
        front_magnet.place(
            ~front_magnet == ~front_clip_magnet_cutout,
            ~front_magnet == ~front_clip_magnet_cutout,
            +front_magnet == +front_clip_magnet_cutout)

        back_magnet_cutouts = cluster.find_children("cluster_back")[0].find_children("magnet_cutout")
        if back_magnet_cutouts[0].mid().x < back_magnet_cutouts[1].mid().x:
            back_left_magnet_cutout = back_magnet_cutouts[0]
            back_right_magnet_cutout = back_magnet_cutouts[1]
        else:
            back_right_magnet_cutout = back_magnet_cutouts[0]
            back_left_magnet_cutout = back_magnet_cutouts[1]

        back_left_magnet.place(
            ~back_left_magnet == ~back_left_magnet_cutout,
            ~back_left_magnet == ~back_left_magnet_cutout,
            +back_left_magnet == +back_left_magnet_cutout)

        back_right_magnet.place(
            ~back_right_magnet == ~back_right_magnet_cutout,
            ~back_right_magnet == ~back_right_magnet_cutout,
            +back_right_magnet == +back_right_magnet_cutout)

        front_support = self.screw_support_assembly(7, 4, 0, name="front_support")
        front_ball_magnet = front_support.find_children("ball_magnet")[0]

        back_left_support = self.screw_support_assembly(13, 8, 0, name="back_left_support")
        back_left_ball_magnet = back_left_support.find_children("ball_magnet")[0]

        back_right_support = self.screw_support_assembly(13, 8, 4, name="back_right_support")
        back_right_ball_magnet = back_right_support.find_children("ball_magnet")[0]

        cluster_group = Group((cluster,
                               pcb,
                               front_clip,
                               south_key,
                               east_key,
                               west_key,
                               north_key,
                               down_key,
                               front_magnet,
                               back_left_magnet,
                               back_right_magnet), name="cluster")

        cluster_group.place(
            ~front_magnet == ~front_support,
            ~front_magnet == ~front_support,
            -front_magnet == +front_support)

        ball_magnet_radius = front_ball_magnet.size().z / 2
        cluster_group.add_named_point("front_support_point",
                                      Point3D.create(
                                          front_magnet.mid().x,
                                          front_magnet.mid().y,
                                          front_magnet.min().z - ball_magnet_radius))
        cluster_group.add_named_point("back_left_support_point",
                                      Point3D.create(
                                          back_left_magnet.mid().x,
                                          back_left_magnet.mid().y,
                                          back_left_magnet.min().z - ball_magnet_radius))
        cluster_group.add_named_point("back_right_support_point",
                                      Point3D.create(
                                          back_right_magnet.mid().x,
                                          back_right_magnet.mid().y,
                                          back_right_magnet.min().z - ball_magnet_radius))

        first_rotation = self.rotate_to_height_matrix(
                front_ball_magnet.mid(),
                Vector3D.create(1, 0, 0),
                cluster_group.named_point("back_left_support_point").point,
                back_left_ball_magnet.mid().z)
        cluster_group.transform(first_rotation)

        back_left_support.place(
            ~back_left_ball_magnet == cluster_group.named_point("back_left_support_point"),
            ~back_left_ball_magnet == cluster_group.named_point("back_left_support_point"),
            ~back_left_ball_magnet == cluster_group.named_point("back_left_support_point"))

        second_rotation = self.rotate_to_height_matrix(
            front_ball_magnet.mid(),
            front_ball_magnet.mid().vectorTo(back_left_ball_magnet.mid()),
            cluster_group.named_point("back_right_support_point").point,
            back_right_ball_magnet.mid().z)
        cluster_group.transform(second_rotation)

        back_right_support.place(
            ~back_right_ball_magnet == cluster_group.named_point("back_right_support_point"),
            ~back_right_ball_magnet == cluster_group.named_point("back_right_support_point"),
            ~back_right_ball_magnet == cluster_group.named_point("back_right_support_point"))

        return Group([
            cluster_group,
            front_support,
            back_left_support,
            back_right_support], name="cluster_assembly")

    def male_thread_chamfer_tool(self, end_radius, angle):
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

    def screw_thread_profile(self, pitch=1.4, angle=37.5, flat_height=.2):
        sloped_side_height = (pitch - flat_height*2)/2

        return (((0, flat_height / 2),
                 (sloped_side_height / math.tan(math.radians(angle)), flat_height / 2 + sloped_side_height),
                 (sloped_side_height / math.tan(math.radians(angle)), flat_height / 2 + sloped_side_height + flat_height),
                 (0, pitch - flat_height / 2)), pitch)

    @MemoizableDesign.MemoizeComponent
    def screw_design(self, screw_length, radius_adjustment=-.2, name="screw"):
        screw_nominal_radius, screw_radius_adjustment, _, _, _ = self.screw_base_parameters()

        screw_radius = screw_nominal_radius + radius_adjustment

        ball = self.ball_magnet()

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
                        *self.screw_thread_profile())

        return Difference(Union(screw, neck), ball, name=name)

    def screw_base_flare(self, clearance=0.0):
        _, _, _, base_min_radius, _ = self.screw_base_parameters()

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

    def screw_base_parameters(self):
        screw_nominal_radius = 3.0
        screw_radius_adjustment = -.2
        screw_hole_radius_adjustment = .1

        screw_hole = Cylinder(10, screw_nominal_radius + screw_hole_radius_adjustment)
        temp_threads = Threads(screw_hole, *self.screw_thread_profile())
        base_min_radius = temp_threads.size().x/2 + .8

        base_clearance = .1

        return (screw_nominal_radius, screw_radius_adjustment, screw_hole_radius_adjustment, base_min_radius,
                base_clearance)

    @MemoizableDesign.MemoizeComponent
    def screw_base_design(self, screw_length, flared_base=True, name=None):
        screw_nominal_radius, _, screw_hole_radius_adjustment, base_min_radius, _ = self.screw_base_parameters()
        screw_hole = Cylinder(screw_length, screw_nominal_radius + screw_hole_radius_adjustment)

        base_polygon = RegularPolygon(6, base_min_radius, is_outer_radius=False, name="polygon")
        base = Extrude(base_polygon, screw_length)

        screw_hole.place(~screw_hole == ~base,
                         ~screw_hole == ~base,
                         -screw_hole == -base)

        if flared_base:
            base = Union(base, self.screw_base_flare())

        # Reverse the axis so the threads "start" on the top. The ensures the top is always at a consistent thread
        # position, so that the nut will tighten down to a consistent rotation.
        return Threads(
            Difference(base, screw_hole),
            *self.screw_thread_profile(),
            reverse_axis=True,
            name=name or "screw_base")

    @MemoizableDesign.MemoizeComponent
    def screw_nut_design(self, name="screw_nut"):
        nut = self.screw_base_design(3, flared_base=False, name=name)
        nut.rx(180, center=nut.mid())
        return nut

    @MemoizableDesign.MemoizeComponent
    def support_base_design(self, name="support_base"):
        _, _, _, base_min_radius, base_clearance = self.screw_base_parameters()

        hole_body_polygon = RegularPolygon(6, base_min_radius + base_clearance, is_outer_radius=False)
        hole_body = Extrude(hole_body_polygon, 4)
        hole_body.rz(360/12)
        flare = self.screw_base_flare(clearance=base_clearance)
        flare.place(
            ~flare == ~hole_body,
            ~flare == ~hole_body,
            -flare == -hole_body)
        flare.rz(360/12)
        hole = Union(hole_body, flare)

        back_magnet = self.vertical_large_thin_double_magnet_cutout(extra_depth=.2)
        back_magnet.rx(180)

        back_magnet.place(
            ~back_magnet == ~hole,
            (-back_magnet == +hole) + 1,
            -back_magnet == -hole)

        front_magnet = back_magnet.copy()
        front_magnet.place(
            ~front_magnet == ~hole,
            (+front_magnet == -hole) - 1,
            -front_magnet == -hole)

        lower_body_polygon = RegularPolygon(6, base_min_radius + base_clearance + .8, is_outer_radius=False)
        lower_body_polygon.rz(360/12)

        back_base = Circle(lower_body_polygon.size().x / 2)
        back_base.place(
            ~back_base == ~lower_body_polygon,
            (+back_base == +back_magnet) + 2,
            -back_base == -lower_body_polygon)

        front_base = back_base.copy()
        front_base.place(
            ~front_base == ~lower_body_polygon,
            (-front_base == -front_magnet) - 2,
            -front_base == -lower_body_polygon)

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
            Extrude(Hull(Union(lower_body_polygon, back_base, front_base)), 4),
            mid_side_cutout,
            hole,
            back_magnet,
            front_magnet, name=name)
        return assembly

    @MemoizableDesign.MemoizeComponent
    def screw_support_assembly(self, screw_length, base_length, screw_height, name=None):
        screw = self.screw_design(screw_length)
        screw.rz(360/12)

        screw_base = self.screw_base_design(base_length)
        screw_base.rz(360/12)

        nut = self.screw_nut_design()
        nut.rz(360/12)

        support_base = self.support_base_design()

        screw_base.place(
            ~screw_base == ~support_base,
            ~screw_base == ~support_base,
            -screw_base == -support_base)

        _, pitch = self.screw_thread_profile()

        screw.place(
            ~screw == ~screw_base,
            ~screw == ~screw_base,
            (-screw == -screw_base) + screw_height)
        screw.rz(-360 * (screw_base.max().z - screw.min().z) / pitch)

        nut.place(
            ~nut == ~screw,
            ~nut == ~screw,
            -nut == +screw_base)

        ball = screw.find_children("ball_magnet")[0]

        return Group([
            screw,
            screw_base,
            nut,
            support_base,
            ball], name=name)

    @MemoizableDesign.MemoizeComponent
    def thumb_base(self, name=None):
        down_key = self.thumb_down_key()
        down_key.ry(180)

        upper_outer_base = self.vertical_key_base(
            extra_height=4, pressed_key_angle=7, fillet_back_keywell_corners=True, name="upper_outer_base")

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

        lower_outer_base = self.vertical_key_base(
            extra_height=4, pressed_key_angle=4.2, fillet_back_keywell_corners=True, name="lower_outer_base")
        lower_outer_base_magnet_front = lower_outer_base.find_children("magnet_cutout")[0].named_faces("front")[0]
        lower_outer_base_negatives = lower_outer_base.find_children("negatives")[0]
        lower_outer_base.rz(-90)
        lower_outer_base.place(
            -lower_outer_base == -upper_outer_base,
            (-lower_outer_base_magnet_front == +down_key) - 30.65,
            +lower_outer_base == +upper_outer_base)

        inner_base = self.vertical_key_base(
            extra_height=4, pressed_key_angle=7, fillet_back_keywell_corners=True, name="inner_key_base")
        inner_base_magnet_front = inner_base.find_children("magnet_cutout")[0].named_faces("front")[0]
        inner_base_negatives = inner_base.find_children("negatives")[0]
        inner_base.rz(90 + 20)
        inner_base.place(
            (~inner_base_magnet_front == ~down_key) + 12.392,
            (~inner_base_magnet_front == +down_key) - 3.2,
            +inner_base == +upper_outer_base)

        upper_base = self.vertical_key_base(
            extra_height=4, pressed_key_angle=7, name="upper_key_base")
        upper_base_magnet_front = upper_base.find_children("magnet_cutout")[0].named_faces("front")[0]
        upper_base_negatives = upper_base.find_children("negatives")[0]
        key_base_upper = upper_base.find_children("upper_base")[0]

        upper_base_lower_fillet = Cylinder(key_base_upper.size().z, 1)
        upper_base_lower_fillet.place(
            ~upper_base_lower_fillet == -upper_base,
            -upper_base_lower_fillet == -upper_base,
            ~upper_base_lower_fillet == ~key_base_upper)

        upper_base_upper_fillet = Cylinder(key_base_upper.size().z, 1)
        upper_base_upper_fillet.place(
            ~upper_base_upper_fillet == +upper_base,
            -upper_base_upper_fillet == -upper_base,
            ~upper_base_upper_fillet == ~key_base_upper)

        upper_base = Group([upper_base, upper_base_lower_fillet, upper_base_upper_fillet])

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

        # Extend the lower part of the body on the "outer" side a bit, so there's more room to get a trace out of that
        # cramped area in the very bottom
        lower_extension = Cylinder(1, 1)
        lower_extension.place(
            -lower_extension == -lower_outer_base,
            ~lower_extension == -lower_outer_base,
            +lower_extension == +lower_outer_base)

        # Extend the back part on the "outer" side, to give more room to fit the hole for the nut
        back_extension = Cylinder(1, 1)
        back_extension.place(
            -back_extension == -upper_outer_base,
            (~back_extension == +upper_outer_base) + 1,
            +back_extension == +upper_outer_base)

        front_attachment = self.underside_magnetic_attachment(key_base_upper.size().z, name="front_attachment")
        front_attachment.place(
            +front_attachment == -upper_base,
            -front_attachment == -lower_extension,
            +front_attachment == +upper_outer_base)

        back_attachment = self.underside_magnetic_attachment(key_base_upper.size().z, name="back_attachment")
        back_attachment.place(
            ~back_attachment == ~down_key,
            (-back_attachment == +down_key_body_hole) + 2,
            +back_attachment == +upper_outer_base)

        side_attachment = self.underside_magnetic_attachment(key_base_upper.size().z, name="side_attachment")
        side_attachment.place(
            -side_attachment == -upper_outer_base,
            ~side_attachment == (upper_outer_base.min().y + lower_outer_base.max().y)/2,
            +side_attachment == +upper_outer_base)

        body_entities = [
            upper_outer_base,
            lower_outer_base,
            inner_base,
            upper_base,
            front_attachment,
            back_attachment,
            side_attachment]

        hull_entities = [
            *body_entities, lower_extension, back_extension, upper_base_upper_fillet, upper_base_lower_fillet]

        hull_entities_group = Group(hull_entities)
        top_face_finder = hull_entities_group.bounding_box.make_box()
        top_face_finder.place(z=-top_face_finder == +hull_entities_group)

        body = Extrude(
            Hull(Union(*[face.make_component().copy(copy_children=False)
                         for face in hull_entities_group.find_faces(top_face_finder)])),
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
        down_key_magnet_extension = Fillet(
            down_key_magnet_extension.shared_edges(
                down_key_magnet_extension.back,
                [down_key_magnet_extension.left, down_key_magnet_extension.right]),
            .8)

        down_key_magnet = self.horizontal_rotated_magnet_cutout(1.8)
        down_key_magnet.place(
            ~down_key_magnet == ~down_key_magnet_extension,
            -down_key_magnet == -down_key_magnet_extension,
            ~down_key_magnet == ~down_key.find_children("magnet")[0])

        down_key_led_cavity = self.make_bottom_entry_led_cavity("down_key_led_cavity")
        down_key_led_cavity.rz(180)
        upper_outer_led_cavity = upper_outer_base.find_children("led_cavity")[0]
        down_key_led_cavity.place(
            (-down_key_led_cavity == +down_key_body_hole) + .8,
            (~down_key_led_cavity == -down_key_body_hole) + 16,
            +down_key_led_cavity == +upper_outer_led_cavity)
        down_key_led_cavity = ExtrudeTo(down_key_led_cavity.named_faces("lens_hole"), down_key_body_hole.copy(False))

        down_key_pt_cavity = self.make_bottom_entry_led_cavity("down_key_pt_cavity")
        down_key_pt_cavity.place(
            (+down_key_pt_cavity == -down_key_body_hole) - .8,
            ~down_key_pt_cavity == ~down_key_led_cavity,
            +down_key_pt_cavity == +upper_outer_led_cavity)
        down_key_pt_cavity = ExtrudeTo(down_key_pt_cavity.named_faces("lens_hole"), down_key_body_hole.copy(False))

        side_nut_negatives, side_nut_positives = self._thumb_side_nut(body, upper_base, front_attachment)

        back_nut_negatives, back_nut_positives = self._thumb_back_nut(body, back_attachment)

        assembly = Union(
            Difference(
                Union(body, *body_entities, down_key_magnet_extension),
                upper_outer_base_negatives, lower_outer_base_negatives,
                inner_base_negatives, upper_base_negatives,
                *front_attachment.find_children("negatives"),
                *back_attachment.find_children("negatives"),
                *side_attachment.find_children("negatives"),
                down_key_slot, down_key_magnet, down_key_led_cavity, down_key_pt_cavity,
                Difference(down_key_body_hole, down_key_right_stop, down_key_left_stop,  name="down_key_void"),
                *side_nut_negatives,
                *back_nut_negatives),
            *side_nut_positives,
            *back_nut_positives,
            name=name or "thumb_cluster")

        assembly = Group([assembly], [down_key], name=assembly.name)

        assembly.add_named_faces(
            "body_bottom",
            *assembly.find_faces(body.end_faces))

        return assembly

    def _thumb_side_nut(self, thumb_body: Component, upper_base, front_attachment):

        angled_side_finder = Box(10,
                                 10,
                                 thumb_body.size().z / 2)
        angled_side_finder.place(
            ~angled_side_finder == ~Group([upper_base, front_attachment]),
            ~angled_side_finder == ~Group([upper_base, front_attachment]),
            ~angled_side_finder == ~thumb_body)

        angled_side = thumb_body.find_faces(
            Intersection(thumb_body, angled_side_finder))[0]

        side_angle = math.degrees(angled_side.make_component().get_plane().normal.angleTo(Vector3D.create(1, 0, 0)))

        thumb_body.rz(side_angle, center=(0, 0, 0))

        nut_cutout = Box(
            5.8,
            6.1,
            2.8,
            name="nut_cutout")
        # rotate the nut so that the back face faces outwards
        nut_cutout.rz(-90)

        nut_cutout.place(
            +nut_cutout == +angled_side,
            ~nut_cutout == ~angled_side,
            (+nut_cutout == +angled_side) - 1.8)

        # This will give a single .2 layer on "top" (when printed upside down) of the nut cavity, so that it can be
        # bridged over. This will fill in the screw hole, but a single layer can be cleaned out/pushed through easily.
        nut_cutout_ceiling = Box(
            nut_cutout.size().x,
            nut_cutout.size().x,
            .2,
            name="nut_cutout_ceiling")
        nut_cutout_ceiling.place(
            ~nut_cutout_ceiling == ~nut_cutout,
            -nut_cutout_ceiling == -nut_cutout,
            +nut_cutout_ceiling == -nut_cutout)

        screw_hole = Cylinder(thumb_body.size().z * 10, 3.1 / 2, name="side_screw_hole")
        screw_hole.place(
            (~screw_hole == -nut_cutout) + nut_cutout.size().y / 2,
            ~screw_hole == ~nut_cutout,
            (+screw_hole == +thumb_body) - .4)

        thumb_body.rz(-side_angle, center=(0, 0, 0))
        nut_cutout.rz(-side_angle, center=(0, 0, 0))
        nut_cutout_ceiling.rz(-side_angle, center=(0, 0, 0))
        screw_hole.rz(-side_angle, center=(0, 0, 0))

        return (nut_cutout, screw_hole), (nut_cutout_ceiling,)

    def _thumb_back_nut(self, thumb_body: Component, back_attachment):
        angled_side_finder = Box(
            back_attachment.size().x,
            back_attachment.size().y,
            thumb_body.size().z / 2)
        angled_side_finder.place(
            +angled_side_finder == -back_attachment,
            ~angled_side_finder == ~back_attachment,
            ~angled_side_finder == ~thumb_body)

        angled_side = thumb_body.find_faces(
            Intersection(thumb_body, angled_side_finder))[0]

        side_angle = math.degrees(angled_side.make_component().get_plane().normal.angleTo(Vector3D.create(0, 1, 0)))

        thumb_body.rz(-side_angle, center=(0, 0, 0))

        nut_cutout = Box(
            5.8,
            6.1,
            2.8,
            name="nut_cutout")

        nut_cutout.place(
            (~nut_cutout == ~angled_side) + 1,
            (+nut_cutout == +angled_side),
            (+nut_cutout == +angled_side) - 1.8)

        # This will give a single .2 layer on "top" (when printed upside down) of the nut cavity, so that it can be
        # bridged over. This will fill in the screw hole, but a single layer can be cleaned out/pushed through easily.
        nut_cutout_ceiling = Box(
            nut_cutout.size().x,
            nut_cutout.size().x,
            .2,
            name="nut_cutout_ceiling")
        nut_cutout_ceiling.place(
            ~nut_cutout_ceiling == ~nut_cutout,
            -nut_cutout_ceiling == -nut_cutout,
            +nut_cutout_ceiling == -nut_cutout)

        screw_hole = Cylinder(thumb_body.size().z * 10, 3.1 / 2, name="back_screw_hole")
        screw_hole.place(
            ~screw_hole == ~nut_cutout,
            (~screw_hole == -nut_cutout) + nut_cutout.size().x / 2,
            (+screw_hole == +thumb_body) - .4)

        thumb_body.rz(side_angle, center=(0, 0, 0))
        nut_cutout.rz(side_angle, center=(0, 0, 0))
        nut_cutout_ceiling.rz(side_angle, center=(0, 0, 0))
        screw_hole.rz(side_angle, center=(0, 0, 0))

        return (nut_cutout, screw_hole), (nut_cutout_ceiling,)

    @MemoizableDesign.MemoizeComponent
    def thumb_silhouette(self):
        thumb_base = self.thumb_base()

        silhouette = Hull(Silhouette(
            thumb_base,
            adsk.core.Plane.create(Point3D.create(0, 0, 0), Vector3D.create(0, 0, 1)),
            name="thumb_cluster_silhouette"))
        silhouette.place(z=~silhouette == -thumb_base.find_children("body")[0])

        # The silhouette seems to have some extraneous vertices, which cause the bounding box to be larger than
        # expected. This removes the extraneous stuff, leaving on the single face geometry
        return silhouette.faces[0].make_component(name="thumb_cluster_silhouette")


    def thumb_pcb(self, thumb_cluster: Component, name="thumb_pcb"):
        hole_size = .35

        down_key_magnet_extension = thumb_cluster.find_children("down_key_magnet_extension")[0]

        body_bottom_face = thumb_cluster.named_faces("body_bottom")[0]
        pcb_silhouette = Silhouette(thumb_cluster.copy(copy_children=False), body_bottom_face.get_plane())

        pcb_silhouette = Silhouette(pcb_silhouette.faces[0].outer_edges, pcb_silhouette.get_plane())

        lower_cutout = thumb_cluster.bounding_box.make_box()
        lower_cutout = Fillet(lower_cutout.shared_edges(
            lower_cutout.back,
            lower_cutout.left), .8)
        lower_cutout.place(
            -lower_cutout == -down_key_magnet_extension,
            +lower_cutout == +down_key_magnet_extension,
            ~lower_cutout == ~pcb_silhouette)

        side_attachment = thumb_cluster.find_children("side_attachment")[0]
        back_attachment = thumb_cluster.find_children("back_attachment")[0]

        side_attachment_cutout = Box(
            side_attachment.size().x,
            side_attachment.size().y,
            1)
        side_attachment_cutout = Fillet(
            side_attachment_cutout.shared_edges(
                side_attachment_cutout.right,
                [side_attachment_cutout.front,
                 side_attachment_cutout.back]), .8)

        side_attachment_cutout.place(
            ~side_attachment_cutout == ~side_attachment,
            ~side_attachment_cutout == ~side_attachment,
            ~side_attachment_cutout == ~pcb_silhouette)

        back_attachment_cutout = Box(
            back_attachment.size().x,
            back_attachment.size().y,
            1)
        back_attachment_cutout = Fillet(
            back_attachment_cutout.shared_edges(
                back_attachment_cutout.front,
                [back_attachment_cutout.left,
                 back_attachment_cutout.right]), .8)
        back_attachment_cutout.place(
            ~back_attachment_cutout == ~back_attachment,
            ~back_attachment_cutout == ~back_attachment,
            ~back_attachment_cutout == ~pcb_silhouette)

        pcb_silhouette = Difference(
            pcb_silhouette,
            side_attachment_cutout,
            back_attachment_cutout,
            lower_cutout)

        pcb_silhouette.tz(-.01)

        bottom_finder = thumb_cluster.bounding_box.make_box()
        bottom_finder.place(
            ~bottom_finder == ~thumb_cluster,
            ~bottom_finder == ~thumb_cluster,
            +bottom_finder == -thumb_cluster)

        pcb_silhouette = Difference(
            pcb_silhouette,
            ExtrudeTo(
                Union(*[face.make_component().copy(copy_children=False)
                        for face in thumb_cluster.find_faces(bottom_finder)]),
                body_bottom_face.make_component().copy(copy_children=False).faces[0]))

        pcb_silhouette = OffsetEdges(
            pcb_silhouette.faces[0],
            pcb_silhouette.faces[0].outer_edges,
            -.2)

        legs = Union(*thumb_cluster.find_children("legs"))
        legs.place(
            z=~legs == ~pcb_silhouette)

        down_key_body_hole = thumb_cluster.find_children("down_key_body_hole")[0]

        connector_holes = self.hole_array(hole_size, 1.5, 7)
        connector_holes.rz(90)
        connector_holes.place(~connector_holes == ~down_key_body_hole,
                              ~connector_holes == ~down_key_body_hole,
                              ~connector_holes == ~pcb_silhouette)

        side_screw_hole = thumb_cluster.find_children("side_screw_hole")[0]
        back_screw_hole = thumb_cluster.find_children("back_screw_hole")[0]

        pcb_silhouette = Difference(pcb_silhouette, legs, connector_holes, side_screw_hole, back_screw_hole)

        pcb = Extrude(pcb_silhouette, -1.6, name=name)
        pcb.add_named_faces("top", *pcb.start_faces)

        return pcb

    def _align_side_key(self, key_base: Component, key: Component):
        base_pivot: Cylinder = key_base.find_children("key_pivot")[0]
        key_pivot: Cylinder = key.find_children("pivot")[0]

        base_pivot_axis = base_pivot.axis
        base_pivot_axis.scaleBy(-1)
        matrix = Matrix3D.create()
        matrix.setToRotateTo(
            key_pivot.axis,
            base_pivot_axis)
        key.transform(matrix)

        key.place(
            ~key_pivot == ~base_pivot,
            ~key_pivot == ~base_pivot,
            -key_pivot == -base_pivot)

    def add_thumb_standoffs(self, thumb_cluster):
        """Add standoffs to a thumb cluster assembly

        :param thumb_cluster: A thumb cluster assembly, as returned by positioned_thumb_assembly
        :return: A Group containing the 3 standoffs for the given cluster
        """

        front_magnet: Box = thumb_cluster.find_children("front_magnet")[0]
        down_normal = front_magnet.bottom.get_plane().normal
        ball_magnet_radius = self.ball_magnet().size().z / 2
        down_normal.normalize()
        down_normal.scaleBy(-ball_magnet_radius)
        ball_magnet_center_vector = down_normal

        cluster_transform = thumb_cluster.find_children("thumb_cluster", recursive=False)[0].world_transform()
        cluster_transform_array = cluster_transform.asArray()

        rz = math.degrees(math.atan2(cluster_transform_array[4], cluster_transform_array[0]))

        front_point = thumb_cluster.find_children("front_magnet")[0].named_point("center_bottom").point
        front_point.translateBy(ball_magnet_center_vector)
        front_standoff = self.standoff_by_ball_center(front_point, name="front_standoff")
        front_standoff.rz(rz, center=front_standoff.mid())

        side_point = thumb_cluster.find_children("side_magnet")[0].named_point("center_bottom").point
        side_point.translateBy(ball_magnet_center_vector)
        side_standoff = self.standoff_by_ball_center(side_point, name="side_standoff")
        side_standoff.rz(rz, center=side_standoff.mid())

        back_point = thumb_cluster.find_children("back_magnet")[0].named_point("center_bottom").point
        back_point.translateBy(ball_magnet_center_vector)
        back_standoff = self.standoff_by_ball_center(back_point, name="back_standoff")
        back_standoff.rz(rz, center=back_standoff.mid())

        return Group([front_standoff, side_standoff, back_standoff], name="standoffs")

    def positioned_thumb_assembly(self, placement: 'AbsoluteThumbClusterPlacement', left_hand=False):
        suffix = "left" if left_hand else "right"
        base = self.thumb_base("thumb_cluster")

        pcb = self.thumb_pcb(base, name="thumb_pcb_" + suffix)
        if left_hand:
            base = base.scale(-1, 1, 1, center=base.mid())
            pcb.scale(-1, 1, 1, center=base.mid())

        down_key = base.find_children("thumb_down_key", recursive=False)[0]
        down_key_top = down_key.named_faces("top")[0]
        down_key.add_named_point("front_upper_mid", (
            down_key.mid().x,
            down_key.max().y,
            down_key.max().z))

        outer_lower_key = self.outer_lower_thumb_key()
        outer_lower_key.rx(90)
        self._align_side_key(base.find_children("lower_outer_base")[0], outer_lower_key)

        outer_upper_key = self.outer_upper_thumb_key()
        outer_upper_key.rx(90)
        self._align_side_key(base.find_children("upper_outer_base")[0], outer_upper_key)

        inner_key = self.inner_thumb_key()
        inner_key.rx(90)
        self._align_side_key(base.find_children("inner_key_base")[0], inner_key)

        mode_key = self.thumb_mode_key("thumb_mode_key_" + suffix)
        mode_key.rx(90)
        if left_hand:
            mode_key.scale(-1, 1, 1)
        self._align_side_key(base.find_children("upper_key_base")[0], mode_key)

        insertion_tool = self.thumb_cluster_insertion_tool(base)

        side_magnet_cutout = base.find_children("side_attachment")[0].find_children("magnet_cutout")[0]
        back_magnet_cutout = base.find_children("back_attachment")[0].find_children("magnet_cutout")[0]
        front_magnet_cutout = base.find_children("front_attachment")[0].find_children("magnet_cutout")[0]

        side_magnet = Box((1/8) * 25.4, (1/8) * 25.4, (1/16) * 25.4, name="side_magnet")
        side_magnet.place(
            ~side_magnet == ~side_magnet_cutout,
            ~side_magnet == ~side_magnet_cutout,
            +side_magnet == +side_magnet_cutout)
        side_magnet.add_named_point("center_bottom",
                                    Point3D.create(
                                        side_magnet.mid().x,
                                        side_magnet.mid().y,
                                        side_magnet.min().z))

        back_magnet = Box((1/8) * 25.4, (1/8) * 25.4, (1/16) * 25.4, name="back_magnet")
        back_magnet.place(
            ~back_magnet == ~back_magnet_cutout,
            ~back_magnet == ~back_magnet_cutout,
            +back_magnet == +back_magnet_cutout)
        back_magnet.add_named_point("center_bottom",
                                     Point3D.create(
                                         back_magnet.mid().x,
                                         back_magnet.mid().y,
                                         back_magnet.min().z))

        front_magnet = Box((1/8) * 25.4, (1/8) * 25.4, (1/16) * 25.4, name="front_magnet")
        front_magnet.place(
            ~front_magnet == ~front_magnet_cutout,
            ~front_magnet == ~front_magnet_cutout,
            +front_magnet == +front_magnet_cutout)
        front_magnet.add_named_point("center_bottom",
                                     Point3D.create(
                                         front_magnet.mid().x,
                                         front_magnet.mid().y,
                                         front_magnet.min().z))

        cluster_group = Group([base,
                               down_key,
                               outer_lower_key,
                               outer_upper_key,
                               inner_key,
                               mode_key,
                               insertion_tool,
                               pcb,
                               side_magnet,
                               back_magnet,
                               front_magnet], name="thumb_cluster_" + suffix)

        # down_key was already part of another component, so cluster_group has a new copy of it.
        # we need to get a reference of this new copy instead
        down_key = cluster_group.find_children(down_key.name, recursive=False)[0]
        cluster_group.transform(placement.rotation_matrix )
        rotation_matrix_array = placement.rotation_matrix .asArray()
        rz = math.degrees(math.atan2(rotation_matrix_array[4], rotation_matrix_array[0]))

        front_upper_mid = down_key.named_point("front_upper_mid")
        cluster_group.place(
            ~front_upper_mid == placement.position,
            ~front_upper_mid == placement.position,
            ~front_upper_mid == placement.position)

        cluster_group = Group(
            cluster_group.children(),
            name="thumb_cluster_assembly")

        return cluster_group

    @MemoizableDesign.MemoizeComponent
    def thumb_assembly(self, left_hand=False):
        suffix = "left" if left_hand else "right"
        base = self.thumb_base("thumb_cluster_" + suffix)
        down_key = base.find_children("thumb_down_key", recursive=False)[0]

        outer_lower_key = self.outer_lower_thumb_key()
        outer_lower_key.rx(90)
        self._align_side_key(base.find_children("lower_outer_base")[0], outer_lower_key)

        outer_upper_key = self.outer_upper_thumb_key()
        outer_upper_key.rx(90)
        self._align_side_key(base.find_children("upper_outer_base")[0], outer_upper_key)

        inner_key = self.inner_thumb_key()
        inner_key.rx(90)
        self._align_side_key(base.find_children("inner_key_base")[0], inner_key)

        mode_key = self.thumb_mode_key("thumb_mode_key_" + suffix)
        mode_key.rx(90)
        self._align_side_key(base.find_children("upper_key_base")[0], mode_key)

        insertion_tool = self.thumb_cluster_insertion_tool(base)

        pcb = self.thumb_pcb(base, name="thumb_pcb_" + suffix)

        side_magnet_cutout = base.find_children("side_attachment")[0].find_children("magnet_cutout")[0]
        back_magnet_cutout = base.find_children("back_attachment")[0].find_children("magnet_cutout")[0]
        front_magnet_cutout = base.find_children("front_attachment")[0].find_children("magnet_cutout")[0]

        side_magnet = Box((1/8) * 25.4, (1/8) * 25.4, (1/16) * 25.4, name="side_magnet")
        side_magnet.place(
            ~side_magnet == ~side_magnet_cutout,
            ~side_magnet == ~side_magnet_cutout,
            +side_magnet == +side_magnet_cutout)

        back_magnet = Box((1/8) * 25.4, (1/8) * 25.4, (1/16) * 25.4, name="back_magnet")
        back_magnet.place(
            ~back_magnet == ~back_magnet_cutout,
            ~back_magnet == ~back_magnet_cutout,
            +back_magnet == +back_magnet_cutout)

        front_magnet = Box((1/8) * 25.4, (1/8) * 25.4, (1/16) * 25.4, name="front_magnet")
        front_magnet.place(
            ~front_magnet == ~front_magnet_cutout,
            ~front_magnet == ~front_magnet_cutout,
            +front_magnet == +front_magnet_cutout)

        side_support = self.screw_support_assembly(13, 8, 3, name="side_support")
        side_ball_magnet = side_support.find_children("ball_magnet")[0]

        back_support = self.screw_support_assembly(13, 8, 4, name="back_support")
        back_ball_magnet = back_support.find_children("ball_magnet")[0]

        front_support = self.screw_support_assembly(13, 8, 0, name="front_support")
        front_ball_magnet = front_support.find_children("ball_magnet")[0]

        cluster_group = Group([base,
                               down_key,
                               outer_lower_key,
                               outer_upper_key,
                               inner_key,
                               mode_key,
                               insertion_tool,
                               pcb,
                               side_magnet,
                               back_magnet,
                               front_magnet], name="thumb_cluster_" + suffix)

        cluster_group.place(
            ~front_magnet == ~front_support,
            ~front_magnet == ~front_support,
            -front_magnet == +front_support)

        ball_magnet_radius = side_ball_magnet.size().z / 2
        cluster_group.add_named_point("side_support_point",
                                      Point3D.create(
                                          side_magnet.mid().x,
                                          side_magnet.mid().y,
                                          side_magnet.min().z - ball_magnet_radius))
        cluster_group.add_named_point("back_support_point",
                                      Point3D.create(
                                          back_magnet.mid().x,
                                          back_magnet.mid().y,
                                          back_magnet.min().z - ball_magnet_radius))
        cluster_group.add_named_point("front_support_point",
                                      Point3D.create(
                                          front_magnet.mid().x,
                                          front_magnet.mid().y,
                                          front_magnet.min().z - ball_magnet_radius))

        first_rotation = self.rotate_to_height_matrix(
            front_ball_magnet.mid(),
            Vector3D.create(1, 0, 0),
            cluster_group.named_point("side_support_point").point,
            side_ball_magnet.mid().z)
        cluster_group.transform(first_rotation)

        side_support.place(
            ~side_ball_magnet == cluster_group.named_point("side_support_point"),
            ~side_ball_magnet == cluster_group.named_point("side_support_point"),
            ~side_ball_magnet == cluster_group.named_point("side_support_point"))

        second_rotation = self.rotate_to_height_matrix(
            front_ball_magnet.mid(),
            front_ball_magnet.mid().vectorTo(side_ball_magnet.mid()),
            cluster_group.named_point("back_support_point").point,
            back_ball_magnet.mid().z)
        cluster_group.transform(second_rotation)

        back_support.place(
            ~back_ball_magnet == cluster_group.named_point("back_support_point"),
            ~back_ball_magnet == cluster_group.named_point("back_support_point"),
            ~back_ball_magnet == cluster_group.named_point("back_support_point"))

        if left_hand:
            cluster_group.scale(-1, 1, 1, center=(0, 0, 0))
            front_support.scale(-1, 1, 1, center=(0, 0, 0))
            side_support.scale(-1, 1, 1, center=(0, 0, 0))
            back_support.scale(-1, 1, 1, center=(0, 0, 0))

        return Group([cluster_group, front_support, side_support, back_support], name="thumb_assembly_" + suffix)

    def place_header(self, header: Component, x: int, y: int):
        pin_size = min(header.size().x, header.size().y)

        header.place((-header == x * 2.54) + pin_size / 2,
                     (-header == y * 2.54) + pin_size / 2,
                     ~header == 0)

    @MemoizableDesign.MemoizeComponent
    def central_pcb(self):
        base = Box(42, 67, 1.6)

        upper_left_screw_hole = Cylinder(base.size().z, 3.1/2, name="screw_hole")
        upper_left_screw_hole.place(
            (-upper_left_screw_hole == -base) + 2,
            (+upper_left_screw_hole == +base) - 2,
            ~upper_left_screw_hole == ~base)

        lower_right_screw_hole = Cylinder(base.size().z, 3.1/2, name="screw_hole")
        lower_right_screw_hole.place(
            (+lower_right_screw_hole == +base) - 2,
            (-lower_right_screw_hole == -base) + 2,
            ~lower_right_screw_hole == ~base)

        antenna_extension = Box(18, 10, .8, name="antenna")
        antenna_extension.place(
            (-antenna_extension == -base) + 4.7,
            (-antenna_extension == -base) - 6.5,
            -antenna_extension == +base)

        pcb = Difference(
            Union(base, antenna_extension), upper_left_screw_hole, lower_right_screw_hole, name="central_pcb")
        pcb.add_named_faces("bottom", *pcb.find_faces(base.bottom))
        return pcb

    @MemoizableDesign.MemoizeComponent
    def central_pcb_sketch(self):
        pcb = self.central_pcb()

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

    def central_pcb_tray(self):
        pcb = self.central_pcb()

        bottom_thickness = 1.2
        base = Box(pcb.size().x + 2.3*2,
                   pcb.size().y + 2.3*2,
                   10)

        base.place(~base == ~pcb,
                   ~base == ~pcb,
                   (-base == -pcb) - bottom_thickness)

        back_magnet = self.horizontal_large_thin_magnet_cutout(name="back_cutout")
        back_magnet.rz(180)
        back_magnet.place(~back_magnet == ~base,
                          +back_magnet == +base,
                          +back_magnet == 8)

        left_magnet = self.horizontal_large_thin_magnet_cutout(name="left_cutout")
        left_magnet.rz(-90)
        left_magnet.place(-left_magnet == -base,
                          (-left_magnet == -base) + 5,
                          +left_magnet == 8)

        right_magnet = self.horizontal_large_thin_magnet_cutout(name="left_cutout")
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

    @MemoizableDesign.MemoizeComponent
    def key_breakout_pcb(self):
        base = Box(20, 13, 1.2)

        upper_connector_holes = self.hole_array(.35, 1.5, 7)
        upper_connector_holes.place(~upper_connector_holes == ~base,
                                    (~upper_connector_holes == +base) - 2.2,
                                    -upper_connector_holes == -base)

        lower_connector_holes = upper_connector_holes.copy()
        lower_connector_holes.place(y=(~lower_connector_holes == -base) + 2.2)

        header_holes = self.hole_array(.40, 2.54, 7)
        header_holes.place(~header_holes == ~base,
                           ~header_holes == ~base,
                           -header_holes == -base)

        all_holes = Union(upper_connector_holes, lower_connector_holes, header_holes)
        all_holes = ExtrudeTo(all_holes, base)

        result = Difference(base, all_holes)
        result.add_named_faces("bottom", *result.find_faces(base.bottom))
        return result

    @MemoizableDesign.MemoizeComponent
    def key_breakout_pcb_sketch(self):
        pcb = self.key_breakout_pcb()

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

    @MemoizableDesign.MemoizeComponent
    def handrest_design(self, left_hand=False):
        script_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
        script_dir = os.path.dirname(script_path)

        handrest_model = import_fusion_archive(
            os.path.join(script_dir, "left_handrest.f3d"), name="handrest")
        handrest_model.scale(10, 10, 10)
        handrest_model.place(~handrest_model == 0,
                             ~handrest_model == 0,
                             -handrest_model == 0)

        pcb = self.central_pcb()

        pcb_slot = Box(pcb.bounding_box.size().x + 2,
                       pcb.bounding_box.size().y * 10,
                       20)
        # temporary placement, in order to find the cut face of the handrest, which is needed to place the pcb
        pcb_slot.place(~pcb_slot == ~handrest_model,
                       ~pcb_slot == ~handrest_model,
                       -pcb_slot == -handrest_model)

        pcb_slot_front_cut_face_tool = Scale(pcb_slot.copy(), .5, 1, .5, center=pcb_slot.mid())
        pcb_slot_front_cut_face_tool.place(y=-pcb_slot_front_cut_face_tool == ~handrest_model)
        # this is the front face of the handrest that will be cut out by the slot
        pcb_slot_front_cut_face = Intersection(handrest_model, pcb_slot).find_faces(
            Intersection(handrest_model, pcb_slot_front_cut_face_tool))[0]

        pcb.place(
            ~pcb == ~pcb_slot,
            (+pcb == -pcb_slot_front_cut_face) - 5,
            (-pcb == -handrest_model) + 2.4)

        pcb_slot.place(
            y=(-pcb_slot == -pcb) + 20)

        # make the back of the slot a bit shorter, to leave plenty of plastic between the top of the slot and the
        # top of the handrest
        shorter_pcb_slot = Box(pcb_slot.size().x, pcb_slot.size().y, pcb_slot.size().z * .75)
        shorter_pcb_slot.place(
            ~shorter_pcb_slot == ~pcb_slot,
            (-shorter_pcb_slot == -pcb) - 2,
            -shorter_pcb_slot == -handrest_model)

        front_left_bottom_magnet = self.vertical_large_thin_magnet_cutout(depth=1, name="bottom_magnet")
        front_left_bottom_magnet.rx(180)
        front_left_bottom_magnet.place((~front_left_bottom_magnet == ~handrest_model) + 27.778,
                                       (~front_left_bottom_magnet == ~handrest_model) + 13.2784,
                                       -front_left_bottom_magnet == -handrest_model)

        front_right_bottom_magnet = self.vertical_large_thin_magnet_cutout(depth=1, name="bottom_magnet")
        front_right_bottom_magnet.rx(180)
        front_right_bottom_magnet.place((~front_right_bottom_magnet == ~handrest_model) - 29.829,
                                        (~front_right_bottom_magnet == ~handrest_model) + 13.2782,
                                        -front_right_bottom_magnet == -handrest_model)

        back_right_bottom_magnet = self.vertical_large_thin_magnet_cutout(depth=1, name="bottom_magnet")
        back_right_bottom_magnet.rx(180)
        back_right_bottom_magnet.place((~back_right_bottom_magnet == ~handrest_model) - 29.829,
                                       (~back_right_bottom_magnet == ~handrest_model) - 37.7218,
                                       -back_right_bottom_magnet == -handrest_model)

        back_left_bottom_magnet = self.vertical_large_thin_magnet_cutout(depth=1, name="bottom_magnet")
        back_left_bottom_magnet.rx(180)
        back_left_bottom_magnet.place((~back_left_bottom_magnet == ~handrest_model) + 27.778,
                                      (~back_left_bottom_magnet == ~handrest_model) - 37.7218,
                                      -back_left_bottom_magnet == -handrest_model)

        handrest = Difference(handrest_model, pcb_slot, shorter_pcb_slot, front_left_bottom_magnet,
                              front_right_bottom_magnet, back_right_bottom_magnet, back_left_bottom_magnet,
                              name="left_handrest" if left_hand else "right_handrest")

        if not left_hand:
            handrest.scale(-1, 1, 1, center=handrest.mid())

        assembly = Group([handrest], [pcb], name=handrest.name)

        return assembly

    @MemoizableDesign.MemoizeComponent
    def steel_sheet_design(self, left_hand=True):
        cluster_area = Rect(50, 90)
        cluster_area.place(
            ~cluster_area == 0,
            ~cluster_area == 0,
            ~cluster_area == 0)

        def radial_translate(component, theta, r):
            x = r * math.sin(math.radians(theta))
            y = r * math.cos(math.radians(theta))
            component.tx(x)
            component.ty(y)

        cluster_1_area = cluster_area.copy(name="cluster_1_area")
        radial_translate(cluster_1_area, 0, 100)

        cluster_2_area = cluster_area.copy(name="cluster_2_area")
        radial_translate(cluster_2_area, -15, 110)
        cluster_2_area.rz(15, center=cluster_2_area.mid())

        cluster_3_area = cluster_area.copy(name="cluster_3_area")
        radial_translate(cluster_3_area, -30, 110)
        cluster_3_area.rz(30, center=cluster_3_area.mid())

        cluster_4_area = cluster_area.copy(name="cluster_4_area")
        radial_translate(cluster_4_area, -45, 95)
        cluster_4_area.rz(45, center=cluster_4_area.mid())

        thumb_cluster_area = Rect(60, 85, name="thumb_cluster_area")
        thumb_cluster_area.place(
            ~thumb_cluster_area == 0,
            ~thumb_cluster_area == 0,
            ~thumb_cluster_area == 0)

        thumb_cluster_trim_tool = Rect(100, 100)
        thumb_cluster_trim_tool.place(
            -thumb_cluster_trim_tool == +thumb_cluster_area,
            -thumb_cluster_trim_tool == -thumb_cluster_area)
        thumb_cluster_trim_tool.rz(-50, center=thumb_cluster_trim_tool.min())
        thumb_cluster_trim_tool.tx(-40)

        thumb_cluster_area = Difference(thumb_cluster_area, thumb_cluster_trim_tool, name=thumb_cluster_area.name)

        radial_translate(thumb_cluster_area, 45, 75)
        thumb_cluster_area.rz(15, center=thumb_cluster_area.mid())

        group = Group(
            [cluster_1_area, cluster_2_area, cluster_3_area, cluster_4_area, thumb_cluster_area], name="metal_base")

        # Now position everything so that it's in the correct position relative to the handrest in it's default
        # "as-imported" position
        group.tx(9.3)
        group.ty(18.3)

        if not left_hand:
            group.scale(-1, 1, 1, center=(0, 0, 0))

        hull = Hull(group, name="exposed_steel")
        return OffsetEdges(hull.faces[0], hull.faces[0].edges, 5, name="sheet_sheet")

    def central_pcb_spacer(self, thickness=2.4):
        central_pcb = self.central_pcb()

        bottom_face = central_pcb.named_faces("bottom")[0]
        spacer = Extrude(bottom_face.make_component(), thickness)

        connector_cutout = Box(
            13,
            23,
            spacer.size().z)
        connector_cutout.place(
            +connector_cutout == +spacer,
            (+connector_cutout == +spacer) - 19,
            -connector_cutout == -spacer)

        usb_port_cutout = Box(
            spacer.size().x - 7.5 - 3,
            10,
            spacer.size().z)

        usb_port_cutout.place(
            (+usb_port_cutout == +spacer) - 3,
            +usb_port_cutout == +spacer,
            -usb_port_cutout == -spacer)

        buttons_cutout = Box(
            10,
            21,
            spacer.size().z)
        buttons_cutout.place(
            -buttons_cutout == -spacer,
            (+buttons_cutout == +spacer) - 16.5,
            -buttons_cutout == -spacer)

        esp_cutout = Box(
            6,
            6,
            spacer.size().z)
        esp_cutout.place(
            (~esp_cutout == -spacer) + 15,
            (~esp_cutout == -spacer) + 9.5,
            -esp_cutout == -spacer)

        spacer = Difference(spacer, connector_cutout, usb_port_cutout, buttons_cutout, esp_cutout, name="pcb_spacer")
        return spacer

    @MemoizableDesign.MemoizeComponent
    def steel_base(self, left_hand=True):
        total_thickness = 6
        steel_thickness = .6
        bottom_thickness = 2
        upper_thickness = 2

        sheet = self.steel_sheet_design(left_hand=left_hand)
        extruded_sheet = Extrude(sheet.copy(), -steel_thickness, name="steel_sheet")

        # Used to add some tolerance between the steel sheet and the lower part of the base..
        # and also between the part of the upper base that fits into the lower base.
        embiggened_sheet = OffsetEdges(sheet.faces[0], sheet.faces[0].edges, .2)

        handrest = self.handrest_design(left_hand=left_hand)

        # get the handrest without the magnet holes or inner void
        full_handrest = handrest.find_children("handrest")[0]

        pcb = handrest.find_children("central_pcb")[0].copy()

        extruded_sheet.place(
            z=(-extruded_sheet == -handrest) - total_thickness + bottom_thickness)

        handrest_bottom_finder = Rect(handrest.size().x, handrest.size().y)
        handrest_bottom_finder.place(
            ~handrest_bottom_finder == ~handrest,
            ~handrest_bottom_finder == ~handrest,
            ~handrest_bottom_finder == -handrest)

        handrest_bottom = full_handrest.find_faces(handrest_bottom_finder)[0]

        front_half_tool = handrest_bottom.bounding_box.make_box()
        front_half_tool.place(
            ~front_half_tool == ~handrest_bottom,
            -front_half_tool == ~handrest_bottom,
            ~front_half_tool == ~handrest_bottom)

        handrest_bottom_front_half = Intersection(handrest_bottom.make_component(), front_half_tool)

        base_outline = Union(
            Hull(Group([
                handrest_bottom_front_half.scale(1, 1, -1),
                OffsetEdges(sheet.faces[0], sheet.faces[0].edges, 2)])),
            handrest_bottom.make_component())

        base_bottom = Extrude(base_outline.copy(), bottom_thickness)
        base_bottom.place(
            z=+base_bottom == -extruded_sheet)

        bottom_raised_edges = Extrude(
            Difference(base_outline.copy(), embiggened_sheet.copy()),
            total_thickness - bottom_thickness - upper_thickness)
        bottom_raised_edges.place(
            z=-bottom_raised_edges == +base_bottom)

        lower_base = Union(base_bottom, bottom_raised_edges, name="lower_base")

        exposed_steel = sheet.find_children("exposed_steel")[0].copy()

        upper_base = Extrude(
            Difference(base_outline.copy(), exposed_steel.copy()), upper_thickness, name="upper_base")
        upper_base.place(
            z=+upper_base == -handrest)

        upper_base_lower_trim = Extrude(
            Union(
                Difference(sheet.copy(), exposed_steel.copy()),
                Intersection(handrest_bottom.make_component(), sheet.copy())),
            (upper_base.max().z - extruded_sheet.max().z) - .2)

        upper_base_lower_trim.place(
            z=+upper_base_lower_trim == +upper_base)

        upper_base = Union(upper_base, upper_base_lower_trim, name=upper_base.name)

        def screw_and_nut():
            nut = Box(6, 6, 5, name="nut")
            shaft = Cylinder(5.8, 3.1/2, name="shaft")
            # the shaft is slightly disconnected form the nut, so that there will be a single sacrifical solid layer
            # above the nut to avoid having to use supports for the underside-hole for the nut.
            shaft.place(
                ~shaft == ~nut,
                ~shaft == ~nut,
                (-shaft == +nut) + .2)
            return Union(nut, shaft, name="screw")

        pcb_screw_holes = pcb.find_children("screw_hole")
        screws = []
        for screw_hole in pcb_screw_holes:
            screw = screw_and_nut()
            screw.place(
                ~screw == ~screw_hole,
                ~screw == ~screw_hole,
                +screw.find_children("nut")[0] == -extruded_sheet)
            screws.append(screw)

        pcb = handrest.find_children("central_pcb")[0]
        pcb_spacer = self.central_pcb_spacer()
        pcb_spacer.place(
            ~pcb_spacer == ~pcb,
            +pcb_spacer == +pcb,
            -pcb_spacer == +upper_base)

        magnet_risers = []
        magnet_riser_cutouts = []
        handrest_magnet_cutouts = []
        for magnet in handrest.find_children("bottom_magnet"):
            magnet_cutout = self.deep_large_thin_magnet_cutout()
            magnet_cutout.place(
                ~magnet_cutout == ~magnet,
                ~magnet_cutout == ~magnet,
                +magnet_cutout == -magnet)
            handrest_magnet_cutouts.append(magnet_cutout)

            magnet_riser = Box(magnet_cutout.size().x + 4, magnet_cutout.size().x + 4, upper_thickness)
            magnet_riser.place(
                ~magnet_riser == ~magnet_cutout,
                ~magnet_riser == ~magnet_cutout,
                -magnet_riser == +lower_base)
            magnet_risers.append(magnet_riser)

            # The cutout for the magnet risers in the upper base
            magnet_riser_cutout = Box(
                magnet_riser.size().x + .6,
                magnet_riser.size().x + .6,
                magnet_riser.size().z)
            magnet_riser_cutout.place(
                ~magnet_riser_cutout == ~magnet_riser,
                ~magnet_riser_cutout == ~magnet_riser,
                ~magnet_riser_cutout == ~magnet_riser)
            magnet_riser_cutouts.append(magnet_riser_cutout)

        trim_magnets = []

        def find_vertex(brep, comparison):
            target_vertex = None
            for vertex in brep.vertices:
                if target_vertex is None or comparison(vertex, target_vertex):
                    target_vertex = vertex
            return target_vertex

        def place_trim_magnet(vertex):
            vertex_vector = Vector3D.create(vertex.geometry.x, vertex.geometry.y, 0)
            # add 2.5mm to the length, in the same direction from the origin to the vertex
            vertex_vector.scaleBy((vertex_vector.length + 2.5)/vertex_vector.length)
            trim_magnet = self.vertical_magnet_cutout()
            trim_magnet.place(
                ~trim_magnet == vertex_vector.x,
                ~trim_magnet == vertex_vector.y,
                -trim_magnet == -upper_base_lower_trim)
            return trim_magnet

        # This finds the vertex of the "cluster rectangle" that was used to build the shape of the steel plate
        # and then uses that to place a magnet a bit further, into the upper base trim.
        if left_hand:
            vertex = find_vertex(sheet.find_children("cluster_3_area")[0].bodies[0].brep,
                                 lambda v1, v2: v1.geometry.x < v2.geometry.x)
        else:
            vertex = find_vertex(sheet.find_children("cluster_3_area")[0].bodies[0].brep,
                                 lambda v1, v2: v1.geometry.x > v2.geometry.x)
        trim_magnets.append(place_trim_magnet(vertex))

        vertex = find_vertex(sheet.find_children("cluster_2_area")[0].bodies[0].brep,
                             lambda v1, v2: v1.geometry.y > v2.geometry.y)
        trim_magnets.append(place_trim_magnet(vertex))

        vertex = find_vertex(sheet.find_children("thumb_cluster_area")[0].bodies[0].brep,
                             lambda v1, v2: v1.geometry.y > v2.geometry.y)
        trim_magnets.append(place_trim_magnet(vertex))

        lower_base = Difference(
            Union(lower_base, *magnet_risers), *screws, *handrest_magnet_cutouts, name=lower_base.name)
        upper_base = Difference(upper_base, *screws, *magnet_riser_cutouts, *trim_magnets, name=upper_base.name)

        return Group([
            extruded_sheet,
            handrest,
            lower_base,
            upper_base,
            pcb_spacer],
            name="steel_base")

    def static_base(self, finger_clusters: Sequence[Component], thumb_cluster: Component, left_hand=True):
        handrest = self.handrest_design(left_hand)

        supports = []
        for finger_cluster in finger_clusters:
            supports.append(self.static_cluster_support(finger_cluster).copy(copy_children=False))
        supports.append(self.static_thumb_support(thumb_cluster).copy(copy_children=False))

        # get the handrest without the magnet holes or inner void
        full_handrest = handrest.find_children("handrest")[0]

        pcb = handrest.find_children("central_pcb")[0].copy()

        temp_group = Group([*supports, full_handrest])

        bottom_finder = temp_group.bounding_box.make_box()
        bottom_finder.place(z=+bottom_finder == -temp_group)

        bottom_faces = Group([face.make_component() for face in temp_group.find_faces(bottom_finder)])
        base = Extrude(Hull(bottom_faces), -3)

        def screw_and_nut():
            nut = Box(6, 6, 2, name="nut")
            shaft = Cylinder(5.8, 3.1/2, name="shaft")
            # the shaft is slightly disconnected form the nut, so that there will be a single sacrifical solid layer
            # above the nut to avoid having to use supports for the underside-hole for the nut.
            shaft.place(
                ~shaft == ~nut,
                ~shaft == ~nut,
                (-shaft == +nut) + .2)
            nut_hole_ceiling = Box(nut.size().x, nut.size().y, .2, name="nut_hole_ceiling")
            nut_hole_ceiling.place(
                ~nut_hole_ceiling == ~nut,
                ~nut_hole_ceiling == ~nut,
                -nut_hole_ceiling == +nut)
            return Group([Union(nut, shaft, name="screw")], [nut_hole_ceiling])

        pcb_screw_holes = pcb.find_children("screw_hole")
        screws = []
        for screw_hole in pcb_screw_holes:
            screw = screw_and_nut()
            screw.place(
                ~screw == ~screw_hole,
                ~screw == ~screw_hole,
                -screw.find_children("nut")[0] == -base)
            screws.append(screw)
        screws = Group(screws, name="screws")

        handrest_magnet_cutouts = []
        for magnet in handrest.find_children("bottom_magnet"):
            magnet_cutout = self.deep_large_thin_magnet_cutout()
            magnet_cutout.place(
                ~magnet_cutout == ~magnet,
                ~magnet_cutout == ~magnet,
                +magnet_cutout == -magnet)
            handrest_magnet_cutouts.append(magnet_cutout)

        return Group([
            Union(
                Difference(
                    base,
                    screws,
                    *handrest_magnet_cutouts),
                *screws.find_children("nut_hole_ceiling"),
                *supports),
            handrest])

    def rotate_to_height_matrix(self, axis_point: Point3D, axis_vector: Vector3D, target_point: Point3D, height: float):
        """Rotate target point around the axis defined by axis_point and axis_vector, such that its final height is
        the specific height.

        There are 2 such rotations of course, so the smaller rotation is used.

        This assumes that axis is not vertical, and that target_point is not on the axis.
        """
        matrix = Matrix3D.create()

        axis = adsk.core.InfiniteLine3D.create(axis_point, axis_vector)
        result = app().measureManager.measureMinimumDistance(target_point, axis)
        distance = result.value
        target_axis_projection = result.positionOne

        circle = Circle(distance)

        matrix.setToRotateTo(
            circle.get_plane().normal,
            axis_vector)

        circle.transform(matrix)
        circle.place(
            ~circle == target_axis_projection,
            ~circle == target_axis_projection,
            ~circle == target_axis_projection)

        # the edge of the circle now corresponds to the path the target point travels as it rotates around axis
        height_plane = adsk.core.Plane.create(
            Point3D.create(0, 0, height),
            Vector3D.create(0, 0, 1))

        intersections = height_plane.intersectWithCurve(circle.edges[0].brep.geometry)
        assert len(intersections) == 2

        first_angle_measurement = app().measureManager.measureAngle(target_point, target_axis_projection, intersections[0])
        second_angle_measurement = app().measureManager.measureAngle(target_point, target_axis_projection, intersections[1])

        # the returned angle seems to be in [0, 180], I think.
        if first_angle_measurement.value < second_angle_measurement.value:
            destination = intersections[0]
        else:
            destination = intersections[1]

        rotation_matrix = Matrix3D.create()
        rotation_matrix.setToRotateTo(
            target_axis_projection.vectorTo(target_point),
            target_axis_projection.vectorTo(destination))

        translation_matrix = Matrix3D.create()
        translation_matrix.translation = target_axis_projection.asVector()
        translation_matrix.invert()

        matrix = Matrix3D.create()
        matrix.transformBy(translation_matrix)
        matrix.transformBy(rotation_matrix)
        translation_matrix.invert()
        matrix.transformBy(translation_matrix)

        return matrix

    @MemoizableDesign.MemoizeComponent
    def _screw_head_cutout(self):
        screw_head = Cylinder(3.4*2, 3, name="screw_head")
        screw_head_extension = Box(
            screw_head.size().x, screw_head.size().y * 2, screw_head.size().z,
            name="screw_head_extension")
        screw_head_extension.place(
            ~screw_head_extension == ~screw_head,
            -screw_head_extension == ~screw_head,
            -screw_head_extension == -screw_head)
        return Union(screw_head, screw_head_extension, name="screw_head_cutout")

    def static_cluster_support(self, cluster: Component):
        body_assembly = self.cluster_body_assembly()
        cluster_front = body_assembly.find_children("cluster_front")[0]
        cluster_back = body_assembly.find_children("cluster_back")[0]

        silhouette = self.cluster_silhouette()

        magnet_cutouts = cluster_back.find_children("magnet_cutout")[0:2]
        magnet_thickness = self.large_magnet().size().z

        base_magnet_cutouts = []
        for magnet_cutout in magnet_cutouts:
            base_magnet_cutout = self.deep_large_thin_magnet_cutout()
            base_magnet_cutout.place(
                ~base_magnet_cutout == ~magnet_cutout,
                ~base_magnet_cutout == ~magnet_cutout,
                +base_magnet_cutout == -cluster_back)
            base_magnet_cutouts.append(base_magnet_cutout)

        front_notch_silhouette_lower = Intersection(silhouette.copy(), cluster_front.find_children("front_notch")[0])
        # offset the sides of the notch silhouette, for some clearance

        for edge in list(front_notch_silhouette_lower.faces[0].edges):
            if isinstance(edge.brep.geometry, adsk.core.Line3D) and edge.brep.geometry.asInfiniteLine().direction.x == 0:
                front_notch_silhouette_lower = OffsetEdges(
                    front_notch_silhouette_lower.faces[0],
                    front_notch_silhouette_lower.find_edges(edge),
                    -.2)

        front_notch_silhouette_upper = front_notch_silhouette_lower.copy()
        front_notch_silhouette_upper.place(
            z=(~front_notch_silhouette_upper == +cluster_front.find_children("front_notch")[0]) - .2)

        front_notch_top_surface = cluster_front.find_children("front_notch")[0].top.make_component()
        front_notch_top_surface.tz(-.2)

        pcb = body_assembly.find_children("pcb")[0]
        pcb_back = pcb.find_children("pcb_back_box")[0]

        pcb_cutout = Rect(
            pcb.size().x * 2,
            pcb_back.min().y - pcb.min().y + .4)
        pcb_cutout.place(
            ~pcb_cutout == ~pcb,
            (-pcb_cutout == -pcb) - .3,
            ~pcb_cutout == ~silhouette)

        inner_void_silhouette = Hull(Intersection(pcb_cutout.copy(), silhouette.copy()))

        inner_void_silhouette.add_named_edges(
            "left_edges",
            *[edge for edge in inner_void_silhouette.edges if edge.max().x < inner_void_silhouette.mid().x])
        inner_void_silhouette.add_named_edges(
            "right_edges",
            *[edge for edge in inner_void_silhouette.edges if edge.min().x > inner_void_silhouette.mid().x])

        pcb_back_cutout = Rect(
            pcb_back.size().x + .6,
            pcb_back.size().y + .6)
        pcb_back_cutout.place(
            ~pcb_back_cutout == ~pcb_back,
            ~pcb_back_cutout == ~pcb_back,
            ~pcb_back_cutout == ~pcb_cutout)

        pcb_cutout_lower = Extrude(Union(pcb_cutout, pcb_back_cutout), -1 * (pcb.max().z - body_assembly.min().z + 1))
        pcb_cutout_upper = Extrude(Union(pcb_cutout, pcb_back_cutout), body_assembly.size().z)
        pcb_cutout = Union(pcb_cutout_lower, pcb_cutout_upper)

        inner_void_silhouette.place(
            z=~inner_void_silhouette == -pcb_cutout)

        screw_hole = cluster_back.find_children("screw_hole")[0]
        screw_head_cutout = self._screw_head_cutout()
        screw_head = screw_head_cutout.find_children("screw_head")[0]
        screw_head_cutout.place(
            ~screw_head == ~screw_hole,
            ~screw_head == ~screw_hole,
            ~screw_head_cutout == -pcb)

        cluster_transform = cluster.find_children("cluster", recursive=False)[0].world_transform()

        silhouette.transform(cluster_transform)
        pcb_cutout.transform(cluster_transform)
        front_notch_silhouette_lower.transform(cluster_transform)
        front_notch_top_surface.transform(cluster_transform)
        inner_void_silhouette.transform(cluster_transform)
        screw_head_cutout.transform(cluster_transform)

        for cutout in base_magnet_cutouts:
            cutout.transform(cluster_transform)

        front_notch_silhouette_upper = front_notch_silhouette_lower.copy()
        front_notch_silhouette_upper.align_to(
            front_notch_top_surface,
            Vector3D.create(0, 0, 1))

        bottom_silhouette = Silhouette(
            silhouette,
            adsk.core.Plane.create(
                Point3D.create(0, 0, 0),
                Vector3D.create(0, 0, 1)))

        inner_void_bottom_silhouette = Silhouette(
            inner_void_silhouette,
            bottom_silhouette.get_plane(),
            named_edges={
                "left_edges": inner_void_silhouette.named_edges("left_edges"),
                "right_edges": inner_void_silhouette.named_edges("right_edges")
            })

        # offset the left side inward
        offset_inner_void_bottom_silhouette = OffsetEdges(
            inner_void_bottom_silhouette.faces[0],
            inner_void_bottom_silhouette.named_edges("left_edges"),
            -2)

        # TODO: fix OffsetEdges in fscad so that it handles this case correctly. Currently, it creates a spurious extra
        #  face that we have to exclude
        if len(offset_inner_void_bottom_silhouette.faces) > 1:
            offset_inner_void_bottom_silhouette = offset_inner_void_bottom_silhouette.faces[1].make_component()

        # and the right side
        offset_inner_void_bottom_silhouette = OffsetEdges(
            offset_inner_void_bottom_silhouette.faces[0],
            offset_inner_void_bottom_silhouette.find_edges(inner_void_bottom_silhouette.named_edges("right_edges")),
            -2)

        # TODO: fix OffsetEdges in fscad so that it handles this case correctly. Currently, it creates a spurious extra
        #  face that we have to exclude
        if len(offset_inner_void_bottom_silhouette.faces) > 1:
            offset_inner_void_bottom_silhouette = offset_inner_void_bottom_silhouette.faces[1].make_component()

        inner_void_silhouette = Intersection(
            Extrude(offset_inner_void_bottom_silhouette, cluster.max().z - offset_inner_void_bottom_silhouette.min().z),
            inner_void_silhouette)

        cluster_rz = math.degrees(math.atan2(cluster_transform.asArray()[4], cluster_transform.asArray()[0]))

        cord_slot = Box(3, body_assembly.size().y / 2, cluster.max().z * 2)
        cord_slot.place(
            ~cord_slot == ~body_assembly,
            -cord_slot == -body_assembly,
            -cord_slot == 0)

        cord_slot.rz(cluster_rz)
        cord_slot.translate(*cluster_transform.translation.asArray()[0:2], 0)

        return Difference(
            Union(
                Loft(bottom_silhouette, silhouette),
                Loft(front_notch_silhouette_lower, front_notch_silhouette_upper)),
            pcb_cutout,
            *base_magnet_cutouts,
            Loft(offset_inner_void_bottom_silhouette, inner_void_silhouette),
            screw_head_cutout,
            cord_slot,
            name="static_support")

    @staticmethod
    def _is_matrix_mirrored(matrix: Matrix3D):
        _, x_vector, y_vector, z_vector = matrix.getAsCoordinateSystem()
        return x_vector.crossProduct(y_vector).dotProduct(z_vector) < 0

    def static_thumb_support(self, thumb_cluster: Component):
        thumb_base = self.thumb_base()
        pcb = self.thumb_pcb(thumb_base)

        cluster_transform = thumb_cluster.find_children("thumb_cluster", recursive=False)[0].world_transform()
        left_hand = self._is_matrix_mirrored(cluster_transform)

        down_key_magnet_extension = thumb_base.find_children("down_key_magnet_extension")[0]

        upper_key_base = thumb_base.find_children("upper_key_base")[0]
        upper_key_base_outer_face: Face = upper_key_base.find_children("key_well")[0].front

        side_attachment = thumb_base.find_children("side_attachment")[0]
        side_magnet_cutout = side_attachment.find_children("magnet_cutout")[0]
        back_attachment = thumb_base.find_children("back_attachment")[0]
        back_magnet_cutout = back_attachment.find_children("magnet_cutout")[0]
        front_attachment = thumb_base.find_children("front_attachment")[0]
        front_magnet_cutout = front_attachment.find_children("magnet_cutout")[0]
        magnet_cutouts = (side_magnet_cutout, back_magnet_cutout, front_magnet_cutout)

        cord_slot = Box(3, thumb_cluster.size().x / 2, thumb_cluster.max().z * 10)

        matrix = Matrix3D.create()
        matrix.setToRotateTo(Vector3D.create(0, 1, 0), upper_key_base_outer_face.get_plane().normal)
        cord_slot.transform(matrix)

        cord_slot.place(
            ~cord_slot == ~upper_key_base_outer_face,
            ~cord_slot == ~upper_key_base_outer_face,
            -cord_slot == 0)

        screw_head_cutouts = []
        nut_cutout: Box
        for nut_cutout in thumb_base.find_children("nut_cutout"):
            screw_head_cutout = self._screw_head_cutout()

            matrix = Matrix3D.create()
            matrix.setToRotateTo(
                Vector3D.create(0, 1, 0),
                nut_cutout.back.get_plane().normal,
                Vector3D.create(0, 0, 1))

            screw_head_cutout.transform(matrix)
            screw_head = screw_head_cutout.find_children("screw_head")[0]
            screw_head_cutout.place(
                ~screw_head == ~nut_cutout,
                ~screw_head == ~nut_cutout,
                ~screw_head_cutout == -pcb)
            screw_head_cutouts.append(screw_head_cutout)
        screw_head_cutouts = Group(screw_head_cutouts)

        silhouette = self.thumb_silhouette()

        inner_void_extent = Rect(
            thumb_base.max().x - side_attachment.max().x + .4,
            back_attachment.min().y - down_key_magnet_extension.max().y + .4)
        inner_void_extent.place(
            +inner_void_extent == +thumb_base,
            -inner_void_extent == +down_key_magnet_extension,
            ~inner_void_extent == ~silhouette)

        thumb_body = thumb_base.find_children("body")[0]

        base_magnet_cutouts = []
        for magnet_cutout in magnet_cutouts:
            base_magnet_cutout = self.deep_large_thin_magnet_cutout()
            base_magnet_cutout.place(
                ~base_magnet_cutout == ~magnet_cutout,
                ~base_magnet_cutout == ~magnet_cutout,
                +base_magnet_cutout == -thumb_body)
            base_magnet_cutouts.append(base_magnet_cutout)

        pcb_silhouette = Silhouette(
            pcb.named_faces("top")[0].outer_edges,
            silhouette.get_plane())
        pcb_cutout_profile = OffsetEdges(pcb_silhouette.faces[0], pcb_silhouette.faces[0].edges, .4)

        pcb_cutout = Extrude(
            pcb_cutout_profile,
            -pcb.size().z - 1.4)

        pcb_cutout = Union(pcb_cutout, Thicken(pcb_cutout.find_faces(
            Extrude(
                Hull(pcb_cutout_profile),
                -pcb_cutout.size().z).side_faces), 5))

        key_well_bottom_finder = thumb_base.bounding_box.make_box()
        key_well_bottom_finder.place(z=+key_well_bottom_finder == -thumb_base)
        key_well_silhouettes = []
        for keywell_bottom_face in thumb_base.find_faces(key_well_bottom_finder):
            key_well_silhouettes.append(OffsetEdges(keywell_bottom_face, keywell_bottom_face.edges, .4))

        down_key_bottom_protrusions = Group([
            down_key_magnet_extension,
            thumb_base.find_children("down_key_slot")[0]])
        down_key_bottom_protrusions_silhouette = Rect(
            down_key_bottom_protrusions.size().x + .8,
            down_key_bottom_protrusions.size().y + .4)
        down_key_bottom_protrusions_silhouette.place(
            ~down_key_bottom_protrusions_silhouette == ~down_key_bottom_protrusions,
            -down_key_bottom_protrusions_silhouette == -down_key_bottom_protrusions,
            ~down_key_bottom_protrusions_silhouette == -down_key_bottom_protrusions)

        inner_void_outer_profile = Intersection(inner_void_extent, silhouette.copy())
        # offset the outer edge, to form the wall. The other 3 sides are already at the correct location
        inner_void_profile = OffsetEdges(
            inner_void_outer_profile.faces[0],
            [edge for edge in inner_void_outer_profile.faces[0].edges if
             edge.brep.geometry.startPoint.x > thumb_base.mid().x and
             edge.brep.geometry.endPoint.x > thumb_base.mid().x],
            -2)
        inner_void_profile.place(z=~inner_void_profile == ~key_well_silhouettes[0])

        silhouette.transform(cluster_transform)
        pcb_cutout.transform(cluster_transform)
        inner_void_profile.transform(cluster_transform)

        for cutout in base_magnet_cutouts:
            cutout.transform(cluster_transform)

        screw_head_cutouts.transform(cluster_transform)

        bottom_silhouette = Silhouette(
            silhouette,
            adsk.core.Plane.create(
                Point3D.create(0, 0, 0),
                Vector3D.create(0, 0, 1)))

        inner_void_bottom_silhouette = Silhouette(
            inner_void_profile,
            bottom_silhouette.get_plane())

        key_well_cutouts = []
        for key_well_silhouette in key_well_silhouettes:
            key_well_silhouette.transform(cluster_transform)
            key_well_cutouts.append(Extrude(key_well_silhouette, -thumb_cluster.max().z * 2))

        down_key_bottom_protrusions_silhouette.transform(cluster_transform)

        cluster_rz = math.degrees(math.atan2(cluster_transform.asArray()[4], cluster_transform.asArray()[0]))

        rotated_upper_key_base_external_face = thumb_cluster.find_children(
            "upper_key_base")[0].find_children("key_well")[0].front
        if left_hand:
            cord_slot.scale(-1, 1, 1)
        cord_slot.rz(cluster_rz)
        cord_slot.place(
            ~cord_slot == ~rotated_upper_key_base_external_face,
            ~cord_slot == ~rotated_upper_key_base_external_face)

        return Difference(
            Union(
                Loft(bottom_silhouette, silhouette)),
            *base_magnet_cutouts,
            pcb_cutout,
            *key_well_cutouts,
            Extrude(down_key_bottom_protrusions_silhouette, thumb_cluster.max().z * 2),
            Loft(inner_void_bottom_silhouette, inner_void_profile),
            Extrude(inner_void_profile, silhouette.mid().z - thumb_base.min().z),
            cord_slot,
            screw_head_cutouts,
            name="static_support")


def run_design(design_func, message_box_on_error=False, print_runtime=True, document_name=None, context=None):
    """
    Exactly the same as the standard fscad.run_design, except message_box_on_error is False by default.
    """
    if not document_name:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        filename = module.__file__
        document_name = pathlib.Path(filename).stem

    import fscad
    if isinstance(context, MemoizableDesign):
        fscad.fscad.run_design(design_func, message_box_on_error, print_runtime, document_name, design_args=[context])
    else:
        fscad.fscad.run_design(
            design_func, message_box_on_error, print_runtime, document_name, design_args=[Lalboard()])


class ClusterRotation(object):
    """This is the superclass for the various Placement objects, which handles the common logic for rotation."""

    def __init__(self, context: Lalboard):
        super().__init__()
        self._matrix = Matrix3D.create()
        self._context = context

    @property
    def rotation_matrix(self) -> Matrix3D:
        return self._matrix

    def set_rotation_by_euler_angles(self, rx: float, ry: float, rz: float):
        """Sets the rotation of the cluster by the given euler angles, applied in rx->ry->rz order.

        :param rx: The rotation about the x axis.
        :param ry: The rotation about the y axis.
        :param rz: The rotation about the z axis.
        :return: self.
        """
        self._matrix = Matrix3D.create()

        matrix = Matrix3D.create()
        matrix.setToRotation(math.radians(rx), Vector3D.create(1, 0, 0), Point3D.create(0, 0, 0))
        self._matrix.transformBy(matrix)

        matrix = Matrix3D.create()
        matrix.setToRotation(math.radians(ry), Vector3D.create(0, 1, 0), Point3D.create(0, 0, 0))
        self._matrix.transformBy(matrix)

        matrix = Matrix3D.create()
        matrix.setToRotation(math.radians(rz), Vector3D.create(0, 0, 1), Point3D.create(0, 0, 0))
        self._matrix.transformBy(matrix)

        return self

    def _set_rotation_by_support_lengths(
            self, lengths: Tuple[float, float, float], support_points: Tuple[Point3D, Point3D, Point3D], rz: float):
        """Sets the rotation of the cluster by the lengths of the 3 supports, along with a z-axis rotation.

        This actually over-specifies the rotation, by also specifying the height of the cluster. However, only the
        rotation is actually used. The height is still specified by one of the absolute or relative positional methods,
        even if it doesn't match the height based on the 3 supports here.

        :param lengths: The lengths of the 3 supports
        :param support_points: The centers of the ball magnets that attach to the bottom of the cluster, when it's in
        an unrotated state.
        :param rz: The rotation around the z-axis.
        """
        # just a placeholder object that we can attach named points to
        placeholder = Box(1, 1, 1)

        placeholder.add_named_point("point1", support_points[0])

        placeholder.add_named_point("point2", support_points[1])

        placeholder.add_named_point("point3", support_points[2])

        # first, translate the whole thing up, so that the first point is at the correct height
        placeholder.place(z=~placeholder.named_point("point1") == lengths[0])

        # next, rotate about an axis that runs through the first point and third points, so that the second point is
        # at the correct height.
        # This assumes that the second point is not colinear with the first and third points.
        first_rotation = self._context.rotate_to_height_matrix(
            axis_point=placeholder.named_point("point1").point,
            axis_vector=placeholder.named_point("point1").point.vectorTo(placeholder.named_point("point3").point),
            target_point=placeholder.named_point("point2").point,
            height=lengths[1])
        placeholder.transform(first_rotation)

        # finally, rotate about an axis that runs through the first and second support points, so that
        # the third support point is at the correct height
        second_rotation = self._context.rotate_to_height_matrix(
            axis_point=placeholder.named_point("point1").point,
            axis_vector=placeholder.named_point("point1").point.vectorTo(
                placeholder.named_point("point2").point),
            target_point=placeholder.named_point("point3").point,
            height=lengths[2])

        self._matrix = Matrix3D.create()
        self._matrix.transformBy(first_rotation)
        self._matrix.transformBy(second_rotation)

        existing_rz = math.degrees(math.atan2(self._matrix.asArray()[4], self._matrix.asArray()[0]))

        matrix = Matrix3D.create()
        matrix.setToRotation(math.radians(rz - existing_rz), Vector3D.create(0, 0, 1), Point3D.create(0, 0, 0))
        self._matrix.transformBy(matrix)

    def set_rotation_matrix(self, matrix: Matrix3D):
        """Sets the rotation of the cluster directly, from the given rotation matrix.

        :param matrix: The rotation matrix to use.
        :return: self
        """
        self._matrix = matrix.copy()
        return self


class FingerClusterRotation(ClusterRotation):

    def set_rotation_by_support_lengths(
            self, front: float, back_left: float, back_right: float, rz: float, tall_front_clip=False):
        """Sets the rotation of the cluster by the lengths of the 3 supports, along with a z-axis rotation.

        :param front: The length of the front support.
        :param back_left: The length of the back left support.
        :param back_right: The length of the back right support.
        :param rz: The rotation around the z-axis.
        :param tall_front_clip: If true, the length of the front support assumes that the "tall" front clip is being
        used.
        :return: self
        """
        self._set_rotation_by_support_lengths(
            (front, back_left, back_right),
            self._get_support_points(tall_front_clip),
            rz)

        return self

    def _get_support_points(self, tall_front_clip):
        cluster_body = self._context.cluster_body_assembly(tall_clip=tall_front_clip)

        front_clip = cluster_body.find_children("cluster_front_mount_clip")[0]
        back = cluster_body.find_children("cluster_back")[0]

        front_magnet_cutout = front_clip.find_children("magnet_cutout")[0]
        back_cutouts = sorted(back.find_children("magnet_cutout")[:2], key=lambda cutout: cutout.mid().x)
        back_left_cutout = back_cutouts[0]
        back_right_cutout = back_cutouts[1]

        ball_magnet = self._context.ball_magnet()
        large_magnet = self._context.large_magnet()
        ball_center_offset = large_magnet.size().z + ball_magnet.size().z / 2

        return (
            Point3D.create(
                front_magnet_cutout.mid().x,
                front_magnet_cutout.mid().y,
                front_magnet_cutout.max().z - ball_center_offset),
            Point3D.create(
                back_left_cutout.mid().x,
                back_left_cutout.mid().y,
                back_left_cutout.max().z - ball_center_offset),
            Point3D.create(
                back_right_cutout.mid().x,
                back_right_cutout.mid().y,
                back_right_cutout.max().z - ball_center_offset))


class ThumbClusterRotation(ClusterRotation):

    def set_rotation_by_support_lengths(
            self, front: float, side: float, back: float, rz: float, left_hand=False):
        """Sets the rotation of the cluster by the lengths of the 3 supports, along with a z-axis rotation.

        :param front: The length of the front support.
        :param side: The length of the side support.
        :param back: The length of the back support.
        :param rz: The rotation around the z-axis.
        :param left_hand: Set the rotation for a right hand or left hand thumb
        :return: self
        """
        self._set_rotation_by_support_lengths(
            (front, side, back),
            self._get_support_points(left_hand),
            rz)

        return self

    def _get_support_points(self, left_hand=False):
        base = self._context.thumb_base()
        if left_hand:
            base.scale(-1, 1, 1, center=base.mid())

        front_cutout = base.find_children("front_attachment")[0].find_children("magnet_cutout")[0]
        side_cutout = base.find_children("side_attachment")[0].find_children("magnet_cutout")[0]
        back_cutout = base.find_children("back_attachment")[0].find_children("magnet_cutout")[0]

        ball_magnet = self._context.ball_magnet()
        large_magnet = self._context.large_magnet()
        ball_center_offset = large_magnet.size().z + ball_magnet.size().z / 2

        return (
            Point3D.create(
                front_cutout.mid().x,
                front_cutout.mid().y,
                front_cutout.max().z - ball_center_offset),
            Point3D.create(
                side_cutout.mid().x,
                side_cutout.mid().y,
                side_cutout.max().z - ball_center_offset),
            Point3D.create(
                back_cutout.mid().x,
                back_cutout.mid().y,
                back_cutout.max().z - ball_center_offset))


class AbsoluteFingerClusterPlacement(FingerClusterRotation):
    """Represents the absolute location and orientation of a finger cluster.

    Position can be defined either by cartesian or cylindrical coordinates.

    Rotation can be specified by rx, ry and rz euler angles (applied in that order), or by the lengths of the 3
    supports.
    """

    def __init__(self, context):
        super().__init__(context)
        self._position = Point3D.create(0, 0, 0)

    @property
    def position(self) -> Point3D:
        return self._position

    def set_cartesian(self, x: float, y: float, z: float):
        """Sets the position of the cluster by (x, y, z) cartesian coordinates.

        This coordinate refers to the center of the top of the "down" key.

        :param x: The x coordinate.
        :param y: The y coordinate.
        :param z: The z coordinate.
        :return: self.
        """
        self._position = Point3D.create(x, y, z)
        return self

    def set_cylindrical(self, r: float, theta: float, z: float):
        """Sets the position of the cluster by (r, theta, z) cylindrical coordinates.

        This coordinate refers to the center of the top of the "down" key.

        :param r: The r coordinate.
        :param theta: The theta coordinate, in degrees. A theta of 0 refers to "straight ahead" (e.g. +y in cartesian).
        :param z: The z coordinate.
        :return: self.
        """
        self._position = Point3D.create(
            r * math.sin(math.radians(theta)),
            r * math.cos(math.radians(theta)),
            z)
        return self


class RelativeFingerClusterPlacement(FingerClusterRotation):
    """Represents the relative location and orientation of a finger cluster.

    You can specify the position by either cylindrical or cartesian coordinates.

    ### Relative cylindrical coordinates

    For cylindrical coordinates, you specify the radius and height, and then the theta is chosen such that the cluster
    is placed so that it's touching the previously added cluster. Or if it's the first cluster, the theta will be 0
    degrees - meaning directly forward (see the "gap" section below, to change this)

    ### Relative cartesian coordinates

    For cartesian coordinates, you specify the y and z values, and the x value is chosen such that the cluster is placed
    so that it's touching the previously added cluster. Or if it's the first cluster, x will be set to 0 (see the "gap"
    section below, to change this).

    ### Gap

    In either case, you can specify a gap to leave between this cluster and the previous cluster. This will cause x or
    theta to be chosen such that there is `gap` space between this cluster and the previous cluster. Or in case of the
    first cluster, the gap specifies an offset from the default position of x=0 or theta=0.
    """

    def __init__(self, context):
        super().__init__(context)
        self._positioning = ("cartesian", 0, 0)
        self._gap = 0

    def set_cylindrical(self, r: float, z: float, gap=0.0):
        """Defines the relative position of the cluster via cylindrical coordinates.

        This coordinate refers to the center of the top of the center "down" key. The unspecified `theta` coordinate
        will be chosen such that the distance between this cluster and the previous is `gap`.

        :param r: The cylindrical radius.
        :param z: The height.
        :param gap: The gap to leave between this cluster and the previous. Or if this is the first cluster, this is an
         offset from the default position of theta=0.
        :return: self.
        """
        self._positioning = ("cylindrical", r, z)
        self._gap = gap
        return self

    def set_cartesian(self, y: float, z: float, gap=0.0):
        """Defines the relative position of the cluster via cartesian coordinates.

        This coordinate refers to the center of the top of the center "down" key. The unspecified `x` coordinate will be
        chosen such that the distance between this cluster and the previous is `gap`.

        :param y: The y coordinate.
        :param z: The z coordinate.
        :param gap: The gap to leave between this cluster and the previous. Or if this is the first cluster, this is an
         offset from the default position of x=0.
        ;return: self.
        """
        self._positioning = ("cartesian", y, z)
        self._gap = gap
        return self

    def resolve(self, previous_cluster: Optional[Component], left_hand=False) -> AbsoluteFingerClusterPlacement:
        """Resolves this relative placement, based on the position of the given cluster.

        :param previous_cluster: The assembly component returned by positioned_cluster_assembly for the previous
        cluster. This should be None in case of the cluster for the first finger, in which case the position will be
        resolved relative to the default position of x=0 or theta=0.
        :param left_hand: True if this placement is for the left hand. This will cause the position to be resolved on
        either the right side (left_hand=False) or left side (left_hand=True) of the given cluster_assembly.

        :return: An AbsoluteFingerClusterPlacement for the resolved position.
        """

        if self._positioning[0] == "cartesian":
            return self._resolve_cartesian(previous_cluster, left_hand)
        else:
            return self._resolve_cylindrical(previous_cluster, left_hand)

    def _resolve_cartesian(self, previous_cluster: Optional[Component], left_hand=False):
        cluster_body = self._context.cluster_body_assembly()

        down_key = self._context.center_key()
        center_key_magnet = down_key.find_children("magnet_cutout")[0]
        center_cluster_magnet = cluster_body.find_children("central_magnet_cutout")[0]
        down_key.rx(180).rz(180)
        down_key.place(
            ~center_key_magnet == ~center_cluster_magnet,
            -center_key_magnet == +center_cluster_magnet,
            ~center_key_magnet == ~center_cluster_magnet)

        cluster_body.add_named_point("down_key_top_center", Point3D.create(
            down_key.mid().x,
            down_key.mid().y,
            down_key.max().z))

        cluster_body.transform(self.rotation_matrix)

        if not previous_cluster:
            cluster_body.place(~cluster_body.named_point("down_key_top_center") == 0)
            alignment_direction = None
        elif left_hand:
            cluster_body.place(+cluster_body == -previous_cluster)
            alignment_direction = Vector3D.create(1, 0, 0)
        else:
            cluster_body.place(-cluster_body == +previous_cluster)
            alignment_direction = Vector3D.create(-1, 0, 0)

        cluster_body.place(
            y=~cluster_body.named_point("down_key_top_center") == self._positioning[1],
            z=~cluster_body.named_point("down_key_top_center") == self._positioning[2])

        if previous_cluster:
            cluster_body.align_to(previous_cluster, alignment_direction)

        if self._gap:
            gap = self._gap
            if left_hand:
                gap *= -1
            cluster_body.tx(gap)

        absolute_placement = AbsoluteFingerClusterPlacement(self._context)
        absolute_placement.set_cartesian(*cluster_body.named_point("down_key_top_center").point.asArray())
        absolute_placement.set_rotation_matrix(self.rotation_matrix)

        return absolute_placement

    def _align_to_cylindrical(self, cluster: Component, cluster_point: Point3D, previous_cluster: Component, left_hand):
        """Similar to fscad's Component.align_to, but performing the alignment by tweaking the cylindrical theta."""

        cluster_point = cluster_point.copy()

        cluster_occurrence = Union(
            *[BRepComponent(body.brep) for body in cluster.bodies]).create_occurrence(create_children=False)
        previous_cluster_occurrence = Union(
            *[BRepComponent(body.brep) for body in previous_cluster.bodies]).create_occurrence(create_children=False)

        try:
            while True:
                result = app().measureManager.measureMinimumDistance(
                    cluster_occurrence, previous_cluster_occurrence)

                if result.value < app().pointTolerance:
                    break

                closest_distance_vector = result.positionOne.vectorTo(result.positionTwo)

                tangential_vector = Point3D.create(0, 0, 0).vectorTo(
                    Point3D.create(result.positionOne.x, result.positionOne.y, 0)).crossProduct(Vector3D.create(0, 0, 1))
                tangential_vector.normalize()

                tangential_distance = closest_distance_vector.dotProduct(tangential_vector)

                # We take the shortest distance vector, and find the projection of that in the tangential direction,
                # and then calculate the angle that would result in that sector circumference, at the radius of the
                # cluster point that we're using.
                # This should be a slight underestimate of the required angle, due to the circumferential distance
                # being slightly longer than the linear distance.

                theta_delta = math.degrees(tangential_distance / self._positioning[1])

                # now, calculate the translation needed in order to move the target point on the cluster in an arc
                # with the given angle

                cluster_point_radius = Vector3D.create(cluster_point.x, cluster_point.y, 0).length
                cluster_point_theta = math.degrees(math.atan2(cluster_point.x, cluster_point.y))

                new_point = Point3D.create(
                    cluster_point_radius * math.sin(math.radians(cluster_point_theta + theta_delta)),
                    cluster_point_radius * math.cos(math.radians(cluster_point_theta + theta_delta)),
                    cluster_point.z)

                translation_matrix = Matrix3D.create()
                translation_matrix.translation = cluster_point.vectorTo(new_point)

                transform = cluster_occurrence.transform
                transform.transformBy(translation_matrix)
                cluster_occurrence.transform = transform

                cluster_point.transformBy(translation_matrix)

            cluster.translate(*cluster_occurrence.transform.translation.asArray())
        finally:
            cluster_occurrence.deleteMe()
            previous_cluster_occurrence.deleteMe()

        return self

    def _resolve_cylindrical(self, previous_cluster: Optional[Component], left_hand=False):
        cluster_body = self._context.cluster_body_assembly()

        down_key = self._context.center_key()
        center_key_magnet = down_key.find_children("magnet_cutout")[0]
        center_cluster_magnet = cluster_body.find_children("central_magnet_cutout")[0]
        down_key.rx(180).rz(180)
        down_key.place(
            ~center_key_magnet == ~center_cluster_magnet,
            -center_key_magnet == +center_cluster_magnet,
            ~center_key_magnet == ~center_cluster_magnet)

        cluster_body.add_named_point("down_key_top_center", Point3D.create(
            down_key.mid().x,
            down_key.mid().y,
            down_key.max().z))

        cluster_body.transform(self.rotation_matrix)

        def circumferential_translation_matrix(point: Point3D, theta_delta):
            translated_point = point.copy()

            matrix = Matrix3D.create()
            matrix.setToRotation(math.radians(theta_delta), Vector3D.create(0, 0, 1), Point3D.create(0, 0, 0))
            translated_point.transformBy(matrix)

            matrix = Matrix3D.create()
            matrix.translation = point.vectorTo(translated_point)
            return matrix

        def place_at_radius_matrix(point: Point3D, target_radius):
            radial_vector = Point3D.create(0, 0, 0).vectorTo(Point3D.create(point.x, point.y, 0))

            radial_translation = target_radius - radial_vector.length

            radial_vector.normalize()
            radial_vector.scaleBy(radial_translation)
            matrix = Matrix3D.create()
            matrix.translation = radial_vector
            return matrix

        if not previous_cluster:
            cluster_body.place(
                ~cluster_body.named_point("down_key_top_center") == 0,
                ~cluster_body.named_point("down_key_top_center") == self._positioning[1],
                ~cluster_body.named_point("down_key_top_center") == self._positioning[2])
        elif left_hand:
            cluster_body.place(
                +cluster_body == -previous_cluster,
                ~cluster_body == ~previous_cluster,
                ~cluster_body.named_point("down_key_top_center") == self._positioning[2])
            cluster_body.transform(
                place_at_radius_matrix(cluster_body.named_point("down_key_top_center").point, self._positioning[1]))
            while cluster_body.bounding_box.raw_bounding_box.intersects(
                    previous_cluster.bounding_box.raw_bounding_box):
                cluster_body.transform(
                    circumferential_translation_matrix(cluster_body.named_point("down_key_top_center").point, 5))
        else:
            cluster_body.place(
                -cluster_body == +previous_cluster,
                ~cluster_body == ~previous_cluster,
                ~cluster_body.named_point("down_key_top_center") == self._positioning[2])
            cluster_body.transform(
                place_at_radius_matrix(cluster_body.named_point("down_key_top_center").point, self._positioning[1]))
            while cluster_body.bounding_box.raw_bounding_box.intersects(
                    previous_cluster.bounding_box.raw_bounding_box):
                cluster_body.transform(
                    circumferential_translation_matrix(cluster_body.named_point("down_key_top_center").point, -5))

        if previous_cluster:
            self._align_to_cylindrical(
                cluster_body, cluster_body.named_point("down_key_top_center").point, previous_cluster,
                left_hand=left_hand)

        if self._gap:
            angle = math.atan2(self._gap, self._positioning[1])
            if not left_hand:
                angle *= -1
            down_key_top_center = cluster_body.named_point("down_key_top_center").point
            matrix = Matrix3D.create()
            matrix.setToRotation(angle, Vector3D.create(0, 0, 1), Point3D.create(0, 0, 0))
            rotated_down_key_top_center = down_key_top_center.copy()
            rotated_down_key_top_center.transformBy(matrix)
            cluster_body.translate(
                *down_key_top_center.vectorTo(rotated_down_key_top_center).asArray())

        absolute_placement = AbsoluteFingerClusterPlacement(self._context)
        absolute_placement.set_cartesian(*cluster_body.named_point("down_key_top_center").point.asArray())
        absolute_placement.set_rotation_matrix(self.rotation_matrix)

        return absolute_placement


class AbsoluteThumbClusterPlacement(ThumbClusterRotation):
    """Represents the absolute location and orientation of a thumb cluster.

    The position for the thumb cluster must be defined by cartesian coordinates.

    Rotation can be specified by rx, ry and rz euler angles (applied in that order), or by the lengths of the 3
    supports.
    """

    def __init__(self, context):
        super().__init__(context)
        self._position = Point3D.create(0, 0, 0)

    @property
    def position(self) -> Point3D:
        return self._position

    def set_cartesian(self, x: float, y: float, z: float):
        """Sets the position of the cluster by (x, y, z) cartesian coordinates.

        This coordinate refers to the center of the top back edge of the down key

        :param x: The x coordinate.
        :param y: The y coordinate.
        :param z: The z coordinate.
        :return: self.
        """
        self._position = Point3D.create(x, y, z)
        return self


class RelativeThumbClusterPlacement(ThumbClusterRotation):
    """Represents the relative location and orientation of a thumb cluster.

    Only cartensian coordinates are supported.

    ### Relative cartesian coordinates

    For cartesian coordinates, you specify the y and z values, and the x value is chosen such that the cluster is
    placed so that it's touching the handrest.

    ### Gap

    You can also specify a gap to leave between the thumb cluster and the handrest. This will cause the x coordinate to
    be chosen such that there is `gap` space between this cluster and the handrest.
    """

    def __init__(self, context):
        super().__init__(context)
        self._positioning = (0, 0)
        self._gap = 0

    def set_cartesian(self, y: float, z: float, gap=0.0):
        """Defines the relative position of the cluster via cartesian coordinates.

        This coordinate refers to the center of the top of the center "down" key. The unspecified `x` coordinate will be
        chosen such that the distance between this cluster and the previous is `gap`.

        :param y: The y coordinate.
        :param z: The z coordinate.
        :param gap: The gap to leave between this cluster and the previous. Or if this is the first cluster, this is an
         offset from the default position of x=0.
        ;return: self.
        """
        self._positioning = (y, z)
        self._gap = gap
        return self

    def resolve(self, handrest: Component, left_hand=False) -> AbsoluteThumbClusterPlacement:
        """Resolves this relative placement, based on the position of the given handrest.

        :param handrest: The handrest component that the thumb cluster will be positioned relative to.
        :param left_hand: True if this placement is for the left hand. This will cause the position to be resolved on
        either the right side (left_hand=False) or left side (left_hand=True) of the given cluster_assembly.

        :return: An AbsoluteThumbClusterPlacement for the resolved position.
        """

        body = self._context.thumb_base()

        down_key = body.find_children("thumb_down_key")[0]

        down_key.add_named_point("front_upper_mid", (
            down_key.mid().x,
            down_key.max().y,
            down_key.max().z))

        if left_hand:
            body.scale(-1, 1, 1)

        body.transform(self.rotation_matrix)

        if left_hand:
            body.place(-body == +handrest)
            alignment_direction = Vector3D.create(-1, 0, 0)
        else:
            body.place(+body == -handrest)
            alignment_direction = Vector3D.create(1, 0, 0)

        body.place(
            y=~down_key.named_point("front_upper_mid") == self._positioning[0],
            z=~down_key.named_point("front_upper_mid") == self._positioning[1])

        body.align_to(handrest, alignment_direction)

        if self._gap:
            gap = self._gap
            if not left_hand:
                gap *= -1
            body.tx(gap)

        absolute_placement = AbsoluteThumbClusterPlacement(self._context)
        absolute_placement.set_cartesian(*down_key.named_point("front_upper_mid").point.asArray())
        absolute_placement.set_rotation_matrix(self.rotation_matrix)

        return absolute_placement
