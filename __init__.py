from ocpa.objects.log.importer.ocel import factory as ocel_import_factory

import Input_Extraction_Definition as IED
import Super_Variant_Definition as SVD
import Within_Variant_Summarization_Visualization as WVSV
import Within_Variant_Summarization as WVSU
import Within_Variant_Selection as WVSE

filename = "EventLogs/order_process.jsonocel"
ocel_order_process = ocel_import_factory.apply(filename)
selection = WVSE.within_variant_selection(ocel_order_process)


filename = "EventLogs/OCEL_example.jsonocel"
ocel_running_example = ocel_import_factory.apply(filename)