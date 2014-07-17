"""
Simulates drainage in order to analyse a mesh for local pooling of rain water and snow.
-
Name: MeshDrainage
Updated: 140621
Author: Anders Holden Deleuran (CITA/KADK)
Copyright: Creative Commons - Attribution 4.0 International
Contact: adel@kadk.dk

    Args:
        Toggle: Activates the component.
        Mesh: The mesh to analyse.
        ParticleCount: The amount of particles to simulate (randomly picked from the mesh vertices).
        MaxSteps: The amount steps to iteratively move the particles.
        Tolerance: The precision with which the particles are moved.
        RandomSeed: The random seed with which the particles are picked.
        
    Returns:
        DrainCurves: Curves constructed through the drain positions of each particle.
        EndPoints: The final position of the particles.
"""

import Rhino as rc
import random
import System.Threading.Tasks as tasks

# Set component name/nick
ghenv.Component.Name = "MeshDrainage"
ghenv.Component.NickName = "MeshDrainage"

def makeDrainMeshPaths(mesh,startPoints,maxSteps,tolerance):
    
    """ Estimates the trail of a drainage path on a mesh. Based on Benjamin 
    Golders concept and Remy's VB code found here:
    http://www.grasshopper3d.com/forum/topics/drainage-direction-script """
    
    # Return list
    drainPaths = []
    
    # Task function
    def drainPath(pt):
        
        # Particle list and current particle plane
        particles = []
        paPl = rc.Geometry.Plane(pt,rc.Geometry.Vector3d.ZAxis)
        
        for j in range(maxSteps):
            
            # Get the point on the mesh closest to the particle
            meshPt = mesh.ClosestMeshPoint(paPl.Origin,0.0)
            paPl = rc.Geometry.Plane(meshPt.Point,mesh.NormalAt(meshPt))
            
            # Check that first step has been taken and that current step is down slope
            if j and paPl.Origin.Z > particles[-1].Z:
                break
            else:
                # Add particle to list
                particles.append(paPl.Origin)
                
                # Move particle down slope
                an = rc.Geometry.Vector3d.VectorAngle(paPl.XAxis,-rc.Geometry.Vector3d.ZAxis,paPl)
                paPl.Rotate(an,paPl.ZAxis)
                paPl.Translate(paPl.XAxis*tolerance)
                
        # Make drain curve
        if len(particles) > 1:
            
            crv = rc.Geometry.Curve.CreateControlPointCurve(particles)
            drainPaths.append(crv)
            
    # Call task function
    tasks.Parallel.ForEach(startPoints,drainPath)
    
    return drainPaths

if Toggle and Mesh:
    
    # Get mesh vertices
    Vertices = Mesh.Vertices.ToPoint3dArray()
    
    # Pick random vertices
    if ParticleCount > len(Vertices):
        ParticleCount = len(Vertices)
    random.seed(RandomSeed)
    Vertices = random.sample(Vertices,ParticleCount)
    
    # Make drain curves
    DrainCurves = makeDrainMeshPaths(Mesh,Vertices,MaxSteps,Tolerance)
    EndPoints = [crv.PointAtEnd for crv in DrainCurves]
