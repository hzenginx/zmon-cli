import yaml

import click

from clickclick import AliasedGroup, Action, ok

from easydict import EasyDict

from zmon_cli.cmds.command import cli, get_client, yaml_output_option, pretty_json
from zmon_cli.output import dump_yaml, Output


@cli.group('dashboard', cls=AliasedGroup)
@click.pass_obj
def dashboard(obj: EasyDict) -> None:
    """Manage ZMON dashboards"""
    pass


@dashboard.command('init')
@click.argument('yaml_file', type=click.File('wb'))
@click.pass_obj
def init(obj: EasyDict, yaml_file: click.File) -> None:
    """Initialize a new dashboard YAML file"""
    name = click.prompt('Dashboard name', default='Example dashboard')
    alert_teams = click.prompt('Alert Teams (comma separated)', default='Team1, Team2')

    user = obj.config.get('user', 'unknown')

    data = {
        'id': '',
        'name': name,
        'last_modified_by': user,
        'alert_teams': [t.strip() for t in alert_teams.split(',')],
        'tags': [],
        'view_mode': 'FULL',
        'shared_teams': [],
        'widget_configuration': [],
    }

    yaml_file.write(dump_yaml(data).encode('utf-8'))
    ok()


@dashboard.command('get')
@click.argument("dashboard_id", type=int)
@click.pass_obj
@yaml_output_option
@pretty_json
def dashboard_get(obj: EasyDict, dashboard_id: int, output: str, pretty: bool) -> None:
    """Get ZMON dashboard"""
    client = get_client(obj.config)
    with Output('Retrieving dashboard ...', nl=True, output=output, pretty_json=pretty) as act:
        dashboard = client.get_dashboard(dashboard_id)
        act.echo(dashboard)


@dashboard.command('update')
@click.argument('yaml_file', type=click.Path(exists=True))
@click.pass_obj
def dashboard_update(obj: EasyDict, yaml_file: click.Path) -> None:
    """Create/Update a single ZMON dashboard"""
    client = get_client(obj.config)
    dashboard = {}  # type: dict

    with open(yaml_file, 'rb') as f:
        dashboard = yaml.safe_load(f)

    msg = 'Creating new dashboard ...'
    if 'id' in dashboard:
        msg = 'Updating dashboard {} ...'.format(dashboard.get('id'))

    with Action(msg, nl=True):
        dash_id = client.update_dashboard(dashboard)
        ok(client.dashboard_url(dash_id))
