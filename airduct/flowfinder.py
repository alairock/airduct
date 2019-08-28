import importlib
import pkgutil


def import_submodules(package, recursive=True):
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = []
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results.append(full_name)
        if recursive and is_pkg:
            results = results + import_submodules(full_name)
    return results


def find_flow_files(folder_path):
    modules = import_submodules(folder_path)
    for module_name in modules:
        importlib.import_module(module_name)
    return modules
