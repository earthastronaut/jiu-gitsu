import prefect


def discover_flows():
    import pkgutil

    flows_info = {}

    for module_info in pkgutil.walk_packages(path=__path__):
        module_name = module_info.name

        module = (
            module_info
            .module_finder
            .find_module(module_name)
            .load_module()
        )

        flow = getattr(module, 'flow', None)
        if flow is not None and isinstance(flow, prefect.Flow):
            flows_info[flow.name] = {
                'flow': flow,
                'module_name': module_name,
                'module': module
            }
    return flows_info


FLOWS_INFO = discover_flows()
FLOWS = {k: FLOWS_INFO[k]['flow'] for k in FLOWS_INFO}
