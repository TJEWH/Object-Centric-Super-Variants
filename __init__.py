from ocpa.objects.log.importer.ocel import factory as ocel_import_factory

import Input_Extraction_Definition as IED
import Super_Variant_Definition as SVD
import Super_Variant_Visualization as SVV
import Within_Variant_Summarization as WVSU
import Within_Variant_Selection as WVSE

filename = "EventLogs/order_process.jsonocel"
ocel_order_process = ocel_import_factory.apply(filename)
WVSE.within_variant_selection(ocel_order_process)
#variant_layouting = variants_visualization_factory.apply(ocel_order_process)
#for variant in ocel_order_process.variants:
#extracted_variant = IED.extract_lanes(variant_layouting[ocel_order_process.variants[8]])
#summarizations = WVS.within_variant_summarization(extracted_variant, False)
#for i in range(len(summarizations)):
    #print(summarizations[i])
    #print(summarizations[i].encode_lexicographically())
#print("--------------------")
#SVV.visualize_variant(variant_layouting[ocel_order_process.variants[9]])

filename = "EventLogs/OCEL_example.jsonocel"
ocel_running_example = ocel_import_factory.apply(filename)
#variant_layouting = variants_visualization_factory.apply(ocel_running_example)
#for variant in ocel_running_example.variants:
    #extracted_variant = IED.extract_lanes(variant_layouting[variant])
    #summarizations = BAPA.within_variant_summarization(extracted_variant, False)
    #for i in range(len(summarizations)):
        #print(summarizations[i].encode_lexicographically())
    #print("--------------------")
#variant_3 = IED.extract_lanes(variant_layouting[ocel_running_example.variants[0]])
#summarizations_variant_3 = BAPA.within_variant_summarization(variant_3)
#for i in range(len(summarizations_variant_3)):
    #print(summarizations_variant_3[i].encode_lexicographically())

#SVV.visualize_variant(variant_layouting[ocel_running_example.variants[1]])
