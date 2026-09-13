"""
Agent Event Cache — generated wire models (VENDORED, DO NOT EDIT BY HAND)
========================================================================

Verbatim copy of ``ninja_agent_event_cache_client/models.py``:

    package:  ninja-agent-event-cache-client
    version:  0.0.65
    source:   https://github.com/NinjaTech-AI/ninja-agent-slack-cache
              (client generated from the service's OpenAPI schema)

Why a copy and not the dependency
---------------------------------
The agent ships as a source zip: the pipeline zips src/ninja/, uploads it to
S3, and the EC2 host curls it, unzips, and runs
``pip install -r infra/requirements.txt`` against public PyPI
(scripts/ninja-install.sh). That host has no CodeArtifact access, so an
internal package cannot reach it — but anything inside src/ninja/ rides along
in the zip for free. Hence this file.

This is not a second source of truth. The generated package stays a CI
dependency (pyproject.toml, dev group), and
tests/unit/clients/test_agent_event_cache_models_drift.py compares this copy
against it name-for-name and field-for-field, so a service contract change that
is not copied here fails the build rather than reaching production.

Refreshing
----------
    poetry update ninja-agent-event-cache-client
    scripts/vendor_event_cache_models.sh

The only deviation from the generated source: ``StrEnum`` is folded into the
stdlib ``enum`` import (3.11+) instead of coming from
``ninja_common.compat``, which is not installable here either. This file is
force-excluded from black and skipped by isort in pyproject.toml so it stays
byte-comparable with the generated original.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum, StrEnum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, RootModel, conint, constr
from typing_extensions import Annotated


class AuthorizeRequest(BaseModel):
    channel_id: str = Field(..., title='Channel Id')
    user_id: str = Field(..., title='User Id')


class AuthorizeResponse(BaseModel):
    status: Optional[str] = Field('authorized', title='Status')
    channel_id: str = Field(..., title='Channel Id')
    workspace_id: str = Field(..., title='Workspace Id')
    user_id: str = Field(..., title='User Id')


class ChannelSummary(BaseModel):
    channel_id: str = Field(..., title='Channel Id')
    name: Optional[str] = Field(None, title='Name')
    workspace_id: Optional[str] = Field(None, title='Workspace Id')
    is_private: Optional[bool] = Field(False, title='Is Private')
    is_archived: Optional[bool] = Field(False, title='Is Archived')
    topic: Optional[str] = Field(None, title='Topic')
    purpose: Optional[str] = Field(None, title='Purpose')


class GetChannelInfoResponse(BaseModel):
    channel_id: str = Field(..., title='Channel Id')
    workspace_id: Optional[str] = Field(None, title='Workspace Id')
    name: Optional[str] = Field(None, title='Name')
    is_private: Optional[bool] = Field(False, title='Is Private')
    is_archived: Optional[bool] = Field(False, title='Is Archived')
    topic: Optional[str] = Field(None, title='Topic')
    purpose: Optional[str] = Field(None, title='Purpose')
    synced_at: Optional[str] = Field(None, title='Synced At')


class GetChannelsResponse(BaseModel):
    channels: List[ChannelSummary] = Field(..., title='Channels')
    total: int = Field(..., title='Total')


class GetMessagesRequest(BaseModel):
    workspace_id: str = Field(
        ..., description='Slack workspace/team ID (e.g. T123)', title='Workspace Id'
    )
    channel_id: str = Field(
        ..., description='Slack channel or DM ID (e.g. C123, D123)', title='Channel Id'
    )
    start_ts: Optional[float] = Field(
        None, description='Lower-bound Unix epoch timestamp (inclusive)', title='Start Ts'
    )
    end_ts: Optional[float] = Field(
        None, description='Upper-bound Unix epoch timestamp (inclusive)', title='End Ts'
    )
    limit: Optional[conint(ge=1, le=200)] = Field(
        50, description='Max messages per page (1–200)', title='Limit'
    )
    next_token: Optional[str] = Field(
        None, description='Pagination cursor from a previous response', title='Next Token'
    )
    thread_ts: Optional[str] = Field(
        None, description='Return only messages belonging to this thread', title='Thread Ts'
    )


class GetMessagesResponse(BaseModel):
    workspace_id: str = Field(..., title='Workspace Id')
    channel_id: str = Field(..., title='Channel Id')
    messages: List[Dict[str, Any]] = Field(..., title='Messages')
    total: int = Field(..., title='Total')
    next_token: Optional[str] = Field(None, title='Next Token')


class GetProviderTokenResponse(BaseModel):
    access_token: Optional[str] = Field(None, title='Access Token')
    expired: Optional[str] = Field(None, title='Expired')
    user_id: Optional[str] = Field(None, title='User Id')
    provider_id: Optional[str] = Field(None, title='Provider Id')
    scopes: Optional[List[str]] = Field(None, title='Scopes')
    email: Optional[str] = Field(None, title='Email')
    extra_field: Optional[Dict[str, str]] = Field(None, title='Extra Field')


class GetTeamsServiceUrlResponse(BaseModel):
    tenant_id: str = Field(..., title='Tenant Id')
    service_url: Optional[str] = Field(None, title='Service Url')


class GetWorkspaceResponse(BaseModel):
    workspace_id: str = Field(..., title='Workspace Id')
    name: Optional[str] = Field(None, title='Name')
    domain: Optional[str] = Field(None, title='Domain')


class HealthResponse(BaseModel):
    status: Optional[str] = Field('ok', title='Status')


class MemberInfo(BaseModel):
    user_id: str = Field(..., title='User Id')
    user_name: Optional[str] = Field(None, title='User Name')
    real_name: Optional[str] = Field(None, title='Real Name')
    is_bot: Optional[bool] = Field(None, title='Is Bot')
    is_deleted: Optional[bool] = Field(None, title='Is Deleted')


class MessageProvider(StrEnum):
    SLACK = 'slack'
    TEAMS = 'teams'


class MessageStateReport(BaseModel):
    message_id: str = Field(..., title='Message Id')
    thread_id: Optional[str] = Field(None, title='Thread Id')
    will_reply: bool = Field(..., title='Will Reply')


class PauseChannelRequest(BaseModel):
    channel_id: str = Field(..., title='Channel Id')
    user_id: str = Field(..., title='User Id')


class PauseResumeStatus(StrEnum):
    PAUSED = 'paused'
    RESUMED = 'resumed'
    NOT_FOUND = 'not_found'


class ReactRequest(BaseModel):
    provider: MessageProvider
    workspace_id: str = Field(
        ...,
        description='Slack team ID, or Microsoft Entra tenant ID for Teams',
        title='Workspace Id',
    )
    channel_id: str = Field(
        ..., description='Target channel or conversation ID', title='Channel Id'
    )
    message_id: str = Field(
        ..., description='Slack ts, or the Teams message ID', title='Message Id'
    )
    emoji: Optional[str] = Field('eyes', description='Emoji name or character', title='Emoji')
    parent_message_id: Optional[str] = Field(
        None,
        description='Parent message ID — required on Teams when reacting to a reply',
        title='Parent Message Id',
    )


class ReactResponse(BaseModel):
    ok: Optional[bool] = Field(True, title='Ok')
    message_id: str = Field(..., title='Message Id')


class ReportMessageStatesRequest(BaseModel):
    workspace_id: str = Field(..., title='Workspace Id')
    channel_id: str = Field(..., title='Channel Id')
    states: List[MessageStateReport] = Field(..., title='States')


class ReportMessageStatesResponse(BaseModel):
    updated: int = Field(..., title='Updated')
    deleted: int = Field(..., title='Deleted')
    not_found: int = Field(..., title='Not Found')


class ReportRepliedRequest(BaseModel):
    workspace_id: str = Field(..., title='Workspace Id')
    channel_id: str = Field(..., title='Channel Id')
    thread_id: Optional[str] = Field(None, title='Thread Id')
    reply_message_id: Optional[str] = Field(None, title='Reply Message Id')


class ReportRepliedResponse(BaseModel):
    deleted: int = Field(..., title='Deleted')


class SendMessageRequest(BaseModel):
    provider: MessageProvider
    workspace_id: str = Field(
        ...,
        description='Slack team ID, or Microsoft Entra tenant ID for Teams',
        title='Workspace Id',
    )
    channel_id: str = Field(
        ..., description='Target channel or conversation ID', title='Channel Id'
    )
    text: constr(min_length=1) = Field(..., description='Message body', title='Text')
    thread_id: Optional[str] = Field(
        None, description='Slack thread_ts, or the parent message ID on Teams', title='Thread Id'
    )
    agent: Optional[str] = Field(
        None, description='Agent whose display identity to post under', title='Agent'
    )
    username: Optional[str] = Field(
        None, description='Display name override (Slack)', title='Username'
    )
    icon_url: Optional[str] = Field(
        None, description='Avatar URL override (Slack)', title='Icon Url'
    )
    icon_emoji: Optional[str] = Field(
        None,
        description='Avatar emoji override in :name: form (Slack). Ignored when icon_url is set',
        title='Icon Emoji',
    )
    blocks: Optional[List[Dict[str, Any]]] = Field(
        None, description='Block Kit payload (Slack)', title='Blocks'
    )


class SendMessageResponse(BaseModel):
    ok: Optional[bool] = Field(True, title='Ok')
    message_id: str = Field(..., title='Message Id')
    thread_id: Optional[str] = Field(None, title='Thread Id')
    channel_id: str = Field(..., title='Channel Id')


class TeamsAuthorizeRequest(BaseModel):
    channel_id: str = Field(..., title='Channel Id')
    teams_id: str = Field(..., title='Teams Id')
    user_id: str = Field(..., title='User Id')


class TeamsAuthorizeResponse(BaseModel):
    status: Optional[str] = Field('authorized', title='Status')
    channel_id: str = Field(..., title='Channel Id')
    team_id: str = Field(..., title='Team Id')
    workspace_id: str = Field(..., title='Workspace Id')
    user_id: str = Field(..., title='User Id')


class TeamsPauseChannelRequest(BaseModel):
    channel_id: str = Field(..., title='Channel Id')
    teams_id: str = Field(..., title='Teams Id')
    user_id: str = Field(..., title='User Id')


class TeamsPauseChannelResponse(BaseModel):
    status: PauseResumeStatus
    channel_id: str = Field(..., title='Channel Id')
    team_id: str = Field(..., title='Team Id')
    user_id: str = Field(..., title='User Id')
    paused_at: Optional[datetime] = Field(None, title='Paused At')


class UploadResponse(BaseModel):
    ok: Optional[bool] = Field(True, title='Ok')
    message_id: Optional[str] = Field(None, title='Message Id')
    file_id: Optional[str] = Field(None, title='File Id')
    permalink: Optional[str] = Field(None, title='Permalink')
    channel_id: str = Field(..., title='Channel Id')


class ValidationError(BaseModel):
    loc: List[Union[str, int]] = Field(..., title='Location')
    msg: str = Field(..., title='Message')
    type: str = Field(..., title='Error Type')
    input: Optional[Any] = Field(None, title='Input')
    ctx: Optional[Dict[str, Any]] = Field(None, title='Context')


class WelcomeRequest(BaseModel):
    provider: MessageProvider
    workspace_id: str = Field(
        ...,
        description='Slack team ID, or Microsoft Entra tenant ID for Teams',
        title='Workspace Id',
    )
    channel_id: str = Field(
        ..., description='Target channel or conversation ID', title='Channel Id'
    )
    text: constr(min_length=1) = Field(
        ..., description='Fully rendered welcome message', title='Text'
    )
    signature: Optional[str] = Field(
        None,
        description="Accepted but not consulted. The 'has this channel been greeted' check runs on cached history instead; see POST /messages/welcome",
        title='Signature',
    )
    agent: Optional[str] = Field(
        None, description='Agent whose display identity to post under', title='Agent'
    )
    username: Optional[str] = Field(
        None, description='Display name override (Slack)', title='Username'
    )
    icon_url: Optional[str] = Field(
        None, description='Avatar URL override (Slack)', title='Icon Url'
    )
    icon_emoji: Optional[str] = Field(
        None,
        description='Avatar emoji override in :name: form (Slack). Ignored when icon_url is set',
        title='Icon Emoji',
    )


class WelcomeSkipReason(StrEnum):
    ALREADY_WELCOMED = 'already_welcomed'
    PRIOR_HUMAN_ACTIVITY = 'prior_human_activity'


class Authorization(RootModel[Optional[str]]):
    root: Optional[str] = Field(..., title='Authorization')


class GetTeamsServiceUrlQueryParams(BaseModel):
    channel_id: Optional[str] = Field(None, title='Channel Id')


class GetDbMessagesQueryParams(BaseModel):
    req: GetMessagesRequest
    channel_id: Optional[str] = Field(None, title='Channel Id')


class PostMessageStatesQueryParams(BaseModel):
    channel_id: Optional[str] = Field(None, title='Channel Id')


class PostMessageRepliedQueryParams(BaseModel):
    channel_id: Optional[str] = Field(None, title='Channel Id')


class GetDbChannelsQueryParams(BaseModel):
    channel_id: Optional[str] = Field(None, title='Channel Id')


class GetDbChannelInfoQueryParams(BaseModel):
    channel_id: str


class GetDbChannelMembersQueryParams(BaseModel):
    channel_id: str


class GetDbWorkspaceQueryParams(BaseModel):
    channel_id: str


class GetTokensQueryParams(BaseModel):
    provider_id: str
    email: Optional[str] = Field(None, description='Target email', title='Email')
    channel_id: Optional[str] = Field(None, title='Channel Id')


class SendMessageQueryParams(BaseModel):
    channel_id: Optional[str] = Field(None, title='Channel Id')


class SendWelcomeQueryParams(BaseModel):
    channel_id: Optional[str] = Field(None, title='Channel Id')


class ReactQueryParams(BaseModel):
    channel_id: Optional[str] = Field(None, title='Channel Id')


class UploadFormData(BaseModel):
    provider: MessageProvider
    workspace_id: str
    channel_id: str
    title: Optional[str] = Field(None, title='Title')
    comment: Optional[str] = Field(None, title='Comment')
    thread_id: Optional[str] = Field(None, title='Thread Id')
    username: Optional[str] = Field(None, title='Username')
    icon_url: Optional[str] = Field(None, title='Icon Url')
    icon_emoji: Optional[str] = Field(None, title='Icon Emoji')


class UploadQueryParams(BaseModel):
    channel_id: Optional[str] = Field(None, title='Channel Id')


class BodyUpload(BaseModel):
    file: str = Field(..., description='File bytes to share', title='File')
    provider: MessageProvider
    workspace_id: str = Field(..., title='Workspace Id')
    channel_id: str = Field(..., title='Channel Id')
    title: Optional[str] = Field(None, title='Title')
    comment: Optional[str] = Field(None, title='Comment')
    thread_id: Optional[str] = Field(None, title='Thread Id')
    username: Optional[str] = Field(None, title='Username')
    icon_url: Optional[str] = Field(None, title='Icon Url')
    icon_emoji: Optional[str] = Field(None, title='Icon Emoji')


class GetChannelMembersResponse(BaseModel):
    channel_id: str = Field(..., title='Channel Id')
    members: List[MemberInfo] = Field(..., title='Members')
    total: int = Field(..., title='Total')


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = Field(None, title='Detail')


class PauseChannelResponse(BaseModel):
    status: PauseResumeStatus
    channel_id: str = Field(..., title='Channel Id')
    user_id: str = Field(..., title='User Id')
    paused_at: Optional[datetime] = Field(None, title='Paused At')


class WelcomeResponse(BaseModel):
    ok: Optional[bool] = Field(True, title='Ok')
    posted: bool = Field(..., title='Posted')
    reason: Optional[WelcomeSkipReason] = None
    message_id: Optional[str] = Field(None, title='Message Id')
    channel_id: str = Field(..., title='Channel Id')


# Update all model forward refs
AuthorizeRequest.model_rebuild()
AuthorizeResponse.model_rebuild()
ChannelSummary.model_rebuild()
GetChannelInfoResponse.model_rebuild()
GetChannelsResponse.model_rebuild()
GetMessagesRequest.model_rebuild()
GetMessagesResponse.model_rebuild()
GetProviderTokenResponse.model_rebuild()
GetTeamsServiceUrlResponse.model_rebuild()
GetWorkspaceResponse.model_rebuild()
HealthResponse.model_rebuild()
MemberInfo.model_rebuild()
MessageStateReport.model_rebuild()
PauseChannelRequest.model_rebuild()
ReactRequest.model_rebuild()
ReactResponse.model_rebuild()
ReportMessageStatesRequest.model_rebuild()
ReportMessageStatesResponse.model_rebuild()
ReportRepliedRequest.model_rebuild()
ReportRepliedResponse.model_rebuild()
SendMessageRequest.model_rebuild()
SendMessageResponse.model_rebuild()
TeamsAuthorizeRequest.model_rebuild()
TeamsAuthorizeResponse.model_rebuild()
TeamsPauseChannelRequest.model_rebuild()
TeamsPauseChannelResponse.model_rebuild()
UploadResponse.model_rebuild()
ValidationError.model_rebuild()
WelcomeRequest.model_rebuild()
GetTeamsServiceUrlQueryParams.model_rebuild()
GetDbMessagesQueryParams.model_rebuild()
PostMessageStatesQueryParams.model_rebuild()
PostMessageRepliedQueryParams.model_rebuild()
GetDbChannelsQueryParams.model_rebuild()
GetDbChannelInfoQueryParams.model_rebuild()
GetDbChannelMembersQueryParams.model_rebuild()
GetDbWorkspaceQueryParams.model_rebuild()
GetTokensQueryParams.model_rebuild()
SendMessageQueryParams.model_rebuild()
SendWelcomeQueryParams.model_rebuild()
ReactQueryParams.model_rebuild()
UploadFormData.model_rebuild()
UploadQueryParams.model_rebuild()
BodyUpload.model_rebuild()
GetChannelMembersResponse.model_rebuild()
HTTPValidationError.model_rebuild()
PauseChannelResponse.model_rebuild()
WelcomeResponse.model_rebuild()
