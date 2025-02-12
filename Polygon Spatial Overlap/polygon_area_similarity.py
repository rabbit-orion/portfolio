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
    QgsFeatureRequest
)
from qgis import processing
from PyQt5.QtCore import QVariant

# TODO: standardized using postal code vs polygon
class PolygonAreaSimilarity(QgsProcessingAlgorithm):
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
        return "polygonareasimilarity"

    def displayName(self) -> str:
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return "Polygon Area Similarity"

    def group(self) -> str:
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return "Custom Scripts"

    def groupId(self) -> str:
        """
        Returns the unique ID of the group this algorithm belongs to.
        """
        return "customscripts"

    def shortHelpString(self) -> str:
        """
        Returns a localised short helper string for the algorithm.
        """
        return "Compares area similarity between two polygon datasets using Jaccard index"

    def initAlgorithm(self, config: Optional[dict[str, Any]] = None):
        # Input polygon layer of new features to compare old features to
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.NEW_POLYGON_LAYER,
                "New polygon layer",
                [QgsProcessing.SourceType.TypeVectorPolygon]
            )
        )
        # Input polygon layer of old features with which to compare new features against
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
        # If inputs were not found, throw an exception
        if new_polygon_layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.NEW_POLYGON_LAYER))
        if old_polygon_layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.OLD_POLYGON_LAYER))
        
        # Prepare output layer fields for sink
        output_layer_fields = QgsFields()
        output_layer_fields.append(QgsField("Name", QVariant.String))
        output_layer_fields.append(QgsField("Jaccard_index", QVariant.Double))
        
        # Set up sink
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT_LAYER,
            context,
            output_layer_fields,
            new_polygon_layer.wkbType(),
            new_polygon_layer.sourceCrs()
        )
        # If sink was not created, throw an exception
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))
  
        # Load old polygons into dictionary
        feedback.pushInfo("Loading old polygons...")
        # Compute the number of steps to display within the progress bar
        total = 100.0 / old_polygon_layer.featureCount()
        old_polygons_dict = {}
        for current, feature in enumerate(old_polygon_layer.getFeatures()):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            
            old_polygons_dict[feature[old_polygon_name_field]] = feature.geometry()
            
            # Update progress bar
            feedback.setProgress(int(current * total))
        
        # Calculate Jaccard index for new polygons
        feedback.pushInfo("Calculating Jaccard index...")
        # Compute the number of steps to display within the progress bar
        total_count = new_polygon_layer.featureCount()
        total = 100.0 / total_count
        for current, new_feature in enumerate(new_polygon_layer.getFeatures()):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            
            # Get matching old feature
            new_feature_name = new_feature.attribute(new_polygon_name_field)
            new_feature_geometry = new_feature.geometry()
            old_feature_geometry = old_polygons_dict.get(new_feature_name)
            # If a matching old feature exists, calculate Jaccard index
            if old_feature_geometry:
                intersection = new_feature_geometry.intersection(old_feature_geometry)
                union = new_feature_geometry.combine(old_feature_geometry)
                jaccard_index = intersection.area() / union.area() if union.area() > 0 else 0
            else:
                jaccard_index = None
            
            # Save results to sink
            output_feature = QgsFeature(output_layer_fields)
            output_feature.setGeometry(new_feature_geometry)
            output_feature.setAttributes([new_feature_name, jaccard_index])
            sink.addFeature(output_feature, QgsFeatureSink.FastInsert)
            
            # Update progress bar
            feedback.setProgress(int(current * total))
            
        # Return the results of the algorithm
        return {self.OUTPUT_LAYER: dest_id}

    def createInstance(self):
        return self.__class__()