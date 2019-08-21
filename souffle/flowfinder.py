from souffle.tasks import Task
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


class TaskNotFoundError(AttributeError):
    pass


class FlowNestingTooDeep(Exception):
    pass


def find_flows(folder_path):
    flows = []
    for module_name in import_submodules(folder_path):
        module = importlib.import_module(module_name)
        if hasattr(module, 'schedule'):
            for task in module.schedule.flow:
                if type(task) is list:
                    for t in task:
                        if type(t) is not Task:
                            raise FlowNestingTooDeep('Reached max nesting level in flow. Only 2 levels allowed')
                        t.module_path = module_name
                else:
                    task.module_path = module_name
            flows.append(module.schedule)
    return flows
