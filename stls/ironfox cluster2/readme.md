#### IronFox's Cluster Modifications

Sources:<br>
[Fusion 360 model](https://a360.co/2PBIouj)<br>
EAGLE files: [lalboard]/eagle/cluster2(...)<br>

##### Printing Instructions

Most parts were designed and successfully tested using a 0.4 Nozzle on a Prusa MK3s.
That being said, using a 0.25mm nozzle is highly recommended for all parts of this cluster design.

You will need the following parts per cluster. All parts are provided as STLs as exported from Fusion 360.
Unless specified differently, print once per finger cluster, aligned as you see it in the STL. All layer heights should be fine using 0.1mm.
###### Main:
* Cluster.stl
* Magnet Frame.stl
* Top[1-8].stl (pick one as desired 1=really strong, 8=really weak)<br>
Flip around to print:<br>
	<img src="https://github.com/IronFox/lalboard/raw/master/stls/ironfox%20cluster2/images/top.png" width="300px"/>
* Tube.stl
###### Keys:
* Shaft.stl<br>Rotate to back to print:<br>
	<img src="https://github.com/IronFox/lalboard/raw/master/stls/ironfox%20cluster2/images/shaft.png" width="300px"/>
* Cap Top.stl
* Cap Mask.stl
* Long Key Shaft.stl<br>Rotate to side to print:<br>
	<img src="https://github.com/IronFox/lalboard/raw/master/stls/ironfox%20cluster2/images/long_shaft.png" width="300px"/>
* 2x Key Shaft.stl (rotate as above)
* Micro Key Shaft.stl (rotate as above)
* Long Key Cap.stl<br>Align to plate to print:<br>
	<img src="https://github.com/IronFox/lalboard/raw/master/stls/ironfox%20cluster2/images/long_cap.png" width="300px"/>
* 2x Key Cap.stl (align as above)
* Micro Key Cap.stl (align as above)


##### Assembly

You need 18x of the original 1/16" magnets per cluster.

1. Insert [Tube.stl] into [Cluster.stl]. The top edge must be level with the corresponding edges of [Cluster.stl]. You may need to file off the bottom edges and surfaces a bit. Also file the inside to reduce friction with [Shaft.stl].

1. After inserting magnets into the openings, insert [Magnet Frame.stl] into [Cluster.stl]. There is a barely visible marker printed into both geometries to help alignment. Generally, however, it should fit only one way.
Make sure the magnets are aligned with their siblings in [* Key Shaft.stl].
The magnets should snap to each other such that no plastic is between the magnets.

1. Insert 5 magnets into the printed [Top*.stl] plate. Make sure they are properly aligned. The four corner magnets must be aligned to their corresponding siblings inserted into the [Cluster.stl] print to snap and hold.
The center magnet must be aligned with the one inserted into the printed [Shaft.stl].

1. Clip [Cap Top.stl] to [Cap Mask.stl]. You may need some force. If it doesn't hold, use glue.
If you haven't already, insert properly aligned magnet into [Shaft.stl].
Press the combined [Cap Top.stl] and [Cap Mask.stl] onto [Shaft.stl]. 
If it does not stick, double check that the magnet is correctly inserted (you won't be able to press it in after top is glued), then use glue.

1. Insert [Shaft.stl] into the central opening of [Top.stl] such that the cap is on the smooth side of [Top.stl].
The key will most likely lean a bit (or a lot). That is perfectly fine at this point. If [Top.stl] and [Shaft.stl] repel each other, then one of the magnets is incorrectly aligned.

1. To test the construction, carefully place [Top.stl] onto [Cluster.stl] such that [Shaft.stl] slides into [Tube.stl].
If everything went well, the central key should now be operational. If it gets stuck when pressing, you may need to disassemble and file [Tube.stl] some more, or possibly [Shaft.stl] a bit.

1. Combine [* Key Cap.stl] and [* Key Shaft.stl].
For the Micro and regular key versions, you should just press them together.
With any luck, and using pliers, they stick without glue.
For the long key variant, this modification has not been implemented yet.
Use some glue here.

1. Press the four keys all the way down into the openings of [Cluster.stl] and [Top.stl].
If all went well, the four keys should now operate as intended.
If they levitate out of the openings or otherwise do not return to idle, you might have inserted some magnets the wrong way.
It can also happen that there is some stray filament printed in the openings.
You may need to file a bit. Make sure you do not remove the ledge that holds the pressed keys in place.

##### Soldering

You need:
* 5x "PT908-7B-F" IR phototransistor
* 5x "IR928-6C-F" IR LEDs
* 1x "4606X-101-151LF" Resistor network
* 1x 7-pin JST ZH male connector
* 1x cluster2 PCB



1. Solder "4606X-101-151LF" Resistor network and 7-pin JST ZH male connector onto the PCB. 
**Important**: The components need to be inserted from the PCB side where the respective outline is drawn.
Make sure to align the JST ZH connector such that it matches its outline.
Conversely, the components' pins are soldered to the PCB on the opposite side (where the component's outline is not drawn).
The resistor network and connector are soldered from opposing sides.
**The drill holes with square soldering pads denote the respective component's ground line.
In case of the resistor network that is where the pin with the dot marker needs to go.**
If all goes well, the soldered result should fit needly into the bottom openings of the cluster.

1. Remove all keys and [Top*.stl] from the cluster.
Leave [Magnet Frame.stl] in.

1. While holding the PCB beneath the cluster, insert "IR928-6C-F" IR LEDs and "PT908-7B-F" IR phototransistors into the matching openings of [Cluster.stl] and the PCB.
The white IR LEDs go into the larger rectangular holes, the thin black phototransistors into the smaller openings with the notch.
You might need to widen some channels using a needle or stitching awl, but generally these components should fit needly.
1. Put [Top*.stl] back onto the cluster.
The LEDs and phototransistors should now be held in place so you can flip the cluster upside-down without any of them being able to move much.
1. Solder all the IR LED and phototransistor pins to the PCB.
Make sure there is no gab between the cluster and the PCB, or between the cluster and [Top*.stl].
Once done, the PCB should be held in place, and you can now re-insert all the keys.
Congratulations, you're done with this cluster.


##### Connection

Connecting to the cluster PCB (as also presented in this branch) requires a point-symmetric wiring.
The left most pin of one side needs to be connected to the left most pin of the other (when viewing both connectors from the same side).
Same goes for the other six cables.
When using pre-crimped wires, this means the cables tend to cross in the middle.
It is not possible to connect the two PCB designs using the pre-assembled wires as in the original BOM.
If you absolutely have to use such cables, adjust one of the two PCBs (probably the cluster) accordingly before ordering.
