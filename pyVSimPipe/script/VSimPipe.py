import click
from pyVSimPipe.vLaunchControl import LaunchControl,setup
import logging
import warnings
import os

def validate_init():
    valid = True
    flist = ['./config.ini','order.csv','GrOpticsConfig','CARE_config']
    for f in flist:
        if(not os.path.exists(f)):
            valid = False
            click.secho('{} does not exist'.format(f),fg='red') 
    if(not valid):
        click.secho('Run directory not initialized',fg='red')
        raise click.Abort()


@click.group()
@click.option('--log-level', default='INFO', help='Logging verbosity level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']))
@click.option('--show-warnings', default=True, help='Show warnings?')
def cli(log_level, show_warnings):
    """VSimPipe 
    \b
    Simple command line tools for running simulations using qsub.

    Be minded you need to have singularity installed to use singularity mode (default).   

    To start a new set of simulations first do:

    > VSimPipe init

    This will generate a set of default configuration files and a order file (order.csv).

    Next, edit the necessary fields in the config file and order file.

    Now, you are ready to send the simulations out:

    > VSimPipe run
    
    """
    logging.basicConfig(level=log_level)

    if not show_warnings:
        warnings.simplefilter('ignore')
@cli.command('init')
def init():
    setup()

@cli.command('run')
@click.option('--dry-run',is_flag=True,help='Dry run. Generate script only.')
def run(dry_run):
    validate_init()
    config_file = './config.ini'
    order_file  = './order.csv'
    control = LaunchControl(config_file,order_file)
    control.buildMissle()
    control.launch(dry_run=dry_run)            

if __name__ == '__main__':
    cli()
