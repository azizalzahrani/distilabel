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

import hashlib
from typing import TYPE_CHECKING, List

from pydantic import Field

from distilabel.steps.base import Step, StepInput

if TYPE_CHECKING:
    from distilabel.steps.typing import StepOutput


class _FormatAnyGenerationSFT(Step):
    outputs: List[str] = Field(default=["prompt", "prompt_id", "messages"], frozen=True)


class FormatTextGenerationSFT(_FormatAnyGenerationSFT):
    """Format the output of a `TextGeneration` task for Supervised Fine-Tuning (SFT).

    `FormatTextGenerationSFT` is a `Step` that formats the output of a `TextGeneration` task for
    Supervised Fine-Tuning (SFT) following the standard formatting from frameworks such as `axolotl`
    or `alignment-handbook`. The output of the `TextGeneration` task is formatted into a chat-like
    conversation with the `instruction` as the user message and the `generation` as the assistant
    message. Optionally, if the `system_prompt` is available, it is included as the first message
    in the conversation.

    Input columns:
        - system_prompt (`str`, optional): The system prompt used within the `LLM` to generate the
            `generation`, if available.
        - instruction (`str`): The instruction used to generate the `generation` with the `LLM`.
        - generation (`str`): The generation produced by the `LLM`.

    Output columns:
        - prompt (`str`): The instruction used to generate the `generation` with the `LLM`.
        - prompt_id (`str`): The `SHA256` hash of the `prompt`.
        - messages (`List[Dict[str, str]]`): The chat-like conversation with the `instruction` as
            the user message and the `generation` as the assistant message.

    Categories:
        - format
        - text-generation
        - instruction
        - generation

    Examples:

        Format your dataset for SFT fine tuning:

        ```python
        from distilabel.steps import FormatTextGenerationSFT

        format_sft = FormatTextGenerationSFT()
        format_sft.load()

        # NOTE: "system_prompt" can be added optionally.
        result = next(
            format_sft.process(
                [
                    {
                        "instruction": "What's 2+2?",
                        "generation": "4"
                    }
                ]
            )
        )
        # >>> result
        # [
        #     {
        #         'instruction': 'What's 2+2?',
        #         'generation': '4',
        #         'prompt': 'What's 2+2?',
        #         'prompt_id': '7762ecf17ad41479767061a8f4a7bfa3b63d371672af5180872f9b82b4cd4e29',
        #         'messages': [{'role': 'user', 'content': "What's 2+2?"}, {'role': 'assistant', 'content': '4'}]
        #     }
        # ]
        ```
    """

    inputs: List[str] = Field(
        default=["instruction", "generation"],
        frozen=True,
        description=(
            "The inputs for the step are the 'instruction' and 'generation'. "
            + "Optionally, one could also provide the 'system_prompt' for the generations."
        ),
    )

    def process(self, *inputs: StepInput) -> "StepOutput":  # type: ignore
        """The `process` method formats the received `StepInput` or list of `StepInput`
        according to the SFT formatting standard.

        Args:
            *inputs: A list of `StepInput` to be combined.

        Yields:
            A `StepOutput` with batches of formatted `StepInput` following the SFT standard.
        """
        for input in inputs:
            for item in input:
                item["prompt"] = item["instruction"]

                item["prompt_id"] = hashlib.sha256(
                    item["prompt"].encode("utf-8")  # type: ignore
                ).hexdigest()

                item["messages"] = [
                    {"role": "user", "content": item["instruction"]},  # type: ignore
                    {"role": "assistant", "content": item["generation"]},  # type: ignore
                ]
                if (
                    "system_prompt" in item
                    and isinstance(item["system_prompt"], str)  # type: ignore
                    and len(item["system_prompt"]) > 0  # type: ignore
                ):
                    item["messages"].insert(
                        0,
                        {"role": "system", "content": item["system_prompt"]},  # type: ignore
                    )

            yield input


class FormatChatGenerationSFT(_FormatAnyGenerationSFT):
    """Format the output of a `ChatGeneration` task for Supervised Fine-Tuning (SFT) following the
    standard formatting from frameworks such as `axolotl` or `alignment-handbook`.

    `FormatChatGenerationSFT` is a `Step` that formats the output of a `ChatGeneration` task for
    Supervised Fine-Tuning (SFT) following the standard formatting from frameworks such as `axolotl`
    or `alignment-handbook`. The output of the `ChatGeneration` task is formatted into a chat-like
    conversation with the `instruction` as the user message and the `generation` as the assistant
    message. Optionally, if the `system_prompt` is available, it is included as the first message
    in the conversation.

    Input columns:
        - instruction (`str`): The instruction used to generate the `generation` with the `LLM`.
        - generation (`str`): The generation produced by the `LLM`.

    Output columns:
        - prompt (`str`): The instruction used to generate the `generation` with the `LLM`.
        - prompt_id (`str`): The `SHA256` hash of the `prompt`.
        - messages (`List[Dict[str, str]]`): The chat-like conversation with the `instruction` as
            the user message and the `generation` as the assistant message.

    Categories:
        - format
        - chat-generation
        - instruction
        - generation

    Examples:

        Format your dataset for Supervised Fine Tuning (SFT):

        ```python
        from distilabel.steps import FormatChatGenerationSFT

        format_sft = FormatChatGenerationSFT()
        format_sft.load()

        result = next(
            format_sft.process(
                [
                    {
                        "messages": [{"role": "user", "content": "What's 2+2?"}],
                        "generation": "4"
                    }
                ]
            )
        )
        # >>> result
        # [
        #     {
        #         'messages': [{'role': 'user', 'content': "What's 2+2?"}, {'role': 'assistant', 'content': '4'}],
        #         'generation': '4',
        #         'prompt': 'What's 2+2?',
        #         'prompt_id': '7762ecf17ad41479767061a8f4a7bfa3b63d371672af5180872f9b82b4cd4e29',
        #     }
        # ]
        ```
    """

    inputs: List[str] = Field(
        default=["messages", "generation"],
        frozen=True,
        description=("The inputs for the step are the 'messages' and 'generation'."),
    )

    def process(self, *inputs: StepInput) -> "StepOutput":  # type: ignore
        """The `process` method formats the received `StepInput` or list of `StepInput`
        according to the SFT formatting standard.

        Args:
            *inputs: A list of `StepInput` to be combined.

        Yields:
            A `StepOutput` with batches of formatted `StepInput` following the SFT standard.
        """
        for input in inputs:
            for item in input:
                item["prompt"] = next(
                    (
                        turn["content"]
                        for turn in item["messages"]
                        if turn["role"] == "user"
                    ),
                    None,
                )

                item["prompt_id"] = hashlib.sha256(
                    item["prompt"].encode("utf-8")  # type: ignore
                ).hexdigest()

                item["messages"] = item["messages"] + [
                    {"role": "assistant", "content": item["generation"]},  # type: ignore
                ]
            yield input
