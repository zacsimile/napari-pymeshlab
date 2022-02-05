def test_something():
    from napari_pymeshlab import convex_hull, laplacian_smooth, taubin_smooth, simplification_clustering_decimation, colorize_curvature_apss
    from skimage.measure import regionprops
    from skimage.measure import marching_cubes
    from skimage.data import cells3d
    from skimage.measure import label
    import numpy as np

    # load example data and segment / label it
    nuclei = cells3d()[:, 1, 60:120, 30:80]
    labels = label(nuclei > 20000)

    # find larges label
    statistics = regionprops(labels)
    label_index = np.argmax([r.area for r in statistics])
    labels_list = [r.label for r in statistics]
    label_id = labels_list[label_index]

    # turn it into a surface
    binary = np.asarray(labels == label_id)
    vertices, faces, normals, values = marching_cubes(binary, 0)
    surface = (vertices, faces, values)

    convex_hull(surface)
    laplacian_smooth(surface)
    taubin_smooth(surface)
    simplification_clustering_decimation(surface)
    colorize_curvature_apss(surface)
