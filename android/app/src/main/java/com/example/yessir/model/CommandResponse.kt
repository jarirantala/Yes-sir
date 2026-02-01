package com.example.yessir.model

data class CommandResponse(
    val type: String, // "meeting", "todo", "error"
    val message: String,
    val data: Any? = null
)
