# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.transform import build_table_output
from azure.cli.core.azclierror import CLIInternalError
from knack.util import todict


def transform_support_types(result):
    for res in result:
        res['auth_types'] = ', '.join(res['auth_types'])
        res['client_types'] = ', '.join(res['client_types'])

    return build_table_output(result, [
        ('Source', 'source'),
        ('Target', 'target'),
        ('AuthType', 'auth_types'),
        ('ClientType', 'client_types'),
    ])


def transform_linkers_properties(result):
    from azure.core.polling import LROPoller
    from ._utils import (
        is_aks_linker_by_id,
        get_aks_resource_name
    )

    if isinstance(result, LROPoller):
        result = result.result()

    linkers = [todict(res) for res in result]
    for linker in linkers:
        resource_id = linker.get('id')
        if is_aks_linker_by_id(resource_id):
            linker['kubernetesResourceName'] = get_aks_resource_name(linker)

    return linkers


def transform_linker_properties(result):
    from azure.core.polling import LROPoller
    from ._utils import (
        run_cli_cmd,
        is_aks_linker_by_id,
        get_aks_resource_name
    )

    # manually polling if result is a poller
    if isinstance(result, LROPoller):
        result = result.result()

    result = todict(result)
    resource_id = result.get('id')
    if is_aks_linker_by_id(resource_id):
        result['kubernetesResourceName'] = get_aks_resource_name(result)
    try:
        output = run_cli_cmd('az webapp connection list-configuration --id "{}" -o json'.format(resource_id))
        result['configurations'] = output.get('configurations')
    except CLIInternalError:
        pass
    return result


def transform_local_linker_properties(result):
    from azure.core.polling import LROPoller
    from ._utils import (
        run_cli_cmd
    )

    # manually polling if result is a poller
    if isinstance(result, LROPoller):
        result = result.result()

    result = todict(result)
    resource_id = result.get('id')
    try:
        output = run_cli_cmd('az connection generate-configuration --id "{}" -o json'.format(resource_id))
        result['configurations'] = output.get('configurations')
    except CLIInternalError:
        pass
    return result


def transform_validation_result(result):
    from azure.core.polling import LROPoller

    # manually polling if result is a poller
    if isinstance(result, LROPoller):
        result = result.result()

    result = todict(result)
    try:
        return result['validationDetail'] or result['additionalProperties']['properties']['validationDetail']
    except Exception:  # pylint: disable=broad-except
        return result
