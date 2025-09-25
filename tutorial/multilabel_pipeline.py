from typing import Union, Optional, Dict, List
import numpy as np
from transformers.pipelines import ArgumentHandler
from transformers import (
    Pipeline,
    PreTrainedTokenizer,
    ModelCard,
    PreTrainedModel,
    TFPreTrainedModel,
)
from transformers.pipelines.base import PIPELINE_INIT_ARGS
import torch


class MultiLabelPipeline(Pipeline):
    def __init__(
        self,
        model: Union[PreTrainedModel, TFPreTrainedModel],
        tokenizer: PreTrainedTokenizer,
        modelcard: Optional[ModelCard] = None,
        framework: Optional[str] = None,
        task: str = "",
        args_parser: ArgumentHandler = None,
        device: int = -1,
        binary_output: bool = False,
        threshold: float = 0.3,
    ):
        super().__init__(
            model=model,
            tokenizer=tokenizer,
            modelcard=modelcard,
            framework=framework,
            args_parser=args_parser,
            device=device,
            binary_output=binary_output,
            task=task,
        )
        self.threshold = threshold

    def _sanitize_parameters(self, **kwargs):
        """
        Sanitize and preprocess pipeline parameters.
        """
        # Allow overriding the threshold during inference
        if "threshold" in kwargs:
            self.threshold = kwargs["threshold"]
        return {}, {}, {}

    def preprocess(self, inputs, **kwargs) -> Dict[str, Union[List[str], torch.Tensor]]:
        """
        Preprocess the input text into tokenized inputs for the model.
        """
        # Tokenize the input text
        tokenized_inputs = self.tokenizer(
            inputs, return_tensors="pt", padding=True, truncation=True
        )
        return tokenized_inputs

    def _forward(self, inputs, **kwargs):
        """
        Run the model on the preprocessed inputs.
        """
        # Move inputs to the correct device (CPU/GPU)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        # Forward pass through the model
        outputs = self.model(**inputs)
        return outputs
    
    def postprocess(self, outputs, **kwargs) -> List[Dict[str, Union[List[str], List[float]]]]:
        """
        Postprocess the model outputs into a user-friendly format.
        """
        # Extract logits from the model outputs
        if isinstance(outputs, tuple):
            # Assume logits are the first element in the tuple
            logits = outputs[0]
        else:
            # If outputs is not a tuple, assume it has a `logits` attribute
            logits = outputs.logits
    
        # Apply sigmoid to convert logits to probabilities
        scores = 1 / (1 + np.exp(-logits.detach().cpu().numpy()))  # Sigmoid
    
        results = []
        for item in scores:
            labels = []
            label_scores = []
            for idx, s in enumerate(item):
                if s > self.threshold:
                    labels.append(self.model.config.id2label[idx])
                    label_scores.append(float(s))
            results.append({"labels": labels, "scores": label_scores})
        return results