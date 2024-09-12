import os
import struct

class BinaryReader:
    def __init__(self, file):
        self.file = file

    def tell(self):
        return self.file.tell()

    def seek(self, offset, whence=0):
        self.file.seek(offset, whence)

    def read(self, size):
        return self.file.read(size)

    def i(self, count=1):
        return struct.unpack('<' + 'I' * count, self.file.read(4 * count))

    def H(self, count=1):
        return struct.unpack('<' + 'H' * count, self.file.read(2 * count))
    
    def h(self, count=1):
        return struct.unpack('<' + 'h' * count, self.file.read(2 * count))

    def B(self, count=1):
        return struct.unpack('<' + 'B' * count, self.file.read(count))

    def half(self, count=1):
        return struct.unpack('<' + 'e' * count, self.file.read(2 * count))

    def f(self, count=1):
        return struct.unpack('<' + 'f' * count, self.file.read(4 * count))

    def word(self, count):
        return self.file.read(count)

    def fileSize(self):
        pos = self.file.tell()
        self.file.seek(0, os.SEEK_END)
        size = self.file.tell()
        self.file.seek(pos)
        return size

def bin_parser(filename):
    with open(filename, 'rb') as f:
        g = BinaryReader(f)

        streams = {}
        materials = {}
        streamsID = []
        mesh_list = []
        meshID = 0
        bonenamelist = []

        while True:
            if g.tell() == g.fileSize():
                break

            vm = g.i(4)
            t = g.tell()
            g.seek(vm[3], 1)
            vc = g.i(7)
            g.word(36)

            if vm[0] == -1742448933:
                vn = g.i(8)
                g.B(160)
                for _ in range(vn[1]):
                    bonenamelist.append(g.word(64))
                for _ in range(vn[1]):
                    v1 = g.h(1)[0] * 2**-14
                    v2 = g.h(1)[0] * 2**-14
                    v3 = g.h(1)[0] * 2**-14
                    v4 = g.h(1)[0] * 2**-14
                    print(v1, v2, v3, v4)

            if vm[0] == 1845060531:
                print(f"Found mesh info section at offset {t}")
                vn = g.i(32)
                off = g.tell()
                offsetlist = g.i(vn[16])
                print(f"Offset list: {offsetlist}")
                for m in range(vn[16]):
                    g.seek(m * 4 + off + offsetlist[m])
                    va = g.i(36)
                    print(f"Mesh {m} info:", va)

                    if str(va[11]) in streams:
                        materialID = va[3]
                        print(f"Material ID: {materialID}")

                        if va[15] not in streamsID:
                            streamsID.append(va[15])
                            meshID += 1

                        # could write to block names for now, just using mesh info offset
                        mesh_filename = f"{filename}_offset_{t}_mesh_{m}.txt"
                        with open(mesh_filename, 'w') as output_file:
                            output_file.write("vertex start\n")

                            vertexstream = streams[str(va[15])]
                            print(f"Seeking to vertex stream at offset {vertexstream[1]} for mesh {m}")
                            g.seek(vertexstream[1])

                            num_vertices = vertexstream[0][4]
                            print(f"Number of vertices: {num_vertices}")

                            vertices = []
                            if vertexstream[0][3] == 16:
                                for n in range(num_vertices):
                                    tn = g.tell()
                                    x = g.h(1)[0] * 2**-14
                                    y = g.h(1)[0] * 2**-14
                                    z = g.h(1)[0] * 2**-14
                                    vertices.append(f"{x} {y} {z}")
                                    g.seek(tn + vertexstream[0][3])
                            if vertexstream[0][3] == 12:
                                for n in range(num_vertices):
                                    tn = g.tell()
                                    vertex = g.f(3)
                                    vertices.append(f"{vertex[0]} {vertex[1]} {vertex[2]}")
                                    g.seek(tn + vertexstream[0][3])

                            if str(va[23]) in streams:
                                uvstream = streams[str(va[23])]
                                g.seek(uvstream[1])

                                num_uvs = uvstream[0][4]
                                print(f"Number of UV pairs: {num_uvs}")

                                if num_uvs == num_vertices:
                                    for n in range(num_uvs):
                                        tn = g.tell()
                                        uv = g.half(2)
                                        vertices[n] += f" {uv[0]} {uv[1]}"
                                        g.seek(tn + uvstream[0][3])
                                else:
                                    print(f"Error: Number of UV pairs ({num_uvs}) does not match number of vertices ({num_vertices}) in mesh {m}. Skipping UVs.")

                            # if match, append uvs to verts
                            output_file.write("\n".join(vertices) + "\n")
                            output_file.write("vertex end\n")

                            output_file.write("index start\n")

                            indicesstream = streams[str(va[11])]
                            print(f"Seeking to indices stream at offset {indicesstream[1]} for mesh {m}")
                            g.seek(indicesstream[1])
                            indices = g.h(indicesstream[0][4])[va[29]:va[29] + va[30] * 3]
                            for i in range(0, len(indices), 3):
                                output_file.write(f"{indices[i]} {indices[i+1]} {indices[i+2]}\n")

                            output_file.write("index end\n")

            if vm[0] == -168275601:
                print("Found material section")
                materials[str(vc[3])] = {}
                vn = g.i(8)
                for _ in range(vn[4]):
                    vp = g.i(8)
                    if vp[0] == -589273463:
                        materials[str(vc[3])]['diffID'] = vp[6]
                    if vp[0] == -1396934011:
                        materials[str(vc[3])]['specID'] = vp[6]

            if vm[0] == 2056721529:
                print("Found streams section")
                v = g.i(32)
                streams[str(vc[3])] = [v, g.tell()]

            g.seek(t + vm[1])

def file_format_parser(filename):
    print(f"Parsing file: {filename}")
    model_id = os.path.basename(filename).split('.')[0]
    dirname = os.path.dirname(filename)
    ext = filename.split('.')[-1].lower()

    if ext == 'bin':
        bin_parser(filename)

if __name__ == "__main__":
    for filename in os.listdir('.'):
        if filename.endswith('.perm.bin'):
            file_format_parser(filename)
