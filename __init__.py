#from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory
from ocpa.algo.util.filtering.log import case_filtering
from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory

import Input_Extraction_Definition as IED
import Super_Variant_Definition as SVD
import Super_Variant_Visualization as SVV
import Within_Variant_Summarization as WVSU
import Within_Variant_Selection as WVSE
import Variant_Visualization as VV
import Between_Variant_Summarization as BVS


filename = "EventLogs/BPI2017-Top10.jsonocel"
parameters = {"execution_extraction": "leading_type",
              "leading_type": "offer"}
ocel = ocel_import_factory.apply(file_path = filename , parameters = parameters)

#variant_layouting = variants_visualization_factory.apply(ocel)
#for i in range(len(ocel.variants)):
    #extracted_variant = IED.extract_lanes(variant_layouting[ocel.variants[i]], ocel.variant_frequencies[-1])
    #VV.visualize_variant(extracted_variant)

selection = WVSE.within_variant_selection(ocel)
summarizations = [selection[key][1][0].to_super_variant(tuple(selection[key][0])) for key in selection.keys()]

for i in range(len(summarizations)):
    for j in range(len(summarizations)):
        if(j>i):
            print("Joining " + str(i) + " and " + str(j) )
            super_variant, cost = BVS.join_super_variants(summarizations[i], summarizations[j], False)
            SVV.visualize_super_variant(super_variant)
            print("At cost " + str(cost))

#super_variant12 = BVS.join_super_variants(super_variant1, super_variant4, False)
#SVV.visualize_super_variant(super_variant12)

#super_variant34 = BVS.join_super_variants(super_variant3, super_variant4)
#SVV.visualize_super_variant(super_variant34)

#super_variant1234 = BVS.join_super_variants(super_variant12, super_variant34)
#SVV.visualize_super_variant(super_variant1234)


#for key in (selection.keys()):
    #print(key)

#print(list(selection.keys())[8])



#filename = "EventLogs/Presentation_example.jsonocel"
#ocel_running_example = ocel_import_factory.apply(filename)
#selection = WVSE.within_variant_selection(ocel_running_example )
#summarizations = [summarization[1][0] for summarization in selection.values()]
#super_variant1 = BVS.join_super_variants(summarizations[-1].to_super_variant(1), summarizations[-2].to_super_variant(0), False)
#for summarization in summarizations:
    #SVV.visualize_super_variant(summarization)
#or summarization in (selection.values()):
#BVS.join_super_variants(summarizations[1], summarizations[2],[],[],[])
#variant_layouting = variants_visualization_factory.apply(ocel_running_example)
#for variant in ocel_running_example.variants:
    #extracted_variant = IED.extract_lanes(variant_layouting[variant], ocel_running_example.variant_frequencies[-1])
    #VV.visualize_variant(extracted_variant)
#summarizations = WVSU.within_variant_summarization(extracted_variant)
#summarization1 = summarizations[-1].to_super_variant(1)

#extracted_variant = IED.extract_lanes(variant_layouting[ocel_running_example.variants[-3]], ocel_running_example.variant_frequencies[-1])
#VV.visualize_variant(extracted_variant)
#summarizations = WVSU.within_variant_summarization(extracted_variant)
#summarization2 = summarizations[-1].to_super_variant(2)

#SVV.visualize_super_variant(summarization1)
#SVV.visualize_super_variant(summarization2)

#super_variant = BVS.join_super_variants(summarization2, summarization1)
#SVV.visualize_super_variant(super_variant) 


