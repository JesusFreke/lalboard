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

import adsk.fusion

import math
import unittest

# note: load_tests is required for the "pattern" test filtering functionality in loadTestsFromModule in run()
from fscad.test_utils import FscadTestCase, load_tests

from fscad.fscad import *
relative_import("../lalboard.py")
import lalboard


context = lalboard.Lalboard()

class FingerClusterPlacementTest(FscadTestCase):

    def test_absolute_cartesian_and_euler_placement(self):

        clusters = [
            context.positioned_cluster_assembly(
                lalboard.AbsoluteFingerClusterPlacement(context)
                        .set_cartesian(8.43, 116.23, 31.09)
                        .set_rotation_by_euler_angles(13.45, -.16, 1.46)),
            context.positioned_cluster_assembly(
                lalboard.AbsoluteFingerClusterPlacement(context)
                        .set_cartesian(-17.77, 120.09, 30.46)
                        .set_rotation_by_euler_angles(13.12, -2.05, 14.03)),
            context.positioned_cluster_assembly(
                lalboard.AbsoluteFingerClusterPlacement(context)
                        .set_cartesian(-43.61, 110.04, 27.73)
                        .set_rotation_by_euler_angles(12.75, -11.36, 21.95)),
            context.positioned_cluster_assembly(
                lalboard.AbsoluteFingerClusterPlacement(context)
                        .set_cartesian(-56.37, 85.04, 21.62)
                        .set_rotation_by_euler_angles(9.68, -12.95, 41.31)),
        ]

        # we only create the center keys, in order to keep the exported test results small
        for cluster in clusters:
            cluster.find_children("center_key")[0].create_occurrence(scale=.1)

    def test_absolute_cylindrical_and_support_lengths_placement(self):

        clusters = [
            context.positioned_cluster_assembly(
                lalboard.AbsoluteFingerClusterPlacement(context)
                        .set_cylindrical(116.53, 4.15, 31.09)
                        .set_rotation_by_support_lengths(23.36, 28.55, 28.60, 1.46)),
            context.positioned_cluster_assembly(
                lalboard.AbsoluteFingerClusterPlacement(context)
                        .set_cylindrical(121.40, -8.42, 30.46)
                        .set_rotation_by_support_lengths(22.84, 27.49, 28.13, 14.03)),
            context.positioned_cluster_assembly(
                lalboard.AbsoluteFingerClusterPlacement(context)
                        .set_cylindrical(118.37, -21.62, 27.73)
                        .set_rotation_by_support_lengths(20.49, 23.33, 26.86, 21.95)),
            context.positioned_cluster_assembly(
                lalboard.AbsoluteFingerClusterPlacement(context)
                        .set_cylindrical(102.03, -33.54, 21.62)
                        .set_rotation_by_support_lengths(15.47, 15.81, 19.83, 41.31)),
        ]

        # we only create the center keys, in order to keep the exported test results small
        for cluster in clusters:
            cluster.find_children("center_key")[0].create_occurrence(scale=.1)

    def test_lefthand_relative_cartesian_placement(self):
        clusters = []
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                        .set_cartesian(116.23, 31.09, gap=-8.43)
                        .set_rotation_by_euler_angles(13.45, -.16, 1.46)
                        .resolve(None, left_hand=True)))

        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                        .set_cartesian(120.09, 30.46)
                        .set_rotation_by_euler_angles(13.12, -2.05, 14.03)
                        .resolve(clusters[-1], left_hand=True)))

        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                        .set_cartesian(110.04, 27.73)
                        .set_rotation_by_euler_angles(12.75, -11.36, 21.95)
                        .resolve(clusters[-1], left_hand=True)))

        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                        .set_cartesian(85.04, 21.62)
                        .set_rotation_by_euler_angles(9.68, -12.95, 41.31)
                        .resolve(clusters[-1], left_hand=True),
                tall_clip=True))

        for i in range(1, 3):
            cluster = clusters[i]
            previous_cluster = clusters[i-1]

            point1, point2 = cluster.closest_points(previous_cluster)
            self.assertLess(point1.vectorTo(point2).length, app().pointTolerance)

        # we only create the center keys, in order to keep the exported test results small
        for cluster in clusters:
            cluster.find_children("center_key")[0].create_occurrence(scale=.1)

    def test_lefthand_relative_cylindrical_placement(self):
        clusters = []
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                        .set_cylindrical(116.53, 31.09, gap=-8.44)
                        .set_rotation_by_euler_angles(13.45, -.16, 1.46)
                        .resolve(None, left_hand=True)))
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                        .set_cylindrical(121.40, 30.46)
                        .set_rotation_by_euler_angles(13.12, -2.05, 14.03)
                        .resolve(clusters[-1], left_hand=True)))
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                        .set_cylindrical(118.37, 27.73)
                        .set_rotation_by_euler_angles(12.75, -11.36, 21.95)
                        .resolve(clusters[-1], left_hand=True)))
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                        .set_cylindrical(102.03, 21.62)
                        .set_rotation_by_euler_angles(9.68, -12.95, 41.31)
                        .resolve(clusters[-1], left_hand=True),
                tall_clip=True))

        for i in range(1, 3):
            cluster = clusters[i]
            previous_cluster = clusters[i-1]

            point1, point2 = cluster.closest_points(previous_cluster)
            self.assertLess(point1.vectorTo(point2).length, app().pointTolerance)

        # we only create the center keys, in order to keep the exported test results small
        for cluster in clusters:
            cluster.find_children("center_key")[0].create_occurrence(scale=.1)

    def test_righthand_relative_cartesian_placement(self):
        clusters = []
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cartesian(114.83, 30.37, gap=-20.79)
                    .set_rotation_by_euler_angles(13.74, 3.31, -8.19)
                    .resolve(None, left_hand=False)))

        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cartesian(121.52, 31.49)
                    .set_rotation_by_euler_angles(10.65, 8.44, -17.92)
                    .resolve(clusters[-1], left_hand=False)))

        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cartesian(111.16, 28.05)
                    .set_rotation_by_euler_angles(8.51, 6.45, -25.54)
                    .resolve(clusters[-1], left_hand=False)))

        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cartesian(89.18, 21.66)
                    .set_rotation_by_euler_angles(10.65, 13.16, -37.05)
                    .resolve(clusters[-1], left_hand=False),
                tall_clip=True))

        for i in range(1, 3):
            cluster = clusters[i]
            previous_cluster = clusters[i-1]

            point1, point2 = cluster.closest_points(previous_cluster)
            self.assertLess(point1.vectorTo(point2).length, app().pointTolerance)

        # we only create the center keys, in order to keep the exported test results small
        for cluster in clusters:
            cluster.find_children("center_key")[0].create_occurrence(scale=.1)

    def test_righthand_relative_cylindrical_placement(self):
        clusters = []
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cylindrical(116.70, 30.37, gap=-21.12)
                    .set_rotation_by_euler_angles(13.74, 3.31, -8.19)
                    .resolve(None, left_hand=False)))
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cylindrical(121.75, 31.49)
                    .set_rotation_by_euler_angles(10.65, 8.44, -17.92)
                    .resolve(clusters[-1], left_hand=False)))
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cylindrical(115.28, 28.05)
                    .set_rotation_by_euler_angles(8.51, 6.45, -25.54)
                    .resolve(clusters[-1], left_hand=False)))
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cylindrical(100.94, 21.66)
                    .set_rotation_by_euler_angles(10.65, 13.16, -37.05)
                    .resolve(clusters[-1], left_hand=False),
                tall_clip=True))

        for i in range(1, 3):
            cluster = clusters[i]
            previous_cluster = clusters[i-1]

            point1, point2 = cluster.closest_points(previous_cluster)
            self.assertLess(point1.vectorTo(point2).length, app().pointTolerance)

        # we only create the center keys, in order to keep the exported test results small
        for cluster in clusters:
            cluster.find_children("center_key")[0].create_occurrence(scale=.1)

    def test_lefthand_relative_cartesian_placement_with_gap(self):
        clusters = []
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.AbsoluteFingerClusterPlacement(context)
                    .set_cylindrical(116.53, 4.15, 31.09)
                    .set_rotation_by_euler_angles(13.45, -.16, 1.46)))

        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cartesian(120.09, 30.46)
                    .set_rotation_by_euler_angles(13.12, -2.05, 14.03)
                    .resolve(clusters[0], left_hand=True)))

        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cartesian(120.09, 30.46, gap=1.25)
                    .set_rotation_by_euler_angles(13.12, -2.05, 14.03)
                    .resolve(clusters[0], left_hand=True)))

        # we only create the center keys, in order to keep the exported test results small
        for cluster in clusters:
            cluster.find_children("center_key")[0].create_occurrence(scale=.1)

    def test_righthand_relative_cartesian_placement_with_gap(self):
        clusters = []
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.AbsoluteFingerClusterPlacement(context)
                    .set_cartesian(-20.79, 114.83, 30.37)
                    .set_rotation_by_euler_angles(13.74, 3.31, -8.19)))

        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cartesian(121.52, 31.49)
                    .set_rotation_by_euler_angles(10.65, 8.44, -17.92)
                    .resolve(clusters[0], left_hand=False)))

        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cartesian(121.52, 31.49, gap=1.25)
                    .set_rotation_by_euler_angles(10.65, 8.44, -17.92)
                    .resolve(clusters[0], left_hand=False)))


        for i in range(1, 3):
            cluster = clusters[i]
            previous_cluster = clusters[i-1]

            point1, point2 = cluster.closest_points(previous_cluster)
            self.assertLess(point1.vectorTo(point2).length, app().pointTolerance)

        # we only create the center keys, in order to keep the exported test results small
        for cluster in clusters:
            cluster.find_children("center_key")[0].create_occurrence(scale=.1)

    def test_lefthand_relative_cylindrical_placement_with_gap(self):
        clusters = []
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.AbsoluteFingerClusterPlacement(context)
                    .set_cylindrical(116.53, 4.15, 31.09)
                    .set_rotation_by_euler_angles(13.45, -.16, 1.46)))

        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cylindrical(121.40, 30.46)
                    .set_rotation_by_euler_angles(13.12, -2.05, 14.03)
                    .resolve(clusters[0], left_hand=True)))
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cylindrical(121.40, 30.46, gap=1.25)
                    .set_rotation_by_euler_angles(13.12, -2.05, 14.03)
                    .resolve(clusters[0], left_hand=True)))

        # we only create the center keys, in order to keep the exported test results small
        for cluster in clusters:
            cluster.find_children("center_key")[0].create_occurrence(scale=.1)

    def test_righthand_relative_cylindrical_placement_with_gap(self):
        clusters = []
        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.AbsoluteFingerClusterPlacement(context)
                    .set_cartesian(-20.79, 114.83, 30.37)
                    .set_rotation_by_euler_angles(13.74, 3.31, -8.19)))

        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cylindrical(121.75, 31.49)
                    .set_rotation_by_euler_angles(10.65, 8.44, -17.92)
                    .resolve(clusters[0], left_hand=False)))

        clusters.append(
            context.positioned_cluster_assembly(
                lalboard.RelativeFingerClusterPlacement(context)
                    .set_cylindrical(121.75, 31.49, gap=1.25)
                    .set_rotation_by_euler_angles(10.65, 8.44, -17.92)
                    .resolve(clusters[0], left_hand=False)))

        # we only create the center keys, in order to keep the exported test results small
        for cluster in clusters:
            cluster.find_children("center_key")[0].create_occurrence(scale=.1)


def run(context):
    import sys
    test_suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__],
                                                                #pattern="righthand_relative_cartesian_placement",
                                                                )
    unittest.TextTestRunner(failfast=True).run(test_suite)
