# Copyright 2023-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from distilabel.steps.tasks.image_generation import ImageGeneration
from tests.unit.conftest import DummyAsyncImageGenerationModel


class TestImageGeneration:
    def test_format_input(self) -> None:
        igm = DummyAsyncImageGenerationModel()
        task = ImageGeneration(image_generation_model=igm)
        task.load()

        assert (
            task.format_input({"prompt": "a white siamese cat"})
            == "a white siamese cat"
        )

    @pytest.mark.parametrize("save_artifacts", [False])
    def test_process(self, save_artifacts: bool) -> None:
        igm = DummyAsyncImageGenerationModel()
        task = ImageGeneration(
            image_generation_model=igm, save_artifacts=save_artifacts
        )
        task.load()
        img_str = "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"

        assert next(task.process([{"prompt": "a white siamese cat"}])) == [
            {
                "prompt": "a white siamese cat",
                "image": img_str,
                "model_name": "test",
                "distilabel_metadata": {
                    "raw_input_image_generation_0": "a white siamese cat",
                    "raw_output_image_generation_0": {
                        "images": [
                            "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"
                        ]
                    },
                },
            }
        ]
