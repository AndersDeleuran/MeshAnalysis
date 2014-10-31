""" 
Calculate shortest paths on a mesh. Uses the NetworkX Python module:
Download here:
http://networkx.lanl.gov/download/networkx/
Read about shortest path algorithms here:
http://networkx.lanl.gov/archive/networkx-1.5/reference/algorithms.shortest_paths.html
-
Name: MeshPaths
Updated: 141031
Author: Anders Holden Deleuran (CITA/KADK)
Copyright: Creative Commons - Attribution 4.0 International
GitHub: www.github.com/AndersDeleuran/MeshAnalysis
Contact: adel@kadk.dk

    Args:
        Mesh: The mesh to calculate paths on.
        Destinations: List of lines representing path source (line start) and path target (line end).
        GraphType: Make the mesh graph nodes from either its vertices or its faces
        PathMode: The algorithm to use when calculating the shortest path (refer to NetworkX documentation).
        WeightMode: The graph edge weight. Can be either metric length or the same weight for all edges (1).
    Returns:
        Paths: The shortest path for each destination line.
        Nodes: The graph nodes.
        Edges: The graph edges.
        Stats: Graph statistics
"""

import copy
import Rhino as rc
import networkx as nx

def meshVertexGraph(mesh,weightMode):
    
    """ Make a networkx graph with mesh vertices as nodes and mesh edges as edges """
    
    # Create graph
    g = nx.Graph()
    
    for i in range(mesh.Vertices.Count):
        
        # Get vertex as point3D
        pt3D = rc.Geometry.Point3d(mesh.Vertices.Item[i])
        
        # Add node to graph and get its neighbours
        g.add_node(i,point=pt3D)
        neighbours = mesh.Vertices.GetConnectedVertices(i)
        
        # Add edges to graph
        for n in neighbours:
            if n > i:
                line = rc.Geometry.Line(mesh.Vertices.Item[i],mesh.Vertices.Item[n])
                if weightMode == "edgeLength":
                    w = line.Length
                elif weightMode == "sameWeight":
                    w = 1
                g.add_edge(i,n,weight=w,line=line)
    return g

def meshFacesGraph(mesh,weightMode):
    
    """ Make a networkx graph with mesh face centers as nodes
    and topological connections (lines) as edges """
    
    # Create graph
    g = nx.Graph()
    
    for i in range(mesh.Faces.Count):
        
        # Add node to graph and get its neighbours
        g.add_node(i,point=mesh.Faces.GetFaceCenter(i))
        neighbours = mesh.Faces.AdjacentFaces(i)
        
        # Add edges to graph
        for n in neighbours:
            if n > i:
                line = rc.Geometry.Line(mesh.Faces.GetFaceCenter(i),mesh.Faces.GetFaceCenter(n))
                if weightMode == "edgeLength":
                    w = line.Length
                elif weightMode == "sameWeight":
                    w = 1
                g.add_edge(i,n,weight=w,line=line)
                
    return g

def hasPath(graph,source,target):
    
    """ Return True if graph has a path from source to target, False otherwise """
    
    try:
        sp = nx.shortest_path(graph,source,target)
    except nx.NetworkXNoPath:
        return False
    return True

def shortestWalk(g,line,mode):
    
    # Get index of closest nodes to line endpoints
    nPts = [g.node[n]["point"] for n in g]
    nPts = rc.Collections.Point3dList(nPts)
    start = nPts.ClosestIndex(line.From)
    end = nPts.ClosestIndex(line.To)
    
    # Check that start and are not the same node
    if start == end:
        
        print "Start and end node is the same"
        
    else:
        
        # Check that a path exist between the two nodes
        if hasPath(g,start,end):
            
            # Calculate shortest path
            
            if mode == "dijkstra_path":
                sp = nx.dijkstra_path(g,start,end,weight = "weight")
                
            elif mode == "shortest_path":
                sp = nx.shortest_path(g,start,end,weight = "weight")
                
            # Make polyline through path
            pts = [g.node[i]["point"] for i in sp]
            pl = rc.Geometry.PolylineCurve(pts)
            
            return pl


# Check input geometry
if Mesh and Destinations:
    
    # Make graph
    if GraphType == "vertexGraph":
        g = meshVertexGraph(Mesh,WeightMode)
    else:
        g = meshFacesGraph(Mesh,WeightMode)
        
    # Calculate shortest paths
    Paths = []
    for l in Destinations:
        sp = shortestWalk(g,l,PathMode)
        Paths.append(sp)
        
    # Output graph geometry and stats
    Nodes = [g.node[i]["point"] for i in g.nodes()]
    Edges = [e[2]["line"] for e in g.edges(data=True)]
    Stats = "Nodes: " + str(len(Nodes)) + "\n" + "Edges: " + str(len(Edges))