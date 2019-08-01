# Using/Editing **rest left.max**

The provided .max file contains the source material for all .STL files in this folder.
It is structured in a way that allows at least some semblance of efficient editing.
You will probably need 3ds Max to edit them.

## Scene Editing
Notice that there is a separate green mesh called *Outer Shell*.
It is linked to all top and bottom rest parts.
If you change this object, all others (except the rubber mask) will adapt automatically.
Likewise, you should take care not to make it too small as that may create holes in the other meshes where you do not want them.
This object is designed to be changed if your hand doesn't fit the mesh and you want to adjust it.

To work faster I would also suggest to reduce the mesh smooth Iterations (modifier list) before actually working on it.
The high number of Iterations (3+) is necessary for export but not for display on screen and will slow down update dramatically.
Also notice that the mesh may temporarily disappear from other objects while you operate on the *Editable Poly* layer.


## Export
Export objects are generally colored blueish in the editor.
They are aligned for printing out of the box.
There are a total of 4 objects (5 if you count the rubber mask) designed to be exported:
**Bottom Export**, **Top Export**, **Board Shield 7**, and **Board Shield 8**.
The rubber mask may require adjustments and or cutting the printed object and is designed to aid in cutting a rubber plate such that it can be glued to the rest bottom.

To export an object (using 3ds Max 2018), first select it, then go to *File->Export->Export...* (**important: NOT Export Selected...**), then select *StereoLitho (.STL)* and in the export settings check *Selected only*

## Printing
I would recommend printing the top part as precise as possible.
I use moderate printing speed, however at 0.05mm layer height, to get smooth results.
With that precision, set infill combination to every 4 layers.
I also recommend a not too shiny material here.

The bottom rest part can be printed at 0.15mm or more.
Same goes for the board shields intended for holding the board onto the rest.
The rubber mask, if used, can take pretty much any precision since the cutting will never be that precise anyway.

Top and bottom rest parts need to be mirrored in your printing software to get the respective right hand rest.
The shields should be printed as is for both left and right without mirroring.
The printed rubber mask can just be flipped upside down.

## Magnets
Most of the objects are designed to use [5mm diameter, 3mm height] round Neodymium magnets.
The bottom rest part leaves just enough flat spacing between them to fit a 1mm rubber layer there, put under pressure by the magnets.
The optional board shield 8 uses [1/8" x 1/8" x 1/16" N48] square Neodymium magnets as found in the original BOM.
I found these to be strong enough, make the shield flatter, and provide some asymmetry to glue the magnets in if need be.
Glueing is somewhat more challenging when using the higher board shield 7, which uses round magnets.
Note that using this version makes the shield's attraction to the rest very strong.
You may or may not want that.