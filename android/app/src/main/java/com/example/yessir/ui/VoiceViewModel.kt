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

    private val _todoItems = kotlinx.coroutines.flow.MutableStateFlow<List<com.example.yessir.model.HistoryItem>>(emptyList())
    val todoItems: kotlinx.coroutines.flow.StateFlow<List<com.example.yessir.model.HistoryItem>> = _todoItems

    private val _noteItems = kotlinx.coroutines.flow.MutableStateFlow<List<com.example.yessir.model.HistoryItem>>(emptyList())
    val noteItems: kotlinx.coroutines.flow.StateFlow<List<com.example.yessir.model.HistoryItem>> = _noteItems

    private val _isHistoryLoading = kotlinx.coroutines.flow.MutableStateFlow(false)
    val isHistoryLoading: kotlinx.coroutines.flow.StateFlow<Boolean> = _isHistoryLoading

    init {
        fetchAllHistory()
    }

    private fun fetchAllHistory() {
        viewModelScope.launch {
            _isHistoryLoading.value = true
            val todoResult = repository.listItems("todo")
            val noteResult = repository.listItems("note")
            
            todoResult.onSuccess { response -> _todoItems.value = response.data }
            noteResult.onSuccess { response -> _noteItems.value = response.data }
            
            _isHistoryLoading.value = false
        }
    }

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
                    
                    // Sync new items to local cache immediately
                    val newItem = com.example.yessir.model.HistoryItem(
                        id = response.data?.get("id") as? String ?: java.util.UUID.randomUUID().toString(),
                        title = response.data?.get("title") as? String,
                        text = response.data?.get("text") as? String,
                        created_at = response.data?.get("created_at") as? String ?: java.time.LocalDateTime.now().toString()
                    )
                    
                    when (response.type) {
                        "todo" -> _todoItems.value = listOf(newItem) + _todoItems.value
                        "note" -> _noteItems.value = listOf(newItem) + _noteItems.value
                    }
                }
            }.onFailure { e ->
                 _uiState.value = VoiceUiState.Error("Command Failed", e.message)
            }
        }
    }
    
    fun reset() {
        _uiState.value = VoiceUiState.Ready
    }

    fun deleteItem(id: String, type: String) {
        viewModelScope.launch {
            val result = repository.deleteItem(id, type)
            result.onSuccess {
                // Remove from local list immediately
                when (type) {
                    "todo" -> _todoItems.value = _todoItems.value.filter { it.id != id }
                    "note" -> _noteItems.value = _noteItems.value.filter { it.id != id }
                }
            }
        }
    }
}
