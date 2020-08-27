import sys
from NekPy.NekMeshUtils import Mesh, Module, ModuleType

# Command line format:
# loadCAD.py INPUT.stp OUTPUT.xml order Volumemesh(True/False) mindelta maxdelta eps blsurfs blthick bllayers blprog
# Must be a .stp file

class CadToMesh(object):
    # initialisation function
    def __init__(self, infile, outfile, nummode, mesh_type, mindel, maxdel, eps): #,
                # blsurfs=None, blthick=None, bllayers=None, blprog=None):
        self.infile = infile
        self.outfile = outfile
        self.mesh_type = bool(mesh_type)
        self.mindel = mindel
        self.maxdel = maxdel
        self.eps = eps
        # self.blsurfs = str(blsurfs)
        # self.blthick = str(blthick)
        # self.bllayers = str(bllayers)
        # self.blprog = str(blprog)

        self.mesh = Mesh()
        self.mesh.verbose = True
        self.mesh.expDim = 3 #set to a default of 3D
        self.mesh.spaceDim = 3 #set to a default of 3D
        self.mesh.nummode = nummode


    def cad_to_mesh(self):
        self.loadcad()
        self.create_octree(self.mindel, self.maxdel, self.eps)
        self.decision()
        self.outcad(self.outfile)

    def decision(self):
        # Method decides whether to create just a surface mesh, or a high
        # order surface mesh. If volume mesh is selected, it will be called
        # within this method.
        if self.mesh.nummode == 1:
            self.surface_mesh()
        else:
            self.surface_mesh()
            self.ho_surface_mesh()

        if self.mesh_type:
            self.volume_mesh()

    def def_and_process(self, mod):
        # Method used to process each module.
        mod.SetDefaults()
        mod.Process()

    def loadcad(self):
        # Method which imports the CAD file to be processed into a mesh.
        # Configs are chosen from the C++ side.
        loadcad = Module.Create(ModuleType.Process, "loadcad", self.mesh)
        loadcad.RegisterConfig("filename", self.infile)
        loadcad.RegisterConfig("verbose", " ")
        self.def_and_process(loadcad)

    def create_octree(self, mindel, maxdel, eps):
        # Creates an octree, which is a way of dividing a cube into equal
        # parts.
        octree = Module.Create(ModuleType.Process, "loadoctree", self.mesh)
        octree.RegisterConfig("mindel", mindel)
        octree.RegisterConfig("maxdel", maxdel)
        octree.RegisterConfig("eps", eps)
        self.def_and_process(octree)

    def surface_mesh(self):
        # Method generates a linear mesh
        surfmesh = Module.Create(ModuleType.Process, "surfacemesh", self.mesh)
        self.def_and_process(surfmesh)
        self.mesh.expDim = 2

    def ho_surface_mesh(self):
        # Method generating a high-order mesh, only called if the order
        # is greater than 1.
        homesh = Module.Create(ModuleType.Process, "hosurface", self.mesh)
        self.def_and_process(homesh)

    def volume_mesh(self):
        volmesh = Module.Create(ModuleType.Process, "volumemesh", self.mesh)
        # volmesh.RegisterConfig("blsurfs", self.blsurfs)
        # volmesh.RegisterConfig("blthick", self.blthick)
        # volmesh.RegisterConfig("bllayers", self.bllayers)
        # volmesh.RegisterConfig("blprog", self.blprog)
        self.mesh.expDim = 3
        self.mesh.spaceDim = 3
        self.def_and_process(volmesh)

    def outcad(self, outfile):
        # Method which saves the file as an .xml file.
        output = Module.Create(ModuleType.Output, "xml", self.mesh)
        output.RegisterConfig("outfile", self.outfile)
        self.def_and_process(output)

# Inputs which the program needs, inputs given within the command line.

infile = sys.argv[1]
outfile = sys.argv[2]
nummode = int(sys.argv[3])
mesh_type = sys.argv[4]
mindel = sys.argv[5]
maxdel = sys.argv[6]
eps = sys.argv[7]

# These are the optional variables which only need to be registered if
# a volume mesh is being created. Therefore, they are defaulted to None.
# blsurfs = sys.argv[8] if mesh_type[0].lower() == 'v' else None
# blthick = sys.argv[9] if mesh_type[0].lower() == 'v' else None
# bllayers = sys.argv[10] if mesh_type[0].lower() == 'v' else None
# blprog = sys.argv[11] if mesh_type[0].lower() == 'v' else None

# Calls the CadToMesh class
c2m = CadToMesh(infile, outfile, nummode, mesh_type, mindel, maxdel, eps)
          # blsurfs=blsurfs,blthick=blthick, bllayers=bllayers, blprog=blprog)

# Executes the CadToMesh Class.
c2m.cad_to_mesh()