"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/plugins/stable/npe2_manifest_specification.html

Replace code below according to your needs.
"""
from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton
from magicgui import magic_factory
from napari.layers import Points
from napari.types import LayerDataTuple
import numpy
import pymeshlab as ml

@magic_factory
def screened_poisson_reconstruction(points_layer: Points, n_neighbors: int = 10, 
                     smooth_iter: int = 0, flip: bool = False, 
                     viewpos: numpy.ndarray = [0,0,0], depth: int = 8, 
                     full_depth: int = 5, cg_depth: int = 0, scale: float = 1.1, 
                     samples_per_node: float = 1.5, point_weight: float = 4, 
                     iters: int = 8, confidence: bool = False, 
                     preclean: bool = False) -> LayerDataTuple:
    """
    Run screened poisson reconstruction on a set of points, using pymeshlab.
    """

    mesh = ml.Mesh(points_layer.data)
    
    ms = ml.MeshSet()
    ms.add_mesh(mesh)

    # compute normals
    ms.compute_normals_for_point_sets(k=n_neighbors,  # number of neighbors
                                      smoothiter=smooth_iter,
                                      flipflag=flip,
                                      viewpos=viewpos)
    # run SPR
    ms.surface_reconstruction_screened_poisson(visiblelayer=False,
                                               depth=depth,
                                               fulldepth=full_depth,
                                               cgdepth=cg_depth,
                                               scale=scale,
                                               samplespernode=samples_per_node,
                                               pointweight=point_weight,
                                               iters=iters,
                                               confidence=confidence,
                                               preclean=preclean)
    
    data = (ms.current_mesh().vertex_matrix(), 
            ms.current_mesh().face_matrix(), 
            ms.current_mesh().vertex_color_matrix().T)
    
    return [(data, {"name": f"Reconstructed {points_layer.name}"}, "surface")]
