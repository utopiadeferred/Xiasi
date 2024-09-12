import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import struct
import os
import glob


resource_types = {
    0x4BCE8537: "ActionTreeResource",
    0x1BCFF4D5: "AlphaState",
    0x8ACF9964: "Animation",
    0x3D0EBC72: "AnimationGroupResource",
    0xAF8870AB: "AudioFXSettings",
    0x2C5C40A8: "BIGFile",
    0x164013D5: "BIGFileNameLookup",
    0x4F05B59A: "BSP",
    0xE2C5C78C: "BSPDebugData",
    0x80EF0B08: "BeamSettings",
    0xE691BB97: "BlendTreeResource",
    0x982456DB: "BonePalette",
    0x7A971479: "Buffer",
    0x45E061F6: "BufferD3DResource",
    0xE445B80C: "ChunkFileFatIndex",
    0x7040F7D2: "ChunkFileIndex",
    0x06526B66: "Cloud",
    0xD49B8DA4: "CloudScene",
    0xA0B2CC13: "CollisionInstance",
    0xBD226A08: "CollisionMeshBundle",
    0x9D6378CC: "CoronaFlareSettings",
    0x5DEB3457: "CoverData",
    0xDCAEC503: "DecalSettings",
    0xE5150CC0: "DynamicCoverData",
    0x7117991B: "DynamicCoverGroupBundle",
    0x230C8A9C: "DynamicLightGroupSettings",
    0x8D0E8333: "DynamicLightSettings",
    0xD9B10F14: "EffectEmitterSettings",
    0x77554FC5: "FXForceSettings",
    0x12289ADB: "FXSettings",
    0xF40E78D9: "FarGroundLayout",
    0x83574C18: "FlareSettings",
    0x2A1BE612: "Font",
    0x52A8963A: "GeoSettings",
    0xAEDF1081: "ImposterGroup",
    0x7480E00F: "LightGroup",
    0xB4AEE124: "LightningSettings",
    0x15506061: "Locators",
    0xF5F8516F: "Material",
    0xEB9FE716: "MaterialTable",
    0x6DF963B3: "ModelData",
    0xF2700F96: "eVertexDecl_UVN", #endian swapped?
    0x9BA68DBC: "eVertexDecl_UVNT",
    0x911E1A51: "eVertexDecl_UVNTC",
    0x78921EA0: "eVertexDecl_UV2NTC",
    0x276B9567: "eVertexDecl_Skinned",
    0xE234EF7A: "eVertexDecl_VehicleUVNTC",
    0x7E0D7533: "eVertexDecl_SlimUV",
    0xAC5D89E2: "eVertexDecl_SkinnedUVNT",
    0x02CD0C47: "MorphTargets",
    0xE9453F67: "MovieResourceData",
    0xC762C801: "NISSpatialData",
    0xDD3C7B19: "NavMeshData",
    0xBDE53ECA: "ParkourContainer",
    0x12D3A53D: "ParkourContainerBundle",
    0xC31501A5: "ParkourInstance",
    0xD05B6976: "ParticleEmitterSettings",
    0x5B9BF81E: "PropertySet",
    0xB27A4B38: "RasterState",
    0x616A903F: "ReflectResource",
    0xD53B5BAC: "ReflectionGroup",
    0x1418DD74: "Rig",
    0x036C2E8E: "RigInfoResource",
    0x5C66C6BD: "RigInstance",
    0x94132761: "RoadNetwork",
    0xE7F23AEE: "SceneLayer",
    0x7480E00B: "SceneryGroup",
    0x657192D6: "ScreenParticleEmitterSettings",
    0x89A7BDF7: "SectionEffects",
    0x3E50F7D5: "SectionLayout",
    0x985BE50C: "ShaderBinary",
    0x0C46AEEF: "ShaderTemplate",
    0x2C81C14B: "Sidewalk",
    0xAF015A94: "StateBlock",
    0xE4868DBE: "SymbolTableResource",
    0xC462DD28: "TerrainData",
    0xCDBFA090: "Texture",
    0x501B8E62: "TextureD3DResource",
    0x86DE69F6: "TrackStripSettings",
    0x90EEF023: "TrueCrowdDataBase",
    0x32890C01: "UELFragmentTable",
    0x90CE6B7A: "UILocalization",
    0x9F34FF46: "UIMinimapTile",
    0x442A39D9: "UIScreen",
    0x2C40FA26: "UniqueUIDTableResource",
    0xF7FC6B2D: "VertexDecl",
    0xA8EB0D0C: "VolumetricEffectSettings",
    0x1146D4C8: "WeightSetGroupResource",
    0x24D0C3A0: "XMLFile",
    0x43FF83A9: "ZoneLayout",
}

cwd = os.getcwd()

def find_resources(file_path):
    results = {}
    with open(file_path, 'rb') as file:
        data = file.read()
        for res_type, res_name in resource_types.items():
            offsets = []
            offset = data.find(struct.pack('<I', res_type))
            while offset != -1:
                detail = ""
                if res_type == 0xCDBFA090:  # Texture resource
                    name_end = data.find(b'\x00', offset + 44)
                    try:
                        texture_name = data[offset + 44:name_end].decode('utf-8')
                    except UnicodeDecodeError:
                        print(f"Skipping texture at offset {offset} due to Unicode decoding error.")
                        offset = data.find(struct.pack('<I', res_type), offset + 1)
                        continue

                    i = name_end + 1
                    while data[i] == 0:
                        i += 1

                    texture_type = struct.unpack('<I', data[i:i + 4])[0]
                    texture_type_str = {1: "DXT1", 2: "DXT3", 3: "DXT5"}.get(texture_type, "Unknown")

                    height, width = struct.unpack('<HH', data[i + 8:i + 12])

                    texturetype2_offset = i + 12
                    texturetype2 = struct.unpack('<I', data[texturetype2_offset:texturetype2_offset + 4])[0]

                    unk_offset = texturetype2_offset + 4
                    unk = data[unk_offset:unk_offset + 28]

                    rawdataoffset_offset = unk_offset + 28
                    rawdataoffset = struct.unpack('<I', data[rawdataoffset_offset:rawdataoffset_offset + 4])[0]

                    rawdatasize_offset = rawdataoffset_offset + 4
                    rawdatasize = struct.unpack('<I', data[rawdatasize_offset:rawdatasize_offset + 4])[0]

                    detail = f"Name: {texture_name}, Type: {texture_type_str}, Height: {height}, Width: {width}, TextureType2: {texturetype2}, RawDataOffset: {rawdataoffset}, RawDataSize: {rawdatasize}"

                else:
                    detail = f"Offset: {offset}"

                offsets.append((offset, detail))
                offset = data.find(struct.pack('<I', res_type), offset + 1)

            if offsets:
                results[res_name] = offsets
    return results

def populate_tree_with_directories(directory_path):
    for i in tree.get_children():
        tree.delete(i)
    for root, dirs, files in os.walk(directory_path):
        for dir in dirs:
            tree.insert('', 'end', text=dir, values=(os.path.join(root, dir), "Zone"))
        for file in files:
            if file.endswith('perm.bin'):
                tree.insert('', 'end', text=file, values=(os.path.join(root, file), "Resource"))
            elif file.endswith('temp.bin'):
                tree.insert('', 'end', text=file, values=(os.path.join(root, file), "Texture"))

def open_single_file():
    file_path = filedialog.askopenfilename(title="Select a perm.bin file", filetypes=[("BIN files", "*.bin")])
    if file_path:
        results = find_resources(file_path)
        for i in tree.get_children():
            tree.delete(i)
        for res_name, offsets in results.items():
            if res_name == "Texture":
                parent_text = f"{res_name} ({len(offsets)})"
                parent = tree.insert('', 'end', text=parent_text)
                for offset, detail in offsets:
                    name = detail.split(', ')[0].split(': ')[1]
                    texture_node = tree.insert(parent, 'end', text=name)
                    tree.insert(texture_node, 'end', text=f"Offset: {offset}")
                    properties = detail.split(', ')
                    for prop in properties[1:]:
                        tree.insert(texture_node, 'end', text=prop)
            else:
                parent_text = f"{res_name} ({len(offsets)})"
                parent = tree.insert('', 'end', text=parent_text)
                for offset, detail in offsets:
                    tree.insert(parent, 'end', text=f"Offset: {offset}")

def open_directory():
    directory_path = filedialog.askdirectory(title="Select a directory containing perm.bin files")
    if directory_path:
        populate_tree_with_directories(directory_path)
        update_directory_bar(directory_path)

def update_directory_bar(path):
    directory_bar.config(text=path)

def go_back():
    parent_directory = os.path.dirname(directory_bar.cget("text"))
    if os.path.exists(parent_directory):
        populate_tree_with_directories(parent_directory)
        update_directory_bar(parent_directory)

def display_perm_bin_contents(file_path):
    for i in tree.get_children():
        tree.delete(i)
    resources = find_resources(file_path)
    for res_name, offsets in resources.items():
        if res_name == "Texture":
            parent = tree.insert('', 'end', text=f"{res_name} ({len(offsets)})")
            for offset, detail in offsets:
                name = detail.split(', ')[0].split(': ')[1]
                texture_node = tree.insert(parent, 'end', text=name)
                tree.insert(texture_node, 'end', text=f"Offset: {offset}")
                properties = detail.split(', ')
                for prop in properties[1:]:
                    tree.insert(texture_node, 'end', text=prop)
        else:
            parent = tree.insert('', 'end', text=f"{res_name} ({len(offsets)})")
            for offset, detail in offsets:
                tree.insert(parent, 'end', text=f"Offset: {offset}")

def on_tree_click(event):
    item = tree.selection()[0]
    path, type = tree.item(item, "values")
    if type == "Zone":
        populate_tree_with_directories(path)
        update_directory_bar(path)
    elif type == "Resource":
        display_perm_bin_contents(path)

root = tk.Tk()
root.title("Xiasi")
root.geometry("1920x1080")

directory_bar = tk.Label(root, text="", anchor="w")
directory_bar.pack(fill='x', padx=10, pady=5)

menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open perm.bin File", command=open_single_file)
file_menu.add_command(label="Open Directory", command=open_directory)
root.config(menu=menu_bar)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)
back_button = tk.Button(button_frame, text="Back", command=go_back)
back_button.pack(side='left', padx=5)

tree_frame = tk.Frame(root)
tree_frame.pack(expand=True, fill='both')
tree = ttk.Treeview(tree_frame, columns=("Path", "Type"), show='tree')
tree.pack(side='left', expand=True, fill='both')
tree.bind("<Double-1>", on_tree_click)

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
scrollbar.pack(side='right', fill='y')
tree.configure(yscrollcommand=scrollbar.set)

root.mainloop()