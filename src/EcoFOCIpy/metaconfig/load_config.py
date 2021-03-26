import yaml

from collections import OrderedDict


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
    )
    return yaml.load(stream, OrderedLoader)

def load_config(filename):

    try:
        d = ordered_load(open(filename))
    except:
        raise RuntimeError(f"{filename} not found")

    return d

def write_config(infile, data):
    """ Input - full path to config file
        Dictionary of parameters to write
        
        Output - None
    """
    infile = str(infile)

    assert 'yaml' in infile, 'File possibly not a yaml config file'

    try:
        yaml.safe_dump(data, open(infile, "w"), default_flow_style=False, sort_keys=False)
    except:
        raise RuntimeError("{0} not found".format(infile))
