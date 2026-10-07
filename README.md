Flood Risk Road Analysis Using ArcPy

Overview

This project automates flood risk assessment for transportation infrastructure using ArcGIS Pro and ArcPy. The workflow combines raster-based terrain and hydrologic analysis with vector-based geoprocessing to identify:
  Roads located near river corridors
  Roads potentially exposed to flooding
  Total lengths of affected primary, secondary, and tertiary roads

The tool processes a Digital Elevation Model (DEM) and road network dataset to derive river channels, generate riverbank and flood-risk zones, and quantify transportation infrastructure exposure.

Key GIS Techniques
  Raster Analysis
  DEM conditioning (Fill)
  Slope analysis
  Flow Direction
  Flow Accumulation
  Stream/River extraction
  Raster reclassification
  Raster-to-vector conversion
  
Vector Analysis
  Projection management
  Buffer analysis
  Spatial intersection
  Dissolve operations
  Polygon processing
  Road network analysis
  Length calculations using ArcPy cursors
  
Technologies
  Python
  ArcPy
  ArcGIS Pro
  Spatial Analyst Extension
