package com.example.yessir.media

import android.content.Context
import android.media.MediaRecorder
import android.os.Build
import android.util.Log
import java.io.File
import java.io.IOException

class AudioRecorder(private val context: Context) {
    private var recorder: MediaRecorder? = null
    private var currentFile: File? = null

    fun start(outputFile: File) {
        currentFile = outputFile
        
        recorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            MediaRecorder(context)
        } else {
            MediaRecorder()
        }

        recorder?.apply {
            setAudioSource(MediaRecorder.AudioSource.MIC)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            setOutputFile(outputFile.absolutePath)
            
            try {
                prepare()
                start()
            } catch (e: IOException) {
                Log.e("AudioRecorder", "prepare() failed")
            }
        }
    }

    fun stop() {
        recorder?.apply {
            try {
                stop()
            } catch (e: RuntimeException) {
                // Handle case where stop() is called immediately after start()
                Log.e("AudioRecorder", "stop() failed: ${e.message}")
            }
            release()
        }
        recorder = null
    }
    
    fun getCurrentFile(): File? = currentFile
}
