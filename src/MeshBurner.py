""" 
Iteratively burns the perimeter of a mesh. Similar to the Grassfire transform 
used in image processing for extracting the medial axis on a raster. Outputs 
each burn front as an individual mesh. Note: Has not been optimized for
performance.
-
Name: MeshBurner
Updated: 141008
Author: Anders Holden Deleuran (CITA/KADK)
Copyright: Creative Commons - Attribution 4.0 International
GitHub: www.github.com/AndersDeleuran/MeshAnalysis
Contact: adel@kadk.dk

    Args:
        Mesh: The mesh to analyse.
    Returns:
        BurnFronts: List of grassfire burn fronts as meshes.
"""

import Rhino as rc

# Set component name/nick
ghenv.Component.Name = "MeshBurner"
ghenv.Component.NickName = "MB"

def getNakedFaceIDs(mesh):
    
    """ Return the face indices of any face with a naked vertex """
    
    nakedFaces = []
    
    # Get naked vertices
    nPts = list( mesh.GetNakedEdgePointStatus())
    nIDs = [i for i,v in enumerate(nPts) if v == True]
    
    for i in range(mesh.Faces.Count):
        
        # Get face vertices
        f = mesh.Faces.Item[i]
        if f.IsTriangle:
            vts = (f.A,f.B,f.C)
        else:
            vts = (f.A,f.B,f.C,f.D)
        
        # Check if they are naked
        naked = False
        for vt in vts:
            if vt in nIDs:
                naked = True
                
        if naked:
            nakedFaces.append(i)
            
    return nakedFaces

def meshBurner(mesh):
    
    """ Dicretize a mesh using a grassfire algorithm """
    
    burnFronts = []
    while mesh.Faces.Count:
        
        # Make burn front mesh and add vertices to it
        bm = rc.Geometry.Mesh()
        bm.Vertices.AddVertices(mesh.Vertices.ToPoint3fArray())
        
        # Add the burn perimeter to the mesh
        nfIDs = getNakedFaceIDs(mesh)
        nf = [mesh.Faces.Item[i] for i in nfIDs]
        bm.Faces.AddFaces(nf)
        
        # Compact and append to output list
        bm.Compact()
        bm.Normals.ComputeNormals()
        burnFronts.append(bm)
        
        # Delete the burned faces
        mesh.Faces.DeleteFaces(nfIDs)
        
    return burnFronts

if Mesh:
    BurnFronts = meshBurner(Mesh)