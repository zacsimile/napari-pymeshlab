"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/plugins/stable/npe2_manifest_specification.html

Replace code below according to your needs.
"""
from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton
from magicgui import magic_factory
from napari.layers import Points
from napari.types import LayerDataTuple, SurfaceData
import numpy as np
import pymeshlab as ml
from enum import Enum

@magic_factory
def screened_poisson_reconstruction(points_layer: Points, n_neighbors: int = 10, 
                     smooth_iter: int = 0, flip: bool = False, 
                     viewpos: np.ndarray = [0,0,0], depth: int = 8,
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


@magic_factory
def _convex_hull(surface: SurfaceData) -> SurfaceData:
    return convex_hull(surface)


def convex_hull(surface: SurfaceData) -> SurfaceData:
    """Determine the convex hull of a surface

    Parameters
    ----------
    surface: napari.types.SurfaceData

    Returns
    -------
    napari.types.SurfaceData

    See Also
    --------
    ..[0] https://pymeshlab.readthedocs.io/en/0.1.9/tutorials/apply_filter.html
    """
    import pymeshlab
    mesh = pymeshlab.Mesh(surface[0], surface[1])
    ms = pymeshlab.MeshSet()
    ms.add_mesh(mesh)
    ms.set_current_mesh(0)

    ms.convex_hull()

    mesh = ms.mesh(1)

    faces = np.asarray(mesh.polygonal_face_list())
    vertices = np.asarray(mesh.vertex_matrix())
    values = np.asarray(mesh.vertex_color_array())

    return (vertices, faces, values)


@magic_factory
def _laplacian_smooth(surface: SurfaceData, step_smooth_num: int = 10) -> SurfaceData:
    return laplacian_smooth(surface, step_smooth_num)

def laplacian_smooth(surface: SurfaceData, step_smooth_num: int = 10) -> SurfaceData:
    """

    Parameters
    ----------
    surface: napari.types.SurfaceData
    step_smooth_num: int, optional

    Returns
    -------
    napari.types.SurfaceData

    See Also
    --------
    ..[0] https://pymeshlab.readthedocs.io/en/0.1.9/filter_list.html#laplacian_smooth
    """
    import pymeshlab
    mesh = pymeshlab.Mesh(surface[0], surface[1])
    ms = pymeshlab.MeshSet()
    ms.add_mesh(mesh)
    ms.set_current_mesh(0)
    ms.laplacian_smooth(stepsmoothnum=step_smooth_num)
    mesh = ms.mesh(0)

    faces = np.asarray(mesh.polygonal_face_list())
    vertices = np.asarray(mesh.vertex_matrix())
    values = np.ones((len(vertices)))

    return (vertices, faces, values)


@magic_factory
def _taubin_smooth(surface: SurfaceData,
                  lambda_: float = 0.5,
                  mu: float = -0.53,
                  step_smooth_num: int = 10
                  ) -> SurfaceData:
    return taubin_smooth(surface, lambda_, mu, step_smooth_num)


def taubin_smooth(surface: SurfaceData,
                  lambda_: float = 0.5,
                  mu: float = -0.53,
                  step_smooth_num: int = 10
                  ) -> SurfaceData:
    """Smooth a surface using Taubin's method [1]

    Parameters
    ----------
    surface: napari.types.SurfaceData
    lambda_: float, optional
    mu: float, optional
    step_smooth_num: int, optional

    Returns
    -------
    napari.types.SurfaceData

    See Also
    --------
    ..[0] https://pymeshlab.readthedocs.io/en/0.1.9/filter_list.html#taubin_smooth
    ..[1] "Gabriel Taubin" A signal processing approach to fair surface design" SIGGRAPH 1995 doi:10.1145/218380.218473
    """
    import pymeshlab

    mesh = pymeshlab.Mesh(surface[0], surface[1])
    ms = pymeshlab.MeshSet()
    ms.add_mesh(mesh)
    ms.set_current_mesh(0)
    ms.taubin_smooth(lambda_=lambda_,
                     mu=mu,
                     stepsmoothnum=step_smooth_num
                     )

    mesh = ms.mesh(0)

    faces = np.asarray(mesh.polygonal_face_list())
    vertices = np.asarray(mesh.vertex_matrix())
    values = np.ones((len(vertices)))

    return (vertices, faces, values)


@magic_factory
def _simplification_clustering_decimation(surface: SurfaceData,
                                         threshold_percentage: float = 1
                                         ) -> SurfaceData:
    return simplification_clustering_decimation(surface, threshold_percentage)


def simplification_clustering_decimation(surface: SurfaceData,
                                         threshold_percentage: float = 1
                                         ) -> SurfaceData:
    """Cluster points of a surface to make it less complex

    Parameters
    ----------
    surface: napari.types.SurfaceData
    threshold_percentage: float, optional
        between 0 and 100

    Returns
    -------
    napari.types.SurfaceData

    See Also
    --------
    ..[0] https://pymeshlab.readthedocs.io/en/0.1.9/filter_list.html#simplification_clustering_decimation
    """
    import pymeshlab

    mesh = pymeshlab.Mesh(surface[0], surface[1])
    ms = pymeshlab.MeshSet()
    ms.add_mesh(mesh)
    ms.set_current_mesh(0)
    ms.simplification_clustering_decimation(threshold=pymeshlab.Percentage(threshold_percentage))
    mesh = ms.mesh(0)

    faces = np.asarray(mesh.polygonal_face_list())
    vertices = np.asarray(mesh.vertex_matrix())
    values = np.ones((len(vertices)))

    return (vertices, faces, values)


class CurvatureType(Enum):
    mean = 'Mean'
    gauss = 'Gauss'
    k1 = 'K1'
    k2 = 'K2'
    approxmean = 'ApproxMean'


@magic_factory
def _colorize_curvature_apss(surface: SurfaceData,
                            filter_scale: float = 2,
                            projection_accuracy: float = 0.0001,
                            max_projection_iterations: int = 15,
                            spherical_parameter: float = 1,
                            curvature_type: CurvatureType = CurvatureType.mean
                            ) -> SurfaceData:
    return _colorize_curvature_apss(surface, filter_scale, projection_accuracy, max_projection_iterations, spherical_parameter, curvature_type)


def colorize_curvature_apss(surface: SurfaceData,
                            filter_scale: float = 2,
                            projection_accuracy: float = 0.0001,
                            max_projection_iterations: int = 15,
                            spherical_parameter: float = 1,
                            curvature_type: CurvatureType = CurvatureType.mean
                            ) -> SurfaceData:
    """Colorize curvature

    Parameters
    ----------
    surface: napari.types.SurfaceData
    filter_scale: float, optional
    projection_accuracy: float, optional
    max_projection_iterations: int, optional
    spherical_parameter: float, optional
    curvature_type: CurvatureType, optional

    Returns
    -------
    ..[1] https://pymeshlab.readthedocs.io/en/0.1.9/filter_list.html#colorize_curvature_apss
    """
    import pymeshlab

    mesh = pymeshlab.Mesh(surface[0], surface[1])
    ms = pymeshlab.MeshSet()
    ms.add_mesh(mesh)
    ms.set_current_mesh(0)
    ms.colorize_curvature_apss(
        filterscale=filter_scale,
        projectionaccuracy=projection_accuracy,
        maxprojectioniters=max_projection_iterations,
        sphericalparameter=spherical_parameter,
        curvaturetype=curvature_type.value
    )

    mesh = ms.mesh(0)

    faces = np.asarray(mesh.polygonal_face_list())
    vertices = np.asarray(mesh.vertex_matrix())
    values = np.asarray(mesh.vertex_color_array())

    return (vertices, faces, values)


