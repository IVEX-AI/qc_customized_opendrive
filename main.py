import argparse
import logging

from lxml import etree

from qc_baselib import Configuration, Result, IssueSeverity, StatusType
from qc_opendrive.base import utils, models

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

BUNDLE_NAME = "ivexCustomXODRBundle"
BUNDLE_VERSION = "0.1.0"

ELEMENTS_CHECKER_ID = "elements_xodr"


def _check_if_roads_exists(checker_data: models.CheckerData) -> None:
    rule_uid = checker_data.result.register_rule(
        checker_bundle_name=BUNDLE_NAME,
        checker_id=ELEMENTS_CHECKER_ID,
        emanating_entity="asam.net",
        standard="xodr",
        definition_setting="1.4.0",
        rule_full_name="road.geometry.param_poly3.length_match",
    )

    road_id_map = utils.get_road_id_map(checker_data.input_file_xml_root)

    if len(road_id_map) == 0:
        # This mean no road was parsed from the OpenDrive file
        checker_data.result.register_issue(
            checker_bundle_name=BUNDLE_NAME,
            checker_id=ELEMENTS_CHECKER_ID,
            description=f"No roads found.",
            level=IssueSeverity.ERROR,
            rule_uid=rule_uid,
        )


def run_element_checks(config: Configuration, result: Result) -> None:
    logging.info("Executing element checks")

    root = etree.parse(config.get_config_param("XodrFile"))

    result.register_checker(
        checker_bundle_name=BUNDLE_NAME,
        checker_id=ELEMENTS_CHECKER_ID,
        description="Evaluates elements in the file and their existence.",
        summary="",
    )

    odr_schema_version = utils.get_standard_schema_version(root)

    checker_data = models.CheckerData(
        input_file_xml_root=root,
        config=config,
        result=result,
        schema_version=odr_schema_version,
    )

    rule_list = [_check_if_roads_exists]

    for rule in rule_list:
        rule(checker_data=checker_data)

    result.set_checker_status(
        checker_bundle_name=BUNDLE_NAME,
        checker_id=ELEMENTS_CHECKER_ID,
        status=StatusType.COMPLETED,
    )


def args_entrypoint() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="IVEX Custom - QC OpenDrive Checker",
        description="This is a collection of scripts for checking validity of OpenDrive (.xodr) files.",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--config_path")

    return parser.parse_args()


def main():
    args = args_entrypoint()

    logging.info("Initializing checks")

    config = Configuration()
    config.load_from_file(xml_file_path=args.config_path)

    result = Result()
    result.register_checker_bundle(
        name=BUNDLE_NAME,
        build_date="2024-07-25",
        description="IVEX Custom OpenDrive checker bundle",
        version=BUNDLE_VERSION,
        summary="",
    )
    result.set_result_version(version=BUNDLE_VERSION)

    run_element_checks(config=config, result=result)

    result.write_to_file(
        config.get_checker_bundle_param(
            checker_bundle_name=BUNDLE_NAME, param_name="resultFile"
        )
    )

    logging.info("Done")


if __name__ == "__main__":
    main()
