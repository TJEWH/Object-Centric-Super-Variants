from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory

import Input_Extraction_Definition as IED
import Super_Variant_Definition as SVD
import Super_Variant_Visualization as SVV
import Within_Variant_Summarization as WVSU
import Within_Variant_Selection as WVSE
import Variant_Visualization as VV
import Between_Variant_Summarization as BVS

filename = "EventLogs/order_process.jsonocel"
ocel_order_process = ocel_import_factory.apply(filename)
selection = WVSE.within_variant_selection(ocel_order_process)
summarizations = [selection[key][1][0].to_super_variant(tuple(selection[key][0])) for key in selection.keys()]

first = summarizations[0]
for summarization in summarizations[1:6]:
    first = BVS.join_super_variants(first, summarization)
SVV.visualize_super_variant(first)   

#for key in (selection.keys()):
    #print(key)

#print(list(selection.keys())[8])



#filename = "EventLogs/OCEL_example.jsonocel"
#ocel_running_example = ocel_import_factory.apply(filename)
#selection = WVSE.within_variant_selection(ocel_running_example )
#summarizations = [summarization[1][0] for summarization in selection.values()]
#or summarization in (selection.values()):
#BVS.join_super_variants(summarizations[1], summarizations[2],[],[],[])
#variant_layouting = variants_visualization_factory.apply(ocel_running_example)
#for variant in ocel_running_example.variants:
#extracted_variant = IED.extract_lanes(variant_layouting[ocel_running_example.variants[1]], ocel_running_example.variant_frequencies[5])
#VV.visualize_variant(extracted_variant)
#summarizations = WVSU.within_variant_summarization(extracted_variant)
#for summarization in list(summarizations):
    #SVV.visualize_super_variant_summarization(summarization)
    #print(summarization.encode_lexicographically())

