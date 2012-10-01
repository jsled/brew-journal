function toggle_node_visibility(node)
{
    node.style['display'] = (node.style['display'] == 'none' ? '' : 'none');
}

function toggle_visibility(base_name)
{
    toggle_node_visibility(document.getElementById(base_name));
    toggle_node_visibility(document.getElementById(base_name + '-alt'));
}
