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

from typing import TYPE_CHECKING, Any, List, Optional

from pydantic import Field
from typing_extensions import override

from distilabel.pipeline.utils import merge_columns
from distilabel.steps.base import Step, StepInput

if TYPE_CHECKING:
    from distilabel.steps.typing import StepOutput


class MergeColumns(Step):
    """Merge columns from a row.

    `MergeColumns` is a `Step` that implements the `process` method that calls the `merge_columns`
    function to handle and combine columns in a `StepInput`. `MergeColumns` provides two attributes
    `columns` and `output_column` to specify the columns to merge and the resulting output column.

    This step can be useful if you have a `Task` that generates instructions for example, and you
    want to have more examples of those. In such a case, you could for example use another `Task`
    to multiply your instructions synthetically, what would yield two different columns splitted.
    Using `MergeColumns` you can merge them and use them as a single column in your dataset for
    further processing.

    Attributes:
        columns: List of strings with the names of the columns to merge.
        output_column: str name of the output column

    Input columns:
        - dynamic (determined by `columns` attribute): The columns to merge.

    Output columns:
        - dynamic (determined by `columns` and `output_column` attributes): The columns
            that were merged.

    Examples:

        Combine columns in rows of a dataset:

        ```python
        from distilabel.steps import MergeColumns

        combiner = MergeColumns(
            columns=["queries", "multiple_queries"],
            output_column="queries",
        )
        combiner.load()

        result = next(
            combiner.process(
                [
                    {
                        "queries": "How are you?",
                        "multiple_queries": ["What's up?", "Everything ok?"]
                    }
                ],
            )
        )
        # >>> result
        # [{'queries': ['How are you?', "What's up?", 'Everything ok?']}]
        ```
    """

    columns: List[str]
    output_column: Optional[str] = None

    inputs: List[str] = Field(
        default_factory=list,
        description="The inputs for the task are the column names in 'columns'.",
    )
    outputs: List[str] = Field(
        default_factory=list,
        description="The outputs for the task are the column names in 'columns'.",
    )

    @override
    def model_post_init(self, __context: Any) -> None:
        """Override this method to perform additional initialization after `__init__` and `model_construct`.
        This is useful if you want to do some validation that requires the entire model to be initialized.
        """
        super().model_post_init(__context)

        self.inputs = self.columns
        self.outputs = [self.output_column] if self.output_column else ["merged_column"]

    @override
    def process(self, inputs: StepInput) -> "StepOutput":
        combined = []
        for input in inputs:
            combined.append(
                merge_columns(
                    input,
                    columns=self.columns,
                    new_column=self.outputs[0],
                )
            )
        yield combined
