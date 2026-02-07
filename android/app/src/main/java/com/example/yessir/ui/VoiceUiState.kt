package com.example.yessir.ui

sealed class VoiceUiState {
    object Ready : VoiceUiState()
    object Listening : VoiceUiState()
    object Transcribing : VoiceUiState()
    object Processing : VoiceUiState()
    data class Success(
        val message: String,
        val type: String?,
        val parsedData: Map<String, Any>?,
        val data: Map<String, Any>?
    ) : VoiceUiState()

    data class Error(val message: String, val details: String? = null) : VoiceUiState()
}
