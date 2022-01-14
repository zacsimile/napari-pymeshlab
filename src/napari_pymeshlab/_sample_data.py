from __future__ import annotations
import numpy as np

"""
Icosahedron code copied from https://github.com/python-microscopy.
It's my (@zacsimile) code, I wrote it, but I wrote it for that package.
"""

def generate_icosahedron():
    """
    Generate an icosahedron in spherical coordinates.
    
    Returns
    -------
        azimuth : np.array
            Length 12, azimuth of icosahedron vertices [0, 2*pi].
        zenith : np.array
            Length 12, zenith of icosahedron vertices [0, pi].
        faces : np.array
            20 x 3, counterclockwise triangles denoting icosahedron faces.
    """
    t = np.arctan(0.5)+np.pi/2
    zenith = np.hstack([0, np.array(5*[np.pi-t,t]).ravel(), np.pi])  # [0, pi]
    azimuth = np.hstack([0, np.arange(0, 2*np.pi, np.pi/5), 0])   # [0, 2*pi]
    idxs = np.arange(len(zenith))[1:-1]
    upper_middle_strip = np.vstack([[v0,v2,v1] for v0,v1,v2 in 
                                    zip(idxs[::2],idxs[1::2],np.roll(idxs[::2],-1))])
    lower_middle_strip = np.vstack([[v0,v2,v1] for v0,v1,v2 in 
                                    zip(np.roll(idxs[::2],-1),idxs[1::2],np.roll(idxs[1::2],-1))])
    upper_cap = np.vstack([[v0,v2,v1] for v0,v1,v2 in 
                        zip(np.zeros(5),idxs[::2],np.roll(idxs[::2],-1))])
    lower_cap = np.vstack([[v0,v2,v1] for v0,v1,v2 in 
                        zip(11*np.ones(5),np.roll(idxs[1::2],-1),idxs[1::2])])
    faces = np.vstack([upper_cap, upper_middle_strip, lower_middle_strip, lower_cap]).astype(np.int)
    
    return azimuth, zenith, faces

def icosahedron_mesh(n_subdivision=1):
    """
    Return an icosahedron subdivided n_subdivision times. This provides a
    quasi-regular sampling of the unit sphere.
    
            v0               v0
            /  \             /  \
           /    \    ==>   v3----v5
          /      \         / \  / \
         v1------v2       v1--v4--v2

    Returns
    -------
        azimuth : np.array
            Azimuth of mesh vertices [0, 2*pi].
        zenith : np.array
            Zenith of mesh vertices [0, pi].
        faces : np.array
            20 x 3, counterclockwise triangles denoting mesh faces.
    """
    
    # First, generate the icosahedron
    azimuth, zenith, faces = generate_icosahedron()
    
    if n_subdivision < 1:
        # We don't need to do anything
        return azimuth, zenith, faces
    
    # Convert pole azimuth to np.nan so we can ignore pole azimuth (irrelevant, detrimental)
    azimuth[0], azimuth[-1] = np.nan, np.nan
    
    # Make azimuth and zenith complex numbers (to deal with phase wrapping)
    azimuth, zenith = np.exp(1j*azimuth), np.exp(1j*zenith)
    
    for k in range(n_subdivision):
        # Average each edge to get new vertex at the center of each face v0,v1,v2
        az_v3 = np.nanmean(azimuth[faces[:,[0,1]]],axis=1)
        az_v4 = np.nanmean(azimuth[faces[:,[1,2]]],axis=1)
        az_v5 = np.nanmean(azimuth[faces[:,[2,0]]],axis=1)
        new_az = np.hstack([az_v3, az_v4, az_v5])
        ze_v3 = np.nanmean(zenith[faces[:,[0,1]]],axis=1)
        ze_v4 = np.nanmean(zenith[faces[:,[1,2]]],axis=1)
        ze_v5 = np.nanmean(zenith[faces[:,[2,0]]],axis=1)
        new_ze = np.hstack([ze_v3, ze_v4, ze_v5])
        
        # Create new vertices, eliminating duplicates (there should be two of each 
        # new vertex, one from each face sharing an edge)
        new_v, new_idxs = np.unique(np.vstack([new_az,new_ze]).T, axis=0, return_inverse=True)
        new_idxs += len(azimuth)
        new_idxs = new_idxs.reshape(3,-1).T  # v3 = new_idxs[:,0], v4 = new_idxs[:,1], v5 = new_idxs[:,2]
        
        # Create new faces (4 faces per old face)
        f0 = np.vstack([faces[:,0], new_idxs[:,0], new_idxs[:,2]]).T
        f1 = np.vstack([faces[:,1], new_idxs[:,1], new_idxs[:,0]]).T
        f2 = np.vstack([faces[:,2], new_idxs[:,2], new_idxs[:,1]]).T
        faces = np.vstack([f0,f1,f2,new_idxs]).astype(np.int)
        
        # Append the new vertices to azimuth
        azimuth = np.hstack([azimuth, new_v[:,0]])
        zenith = np.hstack([zenith, new_v[:,1]])
    
    # Restore poles to azimuth 0 for future conversion to real coordinates
    azimuth[np.isnan(azimuth)] = 0
    
    # Back to angles with you
    azimuth, zenith = np.angle(azimuth), np.angle(zenith)
    azimuth[azimuth<0] = azimuth[azimuth<0]+2*np.pi  # wrap to [0, 2*pi]
    zenith = np.abs(zenith) # wrap to [0, pi]
        
    return azimuth, zenith, faces

def spherical_to_cartesian(az, el, r):
    rsin_zenith = r * np.sin(el)
    x = rsin_zenith * np.cos(az)
    y = rsin_zenith * np.sin(az)
    z = r * np.cos(el)
    return x, y, z

def make_sphere():
    """Generates a sphere by icosahedral subdivision"""
    az, ze, faces = icosahedron_mesh(3)
    x, y, z = spherical_to_cartesian(az, ze, 1)
    vertices = 100*np.vstack([x,y,z]).T
    return [((vertices, faces), {"name": "Sphere"}, "surface")]

def make_shell():
    """Generate random points on a shell"""
    x, y, z = np.random.randn(3, 1000)
    n = np.sqrt(x*x+y*y+z*z)
    pts = 100*np.vstack([x,y,z]).T/n[:,None]
    return [(pts, {"name": "Shell"}, "points")]
