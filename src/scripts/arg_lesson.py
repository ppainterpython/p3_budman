#!/usr/bin/env python3
# coding=utf-8
"""Try something. """

import cmd2
import p3_mvvm as p3m
import budman_command_processor.budman_cp_namespace as cp
import budman_namespace.design_language_namespace as bdm
import argparse

valid_purpose_choices = ["input", "working", "output"]
valid_workflows = ["intake", "categorization", "budget"]

workflow_parser = cmd2.Cmd2ArgumentParser()

subparsers = workflow_parser.add_subparsers()
workflow_cmd_defaults = {
    p3m.CK_CMD_KEY: cp.CV_WORKFLOW_CMD_KEY,   # new way
    p3m.CK_CMD_NAME: cp.CV_WORKFLOW_CMD_NAME,
}
workflow_parser.set_defaults(**workflow_cmd_defaults)
# workflow transfer subcommand
transfer_parser = subparsers.add_parser(
    cp.CV_TRANSFER_SUBCMD_NAME,
    aliases=["tr"], 
    help="Apply Transfer workflow tasks.")
transfer_parser.set_defaults(
    # cmd_key=cp.CV_WORKFLOW_CMD_KEY,   # new way
    # cmd_name=cp.CV_WORKFLOW_CMD_NAME, 
    subcmd_name=cp.CV_TRANSFER_SUBCMD_NAME,
    subcmd_key=cp.CV_WORKFLOW_TRANSFER_SUBCMD_KEY)
transfer_parser.add_argument(
    # src_file_index
    cp.CK_FILE_LIST, nargs='*',
    type=int, default=[], 
    help=("Index of source file."))
transfer_parser.add_argument(
    # dst_wf_key
    f"--{cp.CK_WF_KEY}", "-w",
    choices=bdm.VALID_BDM_WORKFLOWS,
    help="Specify the destination workflow key.")
transfer_parser.add_argument(
    f"--{cp.CK_WF_PURPOSE}", "-p",
    choices=bdm.VALID_WF_PURPOSE_CHOICES,
    help="Specify the destination workflow purpose.")
transfer_parser.add_argument(
    f"--{cp.CK_WB_TYPE}", "-t",
    choices=bdm.VALID_WB_TYPE_VALUES,
    help="Specify the destination workbook type.")
if __name__ == "__main__":
    result = workflow_parser.parse_args(['transfer',
        '1', '2', '-w', 'intake', '-p', 'working', '-t', '.excel_txns'])
    print(result)
    exit(0)

