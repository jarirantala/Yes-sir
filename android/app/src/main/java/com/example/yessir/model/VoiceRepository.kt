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
            val bytes = file.readBytes()
            val base64String = android.util.Base64.encodeToString(bytes, android.util.Base64.NO_WRAP)
            
            // Determine content type (though backend defaults to wav, m4a is what we record)
            val contentType = if (file.name.endsWith(".m4a")) "audio/m4a" else "audio/wav"
            
            val request = AudioUploadRequest(base64String, contentType)
            val response = api.uploadAudio(request)
            
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

    suspend fun listItems(type: String): Result<ListResponse> {
        return try {
            val response = api.listItems(type = type)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("List failed: ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteItem(id: String, type: String): Result<DeleteResponse> {
        return try {
            val request = DeleteRequest(id, type)
            val response = api.deleteItem(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Delete failed: ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getKeywords(): Result<Map<String, String>> {
        return try {
            val response = api.listKeywords()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!.data)
            } else {
                Result.failure(Exception("List keywords failed: ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun saveKeyword(key: String, value: String): Result<CommandResponse> {
        return try {
            val request = KeywordRequest(key = key, value = value)
            val response = api.saveKeyword(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "No error body"
                Result.failure(Exception("Save keyword failed: ${response.code()} $errorBody"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteKeyword(key: String): Result<DeleteResponse> {
        return try {
            // Backend handler expects 'id' to be the key for keyword type
            val request = DeleteRequest(id = key, type = "keyword")
            val response = api.deleteItem(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Delete keyword failed: ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
