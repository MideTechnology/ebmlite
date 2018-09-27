import core

import numpy as np
import matplotlib.pyplot as plt

# Load the IDE file.
schemaFile = './schemata/mide.xml'
ebmlFile = './tests/SSX46714-doesNot.ide'
schema = core.loadSchema(schemaFile)
ideRoot = schema.load(ebmlFile).dump()

# List the channels in the IDE file.
recProps = ideRoot['RecordingProperties']
chList = recProps['ChannelList']

# Print the ID and name of each channel.
print 'Channels:'
print [[ch['ChannelID'], ch['ChannelName']] for ch in chList['Channel']]
print

# Define the channel that we'll be working with.
chId = 8

# Get the channel that we want to work with from the list of channels.
chEl = [ch for ch in chList['Channel'] if ch['ChannelID'] == chId][0]

# Print the ID and name of each subchannel.
print 'Subchannels:'
print [[sch['SubChannelID'], sch['SubChannelName']] for sch in chEl['SubChannel']]
print

# Define the subchannel that we'll be working with.
schId = 0

# Get the channel that we want to work with from the list of channels.
schEl = [sch for sch in chEl['SubChannel'] if sch['SubChannelID'] == schId][0]

# Collect all the channelDataBlocks into a list.
dataBlocks = ideRoot['ChannelDataBlock']

# Filter the dataBlocks to only include blocks for the channel we want.
dataBlocks = [block for block in dataBlocks if block['ChannelIDRef'] == chId]

# Get the raw data from each ChannelDataBlock, and convert to an array.
rawData = ''
for block in dataBlocks:
    rawData += block['ChannelDataPayload']
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
polys = ideRoot['CalibrationList']['UnivariatePolynomial'] + ideRoot['CalibrationList']['BivariatePolynomial']

# filter the polynomials to whichever affect ch8.0
polys = [poly for poly in polys if poly['CalID'] in [chCalId, schCalId]]

# Apply calibration polynomials to the data, channel first, then subchannel.
# The subchannel polynomial is a bivariate polynomial, which references a
# different channel; however, the coefficients simplifies to f(x,y) = x, so we
# completely ignore it.
chPoly = polys[0]['PolynomialCoef']
calData = rawData*chPoly[0] + chPoly[1]

# Plot the calibrated data.
plt.plot(times, calData[:,schId])
plt.title('Calibrated Data')
plt.show()