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

# List of the names of the parts to export. An empty list will export all parts.
parts_to_export = []


def run(_):
    try:
        start = time.time()

        export_dir = pathlib.Path(
            pathlib.Path(os.path.dirname(__file__)).parent,
            "stls")

        file: os.DirEntry
        for file in os.scandir(os.path.dirname(__file__)):
            if file.is_dir():
                if (file.name.startswith("_") or file.name == "__pycache__" or
                        file.name == "scene"):
                    continue

                export_sketch = False
                export_assembly = False
                if file.name.endswith("sketch"):
                    export_sketch = True
                if file.name.endswith("assembly"):
                    export_assembly = True

                if parts_to_export and file.name not in parts_to_export:
                    continue

                path = pathlib.Path(file.path, file.name + ".py")

                module = relative_import(str(path))
                print("Running " + file.name)
                module.run(None)

                if export_sketch:
                    if len(root().sketches) != 1:
                        raise Exception("Unexpected number of sketches in design")
                    sketch: adsk.fusion.Sketch = root().sketches[0]
                    sketch.saveAsDXF(str(pathlib.Path(export_dir, file.name + ".dxf")))
                elif export_assembly:
                    export_stl(export_dir, file)
                    f3d_file =export_f3d(export_dir, file)
                    export_to_fusion_cloud(file, f3d_file)
                else:
                    export_stl(export_dir, file)

                app().activeDocument.close(saveChanges=False)

        end = time.time()
        print("Total run time: %f" % (end-start))
    except Exception:
        print(traceback.format_exc())
        ui().messageBox('Failed:\n{}'.format(traceback.format_exc()))


def export_stl(export_dir, file):
    options = design().exportManager.createSTLExportOptions(
        root(),
        str(pathlib.Path(export_dir, file.name + ".stl")))
    options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    options.sendToPrintUtility = False

    design().exportManager.execute(options)


def export_f3d(export_dir, file):
    options = design().exportManager.createFusionArchiveExportOptions(
        str(pathlib.Path(export_dir, file.name + ".f3d")),
        root())
    design().exportManager.execute(options)
    return str(pathlib.Path(export_dir, file.name + ".f3d"))


printed_export_to_fusion_cloud_warning = False


def export_to_fusion_cloud(file, f3d_file):
    # hardcoded id of my "lalboard exports" project
    dataProject = app().data.dataProjects.itemById("a.cGVyc29uYWw6dWUyZDJjMmQxIzIwMjEwMzE4Mzk0MTc4ODAx")

    if dataProject is None:
        global printed_export_to_fusion_cloud_warning
        if not printed_export_to_fusion_cloud_warning:
            print("Could not find the correct fusion 360 project. You probably need to create a project and change "
                  "the hardcoded id in export_to_fusion_cloud in the export_parts.py script")
            printed_export_to_fusion_cloud_warning = True
            return

    data_file_for_export: adsk.core.DataFile = None
    for data_file in dataProject.rootFolder.dataFiles:
        if data_file and data_file.name == file.name:
            data_file_for_export = data_file
            break
    if not data_file_for_export:
        # first, create the new document as an empty document. We rely on the fact that the first version is empty.
        if not app().activeDocument.saveAs(
                file.name,
                dataProject.rootFolder,
                "",
                ""):
            raise Exception("Oops, couldn't save document")
        return

    export_document = app().documents.open(data_file_for_export)
    export_design: adsk.fusion.Design = export_document.products[0]

    occurrence: adsk.fusion.Occurrence
    for occurrence in list(export_design.rootComponent.occurrences):
        occurrence.deleteMe()

    imported_occurrence: adsk.fusion.Occurrence = app().importManager.importToTarget2(
        app().importManager.createFusionArchiveImportOptions(f3d_file),
        export_design.rootComponent)[0]

    for occurrence in imported_occurrence.component.occurrences:
        export_design.rootComponent.occurrences.addExistingComponent(occurrence.component, occurrence.transform)

    imported_occurrence.deleteMe()
    export_document.save("saved")
    export_document.close(saveChanges=False)
