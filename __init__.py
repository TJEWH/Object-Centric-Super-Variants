from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory

import Input_Extraction_Definition as IED
import Super_Variant_Definition as SVD
import Within_Variant_Visualization as WVVI
import Within_Variant_Summarization as WVSU
import Within_Variant_Selection as WVSE
import Variant_Visualization as VV

#filename = "EventLogs/order_process.jsonocel"
#ocel_order_process = ocel_import_factory.apply(filename)
#selection = WVSE.within_variant_selection(ocel_order_process)

#variant_layouting = variants_visualization_factory.apply(ocel_order_process)
#extracted_variant = IED.extract_lanes(variant_layouting[ocel_order_process.variants[10]], 0)
#summarizations = WVSU.within_variant_summarization(extracted_variant)
#WVVI.visualize_within_variant_summarization(summarizations[0])
#VV.visualize_variant(extracted_variant)
#for summarization in list(selection.values()):
    #WVVI.visualize_within_variant_summarization(summarization[1])


filename = "EventLogs/OCEL_example.jsonocel"
ocel_running_example = ocel_import_factory.apply(filename)
selection = WVSE.within_variant_selection(ocel_running_example)
variant_layouting = variants_visualization_factory.apply(ocel_running_example)
extracted_variant = IED.extract_lanes(variant_layouting[ocel_running_example.variants[1]], 0)
summarizations = WVSU.within_variant_summarization(extracted_variant)
for summarization in summarizations:
    WVVI.visualize_within_variant_summarization(summarization)