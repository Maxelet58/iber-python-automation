# Iber 2D Hydraulic Simulation Automation

## Overview
This repository contains a custom Python workflow engineered to automate 2D hydraulic flood risk modeling using the **Iber** solver. 

Traditional flood risk modeling often suffers from workflow bottlenecks due to manual data entry and simulation monitoring via Graphical User Interfaces (GUIs). This script bypasses the GUI, allowing for the automated batch execution of multiple extreme-weather scenarios, drastic reduction of computational setup time, and scalable sensitivity analysis.

This methodology was specifically developed and applied to stress-test the Francolí River basin (Catalonia) against catastrophic structural failures and climate-change-driven peak inflows, adhering to the Catalan Water Agency (ACA) hazard standards.

## Tech Stack
* **Python:** Core automation, file parsing, and subprocess management.
* **Iber (v3.4):** 2D hydrodynamic numerical solver.
* **QGIS:** Post-processing and spatial vulnerability analysis (Raster map algebra) //does not take part in the code//.

## Key Features
* **Automated Parameter Modification:** Dynamically edits Iber's core configuration files (`Iber2D.dat`, `Iber_Breach.dat`) to adjust Manning's roughness coefficients, inflow hydrographs, and structural breach timings.
* **Batch Processing:** Sequentially executes multiple stress-test scenarios without human intervention.
* **Output Isolation:** Automatically purges old results to prevent false positives and isolates the output raster folders (`RasterResults`) for each specific scenario to ensure clean GIS integration.
* **Execution Logging:** Generates timestamped logs to track computation times and catch potential solver divergences.

## Engineering Context
This tool was built by an Environmental & Mineral Resources Engineering student (UPC) to prove that modern hydro-informatics and algorithmic automation can transform how we evaluate territorial resilience against standard-deviation climate events.
