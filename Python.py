
import arcpy
import random
from arcpy import env
#env.workspace=r"Z:\Python_GIS\Proj\Data\Raster"
#overwrite the output
#env.overwriteOutput=True

##setup sa extension
import arcpy.sa

##checkout out the extension
arcpy.CheckOutExtension("spatial")

## todo: main syntax starts

##replace the values with parameters
inputfc1 = arcpy.GetParameterAsText(0)
inputfc2 = arcpy.GetParameterAsText(1)
outputfc1 = arcpy.GetParameterAsText(2)
outputfc2 = arcpy.GetParameterAsText(3)


#todo 1: fill DEM
in_raster = inputfc1 
fill = arcpy.sa.Fill(in_raster)
fill.save('fill_dem.tif')

#todo 2: calculate slope
in_raster = 'fill_dem.tif'
slope = arcpy.sa.Slope('fill_dem.tif')
slope.save('slope.tif')

#todo 3: calculate Flow Direction and flow accumulation
in_raster = 'fill_dem.tif'
flow_dir = arcpy.sa.FlowDirection(in_raster)
flow_dir.save('flow_dir.tif')

in_raster = 'flow_dir.tif'
flow_acc = arcpy.sa.FlowAccumulation(in_raster)
flow_acc.save('flow_acc.tif')

# todo 4 (4 & 5 run together): Get the threshold of flow accumulation to delineate river
flow_accum = "flow_acc.tif"
max_value = float(arcpy.GetRasterProperties_management(flow_accum, "MAXIMUM").getOutput(0))  ##to get the value and do arithmetic calculation
print(max_value)
# Define threshold to get the river
threshold = 0.0005* max_value  # trial and error, decreasing the value from 0.8 ...

##todo 5: delineate river from flow accumulation
flow_acc = arcpy.Raster('flow_acc.tif')
river = flow_acc > threshold      ##condition for river
river.save('river.tif')  ##save the output

# todo 6: Convert river raster to vector
#arcpy.conversion.RasterToPolygon(in_raster, out_polygon_features, {simplify},
# {raster_field}, {create_multipart_features}, {max_vertices_per_feature})
in_raster = ('river.tif')
out_polyline_features = ('river_vector.shp')
arcpy.conversion.RasterToPolyline(in_raster, out_polyline_features)
##this line was taking forever to load, so i convert it in arcgis pro
print("River extraction converted to vector.")


## todo 7: Change projection system of river.shp to UTM zone 45N
#extracted from model builder
river_vector = "river_vector.shp"
# Process: Project (Project) (management)
river_project = "river_projected.shp"
arcpy.management.Project(in_dataset=river_vector, out_dataset=river_project,
                         out_coor_system="PROJCS[\"WGS_1984_UTM_Zone_45N\","
                                         "GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\","
                                         "6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\","
                                         "0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],"
                                         "PARAMETER[\"False_Easting\",500000.0],PARAMETER[\"False_Northing\",0.0],"
                                         "PARAMETER[\"Central_Meridian\",87.0],PARAMETER[\"Scale_Factor\",0.9996],"
                                         "PARAMETER[\"Latitude_Of_Origin\",0.0],UNIT[\"Meter\",1.0]]")
print(arcpy.GetMessages())

#todo: 8: river buffer
##arcpy.analysis.Buffer(in_features, out_feature_class, buffer_distance_or_field,
# {line_side}, {line_end_type}, {dissolve_option}, {dissolve_field}, {method})
in_features = 'river_projected.shp'
out_feature_class = r'riverbuffer.shp'
buffer_distance_or_field = 500
arcpy.analysis.Buffer(in_features, out_feature_class, buffer_distance_or_field)

##todo: change buffer to raster to get riverside
##arcpy.conversion.PolygonToRaster(in_features, value_field, out_rasterdataset,
# {cell_assignment}, {priority_field}, {cellsize}, {build_rat})
in_features = 'riverbuffer.shp'
out_rasterdataset = 'riverbank.tif'
value_field = 'BUFF_DIST'
#arcpy.conversion.PolygonToRaster(in_features, value_field, out_rasterdataset)
arcpy.conversion.PolygonToRaster(in_features, value_field,
                                 out_rasterdataset, cellsize="20")

##todo 10: check the slope of riverbank
slope = arcpy.Raster('slope.tif')
riverbank = arcpy.Raster('riverbank.tif')
less_slope = slope < 20
less_slope.save('flat_areasAll.tif')
flat_riverbank = (less_slope & riverbank) ##this create raster of 0 and 1
#flat_riverbank = raster >0         ##just 1 is needed for flat riverbank
flat_riverbank.save('flat_riverbank.tif')

##todo 11: create buffer for road
##arcpy.analysis.Buffer(in_features, out_feature_class, buffer_distance_or_field,
# {line_side}, {line_end_type}, {dissolve_option}, {dissolve_field}, {method})
in_features = inputfc2    ##need to use projected
out_feature_class = r'roadbuffer.shp'
buffer_distance_or_field = 20
arcpy.analysis.Buffer(in_features, out_feature_class, buffer_distance_or_field)

#todo 12: change road buffer to raster
##arcpy.conversion.PolygonToRaster(in_features, value_field, out_rasterdataset,
# {cell_assignment}, {priority_field}, {cellsize}, {build_rat})
in_features = 'roadbuffer.shp'
out_rasterdataset = 'road_raster.tif'
value_field = 'BUFF_DIST'
#arcpy.conversion.PolygonToRaster(in_features, value_field, out_rasterdataset)
arcpy.conversion.PolygonToRaster(in_features, value_field,
                                 out_rasterdataset, cellsize="20")




# ##todo 13: find the intersect of road and flat riverbank
raster1 = arcpy.Raster('road_raster.tif')
raster2 = arcpy.Raster('riverbank.tif')
intersect = raster1 & raster2
intersect.save('risk_road_notFlat.tif')

##with slope
raster1 = arcpy.Raster('road_raster.tif')
raster2 = arcpy.Raster('flat_riverbank.tif')
intersect = raster1 & raster2
intersect.save('risk_road.tif')


#todo, convert raster to polygon to calculate the length of the roads
in_raster = 'risk_road_notFlat.tif'
out_polyline_features = 'risk_road_notFlat.shp'
arcpy.conversion.RasterToPolygon(in_raster, out_polyline_features)

#with slope
in_raster = 'risk_road.tif'
out_polyline_features = 'risk_road.shp'
arcpy.conversion.RasterToPolygon(in_raster, out_polyline_features)


##todo: intersect these polygon with road buffer vector
in_features=["risk_road_notFlat.shp","road.shp"] ##this is a list because at least two layers are needed.
out_feature_class = 'intersect_road_noslope.shp'
arcpy.analysis.Intersect(in_features, out_feature_class)

#with slope
in_features=["risk_road.shp","road.shp"] ##this is a list because at least two layers are needed.
out_feature_class = 'intersect_road.shp'
arcpy.analysis.Intersect(in_features, out_feature_class)

##todo: Dissolve both of them based on type of road

#arcpy.management.Dissolve(in_features, out_feature_class,
# {dissolve_field}, {statistics_fields}, {multi_part})
in_features = 'intersect_road_noslope.shp'
out_feature_class1 = outputfc1
arcpy.management.Dissolve(in_features, out_feature_class1,
                          'asset')

# with slope
in_features = 'intersect_road.shp'
out_feature_class2 = outputfc2
arcpy.management.Dissolve(in_features, out_feature_class2,
                          'asset')


##todo: calculate the length of each type of road

# add new field
fc = outputfc1
# arcpy.management.AddField(in_table, field_name, field_type)
in_table = fc
field_name = "Length"
field_type = "LONG"
arcpy.management.AddField(in_table, field_name, field_type)

##add in attribute table
in_table = outputfc1
fields = ["SHAPE@length", "Length", "asset"]
cursor = arcpy.da.UpdateCursor(in_table, fields)  ## Update the cursor

for row in cursor:
    row[1]=row[0]
    cursor.updateRow(row)  ## Apply update to the table
##print
cursor = arcpy.da.SearchCursor(in_table, fields)
total_len = 00
for row in cursor:
    print('Length of ' + str(row[2]) +' road near river: ' + str(row[0]) + 'm')
    total_len = total_len + row[0]

#with slope

# add new field
fc = outputfc2
# arcpy.management.AddField(in_table, field_name, field_type)
in_table = fc
field_name = "Length"
field_type = "LONG"
arcpy.management.AddField(in_table, field_name, field_type)

##add values in attribute table
in_table = outputfc2
fields = ["SHAPE@length", "Length", "asset"]
cursor = arcpy.da.UpdateCursor(in_table, fields)  ## Update the cursor

for row in cursor:
    row[1]=row[0]
    cursor.updateRow(row)  ## Apply update to the table
##print
cursor = arcpy.da.SearchCursor(in_table, fields)
total_len = 00
for row in cursor:
    print('Length of ' + str(row[2]) +' road at risk is ' + str(row[0]) + 'm')
    total_len = total_len + row[0]

del row
del cursor


##check in extension
arcpy.CheckInExtension("spatial")