import ebmlite
import os

# Load in the configuration, store it as a dict
config_schema = ebmlite.loadSchema("mide_config_ui.xml")
doc = config_schema.load("example_config.cfg")
config_dict = doc.dump()
# The config file has a master element of RecorderConfigurationList, with many RecorderConfigurationItem under it
# Each RecorderConfigurationItems has a ConfigID and a Value
# This dict element stores these as a list of OrderedDisct containing ConfigID/Value pairs under the
# RecorderConfigurationItem
for config_item in config_dict["RecorderConfigurationList"]["RecorderConfigurationItem"]:
    if config_item.get("ConfigID", 0) == 0x0CFF7F:      # ID for Recording Delay configuration
        current_delay = config_item.get("UIntValue")
        new_delay = current_delay + 10
        print(f"Current delay = {current_delay}, changing to {new_delay}")
        config_item["UIntValue"] = new_delay
        break
# Save the modified configuration
with open("new_config.cfg", "wb+") as output_file:
    config_schema.encode(output_file, config_dict)
# Read the file back in, to make sure we wrote it correctly
new_doc = config_schema.load("new_config.cfg")
new_config_dict = new_doc.dump()
for config_item in config_dict["RecorderConfigurationList"]["RecorderConfigurationItem"]:
    if config_item.get("ConfigID", 0) == 0x0CFF7F:      # ID for Recording Delay configuration
        print(f"Checking the new file, delay is {config_item.get('UIntValue')}")
        break
