import subprocess

from rule_timer import RuleTimer


class PortOpener:
    IPTABLES_RULE = ('%s -m limit'
                     ' --limit 1/minute'
                     ' --limit-burst 1'
                     ' -m state'
                     ' --state NEW'
                     ' -p tcp'
                     ' -s %s'
                     ' --dport %d'
                     ' -j ACCEPT')


    def open(self, source_ip, port, open_duration, table):
        description = self.IPTABLES_RULE % (table, source_ip, port)
        command     = 'timeout 5 sudo iptables -I ' + description
        command     = command.split()

        print "Opening port %d for %s" % (port, source_ip)
        exitcode = subprocess.call(command, shell=False)

        if not exitcode:
            RuleTimer(open_duration, description).start()

