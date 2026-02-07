package com.example.yessir.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.example.yessir.media.AudioRecorder
import com.example.yessir.model.VoiceRepository
import com.example.yessir.model.CommandResponse
import kotlinx.coroutines.launch
import java.io.File
import java.util.TimeZone

// Sealed UI State moved to VoiceUiState.kt

class VoiceViewModel(application: Application) : AndroidViewModel(application) {

    private val _uiState = MutableLiveData<VoiceUiState>(VoiceUiState.Ready)
    val uiState: LiveData<VoiceUiState> = _uiState

    private val repository = VoiceRepository()
    private val audioRecorder = AudioRecorder(application)
    private var recordingFile: File? = null

    fun startRecording() {
        try {
            val cacheDir = getApplication<Application>().cacheDir
            recordingFile = File.createTempFile("voice_command", ".wav", cacheDir)
            audioRecorder.start(recordingFile!!)
            _uiState.value = VoiceUiState.Listening
        } catch (e: Exception) {
            _uiState.value = VoiceUiState.Error("Error starting recording", e.message)
        }
    }

    fun stopRecording() {
        try {
            audioRecorder.stop()
            processRecording()
        } catch (e: Exception) {
            _uiState.value = VoiceUiState.Error("Error stopping recording", e.message)
        }
    }

    private fun processRecording() {
        val file = recordingFile ?: return
        _uiState.value = VoiceUiState.Transcribing

        viewModelScope.launch {
            val result = repository.transcribeAudio(file)
            result.onSuccess { response ->
                val transcript = response.transcript
                processCommand(transcript)
            }.onFailure { e ->
                _uiState.value = VoiceUiState.Error("Transcription Failed", e.message)
            }
        }
    }

    fun processCommand(transcript: String) {
        _uiState.value = VoiceUiState.Processing

        viewModelScope.launch {
            val timezone = TimeZone.getDefault().id
            val result = repository.sendCommand(transcript, timezone)
            
            result.onSuccess { response ->
                if (response.error != null) {
                    _uiState.value = VoiceUiState.Error(response.error, response.details)
                } else {
                    _uiState.value = VoiceUiState.Success(
                        message = response.message,
                        type = response.type,
                        parsedData = response.parsedData,
                        data = response.data
                    )
                }
            }.onFailure { e ->
                 _uiState.value = VoiceUiState.Error("Command Failed", e.message)
            }
        }
    }
    
    fun reset() {
        _uiState.value = VoiceUiState.Ready
    }
}
