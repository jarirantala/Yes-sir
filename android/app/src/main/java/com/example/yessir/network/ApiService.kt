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
}
