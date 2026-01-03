package com.example.voicecal.network

import com.example.voicecal.model.MeetingRequest
import com.example.voicecal.model.MeetingResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface ApiService {
    @POST("invite")
    suspend fun sendInvite(@Body request: MeetingRequest): Response<MeetingResponse>
}
