"""
This demonstrates the methods `dump()` and `encode()`, in the context of
enDAQ data recorder configuration files.

`dump()` converts an EBML object (a `Document` in this case) into a
dictionary, allowing easy access to modify its contents. The content's values
are keyed by element name. Since a dictionary cannot have duplicate keys,
elements marked as 'multiple' in the schema have lists as values.

`encode()` does the reverse of `dump()`, creating EBML from a dictionary.

enDAQ recorder config files are fairly simple. The root element is a
`RecorderConfigurationList`, which contains multiple
`RecorderConfigurationItem` elements. Each of those contains two child
elements: a `ConfigID` and one of several types of value (`IntValue`,
`UIntValue`, etc.).

This example converts a configuration EBML file to a dictionary, which it
then crawls to find and modify a specific configuration value.

Python 3.6 or later required.
"""
import ebmlite

config_schema = ebmlite.loadSchema("mide_config_ui.xml")

# Load in the configuration, store it as a dict
doc = config_schema.load("example_config.cfg")
config_dict = doc.dump()

# Find a specific configuration item and modify it.
# Iterate the contents of the root `RecorderConfigurationList`. It will have
# one child, `RecorderConfigurationItem`; since that element is marked as
# 'multiple', its value is a list, with one item for each
# `RecorderConfigurationItem` in the EBML.
for config_item in config_dict["RecorderConfigurationList"]["RecorderConfigurationItem"]:
    if config_item.get("ConfigID", 0) == 0x0CFF7F:  # ID for Recording Delay configuration
        current_delay = config_item.get("UIntValue")
        new_delay = current_delay + 10
        print(f"Current delay = {current_delay}, changing to {new_delay}")
        config_item["UIntValue"] = new_delay
        break

# Save the modified configuration.
with open("new_config.cfg", "wb+") as output_file:
    config_schema.encode(output_file, config_dict)

# Read the file back in, to make sure we wrote it correctly.
new_doc = config_schema.load("new_config.cfg")
new_config_dict = new_doc.dump()
for config_item in config_dict["RecorderConfigurationList"]["RecorderConfigurationItem"]:
    if config_item.get("ConfigID", 0) == 0x0CFF7F:  # ID for Recording Delay configuration
        print(f"Checking the new file, delay is {config_item.get('UIntValue')}")
        break
