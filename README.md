##### lalboard - A 3D-printed keyboard inspired by the DataHand.

<img src="https://jesusfreke.github.io/lalboard/lalboard.jpg" alt="drawing" width="595"/>

[More Images](https://github.com/JesusFreke/lalboard/wiki/Images)

[120 WPM Typing Demo](https://www.youtube.com/watch?v=oMhOIgrdeE0)

[V2 Project Logs (hackaday.io)](http://lalboard.com)

I am a long-time user of a DataHand keyboard. With the scarcity and rising cost of second hand
DataHands these days, I wanted to ensure that I always had access to a DataHand-like keyboard. And
so this project was born.

The overall functionality of the lalboard is obviously heavily based on the DataHand, but I designed
all of the specific key mechanisms, etc. from scratch, to be printable on a normal hobby-level
FDM printer.

With my DataHand, I never felt like I could get the keys positioned *quite right* for my hand. So
one of my primary focuses with the lalboard was adjustability. Each key cluster can be independently
adjusted in all 6 degrees of freedom to some extent.

Most parts need to be printed in a very opaque PLA, but there are a few parts that don't work well
in PLA which should be printed in polycarbonate or similar material, for its strength and heat
resistance.

##### Key Mechanisms

All keys use a pair of magnets to provide the clickiness and key return force, and an IR LED and
phototransistor for detecting a keypress. They are all held in place only with magnets, so they
are easily removable for cleaning, etc.

The feel/clickiness of the keys was another focus area. I tried to get them to feel as similar to
those on a DataHand as possible. They require roughly the same amount of force, and have that same
unique clicky feel due to the magnetic holding force.

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

##### [BOM](https://github.com/JesusFreke/lalboard/wiki/BOM)

##### [Printing tips & instructions](https://github.com/JesusFreke/lalboard/wiki/Printing-tips-&-instructions)

##### [Preparing the Vinyl-cut PCBs](https://github.com/JesusFreke/lalboard/wiki/Vinyl-Cut-PCBs)




--------

Note: This is not an officially supported Google product.
