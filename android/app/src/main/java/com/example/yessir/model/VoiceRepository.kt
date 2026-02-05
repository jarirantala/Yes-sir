package com.example.yessir.model

import com.example.yessir.network.RetrofitClient
import com.example.yessir.network.TranscriptResponse
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File

class VoiceRepository {
    private val api = RetrofitClient.apiService

    suspend fun transcribeAudio(file: File): Result<TranscriptResponse> {
        return try {
            val requestBody = file.asRequestBody("audio/mpeg".toMediaTypeOrNull())
            val response = api.uploadAudio(requestBody)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Upload failed: ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun sendCommand(transcript: String, timezone: String): Result<CommandResponse> {
        return try {
            val request = CommandRequest(transcript, timezone)
            val response = api.sendCommand(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Command failed: ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
