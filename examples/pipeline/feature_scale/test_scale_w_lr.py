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
import argparse

from fate_client.pipeline import FateFlowPipeline
from fate_client.pipeline.components.fate import CoordinatedLR, PSI, FeatureScale, Evaluation, Reader
from fate_client.pipeline.utils import test_utils


def main(config="../config.yaml", namespace=""):
    if isinstance(config, str):
        config = test_utils.load_job_config(config)
    parties = config.parties
    guest = parties.guest[0]
    host = parties.host[0]
    arbiter = parties.arbiter[0]

    pipeline = FateFlowPipeline().set_parties(guest=guest, host=host, arbiter=arbiter)
    if config.task_cores:
        pipeline.conf.set("task_cores", config.task_cores)
    if config.timeout:
        pipeline.conf.set("timeout", config.timeout)

    reader_0 = Reader("reader_0", runtime_parties=dict(guest=guest, host=host))
    reader_0.guest.task_parameters(
        namespace=f"experiment{namespace}",
        name="breast_hetero_guest"
    )
    reader_0.hosts[0].task_parameters(
        namespace=f"experiment{namespace}",
        name="breast_hetero_host"
    )

    reader_1 = Reader("reader_1", runtime_parties=dict(guest=guest, host=host))
    reader_1.guest.task_parameters(
        namespace=f"experiment{namespace}",
        name="breast_hetero_guest"
    )
    reader_1.hosts[0].task_parameters(
        namespace=f"experiment{namespace}",
        name="breast_hetero_host"
    )

    psi_0 = PSI("psi_0", input_data=reader_0.outputs["output_data"])
    psi_1 = PSI("psi_1", input_data=reader_0.outputs["output_data"])

    feature_scale_0 = FeatureScale("feature_scale_0",
                                   method="standard",
                                   train_data=psi_0.outputs["output_data"])

    lr_0 = CoordinatedLR("lr_0",
                         epochs=10,
                         batch_size=None,
                         optimizer={"method": "SGD", "optimizer_params": {"lr": 0.21}},
                         init_param={"fit_intercept": True, "method": "random_uniform"},
                         train_data=feature_scale_0.outputs["train_output_data"],
                         learning_rate_scheduler={"method": "linear", "scheduler_params": {"start_factor": 0.7,
                                                                                           "total_iters": 100}})

    evaluation_0 = Evaluation("evaluation_0",
                              runtime_parties=dict(guest=guest),
                              default_eval_setting="binary",
                              input_datas=lr_0.outputs["train_output_data"])

    pipeline.add_tasks([reader_0, reader_1, psi_0, psi_1, feature_scale_0, lr_0, evaluation_0])

    # pipeline.add_task(hetero_feature_binning_0)
    pipeline.compile()
    print(pipeline.get_dag())
    pipeline.fit()

    pipeline.deploy([psi_0, feature_scale_0, lr_0])

    predict_pipeline = FateFlowPipeline()

    reader_2 = Reader("reader_2", runtime_parties=dict(guest=guest, host=host))
    reader_2.guest.task_parameters(
        namespace=f"experiment{namespace}",
        name="breast_hetero_guest"
    )
    reader_2.hosts[0].task_parameters(
        namespace=f"experiment{namespace}",
        name="breast_hetero_host"
    )

    deployed_pipeline = pipeline.get_deployed_pipeline()
    deployed_pipeline.psi_0.input_data = reader_2.outputs["output_data"]

    predict_pipeline.add_tasks([reader_2, deployed_pipeline])

    predict_pipeline.compile()
    # print("\n\n\n")
    # print(predict_pipeline.compile().get_dag())
    predict_pipeline.predict()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("PIPELINE DEMO")
    parser.add_argument("--config", type=str, default="../config.yaml",
                        help="config file")
    parser.add_argument("--namespace", type=str, default="",
                        help="namespace for data stored in FATE")
    args = parser.parse_args()
    main(config=args.config, namespace=args.namespace)
