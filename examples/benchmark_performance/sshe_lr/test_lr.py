#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import argparse

from fate_client.pipeline import FateFlowPipeline
from fate_client.pipeline.components.fate import Evaluation
from fate_client.pipeline.components.fate import SSHELR, PSI, Reader, FeatureScale
from fate_client.pipeline.utils import test_utils


def main(config="../../config.yaml", param="./lr_config.yaml", namespace=""):
    # obtain config
    if isinstance(config, str):
        config = test_utils.load_job_config(config)
    parties = config.parties
    guest = parties.guest[0]
    host = parties.host[0]
    arbiter = parties.arbiter[0]

    if isinstance(param, str):
        param = test_utils.JobConfig.load_from_file(param)

    assert isinstance(param, dict)

    guest_data_table = param.get("data_guest")
    host_data_table = param.get("data_host")

    guest_train_data = {"name": guest_data_table, "namespace": f"experiment{namespace}"}
    host_train_data = {"name": host_data_table, "namespace": f"experiment{namespace}"}
    pipeline = FateFlowPipeline().set_parties(guest=guest, host=host, arbiter=arbiter)
    if config.task_cores:
        pipeline.conf.set("task", dict(engine_run={"cores": config.task_cores}))
    if config.timeout:
        pipeline.conf.set("task", dict(timeout=config.timeout))

    reader_0 = Reader("reader_0", runtime_parties=dict(guest=guest, host=host))
    reader_0.guest.task_parameters(namespace=guest_train_data['namespace'], name=guest_train_data['name'])
    reader_0.hosts[0].task_parameters(namespace=host_train_data['namespace'], name=host_train_data['name'])
    psi_0 = PSI("psi_0", input_data=reader_0.outputs["output_data"])

    feature_scale_0 = FeatureScale("feature_scale_0",
                                   method="min_max",
                                   train_data=psi_0.outputs["output_data"])

    lr_param = {
    }

    config_param = {
        "epochs": param["epochs"],
        "learning_rate": param["learning_rate"],
        "batch_size": param["batch_size"],
        "early_stop": param["early_stop"],
        "init_param": param["init_param"],
        "tol": 1e-9
    }
    lr_param.update(config_param)
    lr_0 = SSHELR("lr_0",
                  train_data=feature_scale_0.outputs["train_output_data"],
                  **lr_param)
    lr_1 = SSHELR("lr_1",
                  test_data=feature_scale_0.outputs["train_output_data"],
                  input_model=lr_0.outputs["output_model"])

    evaluation_0 = Evaluation("evaluation_0",
                              runtime_parties=dict(guest=guest),
                              metrics=["auc", "binary_precision", "binary_accuracy", "binary_recall"],
                              input_datas=lr_0.outputs["train_output_data"])
    pipeline.add_tasks([reader_0, psi_0, feature_scale_0, lr_0, lr_1, evaluation_0])

    pipeline.compile()
    pipeline.fit()

    job_id = pipeline.model_info.job_id
    return job_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser("BENCHMARK-QUALITY PIPELINE JOB")
    parser.add_argument("-c", "--config", type=str,
                        help="config file", default="../../config.yaml")
    parser.add_argument("-p", "--param", type=str,
                        help="config file for params", default="./breast_config.yaml")
    args = parser.parse_args()
    main(args.config, args.param)
