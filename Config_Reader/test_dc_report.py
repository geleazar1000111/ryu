from datacollection_RR import Datacollection_Reporter

reporter = Datacollection_Reporter(["/etc/odin/policies/datacollection/config.yaml", "/etc/odin/world.yaml", "/etc/odin/hardware.yaml"])
reporter.show_report()