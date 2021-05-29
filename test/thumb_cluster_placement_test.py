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

class ThumbClusterPlacementTest(FscadTestCase):

    def test_absolute_cartesian_and_euler_placement_left(self):
        thumb_cluster = context.positioned_thumb_assembly(
            lalboard.AbsoluteThumbClusterPlacement(context)
                    .set_cartesian(47.98, 81.74, 35.11)
                    .set_rotation_by_euler_angles(9.19, -2.67, 14.28),
            left_hand=True)

        # we only create the down key, in order to keep the exported test results small
        thumb_cluster.find_children("thumb_down_key")[0].create_occurrence(scale=.1)

    def test_support_lengths_placement_left(self):
        thumb_cluster = context.positioned_thumb_assembly(
            lalboard.AbsoluteThumbClusterPlacement(context)
                .set_cartesian(47.98, 81.74, 35.11)
                .set_rotation_by_support_lengths(
                    20.03, 23.97, 26.89, rz=14.28, left_hand=True),
            left_hand=True)

        # we only create the down key, in order to keep the exported test results small
        thumb_cluster.find_children("thumb_down_key")[0].create_occurrence(scale=.1)

    def test_relative_placement_left(self):
        handrest = context.handrest_design(left_hand=True)

        thumb_cluster = context.positioned_thumb_assembly(
            lalboard.RelativeThumbClusterPlacement(context)
                .set_cartesian(81.74, 35.11)
                .set_rotation_by_euler_angles(9.19, -2.67, 14.28)
                .resolve(handrest, left_hand=True),
            left_hand=True)

        # we only create the down key, in order to keep the exported test results small
        thumb_cluster.find_children("thumb_down_key")[0].create_occurrence(scale=.1)

    def test_relative_placement_with_gap_left(self):
        handrest = context.handrest_design(left_hand=True)

        thumb_cluster = context.positioned_thumb_assembly(
            lalboard.RelativeThumbClusterPlacement(context)
                .set_cartesian(81.74, 35.11, gap=5.55)
                .set_rotation_by_euler_angles(9.19, -2.67, 14.28)
                .resolve(handrest, left_hand=True),
            left_hand=True)

        # we only create the down key, in order to keep the exported test results small
        thumb_cluster.find_children("thumb_down_key")[0].create_occurrence(scale=.1)

    def test_absolute_cartesian_and_euler_placement_right(self):
        thumb_cluster = context.positioned_thumb_assembly(
            lalboard.AbsoluteThumbClusterPlacement(context)
                .set_cartesian(-50.35, 83.96, 36.26)
                .set_rotation_by_euler_angles(10.39, -1.44, -7.77),
            left_hand=False)

        # we only create the down key, in order to keep the exported test results small
        thumb_cluster.find_children("thumb_down_key")[0].create_occurrence(scale=.1)

    def test_support_lengths_placement_right(self):
        thumb_cluster = context.positioned_thumb_assembly(
            lalboard.AbsoluteThumbClusterPlacement(context)
                .set_cartesian(-50.35, 83.96, 36.26)
                .set_rotation_by_support_lengths(
                21.16, 23.80, 28.19, rz=-7.77, left_hand=False),
            left_hand=False)

        # we only create the down key, in order to keep the exported test results small
        thumb_cluster.find_children("thumb_down_key")[0].create_occurrence(scale=.1)

    def test_relative_placement_right(self):
        handrest = context.handrest_design(left_hand=False)

        thumb_cluster = context.positioned_thumb_assembly(
            lalboard.RelativeThumbClusterPlacement(context)
                .set_cartesian(83.96, 36.26)
                .set_rotation_by_euler_angles(10.39, -1.44, -7.77)
                .resolve(handrest, left_hand=False),
            left_hand=False)

        # we only create the down key, in order to keep the exported test results small
        thumb_cluster.find_children("thumb_down_key")[0].create_occurrence(scale=.1)

    def test_relative_placement_with_gap_right(self):
        handrest = context.handrest_design(left_hand=False)

        thumb_cluster = context.positioned_thumb_assembly(
            lalboard.RelativeThumbClusterPlacement(context)
                .set_cartesian(83.96, 36.26, gap=6.925)
                .set_rotation_by_euler_angles(10.39, -1.44, -7.77)
                .resolve(handrest, left_hand=False),
            left_hand=False)

        # we only create the down key, in order to keep the exported test results small
        thumb_cluster.find_children("thumb_down_key")[0].create_occurrence(scale=.1)


def run(context):
    import sys
    test_suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__],
                                                                #pattern="relative_placement_with_gap_right",
                                                                )
    unittest.TextTestRunner(failfast=True).run(test_suite)
