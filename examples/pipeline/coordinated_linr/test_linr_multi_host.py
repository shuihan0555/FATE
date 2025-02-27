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
from fate_client.pipeline.components.fate import CoordinatedLinR, PSI, Reader
from fate_client.pipeline.components.fate import Evaluation
from fate_client.pipeline.utils import test_utils


def main(config="../config.yaml", namespace=""):
    if isinstance(config, str):
        config = test_utils.load_job_config(config)
    parties = config.parties
    guest = parties.guest[0]
    host = parties.host
    arbiter = parties.arbiter[0]

    pipeline = FateFlowPipeline().set_parties(guest=guest, host=host, arbiter=arbiter)

    reader_0 = Reader("reader_0", runtime_parties=dict(guest=guest, host=host))
    reader_0.guest.task_parameters(namespace=f"experiment{namespace}", name="motor_hetero_guest")
    reader_0.hosts[[0, 1]].task_parameters(namespace=f"experiment{namespace}", name="motor_hetero_host")
    psi_0 = PSI("psi_0", input_data=reader_0.outputs["output_data"])
    linr_0 = CoordinatedLinR("linr_0",
                             epochs=5,
                             batch_size=None,
                             early_stop="weight_diff",
                             optimizer={"method": "SGD", "optimizer_params": {"lr": 0.1},
                                        "alpha": 0.001},
                             init_param={"fit_intercept": True, "method": "random_uniform"},
                             train_data=psi_0.outputs["output_data"],
                             learning_rate_scheduler={"method": "constant", "scheduler_params": {"factor": 1.0,
                                                                                                 "total_iters": 100}})

    evaluation_0 = Evaluation("evaluation_0",
                              runtime_parties=dict(guest=guest),
                              default_eval_setting="regression",
                              input_datas=linr_0.outputs["train_output_data"])

    pipeline.add_tasks([reader_0, psi_0, linr_0, evaluation_0])

    pipeline.compile()
    # print(pipeline.get_dag())
    pipeline.fit()

    pipeline.deploy([psi_0, linr_0])

    predict_pipeline = FateFlowPipeline()

    reader_1 = Reader("reader_0", runtime_parties=dict(guest=guest, host=host))
    reader_1.guest.task_parameters(namespace=f"experiment{namespace}", name="motor_hetero_guest")
    reader_1.hosts[[0, 1]].task_parameters(namespace=f"experiment{namespace}", name="motor_hetero_host")

    deployed_pipeline = pipeline.get_deployed_pipeline()
    deployed_pipeline.psi_0.input_data = reader_1.outputs["output_data"]

    predict_pipeline.add_tasks([reader_1, deployed_pipeline])
    predict_pipeline.compile()
    # print("\n\n\n")
    # print(predict_pipeline.compile().get_dag())
    predict_pipeline.predict()
    # print(f"predict linr_0 data: {pipeline.get_task_info('linr_0').get_output_data()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("PIPELINE DEMO")
    parser.add_argument("--config", type=str, default="../config.yaml",
                        help="config file")
    parser.add_argument("--namespace", type=str, default="",
                        help="namespace for data stored in FATE")
    args = parser.parse_args()
    main(config=args.config, namespace=args.namespace)
