from .remover import init_remover
from .checker import init_viewer

def modules():
    return [init_remover, init_viewer]