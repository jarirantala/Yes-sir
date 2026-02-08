package com.example.yessir.network

import com.example.yessir.model.CommandRequest
import com.example.yessir.model.CommandResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.Headers
import retrofit2.http.POST

interface ApiService {
    @POST(".")
    @Headers("Content-Type: application/json")
    suspend fun sendCommand(@Body request: CommandRequest): Response<CommandResponse>

    @POST(".")
    @Headers("Content-Type: application/json")
    suspend fun uploadAudio(@Body request: com.example.yessir.model.AudioUploadRequest): Response<TranscriptResponse>

    @retrofit2.http.GET(".")
    suspend fun listItems(
        @retrofit2.http.Query("action") action: String = "list",
        @retrofit2.http.Query("type") type: String
    ): Response<com.example.yessir.model.ListResponse>

    @retrofit2.http.HTTP(method = "DELETE", path = ".", hasBody = true)
    suspend fun deleteItem(@Body request: com.example.yessir.model.DeleteRequest): Response<com.example.yessir.model.DeleteResponse>
}

data class TranscriptResponse(val transcript: String)
