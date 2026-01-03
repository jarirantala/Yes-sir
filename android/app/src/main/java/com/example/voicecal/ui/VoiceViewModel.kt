package com.example.voicecal.ui

import android.app.Application
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.util.Log
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.voicecal.model.MeetingRequest
import com.example.voicecal.network.ApiService
import kotlinx.coroutines.launch
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.Locale
import java.util.TimeZone

class VoiceViewModel(application: Application) : AndroidViewModel(application) {

    private val TAG = "VoiceViewModel"

    var state by mutableStateOf(VoiceState())
        private set

    private var speechRecognizer: SpeechRecognizer? = null
    
    private val api: ApiService = Retrofit.Builder()
        .baseUrl("https://api.example.com/") 
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(ApiService::class.java)

    init {
        val available = SpeechRecognizer.isRecognitionAvailable(application)
        if (available) {
            setupSpeechRecognizer(application)
        } else {
            state = state.copy(status = "Speech Recognition Not Available")
        }
    }

    private fun setupSpeechRecognizer(application: Application) {
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(application).apply {
            setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {
                    Log.d(TAG, "onReadyForSpeech")
                    state = state.copy(status = "Listening...")
                }
                override fun onBeginningOfSpeech() {
                    Log.d(TAG, "onBeginningOfSpeech")
                }
                override fun onRmsChanged(rmsdB: Float) {}
                override fun onBufferReceived(buffer: ByteArray?) {}
                override fun onEndOfSpeech() {
                    Log.d(TAG, "onEndOfSpeech")
                    state = state.copy(status = "Processing...")
                }
                override fun onError(error: Int) {
                    Log.e(TAG, "Speech Error: $error")
                    val errorMessage = when(error) {
                        SpeechRecognizer.ERROR_NO_MATCH -> "No match (Check Mic)"
                        SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Mic Permission Denied"
                        else -> "Speech Error: $error"
                    }
                    state = state.copy(status = errorMessage, isRecording = false)
                }
                override fun onResults(results: Bundle?) {
                    val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    val transcript = matches?.firstOrNull()
                    Log.d(TAG, "onResults: $transcript")
                    if (transcript != null) {
                        state = state.copy(transcript = transcript, isRecording = false)
                        sendInvite(transcript)
                    }
                }
                override fun onPartialResults(partialResults: Bundle?) {}
                override fun onEvent(eventType: Int, params: Bundle?) {}
            })
        }
    }

    fun startRecording() {
        if (speechRecognizer == null) return
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.US.toString())
        }
        speechRecognizer?.startListening(intent)
        state = state.copy(isRecording = true, status = "Listening...")
    }

    fun stopRecording() {
        speechRecognizer?.stopListening()
        state = state.copy(isRecording = false)
    }

    // New: Helper to test the rest of the app without a working mic
    fun simulateTranscript(mockText: String) {
        Log.d(TAG, "Simulating transcript: $mockText")
        state = state.copy(transcript = mockText, isRecording = false)
        sendInvite(mockText)
    }

    private fun sendInvite(transcript: String) {
        viewModelScope.launch {
            state = state.copy(status = "Sending...")
            try {
                val response = api.sendInvite(MeetingRequest(transcript, TimeZone.getDefault().id))
                state = state.copy(status = if (response.isSuccessful) "Success" else "Error: ${response.code()}")
            } catch (e: Exception) {
                state = state.copy(status = "Network Error")
                Log.e(TAG, "Network Error", e)
            }
        }
    }
}

data class VoiceState(
    val isRecording: Boolean = false,
    val transcript: String = "",
    val status: String = "Hold to Speak"
)
