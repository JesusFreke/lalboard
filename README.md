##### lalboard - A 3D-printed keyboard based around the idea of a cluster of 5 buttons per finger.

This was designed to be very adjustable, so you can get the keys positioned exactly right for your
hand. Each key cluster has limited adjustability in all 6 degrees of freedom.

This is printable on a hobby-level FDM 3D printer. e.g. I used a stock Prusa i3 MK2.5 for
everything. Most parts need to be printed in a very opaque PLA, but there are a few parts that don't
work well in PLA which should be printed in polycarbonate or similar material, for its strength and
heat resistance.

##### Key Mechanisms

All keys use a pair of magnets to provide the clickiness and key return force, and an IR LED and
phototransistor for detecting a keypress.

##### Adjustability

The key clusters have a trio of standoffs that are designed to be mounted onto a steel sheet with
magnets. Each standoff has an adjustable height, and is mounted to the key cluster via a
ball socket. This provides a limited 6 degrees of freedom in adjusting the angle and position of
each key cluster, in order to get it perfectly positioned for your hands.

##### Electronics

This design uses copper traces that are cut from adhesive-backed copper tape using a vinyl cutter,
and applied to the bottom of 3D-printed "pcbs" printed with polycarbonate for its excellent heat
resistance during soldering. There are currently no designs for actual pcbs, but I don't think it
should be difficult to do. If someone wants to tackle that, I'm happy to give pointers or otherwise
help in any way I can :)

Each side of the keyboard uses an independent teensy 2.0 board, and are connected with 4 wires
between them to enable communication via i2c. Only one side of the keyboard actually needs to be
plugged into USB. The teensy's run a modified version of the
[teensyhand](https://github.com/JesusFreke/teensyhand) firmware.

##### Handrest

The handrest was first molded for my wrist in plasticine clay, and then scanned in using the
[meshroom](https://github.com/alicevision/meshroom) photogrammetry software. Since they were molded
for my wrists specifically, I'm not sure how "one-size-fits-all" they are, or how comfortable they
would be for someone else to use.

--------

Note: This is not an officially supported Google product.
