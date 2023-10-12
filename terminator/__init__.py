import boto3
import sys
import importlib
import pkgutil

def get_drivers():
    "Returns the list of available drivers"
    out = []
    _drv = importlib.import_module('terminator.drivers')
    for importer, modname, ispkg in pkgutil.iter_modules(_drv.__path__):
        out.append(modname)
    return out

def help_message(driver):
    "Returns the driver's help message"
    _drv = importlib.import_module('terminator.drivers.'+driver)
    return _drv.help_string()

class terminator(object):
    "The terminator wrapper class"

    def __init__(self, driver, include, exclude):
        "Constructor"
        self.driver = driver
        self.drv = importlib.import_module('terminator.drivers.'+driver)
        self.include = include
        self.exclude = exclude
        self.priority = self.drv.priority

    def prepare(self):
        "Prepare the list of resources"
        self.resources = self.drv.prepare(self.include, self.exclude)
        return self.resources

    def print_prepare_message(self):
        "Print the list of resources to be processed"
        self.drv.print_prepare_message(self.resources)
        return True

    def has_resources(self):
        "Return True if object has resources to process"
        if self.resources:
            return True
        else:
            return False

    def process(self, dry_run=True):
        "Process actions"
        self.report = self.drv.process(self.resources, dry_run)
        return self.report
    
    def print_report(self):
        "Print the report"
        self.drv.print_report(self.report)
        return True

