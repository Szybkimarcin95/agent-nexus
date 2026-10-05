"""Deterministic local model for SDK integration tests; never an API test."""
from agents import Model, ModelResponse, Usage
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputText

class RestartProbeModel(Model):
    async def get_response(self, system_instructions, input, model_settings, tools,
                           output_schema, handoffs, tracing, **kwargs):
        outputs = [x for x in input if isinstance(x, dict)
                   and x.get("type") == "function_call_output"] if isinstance(input, list) else []
        if outputs:
            text = str(outputs[-1]["output"])
            output = [ResponseOutputMessage(id="msg_probe", role="assistant",
                status="completed", type="message",
                content=[ResponseOutputText(type="output_text", text=text, annotations=[])])]
        else:
            output = [ResponseFunctionToolCall(id="fc_probe", type="function_call",
                name="publish_report", call_id="call_restart_probe",
                arguments='{"report":"restart-proof"}')]
        return ModelResponse(output=output, usage=Usage(), response_id=None)

    async def stream_response(self, *args, **kwargs):
        raise NotImplementedError("non-streaming test model")
        yield
