# Copyright 2020 Google LLC
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
import os
import pathlib
import time
import traceback

from fscad import *


def run(_):
    try:
        start = time.time()

        export_dir = pathlib.Path(
            pathlib.Path(os.path.dirname(__file__)).parent,
            "stls")

        file: os.DirEntry
        for file in os.scandir(os.path.dirname(__file__)):
            if file.is_dir():
                if (file.name.startswith("_") or file.name.endswith("assembly") or file.name == "__pycache__" or
                        file.name == "scene"):
                    continue

                export_sketch = False
                if file.name.endswith("sketch"):
                    export_sketch = True

                path = pathlib.Path(file.path, file.name + ".py")

                module = relative_import(str(path))
                print("Running " + file.name)
                module.run(None)

                if export_sketch:
                    if len(root().sketches) != 1:
                        raise Exception("Unexpected number of sketches in design")
                    sketch: adsk.fusion.Sketch = root().sketches[0]
                    sketch.saveAsDXF(str(pathlib.Path(export_dir, file.name + ".dxf")))
                else:
                    if len(root().occurrences) != 1:
                        raise Exception("Unexpected number of components in design")
                    options = design().exportManager.createSTLExportOptions(
                        root().occurrences[0],
                        str(pathlib.Path(export_dir, file.name + ".stl")))
                    options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
                    options.sendToPrintUtility = False

                    design().exportManager.execute(options)

                app().activeDocument.close(saveChanges=False)

        end = time.time()
        print("Total run time: %f" % (end-start))
    except Exception:
        print(traceback.format_exc())
        ui().messageBox('Failed:\n{}'.format(traceback.format_exc()))
