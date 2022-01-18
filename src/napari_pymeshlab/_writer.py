"""
This module is an example of a barebones writer plugin for napari.

It implements the Writer specification.
see: https://napari.org/plugins/stable/npe2_manifest_specification.html

Replace code below according to your needs.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Any, Sequence, Tuple, Union

import pymeshlab as ml
import numpy as np

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def write_single_surface(path: str, data: Any, meta: dict):
    """Writes a single surface layer to file"""
    colors = None
    try:
        vertices, faces, colors = data  # unwrap surface data
    except ValueError:
        vertices, faces = data


    if (colors is not None) and (type(colors) == np.ndarray) and (colors.shape[1] == 4):
        mesh = ml.Mesh(vertices, faces, v_color_matrix=colors.T)
    else:
        mesh = ml.Mesh(vertices, faces)

    ms = ml.MeshSet()  # create a mesh set
    ms.add_mesh(mesh)

    # save the mesh
    # TODO: here are a lot of optional arguments to be set
    ms.save_current_mesh(path)

    # TODO: how do we handle metadata?
    return [path]

# def write_multiple(path: str, data: List[FullLayerData]):
#     """Writes multiple layers of different types."""
#     pass
