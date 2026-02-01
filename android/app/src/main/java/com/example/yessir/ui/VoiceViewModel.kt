package com.example.yessir.ui

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.yessir.model.CommandRequest
import com.example.yessir.network.RetrofitClient
import kotlinx.coroutines.launch
import java.util.TimeZone

class VoiceViewModel : ViewModel() {

    private val _uiState = MutableLiveData<String>("Ready")
    val uiState: LiveData<String> = _uiState

    fun processTranscript(transcript: String) {
        _uiState.value = "Processing: $transcript"

        viewModelScope.launch {
            try {
                val timezone = TimeZone.getDefault().id
                val request = CommandRequest(transcript = transcript, timezone = timezone)
                
                val response = RetrofitClient.apiService.sendCommand(request)
                
                if (response.isSuccessful && response.body() != null) {
                    val body = response.body()!!
                    _uiState.value = "Success: ${body.message}"
                } else {
                    _uiState.value = "Error: ${response.code()} ${response.message()}"
                }
            } catch (e: Exception) {
                _uiState.value = "Failed: ${e.localizedMessage}"
                e.printStackTrace()
            }
        }
    }
    
    fun setStatus(status: String) {
        _uiState.value = status
    }
}
