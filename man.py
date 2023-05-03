####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
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

This site is aiming to mine data from evaluated nuclear data libraries (ENDFTABLES) and EXFOR (EXFORTABLES).
There are 4 main tabs for data plotting and retrieval.

##### **1. Cross sections**

Activating the box Cross Sections returns a very compact user interface with

* Target element  Examples: C, c, Pd, pd, PD
* Target mass     Examples: 56, 0 (natural), 242m (metastable)
* Reaction        Examples: n,g     n,total    p,2n 


All three can be entered by the keyboard while for the Reaction also a pull-down menu is available. 
Filling these 3 data entries directly returns a plot. 
The reaction string is given, including the number of experimental datasets which are found 
(though not all may be shown by default, see below)


##### **2. Multiple cross sections (for libraries)**

This tab allows to display multiple reactions for various nuclear data libraries 
at the same time, while the experimental data have been left out for clarity.
Hence, you may specify e.g. at the same time (n,inl) and (n,2n) for ENDF/B, JENDL, JEFF and TENDL.


##### **3. Residual Production cross sections**

The main difference with the "Cross sections" tab is that the Reaction identifier 
is restricted to (p,x), (d,x) etc only and instead you can now enter the 
Residual element and Residual mass.


##### **4. Fission yields**

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
By default the most recent experimental data sets, with a maximum of 10 with less than 200 data points, are shown. 
More data sets can be activated from the table below the figure.

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
* ![title](./assets/figs/pictureit.png) Download plot in png format
* ![title](./assets/figs/zoom.png) Zoom in and out
* ![title](./assets/figs/resetax.png) Download plot in png format
* ![title](./assets/figs/spikeline.png) Show spike line

**Data table and download :**
There are 3 tabs under the plot. Dataset list
* Dataset List: dataset with first author's name, published year, number of data points, energy min and max
* Raw Data: raw data of selected dataset
* Download: download links of .csv, .zip, and individual dataset files which includes reduced metadata and x-y-(z) table

##### **Contact and Terms of Use :**

mail: <nds.contact-point@iaea.org>

[Terms of Use](https://nucleus.iaea.org/Pages/Others/Terms-Of-Use.aspx)

"""
)
