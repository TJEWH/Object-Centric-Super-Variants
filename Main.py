from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory
import Input_Extraction_Definition as IED
import Super_Variant_Definition as SVD
import Propagative_Summarization_Approach as PSA
import Super_Variant_Visualization as SVV
import Branching_Approach_Powerset as BAPO
import Branching_Approach_Partitions as BAPA

filename = "EventLogs/order_process.jsonocel"
ocel_order_process = ocel_import_factory.apply(filename)
variant_layouting = variants_visualization_factory.apply(ocel_order_process)
variant_2 = IED.extract_lanes(variant_layouting[ocel_order_process.variants[10]])
summarizations_variant_2 = BAPA.within_variant_summarization(variant_2)
SVV.visualize_variant(variant_layouting[ocel_order_process.variants[10]])
#summarizations_variant_2 = BAPO.get_all_summarizations(variant_3, False)
#for summarization in summarizations_variant_2:
    #SVV.visualize_summarized_variant(SVD.summarized_variant_layouting(summarization))

#filename = "EventLogs/OCEL_example.jsonocel"
#ocel_running_example = ocel_import_factory.apply(filename)
#variant_layouting = variants_visualization_factory.apply(ocel_running_example)
#variant_3 = IED.extract_lanes(variant_layouting[ocel_running_example.variants[0]])
#summarizations_variant_1 = BAPA.within_variant_summarization(variant_3)
#SVV.visualize_variant(variant_layouting[ocel_running_example.variants[0]])
#summarizations_variant_1 = BAPO.get_all_summarizations(variant_3, False)
#for summarization in summarizations_variant_1:
#    SVV.visualize_summarized_variant(SVD.summarized_variant_layouting(summarization))
