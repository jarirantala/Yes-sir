package com.example.yessir.model

data class MeetingRequest(
    val transcript: String,
    val timezone: String,
    val email: String? = null
)

data class MeetingResponse(
    val message: String?,
    val error: String?,
    val messageId: String?
)

data class AudioUploadRequest(
    val audio_base64: String,
    val content_type: String
)

data class DeleteRequest(
    val id: String,
    val type: String
)

data class DeleteResponse(
    val success: Boolean,
    val message: String
)

data class ListResponse(
    val status: String,
    val type: String,
    val data: List<HistoryItem>
)

data class HistoryItem(
    val id: String,
    val text: String? = null,
    val title: String? = null,
    val priority: String? = null,
    val created_at: String? = null,
    val status: String? = null
)
