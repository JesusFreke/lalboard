<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE eagle SYSTEM "eagle.dtd">
<eagle version="9.3.2">
<drawing>
<settings>
<setting alwaysvectorfont="no"/>
<setting verticaltext="up"/>
</settings>
<grid distance="0.1" unitdist="inch" unit="inch" style="lines" multiple="1" display="no" altdistance="0.01" altunitdist="inch" altunit="inch"/>
<layers>
<layer number="1" name="Top" color="4" fill="1" visible="no" active="no"/>
<layer number="16" name="Bottom" color="1" fill="1" visible="no" active="no"/>
<layer number="17" name="Pads" color="2" fill="1" visible="no" active="no"/>
<layer number="18" name="Vias" color="2" fill="1" visible="no" active="no"/>
<layer number="19" name="Unrouted" color="6" fill="1" visible="no" active="no"/>
<layer number="20" name="Dimension" color="15" fill="1" visible="no" active="no"/>
<layer number="21" name="tPlace" color="7" fill="1" visible="no" active="no"/>
<layer number="22" name="bPlace" color="7" fill="1" visible="no" active="no"/>
<layer number="23" name="tOrigins" color="15" fill="1" visible="no" active="no"/>
<layer number="24" name="bOrigins" color="15" fill="1" visible="no" active="no"/>
<layer number="25" name="tNames" color="7" fill="1" visible="no" active="no"/>
<layer number="26" name="bNames" color="7" fill="1" visible="no" active="no"/>
<layer number="27" name="tValues" color="7" fill="1" visible="no" active="no"/>
<layer number="28" name="bValues" color="7" fill="1" visible="no" active="no"/>
<layer number="29" name="tStop" color="7" fill="3" visible="no" active="no"/>
<layer number="30" name="bStop" color="7" fill="6" visible="no" active="no"/>
<layer number="31" name="tCream" color="7" fill="4" visible="no" active="no"/>
<layer number="32" name="bCream" color="7" fill="5" visible="no" active="no"/>
<layer number="33" name="tFinish" color="6" fill="3" visible="no" active="no"/>
<layer number="34" name="bFinish" color="6" fill="6" visible="no" active="no"/>
<layer number="35" name="tGlue" color="7" fill="4" visible="no" active="no"/>
<layer number="36" name="bGlue" color="7" fill="5" visible="no" active="no"/>
<layer number="37" name="tTest" color="7" fill="1" visible="no" active="no"/>
<layer number="38" name="bTest" color="7" fill="1" visible="no" active="no"/>
<layer number="39" name="tKeepout" color="4" fill="11" visible="no" active="no"/>
<layer number="40" name="bKeepout" color="1" fill="11" visible="no" active="no"/>
<layer number="41" name="tRestrict" color="4" fill="10" visible="no" active="no"/>
<layer number="42" name="bRestrict" color="1" fill="10" visible="no" active="no"/>
<layer number="43" name="vRestrict" color="2" fill="10" visible="no" active="no"/>
<layer number="44" name="Drills" color="7" fill="1" visible="no" active="no"/>
<layer number="45" name="Holes" color="7" fill="1" visible="no" active="no"/>
<layer number="46" name="Milling" color="3" fill="1" visible="no" active="no"/>
<layer number="47" name="Measures" color="7" fill="1" visible="no" active="no"/>
<layer number="48" name="Document" color="7" fill="1" visible="no" active="no"/>
<layer number="49" name="Reference" color="7" fill="1" visible="no" active="no"/>
<layer number="50" name="dxf" color="7" fill="1" visible="no" active="no"/>
<layer number="51" name="tDocu" color="7" fill="1" visible="no" active="no"/>
<layer number="52" name="bDocu" color="7" fill="1" visible="no" active="no"/>
<layer number="88" name="SimResults" color="9" fill="1" visible="yes" active="yes"/>
<layer number="89" name="SimProbes" color="9" fill="1" visible="yes" active="yes"/>
<layer number="90" name="Modules" color="5" fill="1" visible="yes" active="yes"/>
<layer number="91" name="Nets" color="2" fill="1" visible="yes" active="yes"/>
<layer number="92" name="Busses" color="1" fill="1" visible="yes" active="yes"/>
<layer number="93" name="Pins" color="2" fill="1" visible="no" active="yes"/>
<layer number="94" name="Symbols" color="4" fill="1" visible="yes" active="yes"/>
<layer number="95" name="Names" color="7" fill="1" visible="yes" active="yes"/>
<layer number="96" name="Values" color="7" fill="1" visible="yes" active="yes"/>
<layer number="97" name="Info" color="7" fill="1" visible="yes" active="yes"/>
<layer number="98" name="Guide" color="6" fill="1" visible="yes" active="yes"/>
<layer number="100" name="Muster" color="7" fill="1" visible="no" active="no"/>
<layer number="101" name="Bemassung" color="7" fill="1" visible="yes" active="yes"/>
<layer number="102" name="bot_pads" color="7" fill="5" visible="yes" active="yes"/>
<layer number="104" name="S_DOKU" color="7" fill="1" visible="yes" active="yes"/>
<layer number="116" name="Patch_BOT" color="9" fill="4" visible="yes" active="yes"/>
<layer number="199" name="Contour" color="7" fill="1" visible="yes" active="yes"/>
<layer number="200" name="200bmp" color="1" fill="10" visible="no" active="no"/>
<layer number="250" name="Descript" color="3" fill="1" visible="no" active="no"/>
<layer number="251" name="SMDround" color="12" fill="11" visible="no" active="no"/>
<layer number="254" name="OrgLBR" color="13" fill="1" visible="yes" active="yes"/>
</layers>
<schematic xreflabel="%F%N/%S.%C%R" xrefpart="/%S.%C%R">
<libraries>
<library name="teensy">
<packages>
<package name="TEENSY">
<wire x1="15.24" y1="8.89" x2="-15.24" y2="8.89" width="0.1524" layer="21"/>
<wire x1="-15.24" y1="-8.89" x2="15.24" y2="-8.89" width="0.1524" layer="21"/>
<wire x1="15.24" y1="8.89" x2="15.24" y2="6.35" width="0.1524" layer="21"/>
<wire x1="-15.24" y1="8.89" x2="-15.24" y2="6.35" width="0.1524" layer="21"/>
<wire x1="-15.24" y1="-8.89" x2="-15.24" y2="-6.35" width="0.1524" layer="21"/>
<wire x1="-15.24" y1="1.016" x2="-15.24" y2="-1.016" width="0.1524" layer="21" curve="-180"/>
<wire x1="-15.24" y1="6.35" x2="-15.24" y2="1.016" width="0.1524" layer="21"/>
<wire x1="15.24" y1="6.35" x2="15.24" y2="-6.35" width="0.1524" layer="21"/>
<wire x1="-15.24" y1="-6.35" x2="15.24" y2="-6.35" width="0.1524" layer="21"/>
<wire x1="-15.24" y1="-6.35" x2="-15.24" y2="-1.016" width="0.1524" layer="21"/>
<wire x1="15.24" y1="-6.35" x2="15.24" y2="-8.89" width="0.1524" layer="21"/>
<wire x1="-15.24" y1="6.35" x2="15.24" y2="6.35" width="0.1524" layer="21"/>
<pad name="GND" x="-13.97" y="-7.62" drill="0.8128" diameter="1.6764" shape="square" rot="R90"/>
<pad name="B7" x="-1.27" y="-7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="D2" x="6.35" y="-7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="D3" x="8.89" y="-7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="D0" x="1.27" y="-7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="D1" x="3.81" y="-7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="D4" x="13.97" y="5.08" drill="0.8128" diameter="1.6764" rot="R180"/>
<pad name="D5" x="13.97" y="-5.08" drill="0.8128" diameter="1.6764" rot="R180"/>
<pad name="D6" x="13.97" y="7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="D7" x="11.43" y="7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="C6" x="11.43" y="-7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="C7" x="13.97" y="-7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="F7" x="1.27" y="7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="F6" x="-1.27" y="7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="F5" x="-3.81" y="7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="F4" x="-6.35" y="7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="F1" x="-8.89" y="7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="F0" x="-11.43" y="7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="REF" x="-3.81" y="5.08" drill="0.8128" diameter="1.6764" rot="R180"/>
<pad name="GRND1" x="13.97" y="0" drill="0.8128" diameter="1.6764" rot="R180"/>
<pad name="E6" x="-3.81" y="-5.08" drill="0.8128" diameter="1.6764"/>
<pad name="B0" x="-11.43" y="-7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="B1" x="-8.89" y="-7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="B2" x="-6.35" y="-7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="B3" x="-3.81" y="-7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="B4" x="8.89" y="7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="B5" x="6.35" y="7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="B6" x="3.81" y="7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="+5V" x="-13.97" y="7.62" drill="0.8128" diameter="1.6764" rot="R90"/>
<pad name="5V2" x="13.97" y="-2.54" drill="0.8128" diameter="1.6764" rot="R180"/>
<pad name="RST" x="13.97" y="2.54" drill="0.8128" diameter="1.6764" rot="R180"/>
<text x="3.175" y="1.905" size="1.27" layer="27" ratio="10">&gt;VALUE</text>
<text x="-15.748" y="-8.255" size="1.27" layer="25" ratio="10" rot="R90">&gt;NAME</text>
</package>
</packages>
<symbols>
<symbol name="TEENSY">
<wire x1="-7.62" y1="35.56" x2="7.62" y2="35.56" width="0.254" layer="94"/>
<wire x1="7.62" y1="35.56" x2="7.62" y2="-33.02" width="0.254" layer="94"/>
<wire x1="7.62" y1="-33.02" x2="-7.62" y2="-33.02" width="0.254" layer="94"/>
<wire x1="-7.62" y1="-33.02" x2="-7.62" y2="35.56" width="0.254" layer="94"/>
<text x="-5.08" y="38.1" size="1.778" layer="95">&gt;NAME</text>
<text x="-5.08" y="2.54" size="1.778" layer="96" rot="R270">&gt;VALUE</text>
<pin name="_GND" x="-12.7" y="33.02" length="middle"/>
<pin name="_B7" x="-12.7" y="30.48" length="middle"/>
<pin name="_D0" x="-12.7" y="27.94" length="middle"/>
<pin name="_D1" x="-12.7" y="25.4" length="middle"/>
<pin name="_D2" x="-12.7" y="22.86" length="middle"/>
<pin name="_D3" x="-12.7" y="20.32" length="middle"/>
<pin name="_D4" x="-12.7" y="17.78" length="middle"/>
<pin name="_D5" x="-12.7" y="15.24" length="middle"/>
<pin name="_D6" x="-12.7" y="12.7" length="middle"/>
<pin name="_D7" x="-12.7" y="10.16" length="middle"/>
<pin name="_C6" x="-12.7" y="-12.7" length="middle"/>
<pin name="_C7" x="-12.7" y="-15.24" length="middle"/>
<pin name="5V" x="12.7" y="33.02" length="middle" rot="R180"/>
<pin name="_B6" x="12.7" y="30.48" length="middle" rot="R180"/>
<pin name="_B5" x="12.7" y="27.94" length="middle" rot="R180"/>
<pin name="_B4" x="12.7" y="25.4" length="middle" rot="R180"/>
<pin name="_B3" x="12.7" y="22.86" length="middle" rot="R180"/>
<pin name="_B2" x="12.7" y="20.32" length="middle" rot="R180"/>
<pin name="_B1" x="12.7" y="17.78" length="middle" rot="R180"/>
<pin name="_B0" x="12.7" y="15.24" length="middle" rot="R180"/>
<pin name="_E6" x="12.7" y="10.16" length="middle" rot="R180"/>
<pin name="_GND1" x="12.7" y="5.08" length="middle" rot="R180"/>
<pin name="_REF" x="12.7" y="2.54" length="middle" rot="R180"/>
<pin name="_F0" x="12.7" y="-2.54" length="middle" rot="R180"/>
<pin name="_F1" x="12.7" y="-5.08" length="middle" rot="R180"/>
<pin name="_F4" x="12.7" y="-10.16" length="middle" rot="R180"/>
<pin name="_F5" x="12.7" y="-12.7" length="middle" rot="R180"/>
<pin name="_F6" x="12.7" y="-15.24" length="middle" rot="R180"/>
<pin name="_F7" x="12.7" y="-17.78" length="middle" rot="R180"/>
<pin name="_5V2" x="12.7" y="-22.86" length="middle" rot="R180"/>
<pin name="_RST" x="12.7" y="-25.4" length="middle" rot="R180"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="TEENSY" prefix="_">
<description>Teensy 2.0</description>
<gates>
<gate name="G$1" symbol="TEENSY" x="0" y="-2.54"/>
</gates>
<devices>
<device name="" package="TEENSY">
<connects>
<connect gate="G$1" pin="5V" pad="+5V"/>
<connect gate="G$1" pin="_5V2" pad="5V2"/>
<connect gate="G$1" pin="_B0" pad="B0"/>
<connect gate="G$1" pin="_B1" pad="B1"/>
<connect gate="G$1" pin="_B2" pad="B2"/>
<connect gate="G$1" pin="_B3" pad="B3"/>
<connect gate="G$1" pin="_B4" pad="B4"/>
<connect gate="G$1" pin="_B5" pad="B5"/>
<connect gate="G$1" pin="_B6" pad="B6"/>
<connect gate="G$1" pin="_B7" pad="B7"/>
<connect gate="G$1" pin="_C6" pad="C6"/>
<connect gate="G$1" pin="_C7" pad="C7"/>
<connect gate="G$1" pin="_D0" pad="D0"/>
<connect gate="G$1" pin="_D1" pad="D1"/>
<connect gate="G$1" pin="_D2" pad="D2"/>
<connect gate="G$1" pin="_D3" pad="D3"/>
<connect gate="G$1" pin="_D4" pad="D4"/>
<connect gate="G$1" pin="_D5" pad="D5"/>
<connect gate="G$1" pin="_D6" pad="D6"/>
<connect gate="G$1" pin="_D7" pad="D7"/>
<connect gate="G$1" pin="_E6" pad="E6"/>
<connect gate="G$1" pin="_F0" pad="F0"/>
<connect gate="G$1" pin="_F1" pad="F1"/>
<connect gate="G$1" pin="_F4" pad="F4"/>
<connect gate="G$1" pin="_F5" pad="F5"/>
<connect gate="G$1" pin="_F6" pad="F6"/>
<connect gate="G$1" pin="_F7" pad="F7"/>
<connect gate="G$1" pin="_GND" pad="GND"/>
<connect gate="G$1" pin="_GND1" pad="GRND1"/>
<connect gate="G$1" pin="_REF" pad="REF"/>
<connect gate="G$1" pin="_RST" pad="RST"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="SamacSys_Parts">
<description>&lt;b&gt;https://componentsearchengine.com&lt;/b&gt;&lt;p&gt;
&lt;author&gt;Created by SamacSys&lt;/author&gt;</description>
<packages>
<package name="SHDR7W50P0X150_1X7_1200X350X45">
<description>&lt;b&gt;B7B-ZR&lt;/b&gt;&lt;br&gt;
</description>
<pad name="1" x="0" y="0" drill="0.7" diameter="1.1" shape="square"/>
<pad name="2" x="1.5" y="0" drill="0.7" diameter="1.1"/>
<pad name="3" x="3" y="0" drill="0.7" diameter="1.1"/>
<pad name="4" x="4.5" y="0" drill="0.7" diameter="1.1"/>
<pad name="5" x="6" y="0" drill="0.7" diameter="1.1"/>
<pad name="6" x="7.5" y="0" drill="0.7" diameter="1.1"/>
<pad name="7" x="9" y="0" drill="0.7" diameter="1.1"/>
<text x="0" y="0" size="1.27" layer="25" align="center">&gt;NAME</text>
<text x="0" y="0" size="1.27" layer="27" align="center">&gt;VALUE</text>
<wire x1="-1.75" y1="-2.45" x2="-1.75" y2="1.55" width="0.05" layer="51"/>
<wire x1="-1.75" y1="1.55" x2="10.75" y2="1.55" width="0.05" layer="51"/>
<wire x1="10.75" y1="1.55" x2="10.75" y2="-2.45" width="0.05" layer="51"/>
<wire x1="10.75" y1="-2.45" x2="-1.75" y2="-2.45" width="0.05" layer="51"/>
<wire x1="-1.5" y1="-2.2" x2="-1.5" y2="1.3" width="0.1" layer="51"/>
<wire x1="-1.5" y1="1.3" x2="10.5" y2="1.3" width="0.1" layer="51"/>
<wire x1="10.5" y1="1.3" x2="10.5" y2="-2.2" width="0.1" layer="51"/>
<wire x1="10.5" y1="-2.2" x2="-1.5" y2="-2.2" width="0.1" layer="51"/>
<wire x1="0" y1="-2.2" x2="10.5" y2="-2.2" width="0.2" layer="21"/>
<wire x1="10.5" y1="-2.2" x2="10.5" y2="1.3" width="0.2" layer="21"/>
<wire x1="10.5" y1="1.3" x2="-1.5" y2="1.3" width="0.2" layer="21"/>
<wire x1="-1.5" y1="1.3" x2="-1.5" y2="0" width="0.2" layer="21"/>
</package>
</packages>
<symbols>
<symbol name="B7B-ZR_(LF)(SN)">
<wire x1="5.08" y1="2.54" x2="15.24" y2="2.54" width="0.254" layer="94"/>
<wire x1="15.24" y1="-17.78" x2="15.24" y2="2.54" width="0.254" layer="94"/>
<wire x1="15.24" y1="-17.78" x2="5.08" y2="-17.78" width="0.254" layer="94"/>
<wire x1="5.08" y1="2.54" x2="5.08" y2="-17.78" width="0.254" layer="94"/>
<text x="16.51" y="7.62" size="1.778" layer="95" align="center-left">&gt;NAME</text>
<text x="16.51" y="5.08" size="1.778" layer="96" align="center-left">&gt;VALUE</text>
<pin name="1" x="0" y="0" length="middle"/>
<pin name="2" x="0" y="-2.54" length="middle"/>
<pin name="3" x="0" y="-5.08" length="middle"/>
<pin name="4" x="0" y="-7.62" length="middle"/>
<pin name="5" x="0" y="-10.16" length="middle"/>
<pin name="6" x="0" y="-12.7" length="middle"/>
<pin name="7" x="0" y="-15.24" length="middle"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="B7B-ZR_(LF)(SN)" prefix="J">
<description>&lt;b&gt;Connector,Multipole,PCB use,B7B-ZR (LF)( JST ZH Series, 1.5mm Pitch 7 Way 1 Row Straight PCB Header, Solder Termination, 1A&lt;/b&gt;&lt;p&gt;
Source: &lt;a href="http://docs-emea.rs-online.com/webdocs/1147/0900766b81147f94.pdf"&gt; Datasheet &lt;/a&gt;</description>
<gates>
<gate name="G$1" symbol="B7B-ZR_(LF)(SN)" x="0" y="0"/>
</gates>
<devices>
<device name="" package="SHDR7W50P0X150_1X7_1200X350X45">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
<connect gate="G$1" pin="4" pad="4"/>
<connect gate="G$1" pin="5" pad="5"/>
<connect gate="G$1" pin="6" pad="6"/>
<connect gate="G$1" pin="7" pad="7"/>
</connects>
<technologies>
<technology name="">
<attribute name="DESCRIPTION" value="Connector,Multipole,PCB use,B7B-ZR (LF)( JST ZH Series, 1.5mm Pitch 7 Way 1 Row Straight PCB Header, Solder Termination, 1A" constant="no"/>
<attribute name="HEIGHT" value="4.5mm" constant="no"/>
<attribute name="MANUFACTURER_NAME" value="JST (JAPAN SOLDERLESS TERMINALS)" constant="no"/>
<attribute name="MANUFACTURER_PART_NUMBER" value="B7B-ZR (LF)(SN)" constant="no"/>
<attribute name="MOUSER_PART_NUMBER" value="" constant="no"/>
<attribute name="MOUSER_PRICE-STOCK" value="" constant="no"/>
<attribute name="RS_PART_NUMBER" value="7620828" constant="no"/>
<attribute name="RS_PRICE-STOCK" value="https://uk.rs-online.com/web/p/products/7620828" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="TLC59211IN">
<description>&lt;8-Bit DMOS Sink Driver&lt;/b&gt;&lt;p&gt;
&lt;author&gt;Created by SamacSys&lt;/author&gt;</description>
<packages>
<package name="DIP794W53P254L2540H508Q20N">
<description>&lt;b&gt;TLC59211IN&lt;/b&gt;&lt;br&gt;
</description>
<pad name="1" x="-3.97" y="11.43" drill="0.73" diameter="1.13" shape="square"/>
<pad name="2" x="-3.97" y="8.89" drill="0.73" diameter="1.13"/>
<pad name="3" x="-3.97" y="6.35" drill="0.73" diameter="1.13"/>
<pad name="4" x="-3.97" y="3.81" drill="0.73" diameter="1.13"/>
<pad name="5" x="-3.97" y="1.27" drill="0.73" diameter="1.13"/>
<pad name="6" x="-3.97" y="-1.27" drill="0.73" diameter="1.13"/>
<pad name="7" x="-3.97" y="-3.81" drill="0.73" diameter="1.13"/>
<pad name="8" x="-3.97" y="-6.35" drill="0.73" diameter="1.13"/>
<pad name="9" x="-3.97" y="-8.89" drill="0.73" diameter="1.13"/>
<pad name="10" x="-3.97" y="-11.43" drill="0.73" diameter="1.13"/>
<pad name="11" x="3.97" y="-11.43" drill="0.73" diameter="1.13"/>
<pad name="12" x="3.97" y="-8.89" drill="0.73" diameter="1.13"/>
<pad name="13" x="3.97" y="-6.35" drill="0.73" diameter="1.13"/>
<pad name="14" x="3.97" y="-3.81" drill="0.73" diameter="1.13"/>
<pad name="15" x="3.97" y="-1.27" drill="0.73" diameter="1.13"/>
<pad name="16" x="3.97" y="1.27" drill="0.73" diameter="1.13"/>
<pad name="17" x="3.97" y="3.81" drill="0.73" diameter="1.13"/>
<pad name="18" x="3.97" y="6.35" drill="0.73" diameter="1.13"/>
<pad name="19" x="3.97" y="8.89" drill="0.73" diameter="1.13"/>
<pad name="20" x="3.97" y="11.43" drill="0.73" diameter="1.13"/>
<text x="0" y="0" size="1.27" layer="25" align="center">&gt;NAME</text>
<text x="0" y="0" size="1.27" layer="27" align="center">&gt;VALUE</text>
<wire x1="-4.945" y1="13.71" x2="4.945" y2="13.71" width="0.05" layer="51"/>
<wire x1="4.945" y1="13.71" x2="4.945" y2="-13.71" width="0.05" layer="51"/>
<wire x1="4.945" y1="-13.71" x2="-4.945" y2="-13.71" width="0.05" layer="51"/>
<wire x1="-4.945" y1="-13.71" x2="-4.945" y2="13.71" width="0.05" layer="51"/>
<wire x1="-3.3" y1="13.46" x2="3.3" y2="13.46" width="0.1" layer="51"/>
<wire x1="3.3" y1="13.46" x2="3.3" y2="-13.46" width="0.1" layer="51"/>
<wire x1="3.3" y1="-13.46" x2="-3.3" y2="-13.46" width="0.1" layer="51"/>
<wire x1="-3.3" y1="-13.46" x2="-3.3" y2="13.46" width="0.1" layer="51"/>
<wire x1="-3.3" y1="12.19" x2="-2.03" y2="13.46" width="0.1" layer="51"/>
<wire x1="-4.535" y1="13.46" x2="3.3" y2="13.46" width="0.2" layer="21"/>
<wire x1="-3.3" y1="-13.46" x2="3.3" y2="-13.46" width="0.2" layer="21"/>
</package>
</packages>
<symbols>
<symbol name="TLC59211IN">
<wire x1="5.08" y1="2.54" x2="25.4" y2="2.54" width="0.254" layer="94"/>
<wire x1="25.4" y1="-25.4" x2="25.4" y2="2.54" width="0.254" layer="94"/>
<wire x1="25.4" y1="-25.4" x2="5.08" y2="-25.4" width="0.254" layer="94"/>
<wire x1="5.08" y1="2.54" x2="5.08" y2="-25.4" width="0.254" layer="94"/>
<text x="26.67" y="7.62" size="1.778" layer="95" align="center-left">&gt;NAME</text>
<text x="26.67" y="5.08" size="1.778" layer="96" align="center-left">&gt;VALUE</text>
<pin name="N.C._1" x="0" y="0" length="middle"/>
<pin name="D1" x="0" y="-2.54" length="middle"/>
<pin name="D2" x="0" y="-5.08" length="middle"/>
<pin name="D3" x="0" y="-7.62" length="middle"/>
<pin name="D4" x="0" y="-10.16" length="middle"/>
<pin name="D5" x="0" y="-12.7" length="middle"/>
<pin name="D6" x="0" y="-15.24" length="middle"/>
<pin name="D7" x="0" y="-17.78" length="middle"/>
<pin name="D8" x="0" y="-20.32" length="middle"/>
<pin name="N.C._2" x="0" y="-22.86" length="middle"/>
<pin name="VCC" x="30.48" y="0" length="middle" rot="R180"/>
<pin name="!Y1" x="30.48" y="-2.54" length="middle" rot="R180"/>
<pin name="!Y2" x="30.48" y="-5.08" length="middle" rot="R180"/>
<pin name="!Y3" x="30.48" y="-7.62" length="middle" rot="R180"/>
<pin name="!Y4" x="30.48" y="-10.16" length="middle" rot="R180"/>
<pin name="!Y5" x="30.48" y="-12.7" length="middle" rot="R180"/>
<pin name="!Y6" x="30.48" y="-15.24" length="middle" rot="R180"/>
<pin name="!Y7" x="30.48" y="-17.78" length="middle" rot="R180"/>
<pin name="!Y8" x="30.48" y="-20.32" length="middle" rot="R180"/>
<pin name="GND" x="30.48" y="-22.86" length="middle" rot="R180"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="TLC59211IN" prefix="IC">
<description>&lt;b&gt;8-Bit DMOS Sink Driver&lt;/b&gt;&lt;p&gt;
Source: &lt;a href="http://www.ti.com/lit/gpn/tlc59211"&gt; Datasheet &lt;/a&gt;</description>
<gates>
<gate name="G$1" symbol="TLC59211IN" x="0" y="0"/>
</gates>
<devices>
<device name="" package="DIP794W53P254L2540H508Q20N">
<connects>
<connect gate="G$1" pin="!Y1" pad="19"/>
<connect gate="G$1" pin="!Y2" pad="18"/>
<connect gate="G$1" pin="!Y3" pad="17"/>
<connect gate="G$1" pin="!Y4" pad="16"/>
<connect gate="G$1" pin="!Y5" pad="15"/>
<connect gate="G$1" pin="!Y6" pad="14"/>
<connect gate="G$1" pin="!Y7" pad="13"/>
<connect gate="G$1" pin="!Y8" pad="12"/>
<connect gate="G$1" pin="D1" pad="2"/>
<connect gate="G$1" pin="D2" pad="3"/>
<connect gate="G$1" pin="D3" pad="4"/>
<connect gate="G$1" pin="D4" pad="5"/>
<connect gate="G$1" pin="D5" pad="6"/>
<connect gate="G$1" pin="D6" pad="7"/>
<connect gate="G$1" pin="D7" pad="8"/>
<connect gate="G$1" pin="D8" pad="9"/>
<connect gate="G$1" pin="GND" pad="11"/>
<connect gate="G$1" pin="N.C._1" pad="1"/>
<connect gate="G$1" pin="N.C._2" pad="10"/>
<connect gate="G$1" pin="VCC" pad="20"/>
</connects>
<technologies>
<technology name="">
<attribute name="DESCRIPTION" value="8-Bit DMOS Sink Driver" constant="no"/>
<attribute name="HEIGHT" value="5.08mm" constant="no"/>
<attribute name="MANUFACTURER_NAME" value="Texas Instruments" constant="no"/>
<attribute name="MANUFACTURER_PART_NUMBER" value="TLC59211IN" constant="no"/>
<attribute name="MOUSER_PART_NUMBER" value="595-TLC59211IN" constant="no"/>
<attribute name="MOUSER_PRICE-STOCK" value="https://www.mouser.com/Search/Refine.aspx?Keyword=595-TLC59211IN" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="4309R-101-202LF">
<description>&lt;Resistor Networks &amp; Arrays 9pin 2Kohms Bussed Low Profile&lt;/b&gt;&lt;p&gt;
&lt;author&gt;Created by SamacSys&lt;/author&gt;</description>
<packages>
<package name="4309R-101">
<description>&lt;b&gt;4309R-101&lt;/b&gt;&lt;br&gt;
</description>
<pad name="1" x="0" y="0" drill="0.77" diameter="1.27"/>
<pad name="2" x="2.54" y="0" drill="0.75" diameter="1.25"/>
<pad name="3" x="5.08" y="0" drill="0.75" diameter="1.25"/>
<pad name="4" x="7.62" y="0" drill="0.75" diameter="1.25"/>
<pad name="5" x="10.16" y="0" drill="0.75" diameter="1.25"/>
<pad name="6" x="12.7" y="0" drill="0.75" diameter="1.25"/>
<pad name="7" x="15.24" y="0" drill="0.75" diameter="1.25"/>
<pad name="8" x="17.78" y="0" drill="0.75" diameter="1.25"/>
<pad name="9" x="20.32" y="0" drill="0.75" diameter="1.25"/>
<text x="8.41966875" y="-0.26233125" size="1.27" layer="27" align="center">&gt;VALUE</text>
<text x="8.41966875" y="-0.26233125" size="1.27" layer="25" align="center">&gt;NAME</text>
<wire x1="21.565" y1="-1.245" x2="-1.245" y2="-1.245" width="0.2" layer="21"/>
<wire x1="-1.245" y1="-1.245" x2="-1.245" y2="1.245" width="0.2" layer="21"/>
<wire x1="-1.245" y1="1.245" x2="21.565" y2="1.245" width="0.2" layer="21"/>
<wire x1="21.565" y1="1.245" x2="21.565" y2="-1.245" width="0.2" layer="21"/>
<wire x1="21.565" y1="-1.245" x2="-1.245" y2="-1.245" width="0.2" layer="51"/>
<wire x1="-1.245" y1="-1.245" x2="-1.245" y2="1.245" width="0.2" layer="51"/>
<wire x1="-1.245" y1="1.245" x2="21.565" y2="1.245" width="0.2" layer="51"/>
<wire x1="21.565" y1="1.245" x2="21.565" y2="-1.245" width="0.2" layer="51"/>
</package>
</packages>
<symbols>
<symbol name="4309R-101-202LF">
<wire x1="5.08" y1="2.54" x2="15.24" y2="2.54" width="0.254" layer="94"/>
<wire x1="15.24" y1="-12.7" x2="15.24" y2="2.54" width="0.254" layer="94"/>
<wire x1="15.24" y1="-12.7" x2="5.08" y2="-12.7" width="0.254" layer="94"/>
<wire x1="5.08" y1="2.54" x2="5.08" y2="-12.7" width="0.254" layer="94"/>
<text x="16.51" y="7.62" size="1.778" layer="95" align="center-left">&gt;NAME</text>
<text x="16.51" y="5.08" size="1.778" layer="96" align="center-left">&gt;VALUE</text>
<pin name="1" x="0" y="0" length="middle"/>
<pin name="2" x="0" y="-2.54" length="middle"/>
<pin name="3" x="0" y="-5.08" length="middle"/>
<pin name="4" x="0" y="-7.62" length="middle"/>
<pin name="5" x="0" y="-10.16" length="middle"/>
<pin name="6" x="20.32" y="0" length="middle" rot="R180"/>
<pin name="7" x="20.32" y="-2.54" length="middle" rot="R180"/>
<pin name="8" x="20.32" y="-5.08" length="middle" rot="R180"/>
<pin name="9" x="20.32" y="-7.62" length="middle" rot="R180"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="4309R-101-202LF" prefix="RN">
<description>&lt;b&gt;Resistor Networks &amp; Arrays 9pin 2Kohms Bussed Low Profile&lt;/b&gt;&lt;p&gt;
Source: &lt;a href="https://componentsearchengine.com/Datasheets/1/4309R-101-202LF.pdf"&gt; Datasheet &lt;/a&gt;</description>
<gates>
<gate name="G$1" symbol="4309R-101-202LF" x="0" y="0"/>
</gates>
<devices>
<device name="" package="4309R-101">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
<connect gate="G$1" pin="4" pad="4"/>
<connect gate="G$1" pin="5" pad="5"/>
<connect gate="G$1" pin="6" pad="6"/>
<connect gate="G$1" pin="7" pad="7"/>
<connect gate="G$1" pin="8" pad="8"/>
<connect gate="G$1" pin="9" pad="9"/>
</connects>
<technologies>
<technology name="">
<attribute name="DESCRIPTION" value="Resistor Networks &amp; Arrays 9pin 2Kohms Bussed Low Profile" constant="no"/>
<attribute name="HEIGHT" value="mm" constant="no"/>
<attribute name="MANUFACTURER_NAME" value="Bourns" constant="no"/>
<attribute name="MANUFACTURER_PART_NUMBER" value="4309R-101-202LF" constant="no"/>
<attribute name="MOUSER_PART_NUMBER" value="652-4309R-1LF-2K" constant="no"/>
<attribute name="MOUSER_PRICE-STOCK" value="https://www.mouser.com/Search/Refine.aspx?Keyword=652-4309R-1LF-2K" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
</libraries>
<attributes>
</attributes>
<variantdefs>
</variantdefs>
<classes>
<class number="0" name="default" width="0" drill="0">
</class>
</classes>
<parts>
<part name="_1" library="teensy" deviceset="TEENSY" device=""/>
<part name="J1" library="SamacSys_Parts" deviceset="B7B-ZR_(LF)(SN)" device=""/>
<part name="J2" library="SamacSys_Parts" deviceset="B7B-ZR_(LF)(SN)" device=""/>
<part name="J3" library="SamacSys_Parts" deviceset="B7B-ZR_(LF)(SN)" device=""/>
<part name="J4" library="SamacSys_Parts" deviceset="B7B-ZR_(LF)(SN)" device=""/>
<part name="J5" library="SamacSys_Parts" deviceset="B7B-ZR_(LF)(SN)" device=""/>
<part name="J6" library="SamacSys_Parts" deviceset="B7B-ZR_(LF)(SN)" device=""/>
<part name="IC1" library="TLC59211IN" deviceset="TLC59211IN" device=""/>
<part name="RN1" library="4309R-101-202LF" deviceset="4309R-101-202LF" device=""/>
<part name="RN2" library="4309R-101-202LF" deviceset="4309R-101-202LF" device=""/>
</parts>
<sheets>
<sheet>
<plain>
<text x="205.74" y="-22.86" size="1.778" layer="91">Thumb</text>
<text x="205.74" y="68.58" size="1.778" layer="91">Pinky</text>
<text x="205.74" y="45.72" size="1.778" layer="91">Ring Finger</text>
<text x="205.74" y="22.86" size="1.778" layer="91">Middle Finger</text>
<text x="205.74" y="0" size="1.778" layer="91">Fore Finger</text>
</plain>
<instances>
<instance part="_1" gate="G$1" x="101.6" y="48.26" smashed="yes">
<attribute name="NAME" x="96.52" y="86.36" size="1.778" layer="95"/>
<attribute name="VALUE" x="96.52" y="50.8" size="1.778" layer="96" rot="R270"/>
</instance>
<instance part="J1" gate="G$1" x="187.96" y="81.28" smashed="yes">
<attribute name="NAME" x="204.47" y="88.9" size="1.778" layer="95" align="center-left"/>
<attribute name="VALUE" x="204.47" y="86.36" size="1.778" layer="96" align="center-left"/>
</instance>
<instance part="J2" gate="G$1" x="187.96" y="58.42" smashed="yes">
<attribute name="NAME" x="204.47" y="66.04" size="1.778" layer="95" align="center-left"/>
<attribute name="VALUE" x="204.47" y="63.5" size="1.778" layer="96" align="center-left"/>
</instance>
<instance part="J3" gate="G$1" x="187.96" y="35.56" smashed="yes">
<attribute name="NAME" x="204.47" y="43.18" size="1.778" layer="95" align="center-left"/>
<attribute name="VALUE" x="204.47" y="40.64" size="1.778" layer="96" align="center-left"/>
</instance>
<instance part="J4" gate="G$1" x="187.96" y="12.7" smashed="yes">
<attribute name="NAME" x="204.47" y="20.32" size="1.778" layer="95" align="center-left"/>
<attribute name="VALUE" x="204.47" y="17.78" size="1.778" layer="96" align="center-left"/>
</instance>
<instance part="J5" gate="G$1" x="187.96" y="-10.16" smashed="yes">
<attribute name="NAME" x="204.47" y="-2.54" size="1.778" layer="95" align="center-left"/>
<attribute name="VALUE" x="204.47" y="-5.08" size="1.778" layer="96" align="center-left"/>
</instance>
<instance part="J6" gate="G$1" x="43.18" y="48.26" smashed="yes" rot="R180">
<attribute name="NAME" x="26.67" y="40.64" size="1.778" layer="95" rot="R180" align="center-left"/>
<attribute name="VALUE" x="26.67" y="43.18" size="1.778" layer="96" rot="R180" align="center-left"/>
</instance>
<instance part="IC1" gate="G$1" x="139.7" y="121.92" smashed="yes">
<attribute name="NAME" x="166.37" y="129.54" size="1.778" layer="95" align="center-left"/>
<attribute name="VALUE" x="166.37" y="127" size="1.778" layer="96" align="center-left"/>
</instance>
<instance part="RN1" gate="G$1" x="93.98" y="-2.54" smashed="yes">
<attribute name="NAME" x="110.49" y="5.08" size="1.778" layer="95" align="center-left"/>
<attribute name="VALUE" x="110.49" y="2.54" size="1.778" layer="96" align="center-left"/>
</instance>
<instance part="RN2" gate="G$1" x="66.04" y="88.9" smashed="yes" rot="R270">
<attribute name="NAME" x="73.66" y="72.39" size="1.778" layer="95" rot="R270" align="center-left"/>
<attribute name="VALUE" x="71.12" y="72.39" size="1.778" layer="96" rot="R270" align="center-left"/>
</instance>
</instances>
<busses>
</busses>
<nets>
<net name="N$1" class="0">
<segment>
<wire x1="172.72" y1="-12.7" x2="172.72" y2="10.16" width="0.1524" layer="91"/>
<pinref part="J1" gate="G$1" pin="2"/>
<wire x1="172.72" y1="10.16" x2="172.72" y2="33.02" width="0.1524" layer="91"/>
<wire x1="172.72" y1="33.02" x2="172.72" y2="55.88" width="0.1524" layer="91"/>
<wire x1="172.72" y1="55.88" x2="172.72" y2="78.74" width="0.1524" layer="91"/>
<wire x1="187.96" y1="78.74" x2="172.72" y2="78.74" width="0.1524" layer="91"/>
<junction x="172.72" y="78.74"/>
<pinref part="J2" gate="G$1" pin="2"/>
<wire x1="187.96" y1="55.88" x2="172.72" y2="55.88" width="0.1524" layer="91"/>
<junction x="172.72" y="55.88"/>
<pinref part="J3" gate="G$1" pin="2"/>
<wire x1="187.96" y1="33.02" x2="172.72" y2="33.02" width="0.1524" layer="91"/>
<junction x="172.72" y="33.02"/>
<pinref part="J4" gate="G$1" pin="2"/>
<wire x1="187.96" y1="10.16" x2="172.72" y2="10.16" width="0.1524" layer="91"/>
<junction x="172.72" y="10.16"/>
<pinref part="J5" gate="G$1" pin="2"/>
<wire x1="187.96" y1="-12.7" x2="172.72" y2="-12.7" width="0.1524" layer="91"/>
<wire x1="172.72" y1="78.74" x2="172.72" y2="81.28" width="0.1524" layer="91"/>
<pinref part="_1" gate="G$1" pin="5V"/>
<wire x1="114.3" y1="81.28" x2="172.72" y2="81.28" width="0.1524" layer="91"/>
<pinref part="IC1" gate="G$1" pin="VCC"/>
<wire x1="172.72" y1="121.92" x2="170.18" y2="121.92" width="0.1524" layer="91"/>
<wire x1="172.72" y1="81.28" x2="172.72" y2="121.92" width="0.1524" layer="91"/>
<junction x="172.72" y="81.28"/>
</segment>
</net>
<net name="N$2" class="0">
<segment>
<pinref part="_1" gate="G$1" pin="_F1"/>
<wire x1="114.3" y1="43.18" x2="152.4" y2="43.18" width="0.1524" layer="91"/>
<wire x1="152.4" y1="43.18" x2="152.4" y2="53.34" width="0.1524" layer="91"/>
<pinref part="J1" gate="G$1" pin="3"/>
<wire x1="152.4" y1="53.34" x2="152.4" y2="76.2" width="0.1524" layer="91"/>
<wire x1="152.4" y1="76.2" x2="187.96" y2="76.2" width="0.1524" layer="91"/>
<pinref part="J2" gate="G$1" pin="3"/>
<wire x1="187.96" y1="53.34" x2="152.4" y2="53.34" width="0.1524" layer="91"/>
<junction x="152.4" y="53.34"/>
<pinref part="J3" gate="G$1" pin="3"/>
<wire x1="187.96" y1="30.48" x2="152.4" y2="30.48" width="0.1524" layer="91"/>
<wire x1="152.4" y1="30.48" x2="152.4" y2="43.18" width="0.1524" layer="91"/>
<junction x="152.4" y="43.18"/>
<pinref part="J4" gate="G$1" pin="3"/>
<wire x1="187.96" y1="7.62" x2="152.4" y2="7.62" width="0.1524" layer="91"/>
<wire x1="152.4" y1="7.62" x2="152.4" y2="30.48" width="0.1524" layer="91"/>
<junction x="152.4" y="30.48"/>
<wire x1="152.4" y1="-15.24" x2="152.4" y2="-10.16" width="0.1524" layer="91"/>
<junction x="152.4" y="7.62"/>
<pinref part="J5" gate="G$1" pin="3"/>
<wire x1="152.4" y1="-10.16" x2="152.4" y2="7.62" width="0.1524" layer="91"/>
<wire x1="152.4" y1="-15.24" x2="187.96" y2="-15.24" width="0.1524" layer="91"/>
<pinref part="RN1" gate="G$1" pin="9"/>
<wire x1="152.4" y1="-10.16" x2="114.3" y2="-10.16" width="0.1524" layer="91"/>
<junction x="152.4" y="-10.16"/>
</segment>
</net>
<net name="N$4" class="0">
<segment>
<pinref part="_1" gate="G$1" pin="_F5"/>
<wire x1="114.3" y1="35.56" x2="149.86" y2="35.56" width="0.1524" layer="91"/>
<wire x1="149.86" y1="35.56" x2="149.86" y2="50.8" width="0.1524" layer="91"/>
<pinref part="J1" gate="G$1" pin="4"/>
<wire x1="149.86" y1="50.8" x2="149.86" y2="73.66" width="0.1524" layer="91"/>
<wire x1="149.86" y1="73.66" x2="187.96" y2="73.66" width="0.1524" layer="91"/>
<pinref part="J2" gate="G$1" pin="4"/>
<wire x1="187.96" y1="50.8" x2="149.86" y2="50.8" width="0.1524" layer="91"/>
<junction x="149.86" y="50.8"/>
<pinref part="J3" gate="G$1" pin="4"/>
<wire x1="187.96" y1="27.94" x2="149.86" y2="27.94" width="0.1524" layer="91"/>
<wire x1="149.86" y1="27.94" x2="149.86" y2="35.56" width="0.1524" layer="91"/>
<junction x="149.86" y="35.56"/>
<pinref part="J4" gate="G$1" pin="4"/>
<wire x1="187.96" y1="5.08" x2="149.86" y2="5.08" width="0.1524" layer="91"/>
<wire x1="149.86" y1="5.08" x2="149.86" y2="27.94" width="0.1524" layer="91"/>
<junction x="149.86" y="27.94"/>
<wire x1="149.86" y1="-17.78" x2="149.86" y2="-7.62" width="0.1524" layer="91"/>
<junction x="149.86" y="5.08"/>
<pinref part="J5" gate="G$1" pin="4"/>
<wire x1="149.86" y1="-7.62" x2="149.86" y2="5.08" width="0.1524" layer="91"/>
<wire x1="149.86" y1="-17.78" x2="187.96" y2="-17.78" width="0.1524" layer="91"/>
<pinref part="RN1" gate="G$1" pin="8"/>
<wire x1="114.3" y1="-7.62" x2="149.86" y2="-7.62" width="0.1524" layer="91"/>
<junction x="149.86" y="-7.62"/>
</segment>
</net>
<net name="N$5" class="0">
<segment>
<pinref part="_1" gate="G$1" pin="_F7"/>
<wire x1="114.3" y1="30.48" x2="147.32" y2="30.48" width="0.1524" layer="91"/>
<wire x1="147.32" y1="30.48" x2="147.32" y2="48.26" width="0.1524" layer="91"/>
<pinref part="J1" gate="G$1" pin="5"/>
<wire x1="147.32" y1="48.26" x2="147.32" y2="71.12" width="0.1524" layer="91"/>
<wire x1="147.32" y1="71.12" x2="187.96" y2="71.12" width="0.1524" layer="91"/>
<pinref part="J2" gate="G$1" pin="5"/>
<wire x1="187.96" y1="48.26" x2="147.32" y2="48.26" width="0.1524" layer="91"/>
<junction x="147.32" y="48.26"/>
<pinref part="J3" gate="G$1" pin="5"/>
<wire x1="187.96" y1="25.4" x2="147.32" y2="25.4" width="0.1524" layer="91"/>
<wire x1="147.32" y1="25.4" x2="147.32" y2="30.48" width="0.1524" layer="91"/>
<junction x="147.32" y="30.48"/>
<pinref part="J4" gate="G$1" pin="5"/>
<wire x1="187.96" y1="2.54" x2="147.32" y2="2.54" width="0.1524" layer="91"/>
<wire x1="147.32" y1="2.54" x2="147.32" y2="25.4" width="0.1524" layer="91"/>
<junction x="147.32" y="25.4"/>
<wire x1="147.32" y1="-20.32" x2="147.32" y2="-5.08" width="0.1524" layer="91"/>
<junction x="147.32" y="2.54"/>
<pinref part="J5" gate="G$1" pin="5"/>
<wire x1="147.32" y1="-5.08" x2="147.32" y2="2.54" width="0.1524" layer="91"/>
<wire x1="187.96" y1="-20.32" x2="147.32" y2="-20.32" width="0.1524" layer="91"/>
<pinref part="RN1" gate="G$1" pin="7"/>
<wire x1="114.3" y1="-5.08" x2="147.32" y2="-5.08" width="0.1524" layer="91"/>
<junction x="147.32" y="-5.08"/>
</segment>
</net>
<net name="N$7" class="0">
<segment>
<pinref part="J4" gate="G$1" pin="7"/>
<wire x1="187.96" y1="-2.54" x2="154.94" y2="-2.54" width="0.1524" layer="91"/>
<wire x1="154.94" y1="-2.54" x2="154.94" y2="-25.4" width="0.1524" layer="91"/>
<pinref part="J3" gate="G$1" pin="7"/>
<wire x1="187.96" y1="20.32" x2="154.94" y2="20.32" width="0.1524" layer="91"/>
<wire x1="154.94" y1="20.32" x2="154.94" y2="-2.54" width="0.1524" layer="91"/>
<junction x="154.94" y="-2.54"/>
<pinref part="J2" gate="G$1" pin="7"/>
<wire x1="187.96" y1="43.18" x2="154.94" y2="43.18" width="0.1524" layer="91"/>
<wire x1="154.94" y1="43.18" x2="154.94" y2="20.32" width="0.1524" layer="91"/>
<junction x="154.94" y="20.32"/>
<pinref part="J1" gate="G$1" pin="7"/>
<wire x1="187.96" y1="66.04" x2="154.94" y2="66.04" width="0.1524" layer="91"/>
<wire x1="154.94" y1="66.04" x2="154.94" y2="43.18" width="0.1524" layer="91"/>
<junction x="154.94" y="43.18"/>
<pinref part="_1" gate="G$1" pin="_D7"/>
<wire x1="88.9" y1="58.42" x2="86.36" y2="58.42" width="0.1524" layer="91"/>
<pinref part="J5" gate="G$1" pin="7"/>
<wire x1="187.96" y1="-25.4" x2="154.94" y2="-25.4" width="0.1524" layer="91"/>
<wire x1="154.94" y1="-25.4" x2="86.36" y2="-25.4" width="0.1524" layer="91"/>
<junction x="154.94" y="-25.4"/>
<pinref part="RN1" gate="G$1" pin="5"/>
<wire x1="93.98" y1="-12.7" x2="86.36" y2="-12.7" width="0.1524" layer="91"/>
<wire x1="86.36" y1="58.42" x2="86.36" y2="-12.7" width="0.1524" layer="91"/>
<junction x="86.36" y="-12.7"/>
<wire x1="86.36" y1="-12.7" x2="86.36" y2="-25.4" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$3" class="0">
<segment>
<pinref part="J5" gate="G$1" pin="6"/>
<pinref part="_1" gate="G$1" pin="_B4"/>
<wire x1="114.3" y1="73.66" x2="144.78" y2="73.66" width="0.1524" layer="91"/>
<wire x1="144.78" y1="73.66" x2="144.78" y2="68.58" width="0.1524" layer="91"/>
<pinref part="J1" gate="G$1" pin="6"/>
<wire x1="144.78" y1="68.58" x2="187.96" y2="68.58" width="0.1524" layer="91"/>
<pinref part="J2" gate="G$1" pin="6"/>
<wire x1="187.96" y1="45.72" x2="144.78" y2="45.72" width="0.1524" layer="91"/>
<wire x1="144.78" y1="45.72" x2="144.78" y2="68.58" width="0.1524" layer="91"/>
<junction x="144.78" y="68.58"/>
<pinref part="J3" gate="G$1" pin="6"/>
<wire x1="187.96" y1="22.86" x2="144.78" y2="22.86" width="0.1524" layer="91"/>
<wire x1="144.78" y1="22.86" x2="144.78" y2="45.72" width="0.1524" layer="91"/>
<junction x="144.78" y="45.72"/>
<pinref part="J4" gate="G$1" pin="6"/>
<wire x1="187.96" y1="0" x2="144.78" y2="0" width="0.1524" layer="91"/>
<wire x1="144.78" y1="0" x2="144.78" y2="22.86" width="0.1524" layer="91"/>
<junction x="144.78" y="22.86"/>
<wire x1="144.78" y1="-22.86" x2="144.78" y2="-2.54" width="0.1524" layer="91"/>
<junction x="144.78" y="0"/>
<wire x1="144.78" y1="-2.54" x2="144.78" y2="0" width="0.1524" layer="91"/>
<wire x1="187.96" y1="-22.86" x2="144.78" y2="-22.86" width="0.1524" layer="91"/>
<pinref part="RN1" gate="G$1" pin="6"/>
<wire x1="144.78" y1="-2.54" x2="114.3" y2="-2.54" width="0.1524" layer="91"/>
<junction x="144.78" y="-2.54"/>
</segment>
</net>
<net name="N$6" class="0">
<segment>
<pinref part="_1" gate="G$1" pin="_GND"/>
<wire x1="88.9" y1="81.28" x2="83.82" y2="81.28" width="0.1524" layer="91"/>
<wire x1="83.82" y1="81.28" x2="83.82" y2="91.44" width="0.1524" layer="91"/>
<wire x1="83.82" y1="91.44" x2="170.18" y2="91.44" width="0.1524" layer="91"/>
<pinref part="IC1" gate="G$1" pin="GND"/>
<wire x1="170.18" y1="99.06" x2="170.18" y2="91.44" width="0.1524" layer="91"/>
<pinref part="RN1" gate="G$1" pin="1"/>
<wire x1="93.98" y1="-2.54" x2="83.82" y2="-2.54" width="0.1524" layer="91"/>
<wire x1="83.82" y1="-2.54" x2="83.82" y2="48.26" width="0.1524" layer="91"/>
<junction x="83.82" y="81.28"/>
<pinref part="J6" gate="G$1" pin="1"/>
<wire x1="83.82" y1="48.26" x2="83.82" y2="81.28" width="0.1524" layer="91"/>
<wire x1="43.18" y1="48.26" x2="83.82" y2="48.26" width="0.1524" layer="91"/>
<junction x="83.82" y="48.26"/>
</segment>
</net>
<net name="N$9" class="0">
<segment>
<pinref part="_1" gate="G$1" pin="_B5"/>
<pinref part="IC1" gate="G$1" pin="D8"/>
<wire x1="139.7" y1="101.6" x2="137.16" y2="101.6" width="0.1524" layer="91"/>
<wire x1="114.3" y1="76.2" x2="137.16" y2="76.2" width="0.1524" layer="91"/>
<wire x1="137.16" y1="76.2" x2="137.16" y2="101.6" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$8" class="0">
<segment>
<pinref part="IC1" gate="G$1" pin="D7"/>
<wire x1="134.62" y1="104.14" x2="139.7" y2="104.14" width="0.1524" layer="91"/>
<wire x1="134.62" y1="104.14" x2="134.62" y2="78.74" width="0.1524" layer="91"/>
<pinref part="_1" gate="G$1" pin="_B6"/>
<wire x1="134.62" y1="78.74" x2="114.3" y2="78.74" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$10" class="0">
<segment>
<pinref part="_1" gate="G$1" pin="_F6"/>
<wire x1="114.3" y1="33.02" x2="129.54" y2="33.02" width="0.1524" layer="91"/>
<pinref part="IC1" gate="G$1" pin="D5"/>
<wire x1="129.54" y1="33.02" x2="129.54" y2="109.22" width="0.1524" layer="91"/>
<wire x1="129.54" y1="109.22" x2="139.7" y2="109.22" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$11" class="0">
<segment>
<pinref part="_1" gate="G$1" pin="_F4"/>
<wire x1="114.3" y1="38.1" x2="127" y2="38.1" width="0.1524" layer="91"/>
<wire x1="127" y1="38.1" x2="127" y2="114.3" width="0.1524" layer="91"/>
<pinref part="IC1" gate="G$1" pin="D3"/>
<wire x1="127" y1="114.3" x2="139.7" y2="114.3" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$12" class="0">
<segment>
<pinref part="_1" gate="G$1" pin="_F0"/>
<wire x1="114.3" y1="45.72" x2="124.46" y2="45.72" width="0.1524" layer="91"/>
<wire x1="124.46" y1="45.72" x2="124.46" y2="119.38" width="0.1524" layer="91"/>
<pinref part="IC1" gate="G$1" pin="D1"/>
<wire x1="124.46" y1="119.38" x2="139.7" y2="119.38" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$15" class="0">
<segment>
<pinref part="IC1" gate="G$1" pin="!Y5"/>
<wire x1="182.88" y1="109.22" x2="170.18" y2="109.22" width="0.1524" layer="91"/>
<wire x1="182.88" y1="109.22" x2="182.88" y2="58.42" width="0.1524" layer="91"/>
<pinref part="J2" gate="G$1" pin="1"/>
<wire x1="182.88" y1="58.42" x2="187.96" y2="58.42" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$18" class="0">
<segment>
<pinref part="_1" gate="G$1" pin="_D1"/>
<wire x1="88.9" y1="73.66" x2="78.74" y2="73.66" width="0.1524" layer="91"/>
<wire x1="78.74" y1="73.66" x2="78.74" y2="58.42" width="0.1524" layer="91"/>
<pinref part="J6" gate="G$1" pin="5"/>
<wire x1="78.74" y1="58.42" x2="66.04" y2="58.42" width="0.1524" layer="91"/>
<pinref part="RN2" gate="G$1" pin="6"/>
<wire x1="66.04" y1="58.42" x2="43.18" y2="58.42" width="0.1524" layer="91"/>
<wire x1="66.04" y1="68.58" x2="66.04" y2="58.42" width="0.1524" layer="91"/>
<junction x="66.04" y="58.42"/>
</segment>
</net>
<net name="N$20" class="0">
<segment>
<pinref part="_1" gate="G$1" pin="_D0"/>
<wire x1="88.9" y1="76.2" x2="76.2" y2="76.2" width="0.1524" layer="91"/>
<pinref part="J6" gate="G$1" pin="6"/>
<wire x1="76.2" y1="76.2" x2="76.2" y2="60.96" width="0.1524" layer="91"/>
<wire x1="76.2" y1="60.96" x2="63.5" y2="60.96" width="0.1524" layer="91"/>
<pinref part="RN2" gate="G$1" pin="7"/>
<wire x1="63.5" y1="60.96" x2="43.18" y2="60.96" width="0.1524" layer="91"/>
<wire x1="63.5" y1="68.58" x2="63.5" y2="60.96" width="0.1524" layer="91"/>
<junction x="63.5" y="60.96"/>
</segment>
</net>
<net name="N$19" class="0">
<segment>
<pinref part="RN2" gate="G$1" pin="1"/>
<wire x1="66.04" y1="93.98" x2="66.04" y2="88.9" width="0.1524" layer="91"/>
<wire x1="43.18" y1="93.98" x2="66.04" y2="93.98" width="0.1524" layer="91"/>
<pinref part="J6" gate="G$1" pin="7"/>
<wire x1="43.18" y1="63.5" x2="43.18" y2="93.98" width="0.1524" layer="91"/>
<pinref part="_1" gate="G$1" pin="_5V2"/>
<wire x1="114.3" y1="25.4" x2="119.38" y2="25.4" width="0.1524" layer="91"/>
<wire x1="119.38" y1="25.4" x2="119.38" y2="93.98" width="0.1524" layer="91"/>
<wire x1="119.38" y1="93.98" x2="66.04" y2="93.98" width="0.1524" layer="91"/>
<junction x="66.04" y="93.98"/>
</segment>
</net>
<net name="N$22" class="0">
<segment>
<pinref part="J3" gate="G$1" pin="1"/>
<wire x1="187.96" y1="35.56" x2="180.34" y2="35.56" width="0.1524" layer="91"/>
<pinref part="IC1" gate="G$1" pin="!Y3"/>
<wire x1="180.34" y1="114.3" x2="170.18" y2="114.3" width="0.1524" layer="91"/>
<wire x1="180.34" y1="35.56" x2="180.34" y2="114.3" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$23" class="0">
<segment>
<pinref part="J4" gate="G$1" pin="1"/>
<pinref part="IC1" gate="G$1" pin="!Y1"/>
<wire x1="170.18" y1="119.38" x2="177.8" y2="119.38" width="0.1524" layer="91"/>
<wire x1="177.8" y1="119.38" x2="177.8" y2="12.7" width="0.1524" layer="91"/>
<wire x1="177.8" y1="12.7" x2="187.96" y2="12.7" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$24" class="0">
<segment>
<pinref part="J5" gate="G$1" pin="1"/>
<pinref part="IC1" gate="G$1" pin="!Y8"/>
<wire x1="170.18" y1="101.6" x2="175.26" y2="101.6" width="0.1524" layer="91"/>
<wire x1="175.26" y1="101.6" x2="175.26" y2="-10.16" width="0.1524" layer="91"/>
<wire x1="175.26" y1="-10.16" x2="187.96" y2="-10.16" width="0.1524" layer="91"/>
</segment>
</net>
<net name="N$25" class="0">
<segment>
<pinref part="J1" gate="G$1" pin="1"/>
<pinref part="IC1" gate="G$1" pin="!Y7"/>
<wire x1="185.42" y1="104.14" x2="170.18" y2="104.14" width="0.1524" layer="91"/>
<wire x1="187.96" y1="81.28" x2="185.42" y2="81.28" width="0.1524" layer="91"/>
<wire x1="185.42" y1="81.28" x2="185.42" y2="104.14" width="0.1524" layer="91"/>
</segment>
</net>
</nets>
</sheet>
</sheets>
</schematic>
</drawing>
</eagle>
