"""
Amazon Bedrock Client — Wrapper for:
  • Amazon Nova 2 Lite  (Converse API  — threat analysis)
  • Bedrock Agent       (Agent Runtime — Nova Act / Nova Forge decisions)
"""

import asyncio
import json
import logging
import uuid
from typing import Any

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _make_session(settings) -> boto3.Session:
    kwargs: dict[str, Any] = {"region_name": settings.AWS_REGION}
    if settings.AWS_ACCESS_KEY_ID:
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    return boto3.Session(**kwargs)


class BedrockClient:
    """
    Singleton that keeps two boto3 clients:
      self.client       — bedrock-runtime   (Converse API for Nova 2 Lite)
      self.agent_client — bedrock-agent-runtime (invoke_agent for agent alias)
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        settings = get_settings()
        retry_config = BotoConfig(
            region_name=settings.AWS_REGION,
            retries={"max_attempts": 3, "mode": "adaptive"},
        )
        session = _make_session(settings)
        self.client = session.client("bedrock-runtime", config=retry_config)
        self.agent_client = session.client("bedrock-agent-runtime", config=retry_config)
        self._initialized = True
        logger.info("Bedrock clients initialised (region=%s)", settings.AWS_REGION)

    # ── Nova 2 Lite — Converse API ──────────────────────────────────────────

    async def invoke_nova_lite(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 2048,
    ) -> str:
        """Invoke Amazon Nova 2 Lite for threat analysis (Converse API)."""
        settings = get_settings()
        return await self._converse(
            model_id=settings.NOVA_LITE_MODEL_ID,
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
        )

    async def _converse(
        self,
        model_id: str,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 2048,
    ) -> str:
        """Generic Bedrock Converse API call (wraps sync boto3 in executor)."""
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        inference_config = {"maxTokens": max_tokens, "temperature": 0.2, "topP": 0.9}
        kwargs: dict[str, Any] = {
            "modelId": model_id,
            "messages": messages,
            "inferenceConfig": inference_config,
        }
        if system_prompt:
            kwargs["system"] = [{"text": system_prompt}]

        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None, lambda: self.client.converse(**kwargs)
            )
            content = response.get("output", {}).get("message", {}).get("content", [])
            return content[0].get("text", "") if content else ""
        except ClientError as e:
            logger.error("Bedrock Converse error (%s): %s", model_id, e)
            raise
        except Exception as e:
            logger.error("Unexpected Converse error (%s): %s", model_id, e)
            raise

    # ── Bedrock Agent Runtime — Nova Act / Nova Forge ───────────────────────

    async def invoke_nova_agent(
        self,
        prompt: str,
        session_id: str | None = None,
    ) -> str:
        """
        Invoke the Bedrock Agent (Nova Act / Nova Forge) using invoke_agent.

        Requires NOVA_AGENT_ID to be set in config. Falls back to Nova 2 Lite
        Converse API when the agent ID is not configured so the demo still runs
        without a full agent setup.
        """
        settings = get_settings()

        if not settings.NOVA_AGENT_ID:
            # Graceful fallback: use Nova 2 Lite via Converse for response logic
            logger.warning(
                "NOVA_AGENT_ID not set — falling back to Nova 2 Lite for agent response"
            )
            return await self.invoke_nova_lite(prompt)

        sid = session_id or str(uuid.uuid4())

        loop = asyncio.get_event_loop()
        try:
            raw_response = await loop.run_in_executor(
                None,
                lambda: self.agent_client.invoke_agent(
                    agentId=settings.NOVA_AGENT_ID,
                    agentAliasId=settings.NOVA_AGENT_ALIAS_ID,
                    sessionId=sid,
                    inputText=prompt,
                ),
            )
            # The response body is a streaming EventStream — collect all chunks
            completion = ""
            for event in raw_response.get("completion", []):
                chunk = event.get("chunk", {})
                if chunk:
                    raw_bytes = chunk.get("bytes", b"")
                    if isinstance(raw_bytes, (bytes, bytearray)):
                        completion += raw_bytes.decode("utf-8")
                    else:
                        completion += str(raw_bytes)
            logger.info(
                "Bedrock Agent (%s/%s) responded (%d chars)",
                settings.NOVA_AGENT_ID,
                settings.NOVA_AGENT_ALIAS_ID,
                len(completion),
            )
            return completion

        except ClientError as e:
            logger.error("Bedrock Agent error: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected Agent error: %s", e)
            raise


def get_bedrock_client() -> BedrockClient:
    return BedrockClient()

