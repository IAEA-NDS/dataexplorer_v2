####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2024 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
# Change logs:
#    First release: 2021-08-20
#    Update libraries: 2022-09-05, JENDL4.0 and TENDL2019 have been replced by JENDL5.0 and TENDL2021
#
####################################################################

from dash import dcc

manual = dcc.Markdown(
    """

This site is aiming to mine data from evaluated nuclear data libraries (ENDFTABLES) and EXFOR datasets (EXFORTABLES_py). Previous version of dataexplorer with  libraries (ENDFTABLES and EXFORTABLES) is accessible via [dataexplorer-2022](https://nds.iaea.org/dataexplorer-2022/).

There are 3 main selections for data plotting and retrieval.

##### **1. Cross sections**

Activating the box Cross Sections returns a very compact user interface with

* Target element  Examples: C, c, Pd, pd, PD
* Target mass     Examples: 56, 0 (natural), 242m (metastable)
* Projectile      Examples: n, p, d
* Reaction        Examples: n,g     n,total    p,2n 


Filling these 4 inputs directly returns a plot. 
The reaction string is given, including the number of experimental datasets which are found 
(though not all may be shown by default, see below)



##### **2. Residual Production cross sections**

The main difference with the "Cross sections" tab is that the Reaction identifier 
is restricted to (p,x), (d,x) etc only and instead you can now enter the 
Residual element and Residual mass.


##### **3. Fission yields**

This tab allows to display n-, g-, etc induced and spontaneous fission yield data. 
Mass distribution on the left and charge distribution at the specified mass number on the right will be shown.


##### **Features of plot and table**
**Data libraries:**
There are standard colours for the data libraries:

* ENDF/B-VIII.0: blue
* JEFF-3.3: red
* JENDL-5.0: green
* CENDL3.2: yellow
* IRDFF: grey
* TENDL-2021: black


**Experimental data:**
By default all experimental data, which were measured in the mono energetic source, are shown. However, if the number of data points in the one entry excesses more than 10,000, we only use the 500 points to load into the plot.
More data sets can be activated by switching "Use reduced data points" or "Exclude non pure data" options in the left column.


**Energy scale and zooming:**
Below each plot there is a narrow second plot with an energy slider which can be used to zoom in on the energy. 
In general, one can also zoom in easily on the plot itself.
Above the plot, there is a choice for linear or logarithmic x and y axis.
Double clicking at the empty space in the plot will reset the scale of the figure.


**Mouse functions:**
Hovering the mouse over an experimental data point shows the corresponding author name, also available in the legend.
A single click on an entry in the legend removes that particular dataset from the plot. Clicking again makes it appear again.
A double click on an entry makes all other data sets disappear. Double clicking again makes them all appear again


**Icons :**
Just above the legend, you find more than 10 icons for particular actions:
* ![](../assets/figs/pictureit.png) Download plot in png format
* ![](../assets/figs/zoom.png) Zoom in and out
* ![](../assets/figs/resetax.png) Download plot in png format
* ![](../assets/figs/spikeline.png) Show spike line


**Data table and download :**
There are 3 tabs under the plot. Dataset list
* Dataset List: dataset with first author's name, published year, number of data points, energy min and max
* Raw Data: raw data of selected dataset
* Download: download links of .csv, .zip, and individual dataset files which includes reduced metadata and x-y-(z) table

##### **Contact and Terms of Use :**

mail: <nds.contact-point@iaea.org>

[Terms of Use](https://www.iaea.org/about/terms-of-use)

""",
    dangerously_allow_html=True,
)





table_desc_thermal = dcc.Markdown(
"""
##### **Column descriptions **
This table contains cross-section data near thermal energy (2.53E-8 MeV). 
- **Entry Id**: The entry (5 digits), subentry (3 digits), and pointer (1 digit) number taken from EXFOR, formatted as EEEEE-SSS-P.
- **Author**: The name of the first author of the publication.
- **Year**: The publication year of the main publication in `REFERENCE` field in EXFOR.
- **SF4**: EXFOR's reaction subfield 4 (SF4) representing reaction product(s). For example, the 235U(n,g) reaction produces 236U as a reaction product.
- **SF8**: EXFOR's reaction subfield 8 (SF8) indicating modifiers. The list of modifiers can be found [here](https://github.com/IAEA-NDS/exfor_dictionary/blob/b3d79674ea1b55b7c9e889b52cf8dd2e370b5550/src/exfor_dictionary/latest.json#L19984). In many cases, a null value in SF8 indicates that the measurements were done in the monoenergetic environment (or corrected), while `MXW` or `SPA` in SF8 mean the "Maxwellian average" or "Spectrum average", respectively.
- **SF9**: EXFOR's reaction subfield 4 (SF4) representing data types. For example, `DERIV` means Derived data which was not directory measured in the experiment. The list of data types can be found [here](https://github.com/IAEA-NDS/exfor_dictionary/blob/b3d79674ea1b55b7c9e889b52cf8dd2e370b5550/src/exfor_dictionary/latest.json#L20337C24-L20337C50).

"""
)
