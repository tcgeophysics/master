# -*- coding: utf-8 -*-
"""
TC, Nov 29, 2013
Suite of 2D filters to process 2D numpy arrays from GridIO.py
"""
from numpy import linspace ,zeros, real, nan_to_num, isnan, min
from scipy.fftpack import fft2 , fftfreq, ifft2
from numpy.fft import irfft2
from cmath import pi, exp
from math import pow, sqrt, sin, cos
from GridIO import GetGeoGrid, CreateGeoGrid

# IO functions: 
# GeoT, Projection, Bands, SourceType, NDV, xsize, ysize, SourceArray, SourceStats = GetGeoGrid(FileName)
# CreateGeoGrid(FileName, TargetFileName, xsize, ysize, TargetType, TargetArray)
# Return 0 if successful




FileName       =   'can1k_mag_NAD83_crop02_UTM.tiff'
TargetFileName =   'can1k_mag_NAD83_crop02_UTM_RTP.tiff'

#FileName       =   'CAN_Bouguer_NAD83_crop02_UTM.tiff'
#TargetFileName =   'CAN_Bouguer_NAD83_crop02_UTM_prol.tiff'

# Champ magnetique regional (123W 55N - IGRF 2010)
D = 18.595*pi/180      # declination
I = 74.564*pi/180     # inclination
F = 56912             # intensity
print D, I, F
# Champ magnetique regional
l = F*cos(I)*cos(D)
m = F*cos(I)*sin(D)
n = F*sin(I)
print l, m, n
# Import data
SourceOriginX, SourceOriginY, SourcePixelWidth, SourcePixelHeight, Projection, Bands, \
SourceType, NDV, xsize, ysize, SourceArray, SourceStats = GetGeoGrid(FileName)

# get Array info
TempArray = SourceArray
TempArrayShape = TempArray.shape
Nc = TempArrayShape [1] #x length
Nr = TempArrayShape [0] #y length

# assign some real spatial co-ordinates to the grid points   
# first define the edge values
x_min = SourceOriginX
x_max = SourceOriginX + xsize * SourcePixelWidth
y_min = SourceOriginY
y_max = SourceOriginY + ysize * SourcePixelHeight

# then create some empty 2d arrays to hold the individual cell values
x_array = zeros( TempArrayShape , dtype = float )
y_array = zeros( TempArrayShape , dtype = float )

# now fill the arrays with the associated values
for row , y_value in enumerate(linspace (y_min , y_max , num = Nr) ):

  for column , x_value in enumerate(linspace (x_min , x_max , num = Nc) ):

    x_array[row][column] = x_value
    y_array[row][column] = y_value

# now for any row,column pair the x_array and y_array hold the spatial domain
# co-ordinates of the associated point in some_data_grid

# now use the fft to transform the data to the wavenumber domain
TempArray_wavedomain = fft2(TempArray)

# now we can use fftfreq to give us a base for the wavenumber co-ords
# this returns [0.0 , 1.0 , 2.0 , ... , 62.0 , 63.0 , -64.0 , -63.0 , ... , -2.0 , -1.0 ]
n_value = fftfreq( Nr , (1.0 / float(Nr) ) )
m_value = fftfreq( Nc , (1.0 / float(Nc) ) )

# now we can initialize some arrays to hold the wavenumber co-ordinates of each cell
kx_array = zeros( TempArrayShape , dtype = float )
ky_array = zeros( TempArrayShape , dtype = float )
TempArray_wavedomain_proc = zeros( TempArrayShape , dtype = complex )
# before we can calculate the wavenumbers we need to know the total length of the spatial
# domain data in x and y. This assumes that the spatial domain units are metres and
# will result in wavenumber domain units of radians / metre.
x_length = xsize * SourcePixelWidth
y_length = ysize * SourcePixelHeight

nafn = 0
kx = 0
ky = 0

# now the loops to calculate the wavenumbers
for row in xrange(Nr):
    
    for column in xrange(Nc):
        
        kx_array[row][column] = ( 2.0 * pi * n_value[column] ) / x_length
        ky_array[row][column] = ( 2.0 * pi * n_value[row] ) / y_length

# now for any row,column pair kx_array , and ky_array will hold the wavedomain coordinates
# of the correspoing point in some_data_wavedomain
        kw = sqrt(pow(kx_array[row][column],2)+pow(ky_array[row][column],2))
        
        TempArray_wavedomain_proc [row][column] = TempArray_wavedomain [row][column] *\
        (1j * kw /(l*kx_array[row][column] + m*ky_array[row][column] + 1j*n*kw))
        
        if isnan(TempArray_wavedomain_proc [row][column]) == True:
            nafn+=1
            kx = column
            ky = row

print TempArray_wavedomain_proc
print 'nan = ', nafn, 'kx = ', kx, ' ky = ', ky
TempArray_proc = ifft2(nan_to_num(TempArray_wavedomain_proc)) # Nan values in wavenumber domain!!!
print TempArray_proc
TempArray_proc = real(TempArray_proc)
#print amax(TempArray_proc)
#print amin(TempArray_proc)
#print NDV

TargetArray = TempArray_proc
TargetType = SourceType
NDV = -99999

# Export
CreateGeoGrid(FileName, TargetFileName, xsize, ysize, TargetType, TargetArray, NDV)