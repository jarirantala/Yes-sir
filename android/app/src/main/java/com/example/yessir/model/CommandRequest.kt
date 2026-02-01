package com.example.yessir.model

data class CommandRequest(
    val transcript: String,
    val timezone: String = "UTC",
    val email: String? = null
)
