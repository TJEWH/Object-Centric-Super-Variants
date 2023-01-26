#from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory
from ocpa.algo.util.filtering.log import case_filtering
from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory

import Input_Extraction_Definition as IED
import Super_Variant_Definition as SVD
import Super_Variant_Visualization as SVV
import Intra_Variant_Summarization as IAVS
import Summarization_Selection as SS
import Variant_Visualization as VV
import Inter_Variant_Summarization as IEVS
import Super_Variant_Generation as SVG


#filename = "EventLogs/BPI2017-Top10.jsonocel"
#parameters = {"execution_extraction": "leading_type",
              #"leading_type": "offer"}
#ocel = ocel_import_factory.apply(file_path = filename , parameters = parameters)
filename = "EventLogs/order_process.jsonocel"
ocel = ocel_import_factory.apply(file_path = filename)
selection = SS.intra_variant_summarization_selection(ocel)
summarizations = [selection[key][1][0].to_super_variant(tuple(selection[key][0])) for key in selection.keys()]
#hierarchy = SVG.generate_super_variant_hierarchy_uniform(summarizations[0:7], 3)
hierarchy = SVG.generate_super_variant_hierarchy_normal(summarizations[0:8], 4)
#for summarization in summarizations:
 #   SVV.visualize_super_variant(summarization)

#variant_layouting = variants_visualization_factory.apply(ocel)
#extracted_variant = IED.extract_lanes(variant_layouting[ocel.variants[5]], ocel.variant_frequencies[5]) # Extract the variants frequency
#extracted_summarizations = WVSU.within_variant_summarization(extracted_variant, False)
#for summarization in extracted_summarizations:
    #SVV.visualize_super_variant(summarization)

#for i in range(len(summarizations)):
    #for j in range(i+1, len(summarizations)):
        #super_variant_ij, cost = BVS.join_super_variants(summarizations[i], summarizations[j], False)
        #SVV.visualize_super_variant(super_variant_ij)
#SVV.visualize_super_variant(summarizations[4])

#SVV.visualize_super_variant(summarizations[1])
#SVV.visualize_super_variant(summarizations[10])
#super_variant_14, cost = BVS.join_super_variants(summarizations[3], summarizations[5], True)
#super_variant_12, cost = BVS.join_super_variants(summarizations[7], summarizations[8], True)
#super_variant_1214, cost = BVS.join_super_variants(super_variant_14, super_variant_12, True)





