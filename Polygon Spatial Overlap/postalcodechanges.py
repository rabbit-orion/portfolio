from typing import Any, Optional

from qgis.core import (
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsVectorLayer
)
from qgis import processing
from PyQt5.QtCore import QVariant

# TODO: standardized using postal code vs polygon
class PostalCodeChanges(QgsProcessingAlgorithm):
    # Parameters and outputs
    NEW_POLYGON_LAYER = "NEW_POLYGON_LAYER"
    OLD_POLYGON_LAYER = "OLD_POLYGON_LAYER"
    NEW_POLYGON_NAME_FIELD = "NEW_POLYGON_NAME_FIELD"
    OLD_POLYGON_NAME_FIELD = "OLD_POLYGON_NAME_FIELD"
    OUTPUT_LAYER = "OUTPUT_LAYER"

    def name(self) -> str:
        """
        Returns the algorithm name, used for identifying the algorithm.
        """
        return "postalcodechanges"

    def displayName(self) -> str:
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return "Postal Code Changes"

    def group(self) -> str:
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return "My Custom Scripts"

    def groupId(self) -> str:
        """
        Returns the unique ID of the group this algorithm belongs to.
        """
        return "mycustomscripts"

    def shortHelpString(self) -> str:
        """
        Returns a localised short helper string for the algorithm.
        """
        return "Compares the similarity between two postal code polygon datasets"

    def initAlgorithm(self, config: Optional[dict[str, Any]] = None):
        # Input polygon layer of new features to compare old features to.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.NEW_POLYGON_LAYER,
                "New polygon layer",
                [QgsProcessing.SourceType.TypeVectorPolygon]
            )
        )
        
        # Input polygon layer of old features with which to compare new features against.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.OLD_POLYGON_LAYER,
                "Old polygon layer",
                [QgsProcessing.SourceType.TypeVectorPolygon]
            )
        )
        
        # Feature name field for new polygon layer
        self.addParameter(
            QgsProcessingParameterField(
                self.NEW_POLYGON_NAME_FIELD,
                "New polygon name field",
                '',
                self.NEW_POLYGON_LAYER
            )
        )
        
        # Feature name for old polygon layer
        self.addParameter(
            QgsProcessingParameterField(
                self.OLD_POLYGON_NAME_FIELD,
                "Old polygon name field",
                '',
                self.OLD_POLYGON_LAYER
            )
        )

        # Output polygon layer of new features with matching results from old features
        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT_LAYER, "Output layer")
        )

    def processAlgorithm(
        self,
        parameters: dict[str, Any],
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ) -> dict[str, Any]:
        feedback.pushInfo("Setting up environment...")
        
        # Retrieve input layers and fields
        new_polygon_layer = self.parameterAsSource(parameters, self.NEW_POLYGON_LAYER, context)
        old_polygon_layer = self.parameterAsSource(parameters, self.OLD_POLYGON_LAYER, context)
        new_polygon_name_field = self.parameterAsString(parameters, self.NEW_POLYGON_NAME_FIELD, context)
        old_polygon_name_field = self.parameterAsString(parameters, self.OLD_POLYGON_NAME_FIELD, context)
        # If inputs were not found, throw an exception to indicate that the algorithm
        # encountered a fatal error.
        if new_polygon_layer is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.NEW_POLYGON_LAYER)
            )
        if old_polygon_layer is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.OLD_POLYGON_LAYER)
            )
        
        # Prepare output layer fields
        output_layer_fields = QgsFields()
        output_layer_fields.append(QgsField("NAME", QVariant.String))
        output_layer_fields.append(QgsField("jaccard_index", QVariant.Double))
        output_layer_fields.append(QgsField("hausdorff_distance", QVariant.Double))
        output_layer_fields.append(QgsField("hausdorff_distance_normalized", QVariant.Double))
        
        # Set up sink
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT_LAYER,
            context,
            output_layer_fields,
            new_polygon_layer.wkbType(),
            new_polygon_layer.sourceCrs()
        )
        # If sink was not created, throw an exception to indicate that the algorithm
        # encountered a fatal error.
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))
        
        # TODO: step-based progressor bar
        # Load postal code names and geometries
        new_polygons_dict = {feature[new_polygon_name_field]: feature.geometry() for feature in new_polygon_layer.getFeatures()}
        old_polygons_dict = {feature[old_polygon_name_field]: feature.geometry() for feature in old_polygon_layer.getFeatures()}
        
        # Compute the number of steps to display within the progress bar
        total = 100.0 / len(new_polygons_dict) if new_polygons_dict else 0
        
        # Calculate Hausdorff distance and Jaccard Index for new polygons
        feedback.pushInfo("Calculating summary statistics...")
        for current, polygon_name in enumerate(new_polygons_dict.keys()):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            
            # Get polygon geometry
            new_polygon_geometry = new_polygons_dict.get(polygon_name)
            old_polygon_geometry = old_polygons_dict.get(polygon_name)
            
            # Output an empty result if the polygon is missing from the old dataset
            if old_polygon_geometry is None:
                hausdorff_distance = None # Not applicable
                hausdorff_distance_normalized = None # Not applicable
                jaccard_index = 0.0 # No overlap
            else:
                # Calculate Jaccard Index
                intersection = new_polygon_geometry.intersection(old_polygon_geometry)
                union = new_polygon_geometry.combine(old_polygon_geometry)
                jaccard_index = intersection.area() / union.area() if union.area() > 0 else 0
                # Calculate Hausdorff distance
                hausdorff_distance = new_polygon_geometry.hausdorffDistance(old_polygon_geometry)
                # Calculate maximum distance between geometries
                # TODO use something like https://postgis.net/docs/ST_MaxDistance.html
                # Approximate using convex hulls
                # new_polygon_convex_hull = processing.run("native:convexhull", {
                #     'INPUT': new_polygon_geometry,
                #     'OUTPUT': "memory:"
                # })
                # old_polygon_convex_hull = processing.run("native:convexhull", {
                #     'INPUT': old_polygon_geometry,
                #     'OUTPUT': "memory:"
                # })
                # # Calculate maximum distance between convex hulls
                new_polygon_geometry_wkt = new_polygon_geometry.asWkt()
                old_polygon_geometry_wkt = old_polygon_geometry.asWkt()
                sql_query = f"SELECT ST_MaxDistance(ST_GeomFromText('{new_polygon_geometry_wkt}'), ST_GeomFromText('{old_polygon_geometry_wkt}')) AS max_distance"
                virtual_layer = QgsVectorLayer(sql_query, "Max_Distance", "virtual")
                if not virtual_layer.isValid():
                    feedback.pushInfo("Error")
                maximum_distance = next(virtual_layer.getFeatures(), None)
                hausdorff_distance_normalized = maximum_distance
                #feedback.pushInfo(f"Maximum distance of {polygon_name}: {maximum_distance['max_distance']}")
                # # Calculate normalized Hausdorff distance
                # hausdorff_distance_normalized = hausdorff_dist / maximum_distance if maximum_distance > 0 else 0
            
            # Save results
            output_feature = QgsFeature(output_layer_fields)
            output_feature.setAttributes([polygon_name, jaccard_index, hausdorff_distance, hausdorff_distance_normalized])
            sink.addFeature(output_feature, QgsFeatureSink.FastInsert)
            
            # Update the progress bar
            feedback.setProgress(int(current * total))
            
        # Return the results of the algorithm.
        return {self.OUTPUT_LAYER: dest_id}

    def createInstance(self):
        return self.__class__()
