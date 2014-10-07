"""
Analyse mesh curvature. Curvature is defined here as the angle between a vertex normal
and the vector from this vertex to its neighbours. Zero curvature is thus equal to
90 degrees. However to evaluate positive and negative curvatures 90 is subtracted
from this value. Meaning that negative curvature will be a negative value and
positive curvature a positive value.
-
Name: MeshCurvature
Updated: 140818
Author: Anders Holden Deleuran (CITA/KADK)
Copyright: Creative Commons - Attribution 4.0 International
GitHub: www.github.com/AndersDeleuran/MeshAnalysis
Contact: adel@kadk.dk

    Args:
        Toggle: Activates the component.
        Mesh: The mesh to analyse.
        Mode: The curvature mode to calculate ("min","max" or "mean").
        Angle: The angle in degrees at which the mesh is unwelded.
        NegativeOff: If True negative curvature is treated as if positive.
    Returns:
        Mesh: A mesh colored by its curvature values.
        Curvature: The curvature values for each vertex.
        Colors: The curvature color for each vertex.
        CurvatureSum: The total curvature.
        CurvatureBounds: The minimum and maximum curvature.
        CurvatureSorted: Sorted curvature values (for graph mapping).
        MeshArea: The area of the mesh.
"""

import Rhino as rc
import math


# Set component name/nick
ghenv.Component.Name = "MeshCurvatureAnalysis"
ghenv.Component.NickName = "MeshCurvature"

def meshCurvature(mesh,mode,negativeOff):
    
    """ Calculate the curvature of a mesh using vertex normal angle 
    from each vertex to its neighbours """
    
    # Calculate mesh normals
    mesh.FaceNormals.ComputeFaceNormals()
    mesh.Normals.ComputeNormals()
    
    # Output list
    curvature = []
    
    # Iterate mesh vertices
    for i in range(mesh.Vertices.Count):
        
        # Get vertex, vertex normal and vertex neighbour IDs
        centerVertex = mesh.Vertices.Item[i]
        centerNormal = mesh.Normals.Item[i]
        neighbourIDs = mesh.Vertices.GetConnectedVertices(i)
        
        # Iterate neighbouring vertices
        angles = []
        for j in neighbourIDs:
            
            # Make vector from vertex to neighbour and check its length
            neighbourVertex = mesh.Vertices.Item[j]
            neighbourDirection = neighbourVertex - centerVertex
            if neighbourDirection.Length > 0:
                
                # Calculate angle between normal and new vector
                a = rc.Geometry.Vector3d.VectorAngle(centerNormal,neighbourDirection)
                
                # Subtract it from 90 and optionally get absolute value (no negative curvature)
                a = math.degrees(a) - 90
                if negativeOff:
                    a = abs(a)
                    
                # Add to list
                angles.append(a)
                
        # Calculate curvature depending on mode
        if mode == "min":
            curvature.append(min(angles))
            
        elif mode == "max":
            curvature.append(max(angles))
            
        elif mode == "mean":
            curvature.append(sum(angles)/len(angles))
            
    return curvature

def remapValues(values,targetMin,targetMax):
    
    """ Remap numbers into a new numeric domain """
    
    # Check that different values exist
    if len(set(values)) > 1:
        
        remappedValues = []
        
        # Get sourceDomain min and max
        srcMin = min(values)
        srcMax = max(values)
        
        # Iterate the values and remap them
        for v in values:
            rv = ((v-srcMin)/(srcMax-srcMin))*(targetMax-targetMin)+targetMin
            remappedValues.append(rv)
            
        return remappedValues
        
    # Else return targetMax for each value
    else:
        return [targetMin]*len(values)

def mapValueListAsColors(values):
    
    """ Make a list of HSL color where the values are mapped onto a
    0.0 - 0.7 hue domain. Meaning that low values will be red, medium
    values green and large values blue """
    
    colors = []
    remappedValues = remapValues(values,0.0,0.7)
    for v in remappedValues:
        c = rc.Display.ColorHSL(v,1.0,0.5).ToArgbColor()
        colors.append(c)
        
    return colors

def colorMesh(mesh,colors):
    """ Color mesh vertices by list of colors """
    for i,c in enumerate(colors):
        mesh.VertexColors.SetColor(i,c)

# Calls and GH output
if Toggle:
    if Mesh:
        
        # Unweld the mesh at sharp angles
        Mesh.Unweld(math.radians(Angle),True)
        
        # Calculate curvature, sorted values, sum etc,
        Curvature = meshCurvature(Mesh,Mode,NegativeOff)
        CurvatureSorted = sorted(Curvature)
        CurvatureSum = round(sum(Curvature),2)
        CurvatureBounds = (round(min(Curvature),2)),(round(max(Curvature),2))
        
        # Calculate colors and color mesh
        Colors = mapValueListAsColors(Curvature)
        CMesh = Mesh
        colorMesh(CMesh,Colors)
