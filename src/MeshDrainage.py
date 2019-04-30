"""
Geometric drainage simualtion model for analysing a mesh for pooling of rain water.
    Inputs:
        Mesh: The mesh to analyse {item,mesh}
        ParticleCount: Amount of particles randomly picked from Mesh vertices {item,int}
        MaxSteps: Amount of steps to iteratively move the particles {item,int}
        StepSize: The distance by which the particles are moved at each step {item,float}
        RandomSeed: The random seed with which the particles are picked {item,int}
        Threaded: Toggle multithreading {item,bool}
    Outputs:
        DrainagePaths: Polylines through the paths of each particle {list,polyline}
    Remarks:
        Author: Anders Holden Deleuran (BIG Compute/Ideas/Tech)
        License:
        Version: 190311
"""

import Rhino as rc
import random
import System.Threading.Tasks as tasks
import Grasshopper.Kernel.Types as gkt

# Set component name/nick
ghenv.Component.Name = "MeshDrainagePaths"
ghenv.Component.NickName = "MDP"

def makeDrainMeshPaths(mesh,startPoints,maxSteps,stepSize,threaded):
    
    """ Estimates drainage paths on a mesh. Based on Benjamin Golders concept
    found here: www.grasshopper3d.com/forum/topics/drainage-direction-script """
    
    # Return list
    drainPaths = []
    
    # Task function
    def drainPath(pt):
        
        # Make particle list and set current particle plane
        particles = []
        paPl = rc.Geometry.Plane(pt,rc.Geometry.Vector3d.ZAxis)
        for i in range(maxSteps):
            
            # Get point on mesh closest to current particle position
            meshPt = mesh.ClosestMeshPoint(paPl.Origin,0.00)
            if meshPt:
                paPl = rc.Geometry.Plane(meshPt.Point,mesh.NormalAt(meshPt))
                
                # Check first step has been taken and that current step is down slope
                if i and paPl.Origin.Z > particles[-1].Z:
                    break
                else:
                    # Record particle position and move down slope
                    particles.append(paPl.Origin)
                    an = rc.Geometry.Vector3d.VectorAngle(paPl.XAxis,-rc.Geometry.Vector3d.ZAxis,paPl)
                    paPl.Rotate(an,paPl.ZAxis)
                    paPl.Translate(paPl.XAxis*stepSize)
                    
        # Make drain polyline
        if len(particles) > 1:
            pl = rc.Geometry.Polyline(particles)
            drainPaths.append(pl)
                
    # Call task function (use non-threaded for debugging)
    if threaded:
        tasks.Parallel.ForEach(startPoints,drainPath)
    else:
        [drainPath(pt) for pt in startPoints]
        
    return drainPaths

if Mesh:
    
    # Get mesh vertices and pick random
    vts = Mesh.Vertices.ToPoint3dArray()
    if ParticleCount > len(vts):
        ParticleCount = len(vts)
    random.seed(RandomSeed)
    vts = random.sample(vts,int(ParticleCount))
    
    # Make paths and output to GH
    drainagePaths = makeDrainMeshPaths(Mesh,vts,int(MaxSteps),StepSize,Threaded)
    DrainagePaths = [gkt.GH_Curve(pl.ToNurbsCurve()) for pl in drainagePaths]
else:
    DrainagePaths = []
