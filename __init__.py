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
import Intra_Variant_Generation as IAVG
import Inter_Variant_Summarization as IEVS
import Inter_Variant_Generation as IEVG
import Super_Variant_Hierarchy as SVH

MODE = 4

filename = "EventLogs/BPI2017-Top10.jsonocel"
parameters = {"execution_extraction": "leading_type",
              "leading_type": "application"}
ocel = ocel_import_factory.apply(file_path = filename , parameters = parameters)

all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization(ocel)
summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)

#filename = "EventLogs/order_process.jsonocel"
#ocel = ocel_import_factory.apply(file_path = filename)

#variant_layouting = variants_visualization_factory.apply(ocel)
#extracted_variant = IED.extract_lanes(variant_layouting[ocel.variants[5]], ocel.variant_frequencies[5])
#SVV.visualize_variant(extracted_variant)

if(MODE == 1):

    initial_super_variants = IEVG.classify_initial_super_variants_by_activity([summarizations[3], summarizations[4], summarizations[6], summarizations[7], summarizations[8], summarizations[9]], "Refuse offer")
    initial_super_variants = [initial_super_variants[0]] + IEVG.classify_initial_super_variants_by_activity(initial_super_variants[1], "Accept offer")
    hierarchy, final_super_variants = IEVG.generate_super_variant_hierarchy_by_classification(initial_super_variants, 1, 3)
    SVH.visualize_super_variant_layer(final_super_variants)

elif(MODE == 2):
    super_variant, cost = IEVS.join_super_variants(summarizations[6], summarizations[7], False, False)
    super_variant, cost = IEVS.join_super_variants(super_variant, summarizations[8], True, False)
    SVV.visualize_super_variant(super_variant)

elif(MODE == 3):
    super_variant, cost = IEVS.join_super_variants(summarizations[6], summarizations[7], False, False)
    super_variant, cost = IEVS.join_super_variants(super_variant, summarizations[8], False, False)
    super_variant, cost = IEVS.join_super_variants(super_variant, summarizations[9], True, False)
    SVV.visualize_super_variant(super_variant)

elif(MODE == 4):
    super_variant1, cost = IEVS.join_super_variants(summarizations[6], summarizations[7], False, False)
    super_variant2, cost = IEVS.join_super_variants(summarizations[9], summarizations[8], False, False)
    super_variant, cost = IEVS.join_super_variants(super_variant1, super_variant2, False, True)
    SVV.visualize_super_variant(super_variant1)
    SVV.visualize_super_variant(super_variant2)
    SVV.visualize_super_variant(super_variant)

elif(MODE == 5):
    super_variant, cost = IEVS.join_super_variants(summarizations[3], summarizations[6], False, False)
    SVV.visualize_super_variant(summarizations[3])
    SVV.visualize_super_variant(summarizations[6])
    SVV.visualize_super_variant(super_variant)

elif(MODE == 6):
    super_variant, cost = IEVS.join_super_variants(summarizations[3], summarizations[6], False, False)
    super_variant, cost = IEVS.join_super_variants(super_variant, summarizations[7], True, False)
    SVV.visualize_super_variant(super_variant)

elif(MODE == 7):
    SVH.visualize_super_variant_layer([summarizations[6], summarizations[7], summarizations[8]])
    #super_variant, cost = IEVS.join_super_variants(summarizations[4], summarizations[6], False, False)
    #SVH.visualize_single_super_variant_hierarchy(summarizations[4], summarizations[6], super_variant)

elif(MODE == 8):
    for i in range(len(summarizations)-1):
        for j in range(i+1, len(summarizations)):
            super_variant, cost = IEVS.join_super_variants(summarizations[i], summarizations[j], True, False)
            print(i)
            print(j)
            print("---")
            SVV.visualize_super_variant(super_variant)
    #super_variant, cost = IEVS.join_super_variants(summarizations[4], summarizations[6], False, False)
    #SVH.visualize_single_super_variant_hierarchy(summarizations[4], summarizations[6], super_variant)
