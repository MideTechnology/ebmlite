import numpy as np
import matplotlib.pyplot as plt

import core


def getTypeMatch(el, elType):
    """ Returns the first child element of el that matches the type elType """
    return next((x for x in el if type(x) == elType), [])


# Load the IDE file.
schemaFile = './schemata/mide.xml'
ebmlFile = './tests/SSX46714-doesNot.ide'
schema = core.loadSchema(schemaFile)
ideRoot = schema.load(ebmlFile)

# create a list of relevant element types
recPropType = schema[0x18526570]
chListType = schema[0x5270]

# List the channels in the IDE file.
recProps = getTypeMatch(ideRoot, recPropType)
chList = getTypeMatch(recProps, chListType).dump()

# Print the ID and name of each channel.
chIdNames = [[ch['ChannelID'], ch['ChannelName']] for ch in chList['Channel']]
print('Channels:\r\n%s\r\n' % (str(chIdNames)))

# Define the channel that we'll be working with.
chId = 8

# Get the channel that we want to work with from the list of channels.
chEl = next(ch for ch in chList['Channel'] if ch['ChannelID'] == chId)

# Print the ID and name of each subchannel.
schIdNames = [[sch['SubChannelID'], sch['SubChannelName']] for sch in chEl['SubChannel']]
print('Subchannels:\r\n%s\r\n' % (str(schIdNames),))

# Define the subchannel that we'll be working with.
schId = 0

# Get the channel that we want to work with from the list of channels.
schEl = next(sch for sch in chEl['SubChannel'] if sch['SubChannelID'] == schId)

# Collect all the channelDataBlocks into a list.
chDataType = schema[0xA1]
dataBlocks = filter(lambda x: type(x) == chDataType, ideRoot)

# Filter the dataBlocks to only include blocks for the channel we want.
chIdType = schema[0xB0]
dataBlocks = [block for block in dataBlocks if getTypeMatch(block, chIdType).value == chId]

# Get the raw data from each ChannelDataBlock, and convert to an array.
rawData = ''
payloadType = schema[0xB2]
for block in dataBlocks:
    rawData += block.dump()['ChannelDataPayload']
rawData = np.fromstring(str(rawData), dtype=chEl['ChannelFormat'][1])
rawData.resize((len(rawData)/3, 3))

# Calculate the time stamps of the data.
times = np.arange(len(rawData))/5000.0

# Plot the raw data from the IDE file.
h = plt.plot(times, rawData[:, schId])
plt.title('Raw Data')
plt.show()

# Make a list of polynomial IDs that affect ch8.0.
chCalId = chEl['ChannelCalibrationIDRef']
schCalId = chEl['SubChannel'][schId]['SubChannelCalibrationIDRef']

# Create a list of polynomials.
calListType = schema[0x4B00]
calList = getTypeMatch(ideRoot, calListType)
uniType = schema[0x4B01]
biType = schema[0x4B02]
polys = filter(lambda x: type(x) in [uniType, biType], calList)

# filter the polynomials to whichever affect ch8.0
polys = [poly.dump() for poly in polys if poly.dump()['CalID'] in [chCalId, schCalId]]

# Apply calibration polynomials to the data, channel first, then subchannel.
# The subchannel polynomial is a bivariate polynomial, which references a
# different channel; however, the coefficients simplifies to f(x,y) = x, so we
# completely ignore it.
chPoly = polys[0]['PolynomialCoef']
calData = rawData*chPoly[0] + chPoly[1]

# Plot the calibrated data.
plt.plot(times, calData[:, schId])
plt.title('Calibrated Data')
plt.show()
