import logging
from optparse import Values

from ansible.playbook import play
from ansible.executor import task_queue_manager
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible import context
from ansible.plugins import callback

from myansi.common import conf

CONF = conf.CONF
LOG = logging.getLogger(__name__)

loader = None
inv_manager = None
var_manager = None


def init():
    global loader, inv_manager, var_manager

    loader = DataLoader()
    inv_manager = InventoryManager(loader=loader, sources=CONF.inventory)
    var_manager = VariableManager(loader, inv_manager)
    context._init_global_context(Values({'connection': 'smart',
                                         'verbosity': 3}))


class ResultCallback(callback.CallbackBase):

    def __init__(self, display=None, options=None):
        super().__init__(display, options)
        self.host_ok = {}
        self.host_failed = {}
        self.host_unreachable = {}

    def v2_runner_on_ok(self, result):
        self.host_ok[result._host.get_name()] = result._result

    def v2_runner_on_failed(self, result, **kwargs):
        self.host_failed[result._host.get_name()] = result._result

    def v2_runner_on_unreachable(self, result, **kwargs):
        self.host_unreachable[result._host.get_name()] = result._result

    def to_dict(self):
        return {
            'ok': self.host_ok,
            'failed': self.host_failed,
            'unreachable': self.host_unreachable
        }


class MyAnsi(object):

    def run(self, hosts: str, command: str):
        runner = play.Play()
        data = dict(
            name='Run command',
            hosts=hosts,
            tasks=[
                {'action': {'module': 'shell', 'args': command}},
            ]
        )
        LOG.info('inventory path %s', CONF.inventory)
        result_callback = ResultCallback()
        player = runner.load(data)
        tqm = task_queue_manager.TaskQueueManager(
            inventory=inv_manager,
            variable_manager=var_manager,
            loader=loader,
            passwords=None,
            stdout_callback=result_callback
        )
        tqm.run(player)
        return result_callback
