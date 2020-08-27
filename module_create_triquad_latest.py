import NekPy
import sys
from NekPy.LibUtilities import ShapeType
from NekPy.NekMeshUtils import Node, Element, ElmtConfig, NodeSet, Mesh, Module, ModuleType
import numpy as np

class TestInput(Module): #inherits from the Module class
    def __init__(self, mesh): #initialises module with mesh, init function which uses mesh as an argument
        super().__init__(mesh)

        # This for now only works in 2D.
        self.mesh.spaceDim = 2
        self.mesh.expDim = 2

        # Define some configuration options for this module. AddConfigOption
        # requires 3 arguments and has one optional argument:
        # - the name of the option;
        # - the default value for that option to be used if one is not supplied
        #   via RegisterConfig;
        # - a short description, which is useful if one calls PrintConfig;
        # - optionally, if the config option is supposed to be a boolean
        #   (i.e. on or off), specify True for the fourth parameter.
        self.AddConfigOption("nx", "2", "Number of points in x direction")
        self.AddConfigOption("ny", "2", "Number of points in y direction")
        self.AddConfigOption("coord_1x", "0", "Coordinate 1x")
        self.AddConfigOption("coord_1y", "0", "Coordinate 1y")
        self.AddConfigOption("coord_2x", "0", "Coordinate 2x")
        self.AddConfigOption("coord_2y", "0", "Coordinate 2y")
        self.AddConfigOption("comp_ID", "0", "Composite ID")
        self.AddConfigOption("shape_type", "Quadrilateral", "Triangular/Quadrilateral Mesh")
        self.AddConfigOption("chebychev", "False", "Boundary Layer X direction", True)

    def Process(self):
        # Get the input variables from our configuration options. You can use
        # either GetFloatConfig, GetIntConfig, GetBoolConfig or GetStringConfig
        # depending on the type of data that should have been input into the
        # configuration option: in the below we know that the length is a float
        # and the numbers of nodes are ints.
        coord_1x         = self.GetFloatConfig("coord_1x")
        coord_1y         = self.GetFloatConfig("coord_1y")
        coord_2x         = self.GetFloatConfig("coord_2x")
        coord_2y         = self.GetFloatConfig("coord_2y")
        nx              = self.GetIntConfig("nx")
        ny              = self.GetIntConfig("ny")
        comp_ID         = self.GetIntConfig("comp_ID")
        shape_type      = self.GetStringConfig("shape_type")
        chebychev        = self.GetBoolConfig("chebychev")

        chebychev = False

        if chebychev:
            x_points = self._create_chebychev(coord_1x, coord_2x, nx)
        else:
            x_points = np.linspace(coord_1x, coord_2x, nx)

        y_points = np.linspace(coord_1y, coord_2y, ny)

        nodes = []
        id_cnt = 0

        for y in range(ny):
            tmp = []
            for x in range(nx):
                tmp.append(Node(id_cnt, x_points[x], y_points[y], 0.0))
                id_cnt += 1
            nodes.append(tmp)

        if shape_type[0].lower() == "q":
            self._create_quadrilateral(nodes, nx, ny, comp_ID)

        if shape_type[0].lower() == "t":
            self._create_triangle(nodes, nx, ny, comp_ID)

        self._call_module()

    def _create_chebychev(self, a, b, npts):
        k = np.arange(1, npts-1)
        x_points_temp = np.array([-1.0] + np.cos((2*k -1) / (2 * (npts-2)) * np.pi).tolist()[::-1] + [1.0])
        # transform [-1,1] -> [a,b]
        #     #     [-1, 1] add 1 -> [0, 2]
        #     #     [0, 2] /2 -> [0, 1]
        #     #     [0,1] mult (b-a) [0, b-a]
        #     #     [0, b-a] add a -> [a,b]
        return (b-a) * 0.5 * (x_points_temp + 1.0) + a

    def _create_quadrilateral(self, nodes, nx, ny, comp_ID):
        for y in range(ny-1):
            for x in range(nx-1):
                config = ElmtConfig(ShapeType.Quadrilateral, 1, False, False)
                self.mesh.element[2].append(
                    Element.Create(
                        config, # Element configuration
                        [nodes[y][x], nodes[y][x+1], nodes[y+1][x+1], nodes[y+1][x]], # node list
                        [comp_ID])) # tag for composite.

    def _create_triangle(self, nodes, nx, ny, comp_ID):
        for y in range(ny-1):
            for x in range(nx-1):
                config = ElmtConfig(ShapeType.Triangle, 1, False, False)
                self.mesh.element[2].append(
                    Element.Create(
                    config,
                    [nodes[y][x], nodes[y+1][x+1], nodes[y+1][x]],
                    [comp_ID]))
                self.mesh.element[2].append(
                    Element.Create(
                    config,
                    [nodes[y][x], nodes[y][x+1], nodes[y+1][x+1]],
                    [comp_ID]))

    def _call_module(self):
        # Call the Module functions to create all of the edges, faces and
        # composites.
        self.ProcessVertices()
        self.ProcessEdges()
        self.ProcessFaces()
        self.ProcessElements()
        self.ProcessComposites()


# Register our TestInput module with the factory.
Module.Register(ModuleType.Input, "test", TestInput)


# Create a 'pipeline' of the input and output modules.
mesh = Mesh()
mod1 = Module.Create(ModuleType.Input, "test", mesh)
mod2 = Module.Create(ModuleType.Output, "xml", mesh)

# Print out config options that we registered in TestInput, just for fun and to
# test they registered correctly!
# mod1.PrintConfig()

# Now register some sample input configuration options with the module, so that
# it will know the appropriate parameters to generate a mesh for.
mod1.RegisterConfig("nx", input("Number of nodes in x direction: "))
mod1.RegisterConfig("ny", input("Number of nodes in y direction: "))
mod1.RegisterConfig("coord_1x",input("Coord_1x: "))
mod1.RegisterConfig("coord_1y", input("Coord_1y: "))
mod1.RegisterConfig("coord_2x", input("Coord_2x: "))
mod1.RegisterConfig("coord_2y", input("Coord_2y: "))
mod1.RegisterConfig("chebychev", input("Chebychev Points, True/False: "))
mod1.RegisterConfig("comp_ID", input("Comp_ID: "))
mod1.RegisterConfig("shape_type", input("Shape Type, Quad or Tri: "))


# Tell the output module where to write the file.
mod2.RegisterConfig("outfile", input("Save File Name: "))
modules = [mod1, mod2]

for mod in modules:
    mod.SetDefaults()
    mod.Process()
