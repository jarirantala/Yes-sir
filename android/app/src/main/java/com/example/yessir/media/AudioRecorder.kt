package com.example.yessir.media

import android.annotation.SuppressLint
import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import java.io.File
import java.io.FileOutputStream
import java.io.RandomAccessFile
import kotlin.concurrent.thread

class AudioRecorder(private val context: Context) {
    private var audioRecord: AudioRecord? = null
    private var isRecording = false
    private var recordingFile: File? = null
    
    companion object {
        private const val SAMPLE_RATE = 16000
        private const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        private const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
        private val BUFFER_SIZE = AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT)
        
        private const val HEADER_SIZE = 44
    }

    @SuppressLint("MissingPermission")
    @Synchronized
    fun start(outputFile: File) {
        if (isRecording) {
            Log.w("AudioRecorder", "Recording already in progress, ignoring start()")
            return
        }

        recordingFile = outputFile
        
        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            SAMPLE_RATE,
            CHANNEL_CONFIG,
            AUDIO_FORMAT,
            BUFFER_SIZE
        )

        if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
            Log.e("AudioRecorder", "AudioRecord initialization failed")
            return
        }

        audioRecord?.startRecording()
        isRecording = true
        
        thread(name = "AudioRecorderThread") {
            writeAudioDataToFile(outputFile)
        }
    }

    private fun writeAudioDataToFile(file: File) {
        val data = ByteArray(BUFFER_SIZE)
        try {
            FileOutputStream(file).use { os ->
                // Write initial empty header
                os.write(ByteArray(HEADER_SIZE))
                
                var totalBytesWritten = 0
                while (isRecording) {
                    val read = audioRecord?.read(data, 0, BUFFER_SIZE) ?: 0
                    if (read > 0) {
                        os.write(data, 0, read)
                        totalBytesWritten += read
                    }
                }
                
                // Update header with correct sizes
                updateWavHeader(file, totalBytesWritten)
            }
        } catch (e: Exception) {
            Log.e("AudioRecorder", "Error writing audio to file: ${e.message}")
        }
    }

    private fun updateWavHeader(file: File, totalAudioLen: Int) {
        val totalDataLen = totalAudioLen + 36
        val byteRate = SAMPLE_RATE * 2 // 16 bit * 1 channel / 8 bits per byte

        RandomAccessFile(file, "rw").use { raf ->
            val header = ByteArray(HEADER_SIZE)
            // RIFF chunk descriptor
            header[0] = 'R'.code.toByte()
            header[1] = 'I'.code.toByte()
            header[2] = 'F'.code.toByte()
            header[3] = 'F'.code.toByte()
            header[4] = (totalDataLen and 0xff).toByte()
            header[5] = (totalDataLen shr 8 and 0xff).toByte()
            header[6] = (totalDataLen shr 16 and 0xff).toByte()
            header[7] = (totalDataLen shr 24 and 0xff).toByte()
            // WAVE chunk
            header[8] = 'W'.code.toByte()
            header[9] = 'A'.code.toByte()
            header[10] = 'V'.code.toByte()
            header[11] = 'E'.code.toByte()
            // fmt sub-chunk
            header[12] = 'f'.code.toByte()
            header[13] = 'm'.code.toByte()
            header[14] = 't'.code.toByte()
            header[15] = ' '.code.toByte()
            header[16] = 16 // SubChunk1Size (16 for PCM)
            header[17] = 0
            header[18] = 0
            header[19] = 0
            header[20] = 1 // AudioFormat (1 for PCM)
            header[21] = 0
            header[22] = 1 // NumChannels (1 for Mono)
            header[23] = 0
            header[24] = (SAMPLE_RATE and 0xff).toByte()
            header[25] = (SAMPLE_RATE shr 8 and 0xff).toByte()
            header[26] = (SAMPLE_RATE shr 16 and 0xff).toByte()
            header[27] = (SAMPLE_RATE shr 24 and 0xff).toByte()
            header[28] = (byteRate and 0xff).toByte()
            header[29] = (byteRate shr 8 and 0xff).toByte()
            header[30] = (byteRate shr 16 and 0xff).toByte()
            header[31] = (byteRate shr 24 and 0xff).toByte()
            header[32] = 2 // BlockAlign (NumChannels * BitsPerSample / 8)
            header[33] = 0
            header[34] = 16 // BitsPerSample
            header[35] = 0
            // data sub-chunk
            header[36] = 'd'.code.toByte()
            header[37] = 'a'.code.toByte()
            header[38] = 't'.code.toByte()
            header[39] = 'a'.code.toByte()
            header[40] = (totalAudioLen and 0xff).toByte()
            header[41] = (totalAudioLen shr 8 and 0xff).toByte()
            header[42] = (totalAudioLen shr 16 and 0xff).toByte()
            header[43] = (totalAudioLen shr 24 and 0xff).toByte()

            raf.seek(0)
            raf.write(header)
        }
    }

    @Synchronized
    fun stop() {
        if (!isRecording) return
        
        isRecording = false
        audioRecord?.apply {
            try {
                stop()
            } catch (e: Exception) {
                Log.e("AudioRecorder", "Error stopping AudioRecord: ${e.message}")
            } finally {
                release()
            }
        }
        audioRecord = null
    }
    
    fun getCurrentFile(): File? = recordingFile
}
