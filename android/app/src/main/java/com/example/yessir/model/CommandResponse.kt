package com.example.yessir.model

import com.google.gson.annotations.SerializedName

data class CommandResponse(
    val type: String?,
    val message: String,
    @SerializedName("parsed_data")
    val parsedData: Map<String, Any>?,
    val data: Map<String, Any>?,
    val error: String?,
    val details: String?
)
