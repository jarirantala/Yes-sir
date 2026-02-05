package com.example.yessir.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.example.yessir.media.AudioRecorder
import com.example.yessir.model.VoiceRepository
import kotlinx.coroutines.launch
import java.io.File
import java.util.TimeZone

class VoiceViewModel(application: Application) : AndroidViewModel(application) {

    private val _uiState = MutableLiveData<String>("Ready")
    val uiState: LiveData<String> = _uiState

    private val repository = VoiceRepository()
    private val audioRecorder = AudioRecorder(application)
    private var recordingFile: File? = null

    fun startRecording() {
        try {
            val cacheDir = getApplication<Application>().cacheDir
            recordingFile = File.createTempFile("voice_command", ".m4a", cacheDir)
            audioRecorder.start(recordingFile!!)
            _uiState.value = "Listening..."
        } catch (e: Exception) {
            _uiState.value = "Error starting recording: ${e.message}"
        }
    }

    fun stopRecording() {
        try {
            audioRecorder.stop()
            processRecording()
        } catch (e: Exception) {
            _uiState.value = "Error stopping recording: ${e.message}"
        }
    }

    private fun processRecording() {
        val file = recordingFile ?: return
        _uiState.value = "Transcribing..."

        viewModelScope.launch {
            val result = repository.transcribeAudio(file)
            result.onSuccess { response ->
                val transcript = response.transcript
                _uiState.value = "Transcript: $transcript"
                // Auto-confirm for now, or we could wait for user input
                processCommand(transcript)
            }.onFailure { e ->
                _uiState.value = "Transcription Failed: ${e.message}"
            }
        }
    }

    fun processCommand(transcript: String) {
        _uiState.value = "Executing: $transcript"

        viewModelScope.launch {
            val timezone = TimeZone.getDefault().id
            val result = repository.sendCommand(transcript, timezone)
            
            result.onSuccess { response ->
                _uiState.value = "Success: ${response.message}"
            }.onFailure { e ->
                _uiState.value = "Command Failed: ${e.message}"
            }
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        // Ensure recorder is cleaned up
        // audioRecorder.release() // if we had a release method
    }
}
