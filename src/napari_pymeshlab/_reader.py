import pymeshlab as ml

def get_mesh_reader(path):
    """Check if we can use the mesh reader here.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    exts = tuple(['.3ds', '.apts', '.asc', '.bre', '.ctm', 
                  '.dae', '.e57', '.es', '.fbx', '.glb', 
                  '.gltf', '.obj', '.off', '.pdb', '.ply',
                  '.ptx', '.qobj', '.stl', '.vmi', '.wrl',
                  '.x3d', '.x3dv'])
    if not path.endswith(exts):
        return None

    # otherwise we return the *function* that can read ``path``.
    return mesh_reader


def mesh_reader(path):
    """Read a mesh in using pymeshlab.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        List of surfaces, one per file path.
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path

    ms = ml.MeshSet()  # create a mesh set
    
    # load all files into the mesh set
    for _path in paths:
        ms.load_new_mesh(_path)

    # loop through the mesh set and parse the surfaces
    surfaces = []
    for i in range(ms.number_meshes()):
        ms.set_current_mesh(i)
        surfaces.append((ms.current_mesh().vertex_matrix(), 
                         ms.current_mesh().face_matrix(), 
                         ms.current_mesh().vertex_color_matrix().T))

    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {}

    return [(surface, add_kwargs, "surface") for surface in surfaces]
