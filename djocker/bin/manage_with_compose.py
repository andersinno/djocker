import sys
from subprocess import call

from djocker.config import config
from djocker.utils import cli


class ManageWithCompose(cli.Command):
    def get_management_args(self):
        return ' '.join(self.argv[1:])

    def add_arguments(self, parser):
        parser.add_argument('command', nargs='+')

    def get_args(self):
        argv = sys.argv
        if len(argv) > 1 and argv[1] in ['-h', '--help']:
            return super().get_args()

        # Do not handle anything with ArgumentParser unless it is the help
        return None

    def handle(self, *args, **options):
        command_template = 'docker-compose exec {container_name} {python_bin} manage.py {management_command}'
        management_command = self.get_management_args()

        command = command_template.format(
            container_name=config.compose_service_name,
            python_bin=config.python_bin,
            management_command=management_command,
        )
        print("Running command: {}".format(command))

        call(command, shell=True)


if __name__ == "__main__":
    cli.run_command(ManageWithCompose)
