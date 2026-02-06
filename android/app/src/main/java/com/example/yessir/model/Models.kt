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
