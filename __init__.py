from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.visualization.log.variants import factory as variants_visualization_factory
from ocpa.algo.util.filtering.log import case_filtering
from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory
from ocpa.algo.util.filtering.log import variant_filtering

import Input_Extraction_Definition as IED
import Super_Variant_Definition as SVD
import Super_Variant_Visualization as SVV
import Intra_Variant_Summarization as IAVS
import Summarization_Selection as SS
import Intra_Variant_Generation as IAVG
import Inter_Variant_Summarization as IEVS
import Inter_Variant_Generation as IEVG
import Super_Variant_Hierarchy as SVH

''' Ensure version compatibility
from .Intra_Variant_Generation import (complete_intra_variant_summarization_from_process as
                                       complete_intra_variant_summarization)
from .Intra_Variant_Generation import (get_unique_summarizations_from_process as
                                       get_unique_summarizations)'''

branching = {
    "main": {
        "mode": 8,
        "file": "EventLogs/BPI2017-Top10.jsonocel",
        "parameters": {"execution_extraction": "leading_type"},
        "alignment": {"align": False, "repeat": None},
    },
    "expl": {
        "mode": None,
        "file": "EventLogs/test_log.jsonocel",
        "alignment": {"align": True, "repeat": True},
    },
    "eval": {
        "mode": 9,
        "file": "EventLogs/test_log.jsonocel",
        "alignment": {"align": False, "repeat": None},
    },
    "publ": {
        "mode": 9,
        "file": "EventLogs/Presentation_Example.jsonocel",
        "alignment": {"align": True, "repeat": True},
    },
}

BRANCH = branching["publ"]


MODE = BRANCH["mode"]
filename = BRANCH["file"]
parameters = BRANCH["parameters"] if "parameters" in BRANCH else None

ocel = ocel_import_factory.apply(file_path=filename, parameters=parameters)


if BRANCH == "main":
    all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_process(ocel)
    summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)

    IEVG.NESTED_STRUCTURES = True
    if MODE == 1:
        initial_super_variants = IEVG.classify_initial_super_variants_by_activity(
            [summarizations[3], summarizations[4], summarizations[6], summarizations[7], summarizations[8],
             summarizations[9]], "Refuse offer")
        initial_super_variants = [initial_super_variants[0]] + IEVG.classify_initial_super_variants_by_activity(
            initial_super_variants[1], "Accept offer")
        hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy_by_classification(
            initial_super_variants, 1, 3, base=3)

        for hierarchy in hierarchies:
            SVH.explore_hierarchy_bottom_up(hierarchy)

    elif MODE == 2:
        initial_super_variants = IEVG.classify_initial_super_variants_by_activity(
            [
                summarizations[3],
                summarizations[4],
                summarizations[6],
                summarizations[7],
                summarizations[8],
                summarizations[9]],
            "Refuse offer")
        initial_super_variants = [initial_super_variants[0]] + IEVG.classify_initial_super_variants_by_activity(
            initial_super_variants[1], "Accept offer")
        hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy_by_classification(
            initial_super_variants,1, 3, base=2)

        SVH.explore_hierarchy_bottom_up(hierarchies[2])

    elif MODE == 3:
        initial_super_variants = IEVG.classify_initial_super_variants_by_activity(
            [
                summarizations[3],
                summarizations[4],
                summarizations[6],
                summarizations[7],
                summarizations[8],
                summarizations[9]],
            "Refuse offer")
        initial_super_variants = [initial_super_variants[0]] + IEVG.classify_initial_super_variants_by_activity(
            initial_super_variants[1], "Accept offer")
        hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy_by_classification(
            initial_super_variants, 1, 3, base=2)

        for super_variant in final_super_variants:
            SVH.explore_hierarchy_top_down(super_variant[0])

    elif MODE == 4:
        initial_set = [summarizations[i] for i in range(len(summarizations)) if i != 5]
        hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(
            initial_set, 4, frequency_distribution_type=IEVG.Distribution.NORMAL)

        for super_variant in final_super_variants[0]:
            SVH.explore_hierarchy_top_down(super_variant)

    elif MODE == 5:
        IEVG.NESTED_STRUCTURES = False
        initial_set = [summarizations[i] for i in range(len(summarizations)) if i not in [0, 2, 5]]
        hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(
            initial_set, 1, frequency_distribution_type=IEVG.Distribution.UNIFORM)

        for super_variant in final_super_variants[0]:
            SVH.explore_hierarchy_top_down(super_variant)

    elif MODE == 6:
        super_variant, cost = IEVS.join_super_variants(summarizations[0], summarizations[1], False, False)
        super_variant, cost = IEVS.join_super_variants(super_variant, summarizations[6], True, False)
        super_variant, cost = IEVS.join_super_variants(super_variant, summarizations[7], True, False)

        SVV.visualize_super_variant(super_variant, mode=SVV.Mode.ACTIVITY_FREQUENCY)

    elif MODE == 7:
        super_variant1, cost = IEVS.join_super_variants(summarizations[6], summarizations[7], False, False)
        super_variant2, cost = IEVS.join_super_variants(summarizations[9], summarizations[8], False, False)
        super_variant, cost = IEVS.join_super_variants(super_variant1, super_variant2, False, False)

        SVV.visualize_super_variant(super_variant, mode=SVV.Mode.LANE_FREQUENCY)

    elif MODE == 8:
        super_variant, cost = IEVS.join_super_variants(summarizations[9], summarizations[5], True, True)
        # super_variant, cost = IEVS.join_super_variants(super_variant, summarizations[7], True, False)

        SVV.visualize_super_variant(super_variant, mode=SVV.Mode.NO_FREQUENCY)

if BRANCH == "eval":
    all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_process(
        ocel)
    summarizations = SS.intra_variant_summarization_selection(all_summarizations, per_variant_dict, per_encoding_dict)

    initial_super_variants = summarizations[:10]
    IEVG.NESTED_STRUCTURES = False

    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(
        initial_super_variants, 3, frequency_distribution_type=IEVG.Distribution.NORMAL)

    final_super_variants = final_super_variants[0]
    for final_super_variant in final_super_variants:
        SVH.explore_hierarchy_top_down(final_super_variant)

if BRANCH == "eval":
    variant_layout = variants_visualization_factory.apply(ocel)
    for i in range(len(ocel.variants)):
        extracted_variant = IED.extract_lanes(variant_layout[ocel.variants[i]], ocel.variant_frequencies[i])
        # SVV.visualize_variant(extracted_variant,i)

    all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_process(
        ocel)

if BRANCH == "publ":
    variant_layout = variants_visualization_factory.apply(ocel)
    for i in range(len(ocel.variants)):
        extracted_variant = IED.extract_lanes(variant_layout[ocel.variants[i]], ocel.variant_frequencies[i])
        SVV.visualize_variant(extracted_variant, i)

    all_summarizations, per_variant_dict, per_encoding_dict = IAVG.complete_intra_variant_summarization_from_variants(
        ocel, list(zip(ocel.variants[:4], ocel.variant_frequencies[:4])))
    summarizations = SS.intra_variant_summarization_selection(
        all_summarizations, per_variant_dict, per_encoding_dict)

    SVV.visualize_super_variant(all_summarizations[0][1][1][0].to_super_variant(tuple() + (0,)))
    SVV.visualize_super_variant(all_summarizations[1][1][1][0].to_super_variant(tuple() + (1,)))
    SVV.visualize_super_variant(all_summarizations[2][1][1][0].to_super_variant(tuple() + (1,)))
    SVV.visualize_super_variant(all_summarizations[3][1][1][0].to_super_variant(tuple() + (1,)))

    super_variant_1, cost = IEVS.join_super_variants(
        all_summarizations[0][1][1][0].to_super_variant(tuple() + (0,)),
        all_summarizations[1][1][1][0].to_super_variant(tuple() + (1,)),
        False, False)
    super_variant_2, cost = IEVS.join_super_variants(
        all_summarizations[2][1][1][0].to_super_variant(tuple() + (0,)),
        super_variant_1,False, False)

    SVV.visualize_super_variant(super_variant_1, mode=SVV.Mode.NO_FREQUENCY)
    SVV.visualize_super_variant(super_variant_2, mode=SVV.Mode.NO_FREQUENCY)
