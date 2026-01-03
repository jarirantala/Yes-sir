package com.example.voicecal.model

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
