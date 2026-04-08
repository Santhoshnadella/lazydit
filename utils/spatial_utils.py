import numpy as np
import xml.etree.ElementTree as ET
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class AtmosObject:
    """
    Representation of a Spatial Audio Object with X, Y, Z keyframing.
    Coordinates are normalized: X [-1, 1], Y [-1, 1], Z [-1, 1].
    """
    def __init__(self, object_id: str, name: str, source_wav: str):
        self.object_id = object_id
        self.name = name
        self.source_wav = source_wav
        self.keyframes = [] # List of dicts: {"time": float, "pos": [x, y, z], "gain": float}

    def add_keyframe(self, time: float, x: float, y: float, z: float, gain: float = 1.0):
        self.keyframes.append({
            "time": time,
            "pos": [np.clip(x, -1, 1), np.clip(y, -1, 1), np.clip(z, -1, 1)],
            "gain": np.clip(gain, 0, 1)
        })
        self.keyframes.sort(key=lambda x: x["time"])

class ADMGenerator:
    """
    Generates ITU-R BS.2076 (ADM) compliant XML metadata for Atmos objects.
    Enables spatial audio definition within a single WAV or as a sidecar.
    """
    def __init__(self):
        self.objects: List[AtmosObject] = []

    def add_object(self, obj: AtmosObject):
        self.objects.append(obj)

    def generate_xml(self) -> str:
        """Builds the ADM XML document."""
        root = ET.Element("ituADM", version="1.0")
        
        # Audio Programme
        programme = ET.SubElement(root, "audioProgramme", audioProgrammeName="LazyDit_Atmos_Master")
        programme_id = "APR_1001"
        programme.set("audioProgrammeID", programme_id)

        # Audio Content
        content = ET.SubElement(root, "audioContent", audioContentName="Cinematic_Objects")
        content_id = "ACO_1001"
        content.set("audioContentID", content_id)
        ET.SubElement(programme, "audioContentIDRef").text = content_id

        # Process each object
        for i, obj in enumerate(self.objects):
            obj_id = f"AO_{1001+i:04d}"
            a_obj = ET.SubElement(root, "audioObject", audioObjectName=obj.name)
            a_obj.set("audioObjectID", obj_id)
            ET.SubElement(content, "audioObjectIDRef").text = obj_id

            # Channel Format (Spatial Definition)
            chan_id = f"AC_{1001+i:04d}"
            chan_format = ET.SubElement(root, "audioChannelFormat", audioChannelName=f"{obj.name}_Path")
            chan_format.set("audioChannelFormatID", chan_id)
            chan_format.set("typeLabel", "0003") # Object type
            chan_format.set("typeDefinition", "Objects")
            
            # Pack Format (Group definition)
            pack_id = f"AP_{1001+i:04d}"
            pack_format = ET.SubElement(root, "audioPackFormat", audioPackName=f"{obj.name}_Pack")
            pack_format.set("audioPackFormatID", pack_id)
            pack_format.set("typeLabel", "0003")
            pack_format.set("typeDefinition", "Objects")
            
            ET.SubElement(a_obj, "audioPackFormatIDRef").text = pack_id
            ET.SubElement(pack_format, "audioChannelFormatIDRef").text = chan_id

            # Keyframes (Block Formats)
            for j, kf in enumerate(obj.keyframes):
                block = ET.SubElement(chan_format, "audioBlockFormat")
                block.set("audioBlockFormatID", f"AB_{1001+i:04d}_{j:08d}")
                block.set("rtime", f"{kf['time']:.5f}")
                
                # Coordinates
                ET.SubElement(block, "position", coordinate="X").text = f"{kf['pos'][0]:.5f}"
                ET.SubElement(block, "position", coordinate="Y").text = f"{kf['pos'][1]:.5f}"
                ET.SubElement(block, "position", coordinate="Z").text = f"{kf['pos'][2]:.5f}"
                ET.SubElement(block, "gain").text = f"{kf['gain']:.5f}"

        # Return pretty XML string
        return ET.tostring(root, encoding="unicode")

    def export_adm_bwf(self, output_wav: str, metadata_xml: str):
        """
        Exports the ADM metadata as a sidecar or potentially as an iXML chunk.
        For now, we export as a sidecar .xml matching the .wav name.
        """
        sidecar_path = os.path.splitext(output_wav)[0] + ".adm.xml"
        with open(sidecar_path, "w", encoding="utf-8") as f:
            f.write(metadata_xml)
        logger.info(f"✅ ADM Metadata Exported: {sidecar_path}")
        return sidecar_path
