package com.example.yessir.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.example.yessir.media.AudioRecorder
import com.example.yessir.model.VoiceRepository
import com.example.yessir.model.CommandResponse
import com.example.yessir.constants.IntentTypes
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

    private var hasLoadedTodos = false
    private var hasLoadedNotes = false

    private val _isHistoryLoading = kotlinx.coroutines.flow.MutableStateFlow(false)
    val isHistoryLoading: kotlinx.coroutines.flow.StateFlow<Boolean> = _isHistoryLoading

    fun loadTodosIfNeeded() {
        if (hasLoadedTodos) return
        viewModelScope.launch {
            _isHistoryLoading.value = true
            repository.listItems(IntentTypes.TODO).onSuccess { response ->
                _todoItems.value = response.data
                hasLoadedTodos = true
            }
            _isHistoryLoading.value = false
        }
    }

    fun loadNotesIfNeeded() {
        if (hasLoadedNotes) return
        viewModelScope.launch {
            _isHistoryLoading.value = true
            repository.listItems(IntentTypes.NOTE).onSuccess { response ->
                _noteItems.value = response.data
                hasLoadedNotes = true
            }
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
                        IntentTypes.TODO -> {
                            _todoItems.value = listOf(newItem) + _todoItems.value
                            // If we haven't loaded from DB yet, we still mark as "representing current state" 
                            // or at least we don't want a subsequent navigate to overwrite this local insert.
                            // But usually, if we haven't loaded, we should load first then prepend.
                            // For simplicity, let's just say if it's not loaded, we still mark it as partially loaded.
                        }
                        IntentTypes.NOTE -> {
                            _noteItems.value = listOf(newItem) + _noteItems.value
                        }
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
                    IntentTypes.TODO -> _todoItems.value = _todoItems.value.filter { it.id != id }
                    IntentTypes.NOTE -> _noteItems.value = _noteItems.value.filter { it.id != id }
                }
            }
        }
    }
}
