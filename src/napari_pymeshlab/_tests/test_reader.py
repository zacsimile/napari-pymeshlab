import numpy as np
from napari_pymeshlab import get_mesh_reader, make_sphere, write_single_surface


# at least check reading and writing works
def test_reader(tmp_path):

    # write some fake data using your supported file format
    test_file = str(tmp_path / "sphere.stl")
    original_data = make_sphere()[0][0]
    write_single_surface(test_file, original_data, {})

    # try to read it back in
    reader = get_mesh_reader(test_file)
    assert callable(reader)

    # make sure we're delivering the right format
    layer_data_list = reader(test_file)
    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    layer_data_tuple = layer_data_list[0]
    assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0

    # TODO: make sure it's the same as it started
    # pymeshlab does some weird stuff
    # np.testing.assert_allclose(original_data[0], layer_data_tuple[0][0])
    # np.testing.assert_allclose(original_data[1], layer_data_tuple[0][1])


def test_get_reader_pass():
    reader = get_mesh_reader("fake.file")
    assert reader is None
