class Profile:
    def __init__(self, config):
        self._config = config


    def match_hostport(self, host, port):
        """Check if the profile is suitable for destination host name and port.
        """
        return self._config.host == host and self._config.port


    def match(self, log_entry):
        """Check if the iptables log entry is suitable for this profile. Checks
        includes transport protocol and destination port.
        """
        raise NotImplementedError()


    def verify(self, log_entry):
        """Verify incoming `data` and return the port to open. For methods
        with port-knocking sequences this acts as a feed function.
        """
        raise NotImplementedError()


    def generate(self):
        """Generate packets on the client site for knocking purpose. Returns
        a list of packets.
        """
        raise NotImplementedError()
