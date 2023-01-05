from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory
import pm4py

import Input_Extraction_Definition as IED
import Super_Variant_Definition as SVD
import Super_Variant_Visualization as SVV
import Within_Variant_Summarization as WVSU
import Within_Variant_Selection as WVSE
import Variant_Visualization as VV
import Between_Variant_Summarization as BVS


#filename = "EventLogs/BPIChallenge2017.csv"
#object_types = ["Application", "Workflow", "Offer"]
#parameters = {"obj_names":"EventOrigin",
              #"val_names":["FirstWithdrawalAmount", "NumberOfTerms", "Accepted", "MonthlyCost", "Selected", "CreditScore", "OfferedAmount", "OfferID"],
              #"val_names":[],
              #"act_name":"concept:name",
              #"time_name":"time:timestamp",
              #"sep":","}
#ocel = ocel_import_factory.apply(file_path= filename,parameters = parameters)

filename = "EventLogs/order_process.jsonocel"
#parameters = {"execution_extraction": "leading_type",
              #"leading_type": "delivery",
              #"variant_calculation": "two_phase",
              #"exact_variant_calculation":True}
#ocel_order_process = ocel_import_factory.apply(filename, parameters = parameters)
ocel_order_process = ocel_import_factory.apply(filename)
#variant_layouting = variants_visualization_factory.apply(ocel_order_process)
#for i in range(len(ocel_order_process.variants)):
    #extracted_variant = IED.extract_lanes(variant_layouting[ocel_order_process.variants[i]], ocel_order_process.variant_frequencies[i])
    #VV.visualize_variant(extracted_variant)
selection = WVSE.within_variant_selection(ocel_order_process)
summarizations = [selection[key][1][0].to_super_variant(tuple(selection[key][0])) for key in selection.keys()]


super_variant1 = BVS.join_super_variants(summarizations[0], summarizations[1], False)
SVV.visualize_super_variant(super_variant1)
super_variant2 = BVS.join_super_variants(summarizations[2], summarizations[3], False)
SVV.visualize_super_variant(super_variant2)  
super_variant3 = BVS.join_super_variants(summarizations[4], summarizations[5])
SVV.visualize_super_variant(super_variant3)  
super_variant4 = BVS.join_super_variants(summarizations[6], summarizations[7])
SVV.visualize_super_variant(super_variant4) 

super_variant12 = BVS.join_super_variants(super_variant1, super_variant2, False)
SVV.visualize_super_variant(super_variant12)

super_variant34 = BVS.join_super_variants(super_variant3, super_variant4)
SVV.visualize_super_variant(super_variant34)

super_variant1234 = BVS.join_super_variants(super_variant12, super_variant34)
SVV.visualize_super_variant(super_variant1234)


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


